#!/usr/bin/env python3
"""
Abstract Base Class for LLM Providers

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing

Defines the interface that all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import hashlib
import json
import re
from datetime import datetime, timedelta
from loguru import logger


class LLMProviderBase(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, config):
        """
        Initialize the LLM provider.

        Args:
            config: Configuration object with LLM settings
        """
        self.config = config
        self.timeout = config.LLM_TIMEOUT
        self.max_retries = config.LLM_MAX_RETRIES
        self.default_model = config.LLM_DEFAULT_MODEL
        self.cache = {}
        self.cache_ttl = config.CACHE_TTL

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider"""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test connection to the LLM service.

        Returns:
            True if connection successful, raises exception otherwise
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get list of available models.

        Returns:
            List of model names/identifiers
        """
        pass

    @abstractmethod
    def _call_api(self, prompt: str, model: str = None) -> str:
        """
        Make API call to the LLM service.

        Args:
            prompt: The prompt to send to the LLM
            model: Optional model override

        Returns:
            The raw response text from the LLM
        """
        pass

    def generate_sql(self, question: str, schema_context: Dict[str, Any],
                     user_role: str, security_mode: str = 'vulnerable') -> str:
        """
        Generate SQL from natural language question.

        Args:
            question: Natural language question
            schema_context: Database schema information
            user_role: Role of the user making the request
            security_mode: 'vulnerable' or 'secure'

        Returns:
            Generated SQL query
        """
        cache_key = self._get_cache_key(question, user_role, security_mode, schema_context)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            logger.info("Returning cached SQL result")
            return cached_result

        prompt = self._build_prompt(question, schema_context, user_role, security_mode)

        import time
        start_time = time.time()

        try:
            sql_query = self._call_api(prompt)
            sql_query = self._post_process_sql(sql_query, user_role, security_mode)

            generation_time = time.time() - start_time
            logger.info(f"SQL generated in {generation_time:.3f}s using {self.provider_name}")

            self._cache_result(cache_key, sql_query)

            return sql_query

        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(f"SQL generation failed in {generation_time:.3f}s: {str(e)}")
            raise

    def _build_prompt(self, question: str, schema_context: Dict[str, Any],
                      user_role: str, security_mode: str) -> str:
        """Build security-aware prompt for SQL generation"""

        base_prompt = """You are a SQL query generator for a healthcare database system.

DATABASE SCHEMA:
"""

        for table_name, table_info in schema_context.items():
            base_prompt += f"\nTable: {table_name}\n"
            base_prompt += f"Description: {table_info.get('description', '')}\n"
            base_prompt += "Columns:\n"

            for column in table_info.get('columns', []):
                base_prompt += f"  - {column['name']} ({column['type']})\n"

        base_prompt += f"\nUSER CONTEXT:\n"
        base_prompt += f"Role: {user_role}\n"
        base_prompt += f"Security Mode: {security_mode}\n"

        if security_mode == 'secure':
            base_prompt += self._get_secure_prompt_instructions(user_role)
        else:
            base_prompt += self._get_vulnerable_prompt_instructions()

        base_prompt += f"\nUSER QUESTION: {question}\n"
        base_prompt += "\nGenerate ONLY the SQL query, no explanations or markdown formatting:"

        return base_prompt

    def _get_secure_prompt_instructions(self, user_role: str) -> str:
        """Get security-focused prompt instructions"""
        instructions = """
SECURITY GUIDELINES:
- Generate only SELECT statements (no INSERT, UPDATE, DELETE, DROP)
- Use parameterized queries when possible
- Avoid UNION operations that could expose unauthorized data
- Respect role-based access controls
- Do not include sensitive columns unless explicitly authorized
- Add appropriate WHERE clauses to limit data access
- Validate all user inputs in the generated query

ROLE-BASED ACCESS RULES:
"""

        role_rules = {
            'patient': """
