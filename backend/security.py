#!/usr/bin/env python3
"""
Security Validation and Controls for Healthcare Security Research API

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/Database_Security_TestApp

Implements both vulnerable and secure modes for security research,
including SQL injection detection, role-based access controls,
and comprehensive security monitoring.
"""

import re
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib
import json
from loguru import logger

from config import Config
from models import SecurityEvent, QueryResult


class SecurityMode(Enum):
    """Security mode enumeration"""
    VULNERABLE = "vulnerable"
    SECURE = "secure"


class SecurityManager:
    """Manages security controls and validation for research purposes"""
    
    def __init__(self):
        self.current_mode = SecurityMode.VULNERABLE
        self.security_events = []
        self.blocked_queries = []
        self.sql_injection_patterns = Config.SQL_INJECTION_PATTERNS
        self.sensitive_columns = Config.SENSITIVE_COLUMNS
        self.role_permissions = Config.ROLE_PERMISSIONS
        
        logger.info(f"Security Manager initialized in {self.current_mode.value} mode")
    
    def set_mode(self, mode: SecurityMode):
        """Set security mode for testing"""
        old_mode = self.current_mode
        self.current_mode = mode
        
        event = SecurityEvent(
            event_type='SECURITY_MODE_CHANGE',
            severity='MEDIUM',
            message=f'Security mode changed from {old_mode.value} to {mode.value}',
            details={'old_mode': old_mode.value, 'new_mode': mode.value}
        )
        self.log_security_event(event)
        
        logger.info(f"Security mode changed to {mode.value}")
    
    def get_current_mode(self) -> SecurityMode:
        """Get current security mode"""
        return self.current_mode
    
    def validate_question(self, question: str, user_role: str) -> Dict[str, Any]:
        """Validate natural language question for security issues"""
        validation_result = {
            'valid': True,
            'warnings': [],
            'reason': None,
            'risk_score': 0
        }
        
        if self.current_mode == SecurityMode.VULNERABLE:
            return validation_result
        
        question_lower = question.lower().strip()
        
        prompt_injection_result = self._detect_prompt_injection(question)
        if prompt_injection_result['detected']:
            validation_result['warnings'].extend(prompt_injection_result['warnings'])
            validation_result['risk_score'] += prompt_injection_result['risk_score']
        
        sql_injection_result = self._detect_sql_injection_in_question(question)
        if sql_injection_result['detected']:
            validation_result['warnings'].extend(sql_injection_result['warnings'])
            validation_result['risk_score'] += sql_injection_result['risk_score']
        
        privilege_escalation_result = self._detect_privilege_escalation(question, user_role)
        if privilege_escalation_result['detected']:
            validation_result['warnings'].extend(privilege_escalation_result['warnings'])
            validation_result['risk_score'] += privilege_escalation_result['risk_score']
        
        if validation_result['risk_score'] >= 5:
            validation_result['valid'] = False
            validation_result['reason'] = 'High-risk security patterns detected'
            
            event = SecurityEvent(
                event_type='QUESTION_BLOCKED',
                severity='HIGH',
                message=f'Question blocked due to security concerns: {question[:100]}...',
                details={
                    'question': question,
                    'user_role': user_role,
                    'risk_score': validation_result['risk_score'],
                    'warnings': validation_result['warnings']
                }
            )
            self.log_security_event(event)
        
        return validation_result
    
    def validate_sql(self, sql_query: str, user_role: str) -> Dict[str, Any]:
        """Validate generated SQL query for security compliance"""
        validation_result = {
            'valid': True,
            'warnings': [],
            'reason': None,
            'risk_score': 0
        }
        
        if self.current_mode == SecurityMode.VULNERABLE:
            return validation_result
        
        sql_lower = sql_query.lower().strip()
        
        dangerous_operations = self._check_dangerous_operations(sql_query)
        if dangerous_operations['detected']:
            validation_result['valid'] = False
            validation_result['reason'] = 'Dangerous SQL operations detected'
            validation_result['warnings'].extend(dangerous_operations['warnings'])
            validation_result['risk_score'] += dangerous_operations['risk_score']
        
        injection_patterns = self._check_sql_injection_patterns(sql_query)
        if injection_patterns['detected']:
            validation_result['warnings'].extend(injection_patterns['warnings'])
            validation_result['risk_score'] += injection_patterns['risk_score']
        
        union_attacks = self._check_union_attacks(sql_query, user_role)
        if union_attacks['detected']:
            validation_result['warnings'].extend(union_attacks['warnings'])
            validation_result['risk_score'] += union_attacks['risk_score']
            
            if user_role != 'admin':
                validation_result['valid'] = False
                validation_result['reason'] = 'UNION operations not allowed for this role'
        
        unauthorized_tables = self._check_table_access(sql_query, user_role)
        if unauthorized_tables['detected']:
            validation_result['valid'] = False
            validation_result['reason'] = 'Access to unauthorized tables detected'
            validation_result['warnings'].extend(unauthorized_tables['warnings'])
            validation_result['risk_score'] += unauthorized_tables['risk_score']
        
        sensitive_data = self._check_sensitive_data_access(sql_query, user_role)
        if sensitive_data['detected']:
            validation_result['warnings'].extend(sensitive_data['warnings'])
            validation_result['risk_score'] += sensitive_data['risk_score']
            
            if user_role not in ['admin', 'doctor']:
                validation_result['valid'] = False
                validation_result['reason'] = 'Access to sensitive data not authorized'
        
        if not validation_result['valid']:
            event = SecurityEvent(
                event_type='SQL_BLOCKED',
                severity='HIGH',
                message=f'SQL query blocked: {validation_result["reason"]}',
                details={
                    'sql_query': sql_query,
                    'user_role': user_role,
                    'risk_score': validation_result['risk_score'],
                    'warnings': validation_result['warnings']
                }
            )
            self.log_security_event(event)
            self.blocked_queries.append({
                'query': sql_query,
                'user_role': user_role,
                'reason': validation_result['reason'],
                'timestamp': datetime.utcnow()
            })
        
        return validation_result
    
    def filter_schema_by_role(self, schema: Dict[str, Any], user_role: str) -> Dict[str, Any]:
        """Filter database schema based on user role"""
        if self.current_mode == SecurityMode.VULNERABLE or user_role == 'admin':
            return schema
        
        allowed_tables = self.role_permissions.get(user_role, {}).get('tables', [])
        filtered_schema = {}
        
        for table_name, table_info in schema.items():
            if table_name in allowed_tables:
                filtered_table = table_info.copy()
                
                allowed_columns = self.role_permissions.get(user_role, {}).get('columns', {}).get(table_name, [])
                if allowed_columns != '*':
                    filtered_columns = []
                    for column in table_info.get('columns', []):
                        if column['name'] in allowed_columns:
                            filtered_columns.append(column)
                    filtered_table['columns'] = filtered_columns
                
                if user_role in ['nurse', 'patient']:
                    filtered_columns = []
                    for column in filtered_table.get('columns', []):
                        if column['name'].lower() not in [col.lower() for col in self.sensitive_columns]:
                            filtered_columns.append(column)
                    filtered_table['columns'] = filtered_columns
                
                filtered_schema[table_name] = filtered_table
        
        return filtered_schema
    
    def filter_results_by_role(self, results: List[Dict[str, Any]], user_role: str, user_patient_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Filter query results based on user role"""
        if self.current_mode == SecurityMode.VULNERABLE or user_role == 'admin':
            return results
        
        filtered_results = []
        
        for row in results:
            # CRITICAL FIX: Row-level filtering for patient role
            # Patient role should only see their own records
            if user_role == 'patient' and user_patient_id:
                # Check if this row belongs to the patient
                row_patient_id = row.get('patient_id')
                if row_patient_id is not None and row_patient_id != user_patient_id:
                    # Skip this row - it doesn't belong to this patient
                    continue
            
            # Column-level filtering (redaction of sensitive data)
            filtered_row = {}
            
            for column, value in row.items():
                if user_role == 'patient':
                    if column.lower() in [col.lower() for col in self.sensitive_columns]:
                        filtered_row[column] = '***RESTRICTED***'
                    else:
                        filtered_row[column] = value
                
                elif user_role == 'nurse':
                    restricted_columns = ['ssn', 'license_number', 'password_hash']
                    if column.lower() in [col.lower() for col in restricted_columns]:
                        filtered_row[column] = '***REDACTED***'
                    else:
                        filtered_row[column] = value
                
                elif user_role == 'doctor':
                    admin_columns = ['password_hash']
                    if column.lower() in [col.lower() for col in admin_columns]:
                        filtered_row[column] = '***REDACTED***'
                    else:
                        filtered_row[column] = value
                
                else:
                    filtered_row[column] = value
            
            filtered_results.append(filtered_row)
        
        return filtered_results
    
    def _detect_prompt_injection(self, question: str) -> Dict[str, Any]:
        """Detect prompt injection attempts"""
        result = {
            'detected': False,
            'warnings': [],
            'risk_score': 0
        }
        
        injection_patterns = [
            (r'ignore\s+previous\s+instructions', 'Instruction override attempt'),
            (r'forget\s+everything', 'Memory reset attempt'),
            (r'new\s+instructions', 'Instruction replacement attempt'),
            (r'system\s*:', 'System prompt injection'),
            (r'assistant\s*:', 'Assistant impersonation'),
            (r'role\s*:.*admin', 'Role escalation attempt'),
            (r'you\s+are\s+now', 'Identity change attempt'),
            (r'pretend\s+to\s+be', 'Impersonation attempt'),
            (r'act\s+as\s+if', 'Behavior modification attempt'),
            (r'instead\s+of.*sql', 'Task redirection attempt')
        ]
        
        question_lower = question.lower()
        
        for pattern, description in injection_patterns:
            if re.search(pattern, question_lower):
                result['detected'] = True
                result['warnings'].append(f'Prompt injection detected: {description}')
                result['risk_score'] += 2
        
        return result
    
    def _detect_sql_injection_in_question(self, question: str) -> Dict[str, Any]:
        """Detect SQL injection patterns in natural language question"""
        result = {
            'detected': False,
            'warnings': [],
            'risk_score': 0
        }
        
        sql_patterns = [
            (r"'\s*or\s*'1'\s*=\s*'1", 'Classic SQL injection pattern'),
            (r"'\s*or\s*1\s*=\s*1", 'Numeric SQL injection pattern'),
            (r"union\s+select", 'UNION-based injection'),
            (r";\s*drop\s+table", 'Table deletion attempt'),
            (r";\s*delete\s+from", 'Data deletion attempt'),
            (r"--\s*", 'Comment-based injection'),
            (r"/\*.*\*/", 'Block comment injection'),
            (r"0x[0-9a-f]+", 'Hexadecimal injection'),
            (r"char\s*\(\s*\d+\s*\)", 'Character encoding injection')
        ]
        
        question_lower = question.lower()
        
        for pattern, description in sql_patterns:
            if re.search(pattern, question_lower):
                result['detected'] = True
                result['warnings'].append(f'SQL injection pattern detected: {description}')
                result['risk_score'] += 3
        
        return result
    
    def _detect_privilege_escalation(self, question: str, user_role: str) -> Dict[str, Any]:
        """Detect privilege escalation attempts"""
        result = {
            'detected': False,
            'warnings': [],
            'risk_score': 0
        }
        
        question_lower = question.lower()
        
        admin_keywords = ['admin', 'administrator', 'password', 'credential', 'authentication', 'login']
        sensitive_data_keywords = ['ssn', 'social security', 'license number', 'all patients', 'all records']
        
        if user_role in ['nurse', 'patient']:
            for keyword in admin_keywords:
                if keyword in question_lower:
                    result['detected'] = True
                    result['warnings'].append(f'Administrative access attempt detected: {keyword}')
                    result['risk_score'] += 2
        
        if user_role == 'patient':
            for keyword in sensitive_data_keywords:
                if keyword in question_lower:
                    result['detected'] = True
                    result['warnings'].append(f'Sensitive data access attempt: {keyword}')
                    result['risk_score'] += 2
        
        return result
    
    def _check_dangerous_operations(self, sql_query: str) -> Dict[str, Any]:
        """Check for dangerous SQL operations"""
        result = {
            'detected': False,
            'warnings': [],
            'risk_score': 0
        }
        
        dangerous_patterns = [
            (r'\bdrop\s+table\b', 'Table deletion operation'),
            (r'\bdelete\s+from\b', 'Data deletion operation'),
            (r'\bupdate\s+.*\bset\b', 'Data modification operation'),
            (r'\binsert\s+into\b', 'Data insertion operation'),
            (r'\balter\s+table\b', 'Schema modification operation'),
            (r'\bcreate\s+table\b', 'Table creation operation'),
            (r'\btruncate\s+table\b', 'Table truncation operation'),
            (r'\bexec\b', 'Code execution attempt'),
            (r'\bexecute\b', 'Code execution attempt'),
            (r'\bxp_cmdshell\b', 'System command execution attempt'),
            (r'\bsp_executesql\b', 'Dynamic SQL execution attempt')
        ]
        
        sql_lower = sql_query.lower()
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, sql_lower):
                result['detected'] = True
                result['warnings'].append(f'Dangerous operation detected: {description}')
                result['risk_score'] += 5
        
        return result
    
    def _check_sql_injection_patterns(self, sql_query: str) -> Dict[str, Any]:
        """Check for SQL injection patterns in generated query"""
        result = {
            'detected': False,
            'warnings': [],
            'risk_score': 0
        }
        
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                result['detected'] = True
                result['warnings'].append(f'SQL injection pattern detected: {pattern}')
                result['risk_score'] += 2
        
        return result
    
    def _check_union_attacks(self, sql_query: str, user_role: str) -> Dict[str, Any]:
        """Check for UNION-based attacks"""
        result = {
            'detected': False,
            'warnings': [],
            'risk_score': 0
        }
        
        union_pattern = r'\bunion\s+(all\s+)?select\b'
        if re.search(union_pattern, sql_query, re.IGNORECASE):
            result['detected'] = True
            result['warnings'].append('UNION operation detected')
            result['risk_score'] += 3
            
            sensitive_tables = ['admin_users', 'audit_log']
            for table in sensitive_tables:
                if table in sql_query.lower():
                    result['warnings'].append(f'UNION with sensitive table detected: {table}')
                    result['risk_score'] += 2
        
        return result
    
    def _check_table_access(self, sql_query: str, user_role: str) -> Dict[str, Any]:
        """Check for unauthorized table access"""
        result = {
            'detected': False,
            'warnings': [],
            'risk_score': 0
        }
        
        allowed_tables = self.role_permissions.get(user_role, {}).get('tables', [])
        
        table_pattern = r'\bfrom\s+(\w+)|\bjoin\s+(\w+)'
        table_matches = re.findall(table_pattern, sql_query.lower())
        
        for match_group in table_matches:
            for table in match_group:
                if table and table not in [t.lower() for t in allowed_tables]:
                    result['detected'] = True
                    result['warnings'].append(f'Unauthorized table access: {table}')
                    result['risk_score'] += 3
        
        return result
    
    def _check_sensitive_data_access(self, sql_query: str, user_role: str) -> Dict[str, Any]:
        """Check for sensitive data access"""
        result = {
            'detected': False,
            'warnings': [],
            'risk_score': 0
        }
        
        for column in self.sensitive_columns:
            if re.search(rf'\b{column}\b', sql_query, re.IGNORECASE):
                result['detected'] = True
                result['warnings'].append(f'Sensitive column access: {column}')
                result['risk_score'] += 1
        
        return result
    
    def log_security_event(self, event: SecurityEvent):
        """Log security event for analysis"""
        self.security_events.append(event)

        # Log using loguru with appropriate level
        log_message = f"Security Event: {event.event_type} - {event.message}"
        if event.severity == 'CRITICAL':
            logger.critical(log_message)
        elif event.severity == 'HIGH':
            logger.error(log_message)
        elif event.severity == 'MEDIUM':
            logger.warning(log_message)
        else:
            logger.info(log_message)

        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-500:]
    
    def get_security_events(self, limit: int = 100, severity: str = None) -> List[Dict[str, Any]]:
        """Get recent security events"""
        events = self.security_events
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        events = sorted(events, key=lambda x: x.timestamp, reverse=True)
        
        return [event.to_dict() for event in events[:limit]]
    
    def get_blocked_queries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recently blocked queries"""
        return sorted(
            self.blocked_queries,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        total_events = len(self.security_events)
        
        event_counts = {}
        severity_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
        
        for event in self.security_events:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
            severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1
        
        recent_high_risk = [
            event for event in self.security_events[-50:]
            if event.severity in ['HIGH', 'CRITICAL']
        ]
        
        return {
            'summary': {
                'total_security_events': total_events,
                'blocked_queries': len(self.blocked_queries),
                'current_security_mode': self.current_mode.value,
                'high_risk_events_recent': len(recent_high_risk)
            },
            'event_types': event_counts,
            'severity_distribution': severity_counts,
            'recent_high_risk_events': [event.to_dict() for event in recent_high_risk],
            'blocked_queries_sample': self.get_blocked_queries(10),
            'recommendations': self._generate_security_recommendations()
        }
    
    def _generate_security_recommendations(self) -> List[str]:
        """Generate security recommendations based on observed patterns"""
        recommendations = []
        
        recent_events = self.security_events[-100:]
        
        sql_injection_attempts = len([e for e in recent_events if e.event_type == 'SQL_BLOCKED'])
        if sql_injection_attempts > 5:
            recommendations.append("High number of SQL injection attempts detected - consider additional input validation")
        
        prompt_injections = len([e for e in recent_events if e.event_type == 'QUESTION_BLOCKED'])
        if prompt_injections > 3:
            recommendations.append("Prompt injection attempts detected - review LLM prompting strategy")
        
        privilege_escalations = len([e for e in recent_events if 'privilege' in e.message.lower()])
        if privilege_escalations > 2:
            recommendations.append("Privilege escalation attempts detected - review role-based access controls")
        
        if self.current_mode == SecurityMode.VULNERABLE:
            recommendations.append("Currently running in vulnerable mode - switch to secure mode for production")
        
        if not recommendations:
            recommendations.append("No significant security issues detected - continue monitoring")
        
        return recommendations
    
    def reset_security_logs(self):
        """Reset security logs (for testing purposes)"""
        self.security_events.clear()
        self.blocked_queries.clear()
        
        logger.info("Security logs reset")
    
    def export_security_data(self) -> Dict[str, Any]:
        """Export security data for external analysis"""
        return {
            'security_events': [event.to_dict() for event in self.security_events],
            'blocked_queries': self.blocked_queries,
            'current_mode': self.current_mode.value,
            'configuration': {
                'sql_injection_patterns': self.sql_injection_patterns,
                'sensitive_columns': self.sensitive_columns,
                'role_permissions': self.role_permissions
            },
            'export_timestamp': datetime.utcnow().isoformat()
        }