#!/usr/bin/env python3
"""
Utility Functions for Healthcare Security Research API

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing

Provides helper functions for security analysis, data validation,
logging setup, and common operations across the application.
"""

import re
import logging
import logging.handlers
import json
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from flask import jsonify, request
import bleach
from urllib.parse import urlparse
import os
import sys
from loguru import logger

from config import Config


def setup_logging():
    """Setup comprehensive logging for security research using Loguru"""

    import os

    # Ensure logs directory exists
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Remove default handler
    logger.remove()

    # Determine log level from config
    log_level = Config.LOG_LEVEL.upper()

    # Add console handler with color and formatting
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    # Add main log file handler with rotation
    if Config.LOG_FILE:
        logger.add(
            Config.LOG_FILE,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            enqueue=True  # Async logging for better performance
        )
        logger.info(f"Main log file configured: {Config.LOG_FILE}")

    # Add audit log file handler for security events
    if Config.AUDIT_LOG_FILE:
        logger.add(
            Config.AUDIT_LOG_FILE,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | AUDIT | {level: <8} | {message}",
            level="INFO",
            rotation="50 MB",
            retention="30 days",
            compression="zip",
            filter=lambda record: "AUDIT" in record["extra"].get("type", ""),
            enqueue=True
        )
        logger.info(f"Audit log file configured: {Config.AUDIT_LOG_FILE}")

    # Add separate connectivity log for debugging connection issues
    connectivity_log = "logs/connectivity_debug.log"
    logger.add(
        connectivity_log,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="5 MB",
        retention="3 days",
        filter=lambda record: any(keyword in record["message"].lower() for keyword in ["connection", "connect", "authentication", "login", "llm", "database"]),
        enqueue=True
    )

    # Add login-specific log for authentication tracking
    login_log = "logs/login_audit.log"
    logger.add(
        login_log,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        filter=lambda record: any(keyword in record["message"].lower() for keyword in ["login", "authentication", "logout", "token"]),
        enqueue=True
    )

    # Configure standard library logging to work with loguru
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # Suppress verbose loggers
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.INFO)

    logger.success("Loguru logging system initialized successfully")
    logger.info(f"Log level set to: {log_level}")
    logger.info(f"Connectivity debugging enabled in: {connectivity_log}")
    logger.info(f"Login audit tracking enabled in: {login_log}")


def validate_json_input(request_obj, required_fields: List[str]) -> Union[Dict[str, Any], Tuple[Any, int]]:
    """Validate JSON input with required fields"""
    try:
        if not request_obj.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request_obj.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        for field in data:
            if isinstance(data[field], str):
                data[field] = data[field].strip()
        
        return data
        
    except Exception as e:
        logging.getLogger(__name__).error(f"JSON validation error: {str(e)}")
        return jsonify({'error': 'Invalid JSON format'}), 400