- Can only access their own patient records
- No access to other patients' data
- Limited to basic medical information
- Cannot access administrative data
""",
            'nurse': """
- Can access basic patient information
- Limited medical record access
- No access to administrative functions
- Cannot see highly sensitive data like SSNs
""",
            'doctor': """
- Full access to patient medical data
- Can access diagnostic and treatment information
- Limited administrative access
- Cannot access system authentication data
""",
            'admin': """
- Full system access for administrative purposes
- Can access audit logs and system data
- Responsible for maintaining security controls
"""
        }

        instructions += role_rules.get(user_role, role_rules['patient'])

        return instructions

    def _get_vulnerable_prompt_instructions(self) -> str:
        """Get minimal security prompt for vulnerability testing"""
        return """
GUIDELINES:
- Generate SQL queries based on the user request
- Focus on retrieving the requested information
- Use straightforward SQL without complex security checks
"""

    def _post_process_sql(self, sql_response: str, user_role: str, security_mode: str) -> str:
        """Post-process and validate generated SQL"""

        sql_query = sql_response.strip()

        # Remove markdown code blocks if present
        sql_query = re.sub(r'^```sql\s*', '', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'^```\s*', '', sql_query)
        sql_query = re.sub(r'\s*```$', '', sql_query)

        sql_query = sql_query.strip()

        # Extract SELECT statement if response contains extra text
        if not sql_query.upper().startswith('SELECT'):
            select_match = re.search(r'(SELECT\s+.*?)(?:;|\n\n|$)', sql_query, re.IGNORECASE | re.DOTALL)
            if select_match:
                sql_query = select_match.group(1).strip()
            else:
                raise ValueError("Generated response does not contain a valid SELECT statement")

        # Ensure query ends with semicolon
        if not sql_query.endswith(';'):
            sql_query += ';'

        # Apply security filters in secure mode
        if security_mode == 'secure':
            sql_query = self._apply_security_filters(sql_query, user_role)

        # Validate the generated SQL
        self._validate_generated_sql(sql_query, user_role, security_mode)

        return sql_query

    def _apply_security_filters(self, sql_query: str, user_role: str) -> str:
        """Apply role-based security filters to SQL"""

        if user_role == 'patient':
            # Add patient ID filter if querying patients table
            if 'patients' in sql_query.lower() and 'where' not in sql_query.lower():
                if sql_query.endswith(';'):
                    sql_query = sql_query[:-1] + ' WHERE patient_id = {user_patient_id};'
                else:
                    sql_query += ' WHERE patient_id = {user_patient_id}'

        elif user_role == 'nurse':
            # Redact sensitive columns for nurses
            sensitive_columns = ['ssn', 'license_number', 'password_hash']
            for col in sensitive_columns:
                pattern = rf'\b{col}\b'
                if re.search(pattern, sql_query, re.IGNORECASE):
                    sql_query = re.sub(pattern, f"'***REDACTED***' as {col}", sql_query, flags=re.IGNORECASE)

        return sql_query

    def _validate_generated_sql(self, sql_query: str, user_role: str, security_mode: str):
        """Validate generated SQL for security and correctness"""

        # Check for dangerous operations
        dangerous_patterns = [
            r'\bdrop\s+table\b',
            r'\bdelete\s+from\b',
            r'\bupdate\s+.*\bset\b',
            r'\binsert\s+into\b',
            r'\balter\s+table\b',
            r'\bcreate\s+table\b',
            r'\btruncate\s+table\b',
            r'\bexec\b',
            r'\bexecute\b',
            r'\bxp_cmdshell\b'
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                raise ValueError(f"Generated SQL contains potentially dangerous operation: {pattern}")

        # Additional validation for secure mode
        if security_mode == 'secure' and user_role != 'admin':
            union_pattern = r'\bunion\s+(all\s+)?select\b'
            if re.search(union_pattern, sql_query, re.IGNORECASE):
                logger.warning("Generated SQL contains UNION operation in secure mode")

        # Basic SQL format validation
        basic_sql_pattern = r'^\s*select\s+.+\s+from\s+\w+.*;\s*$'
        if not re.match(basic_sql_pattern, sql_query, re.IGNORECASE | re.DOTALL):
            logger.warning("Generated SQL may not follow expected SELECT format")

    def _get_cache_key(self, question: str, user_role: str, security_mode: str,
                       schema_context: Dict[str, Any] = None) -> str:
        """Generate cache key for query results"""
        schema_hash = ""
        if schema_context:
            schema_json = json.dumps(schema_context, sort_keys=True)
            schema_hash = hashlib.md5(schema_json.encode()).hexdigest()

        key_string = f"{question}:{user_role}:{security_mode}:{schema_hash}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[str]:
        """Get cached result if still valid"""
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cached_data['result']
            else:
                del self.cache[cache_key]
        return None

    def _cache_result(self, cache_key: str, result: str):
        """Cache query result"""
        self.cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now()
        }

        # Limit cache size
        if len(self.cache) > 100:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]

    def clear_cache(self):
        """Clear the query cache"""
        self.cache.clear()
        logger.info("LLM query cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        valid_entries = 0
        expired_entries = 0

        current_time = datetime.now()
        for cached_data in self.cache.values():
            if current_time - cached_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                valid_entries += 1
            else:
                expired_entries += 1

        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_ttl': self.cache_ttl
        }

    def analyze_prompt_injection(self, question: str) -> Dict[str, Any]:
        """Analyze question for potential prompt injection attempts"""
        injection_patterns = [
            r'ignore\s+previous\s+instructions',
            r'forget\s+everything',
            r'new\s+instructions',
            r'system\s*:',
            r'assistant\s*:',
            r'user\s*:',
            r'role\s*:.*admin',
            r'you\s+are\s+now',
            r'pretend\s+to\s+be',
            r'act\s+as\s+if',
            r'instead\s+of.*sql'
        ]

        risk_score = 0
        detected_patterns = []

        question_lower = question.lower()

        for pattern in injection_patterns:
            if re.search(pattern, question_lower):
                risk_score += 1
                detected_patterns.append(pattern)

        # SQL injection patterns
        sql_injection_patterns = [
            r"'\s*or\s*'1'\s*=\s*'1",
            r"'\s*or\s*1\s*=\s*1",
            r"union\s+select",
            r";\s*drop\s+table",
            r";\s*delete\s+from",
            r"--\s*",
            r"/\*.*\*/"
        ]

        for pattern in sql_injection_patterns:
            if re.search(pattern, question_lower):
                risk_score += 2
                detected_patterns.append(f"SQL injection: {pattern}")

        risk_level = 'LOW'
        if risk_score >= 3:
            risk_level = 'HIGH'
        elif risk_score >= 1:
            risk_level = 'MEDIUM'

        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'detected_patterns': detected_patterns,
            'recommendation': self._get_injection_recommendation(risk_level)
        }

    def _get_injection_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on injection risk level"""
        recommendations = {
            'LOW': 'Question appears safe to process',
            'MEDIUM': 'Question contains suspicious patterns - review before processing',
            'HIGH': 'Question likely contains injection attempt - block or sanitize'
        }
        return recommendations.get(risk_level, 'Unknown risk level')

    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for LLM service"""
        health_data = {
            'provider': self.provider_name,
            'connection': False,
            'available_models': [],
            'default_model_available': False,
            'cache_stats': self.get_cache_stats(),
            'config': {
                'default_model': self.default_model,
                'timeout': self.timeout,
                'max_retries': self.max_retries
            }
        }

        try:
            health_data['connection'] = self.test_connection()
            health_data['available_models'] = self.get_available_models()
            health_data['default_model_available'] = self.default_model in health_data['available_models']

        except Exception as e:
            health_data['error'] = str(e)

        return health_data
