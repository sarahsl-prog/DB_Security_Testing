#!/usr/bin/env python3
"""
LLM Client for Ollama Integration

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/Database_Security_TestApp

Handles communication with Ollama LLM service on Windows host for
natural language to SQL conversion with security-aware prompting.
"""

import requests
import json
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin
import hashlib
from loguru import logger

from config import Config


class LLMClient:
    """Client for Ollama LLM service with security research features"""
    
    def __init__(self):
        self.base_url = Config.LLM_BASE_URL
        self.default_model = Config.LLM_DEFAULT_MODEL
        self.timeout = Config.LLM_TIMEOUT
        self.max_retries = Config.LLM_MAX_RETRIES
        self.cache = {}
        self.cache_ttl = Config.CACHE_TTL

        logger.info(f"LLM Client initialized for {self.base_url}")
        logger.debug(f"LLM Configuration: model={self.default_model}, timeout={self.timeout}s, max_retries={self.max_retries}")
    
    def test_connection(self) -> bool:
        """Test connection to Ollama service"""
        try:
            logger.info(f"Testing connection to Ollama LLM service at {self.base_url}")
            start_time = time.time()

            response = requests.get(
                urljoin(self.base_url, '/api/tags'),
                timeout=5
            )
            response.raise_for_status()

            elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

            models = response.json().get('models', [])
            model_names = [model.get('name', 'unknown') for model in models]

            logger.success(f"Ollama LLM connection successful ({elapsed_time:.2f}ms)")
            logger.info(f"Available models ({len(models)}): {', '.join(model_names[:5])}")

            if self.default_model not in model_names:
                logger.warning(f"Default model '{self.default_model}' not found in available models")

            return True

        except requests.exceptions.Timeout:
            logger.error(f"Ollama LLM connection timeout after 5s to {self.base_url}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ollama LLM connection failed - Cannot reach {self.base_url}: {str(e)}")
            logger.exception("LLM connection error details")
            raise
        except Exception as e:
            logger.error(f"Ollama LLM connection failed: {str(e)}")
            logger.exception("LLM connection error details")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get(
                urljoin(self.base_url, '/api/tags'),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            models_data = response.json().get('models', [])
            models = [model['name'] for model in models_data]
            
            logger.info(f"Available models: {models}")
            return models
            
        except Exception as e:
            logger.error(f"Failed to get available models: {str(e)}")
            return []
    
    def generate_sql(self, question: str, schema_context: Dict[str, Any], 
                     user_role: str, security_mode: str = 'vulnerable') -> str:
        """Generate SQL from natural language question"""
        
        cache_key = self._get_cache_key(question, user_role, security_mode, schema_context)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            logger.info("Returning cached SQL result")
            return cached_result
        
        prompt = self._build_prompt(question, schema_context, user_role, security_mode)
        
        start_time = time.time()
        
        try:
            sql_query = self._call_ollama(prompt)
            sql_query = self._post_process_sql(sql_query, user_role, security_mode)
            
            generation_time = time.time() - start_time
            logger.info(f"SQL generated in {generation_time:.3f}s")
            
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
    
    def _call_ollama(self, prompt: str, model: str = None) -> str:
        """Make API call to Ollama service with retry logic"""
        if model is None:
            model = self.default_model

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for consistent SQL generation
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 256  # Limit response length
            }
        }

        logger.info(f"Calling Ollama LLM API with model: {model}")
        logger.debug(f"Prompt length: {len(prompt)} characters")

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Ollama API call attempt {attempt + 1}/{self.max_retries}")
                start_time = time.time()

                response = requests.post(
                    urljoin(self.base_url, '/api/generate'),
                    json=payload,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )

                response.raise_for_status()

                result = response.json()

                if 'response' not in result:
                    raise ValueError("Invalid response format from Ollama")

                sql_response = result['response'].strip()

                if not sql_response:
                    raise ValueError("Empty response from Ollama")

                elapsed_time = time.time() - start_time
                logger.success(f"Ollama LLM response received in {elapsed_time:.3f}s ({len(sql_response)} characters)")
                logger.debug(f"Generated response preview: {sql_response[:100]}...")

                return sql_response

            except requests.exceptions.Timeout:
                wait_time = 2 ** attempt
                logger.warning(f"Ollama API timeout on attempt {attempt + 1}/{self.max_retries} (waited {self.timeout}s)")
                if attempt == self.max_retries - 1:
                    logger.error(f"Ollama API timeout after all {self.max_retries} retries")
                    raise TimeoutError("Ollama API timeout after all retries")
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)  # Exponential backoff

            except requests.exceptions.ConnectionError as e:
                wait_time = 2 ** attempt
                logger.warning(f"Ollama connection error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Cannot connect to Ollama service after {self.max_retries} retries")
                    raise ConnectionError("Cannot connect to Ollama service")
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)

            except Exception as e:
                logger.error(f"Ollama API error on attempt {attempt + 1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.exception("Final LLM API error details")
                    raise
                time.sleep(1)
    
    def _post_process_sql(self, sql_response: str, user_role: str, security_mode: str) -> str:
        """Post-process and validate generated SQL"""
        
        sql_query = sql_response.strip()
        
        sql_query = re.sub(r'^```sql\s*', '', sql_query, flags=re.IGNORECASE)
        sql_query = re.sub(r'^```\s*', '', sql_query)
        sql_query = re.sub(r'\s*```$', '', sql_query)
        
        sql_query = sql_query.strip()
        
        if not sql_query.upper().startswith('SELECT'):
            
            select_match = re.search(r'(SELECT\s+.*?)(?:;|\n\n|$)', sql_query, re.IGNORECASE | re.DOTALL)
            if select_match:
                sql_query = select_match.group(1).strip()
            else:
                raise ValueError("Generated response does not contain a valid SELECT statement")
        
        if not sql_query.endswith(';'):
            sql_query += ';'
        
        if security_mode == 'secure':
            sql_query = self._apply_security_filters(sql_query, user_role)
        
        self._validate_generated_sql(sql_query, user_role, security_mode)
        
        return sql_query
    
    def _apply_security_filters(self, sql_query: str, user_role: str) -> str:
        """Apply role-based security filters to SQL"""
        
        if user_role == 'patient':
            
            if 'patients' in sql_query.lower() and 'where' not in sql_query.lower():
                if sql_query.endswith(';'):
                    sql_query = sql_query[:-1] + ' WHERE patient_id = {user_patient_id};'
                else:
                    sql_query += ' WHERE patient_id = {user_patient_id}'
        
        elif user_role == 'nurse':
            
            sensitive_columns = ['ssn', 'license_number', 'password_hash']
            for col in sensitive_columns:
                pattern = rf'\b{col}\b'
                if re.search(pattern, sql_query, re.IGNORECASE):
                    sql_query = re.sub(pattern, f"'***REDACTED***' as {col}", sql_query, flags=re.IGNORECASE)
        
        return sql_query
    
    def _validate_generated_sql(self, sql_query: str, user_role: str, security_mode: str):
        """Validate generated SQL for security and correctness"""
        
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
        
        if security_mode == 'secure' and user_role != 'admin':
            union_pattern = r'\bunion\s+(all\s+)?select\b'
            if re.search(union_pattern, sql_query, re.IGNORECASE):
                logger.warning("Generated SQL contains UNION operation in secure mode")
        
        basic_sql_pattern = r'^\s*select\s+.+\s+from\s+\w+.*;\s*$'
        if not re.match(basic_sql_pattern, sql_query, re.IGNORECASE | re.DOTALL):
            logger.warning("Generated SQL may not follow expected SELECT format")
    
    def _get_cache_key(self, question: str, user_role: str, security_mode: str, schema_context: Dict[str, Any] = None) -> str:
        """Generate cache key for query results"""
        # CRITICAL FIX: Include schema context hash to detect schema changes
        # This prevents returning stale cached results when schema is modified
        schema_hash = ""
        if schema_context:
            # Generate deterministic hash of schema context
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
            'ollama_connection': False,
            'available_models': [],
            'default_model_available': False,
            'cache_stats': self.get_cache_stats(),
            'config': {
                'base_url': self.base_url,
                'default_model': self.default_model,
                'timeout': self.timeout,
                'max_retries': self.max_retries
            }
        }
        
        try:
            health_data['ollama_connection'] = self.test_connection()
            health_data['available_models'] = self.get_available_models()
            health_data['default_model_available'] = self.default_model in health_data['available_models']
            
        except Exception as e:
            health_data['error'] = str(e)
        
        return health_data