def sanitize_input(input_string: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent XSS and injection attacks"""
    if not isinstance(input_string, str):
        return str(input_string)
    
    sanitized = input_string.strip()
    
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    sanitized = bleach.clean(
        sanitized,
        tags=[],  # No HTML tags allowed
        attributes={},
        strip=True
    )
    
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*='
    ]
    
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    return sanitized


def sanitize_query(sql_query: str) -> str:
    """Basic SQL query sanitization (for vulnerable mode research)"""
    if not isinstance(sql_query, str):
        return ""
    
    sanitized = sql_query.strip()
    
    sanitized = re.sub(r';\s*--.*$', ';', sanitized, flags=re.MULTILINE)
    sanitized = re.sub(r'/\*.*?\*/', ' ', sanitized, flags=re.DOTALL)
    
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    return sanitized


def detect_sql_injection(input_string: str) -> Dict[str, Any]:
    """Detect potential SQL injection attempts"""
    detection_result = {
        'is_suspicious': False,
        'risk_level': 'LOW',
        'detected_patterns': [],
        'confidence': 0.0
    }
    
    if not isinstance(input_string, str):
        return detection_result
    
    input_lower = input_string.lower().strip()
    
    high_risk_patterns = [
        (r"'\s*or\s*'1'\s*=\s*'1", 'Classic SQL injection'),
        (r"'\s*or\s*1\s*=\s*1", 'Numeric SQL injection'),
        (r"union\s+select", 'UNION-based injection'),
        (r";\s*drop\s+table", 'Table deletion attempt'),
        (r";\s*delete\s+from", 'Data deletion attempt'),
        (r"exec\s*\(", 'Code execution attempt'),
        (r"xp_cmdshell", 'System command injection')
    ]
    
    medium_risk_patterns = [
        (r"--\s*", 'Comment injection'),
        (r"/\*.*\*/", 'Block comment injection'),
        (r"'\s*and\s*", 'AND-based injection'),
        (r"0x[0-9a-f]+", 'Hexadecimal injection'),
        (r"char\s*\(\s*\d+\s*\)", 'Character encoding')
    ]
    
    low_risk_patterns = [
        (r"'.*'", 'Single quotes present'),
        (r"=\s*", 'Equality operators'),
        (r"\bselect\b", 'SELECT keyword'),
        (r"\bwhere\b", 'WHERE clause')
    ]
    
    confidence = 0.0
    
    for pattern, description in high_risk_patterns:
        if re.search(pattern, input_lower):
            detection_result['detected_patterns'].append(description)
            detection_result['is_suspicious'] = True
            confidence += 0.8
    
    for pattern, description in medium_risk_patterns:
        if re.search(pattern, input_lower):
            detection_result['detected_patterns'].append(description)
            confidence += 0.5
    
    for pattern, description in low_risk_patterns:
        if re.search(pattern, input_lower):
            detection_result['detected_patterns'].append(description)
            confidence += 0.2
    
    if confidence >= 0.8:
        detection_result['risk_level'] = 'HIGH'
        detection_result['is_suspicious'] = True
    elif confidence >= 0.5:
        detection_result['risk_level'] = 'MEDIUM'
        detection_result['is_suspicious'] = True
    elif confidence >= 0.3:
        detection_result['risk_level'] = 'LOW'
    
    detection_result['confidence'] = min(confidence, 1.0)
    
    return detection_result


def generate_response(data: Any, status_code: int = 200, 
                     headers: Dict[str, str] = None) -> Tuple[Any, int, Dict[str, str]]:
    """Generate standardized API response"""
    response_headers = {
        'Content-Type': 'application/json',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block'
    }
    
    if headers:
        response_headers.update(headers)
    
    if isinstance(data, dict):
        data['timestamp'] = datetime.utcnow().isoformat()
        data['api_version'] = '1.0'
    
    return jsonify(data), status_code, response_headers


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash"""
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def validate_email(email: str) -> bool:
    """Validate email address format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    phone_clean = re.sub(r'[^\d]', '', phone)
    return len(phone_clean) >= 10


def validate_ssn(ssn: str) -> bool:
    """Validate SSN format (for testing purposes only)"""
    ssn_pattern = r'^\d{3}-\d{2}-\d{4}$'
    return re.match(ssn_pattern, ssn) is not None


def mask_sensitive_data(data: str, mask_char: str = '*', 
                       visible_chars: int = 4) -> str:
    """Mask sensitive data for logging"""
    if not data or len(data) <= visible_chars:
        return mask_char * len(data) if data else ""
    
    visible_part = data[-visible_chars:]
    masked_part = mask_char * (len(data) - visible_chars)
    
    return masked_part + visible_part


def log_security_event(event_type: str, message: str, user_id: int = None, 
                      details: Dict[str, Any] = None, severity: str = 'INFO'):
    """Log security-related events"""
    security_logger = logging.getLogger('security')
    audit_logger = logging.getLogger('audit')
    
    log_data = {
        'event_type': event_type,
        'message': message,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat(),
        'ip_address': get_client_ip(),
        'user_agent': request.headers.get('User-Agent', 'Unknown') if request else 'System',
        'details': details or {}
    }
    
    log_message = f"{event_type}: {message}"
    if user_id:
        log_message += f" (User: {user_id})"
    
    security_logger.log(getattr(logging, severity), log_message)
    audit_logger.info(json.dumps(log_data))


def get_client_ip() -> str:
    """Get client IP address from request"""
    if not request:
        return 'unknown'
    
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    elif 'X-Real-IP' in request.headers:
        return request.headers['X-Real-IP']
    else:
        return request.remote_addr or 'unknown'


def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def calculate_query_hash(query: str, parameters: Dict[str, Any] = None) -> str:
    """Calculate hash for query caching"""
    query_string = query.lower().strip()
    if parameters:
        param_string = json.dumps(parameters, sort_keys=True)
        query_string += param_string
    
    return hashlib.sha256(query_string.encode()).hexdigest()


def format_execution_time(start_time: float, end_time: float = None) -> str:
    """Format execution time for display"""
    if end_time is None:
        end_time = datetime.now().timestamp()
    
    duration = end_time - start_time
    
    if duration < 1:
        return f"{duration * 1000:.1f}ms"
    elif duration < 60:
        return f"{duration:.2f}s"
    else:
        minutes = int(duration // 60)
        seconds = duration % 60
        return f"{minutes}m {seconds:.1f}s"


def chunk_list(input_list: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]


def deep_merge_dict(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dict(result[key], value)
        else:
            result[key] = value
    
    return result


def validate_database_connection_string(connection_string: str) -> bool:
    """Validate database connection string format"""
    try:
        if not connection_string.startswith('postgresql://'):
            return False
        
        parsed = urlparse(connection_string)
        return all([parsed.hostname, parsed.port, parsed.username, parsed.path])
    except Exception:
        return False


def escape_sql_identifier(identifier: str) -> str:
    """Escape SQL identifier (table/column names)"""
    if not isinstance(identifier, str):
        raise ValueError("Identifier must be a string")
    
    identifier = identifier.strip()
    
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError("Invalid identifier format")
    
    return f'"{identifier}"'


def analyze_query_complexity(query: str) -> Dict[str, Any]:
    """Analyze SQL query complexity for security assessment"""
    analysis = {
        'complexity_score': 0,
        'table_count': 0,
        'join_count': 0,
        'subquery_count': 0,
        'function_count': 0,
        'risk_factors': []
    }
    
    query_upper = query.upper()
    
    tables = len(re.findall(r'\bFROM\s+\w+|\bJOIN\s+\w+', query_upper))
    analysis['table_count'] = tables
    analysis['complexity_score'] += tables * 2
    
    joins = len(re.findall(r'\b(?:INNER|LEFT|RIGHT|FULL|CROSS)\s+JOIN\b', query_upper))
    analysis['join_count'] = joins
    analysis['complexity_score'] += joins * 3
    
    subqueries = len(re.findall(r'\(\s*SELECT\b', query_upper))
    analysis['subquery_count'] = subqueries
    analysis['complexity_score'] += subqueries * 5
    
    functions = len(re.findall(r'\b\w+\s*\(', query_upper))
    analysis['function_count'] = functions
    analysis['complexity_score'] += functions
    
    if 'UNION' in query_upper:
        analysis['risk_factors'].append('UNION operation')
        analysis['complexity_score'] += 10
    
    if re.search(r'\bWHERE\s+.*\bOR\b', query_upper):
        analysis['risk_factors'].append('Complex WHERE with OR')
        analysis['complexity_score'] += 3
    
    if subqueries > 2:
        analysis['risk_factors'].append('Multiple nested subqueries')
    
    if tables > 5:
        analysis['risk_factors'].append('Many table joins')
    
    return analysis


def create_test_data_generator():
    """Create generator for test data creation"""
    import faker
    fake = faker.Faker()
    
    def generate_patient_data(count: int = 100) -> List[Dict[str, Any]]:
        patients = []
        for i in range(count):
            patient = {
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'date_of_birth': fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
                'ssn': fake.ssn(),
                'insurance_id': f"INS{fake.random_number(digits=6)}",
                'phone_number': fake.phone_number(),
                'email': fake.email(),
                'address': fake.address().replace('\n', ', '),
                'emergency_contact': f"{fake.name()} {fake.phone_number()}"
            }
            patients.append(patient)
        return patients
    
    def generate_doctor_data(count: int = 20) -> List[Dict[str, Any]]:
        specializations = [
            'Cardiology', 'Neurology', 'Pediatrics', 'Oncology',
            'Orthopedics', 'Dermatology', 'Psychiatry', 'Emergency Medicine',
            'Internal Medicine', 'Surgery', 'Radiology', 'Anesthesiology'
        ]
        
        doctors = []
        for i in range(count):
            doctor = {
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'specialization': fake.random_element(specializations),
                'license_number': f"MD{fake.random_number(digits=5)}",
                'phone_number': fake.phone_number(),
                'email': fake.email(),
                'department': fake.random_element(specializations),
                'hire_date': fake.date_between(start_date='-10y', end_date='today').isoformat()
            }
            doctors.append(doctor)
        return doctors
    
    return {
        'generate_patients': generate_patient_data,
        'generate_doctors': generate_doctor_data
    }


def export_security_logs(output_file: str = None) -> str:
    """Export security logs for analysis"""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"security_export_{timestamp}.json"
    
    security_data = {
        'export_timestamp': datetime.utcnow().isoformat(),
        'log_files': [],
        'summary': {
            'total_files_processed': 0,
            'total_log_entries': 0
        }
    }
    
    try:
        for log_file in [Config.LOG_FILE, Config.AUDIT_LOG_FILE]:
            if log_file and os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    security_data['log_files'].append({
                        'filename': log_file,
                        'entries': [line.strip() for line in lines[-1000:]],  # Last 1000 entries
                        'entry_count': len(lines)
                    })
                    security_data['summary']['total_log_entries'] += len(lines)
                    security_data['summary']['total_files_processed'] += 1
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(security_data, f, indent=2, ensure_ascii=False)
        
        logging.getLogger(__name__).info(f"Security logs exported to {output_file}")
        return output_file
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to export security logs: {str(e)}")
        raise


def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging"""
    import platform
    import psutil
    
    return {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'memory_available': psutil.virtual_memory().available,
        'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
        'timestamp': datetime.utcnow().isoformat()
    }