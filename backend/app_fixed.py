#!/usr/bin/env python3
"""
Healthcare Database Security Research API

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing

A Flask-based API for researching SQL injection vulnerabilities and defense mechanisms
in healthcare database systems. Supports both vulnerable and secure modes for testing.

Purpose: Educational security testing and vulnerability research
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import jwt
import time
import logging
from datetime import datetime, timedelta
from functools import wraps
import traceback
from loguru import logger

from common.config import Config
from database import DatabaseManager
from llm_client import LLMClient
from security import SecurityManager, SecurityMode
from models import User, AuditLog
from utils import generate_response, validate_json_input, setup_logging

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS, "allow_headers": ["Content-Type", "Authorization"], "methods": ["GET", "POST", "OPTIONS"]}}, supports_credentials=False)

try:
    db_manager = DatabaseManager()
    llm_client = LLMClient()
    security_manager = SecurityManager()

    setup_logging()

    logger.info("Application services initialized successfully at startup")
except Exception as e:
    logger.error(f"Failed to initialize services at startup: {str(e)}")
    logger.warning("Application will attempt to initialize services on first request")
    db_manager = None
    llm_client = None
    security_manager = None

# Simple in-memory token blacklist for logout functionality
# For production, use Redis or a database-backed blacklist
token_blacklist = set()

def token_required(f):
    """JWT token validation decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]
        except Exception as e:
            return jsonify({'error': 'Invalid token format'}), 401

        # Check if token is blacklisted
        if token in token_blacklist:
            return jsonify({'error': 'Token has been revoked'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = db_manager.get_user_by_id(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
            g.current_user = current_user
            g.token = token
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Admin role validation decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

def get_allowed_operations_for_role(role):
    """Get allowed operations for a given role"""
    operations = {
        'doctor': [
            'Read patient records',
            'Read appointment data',
            'Read department information',
            'Update patient notes',
            'Create prescriptions'
        ],
        'nurse': [
            'Read patient basic info',
            'Read appointment schedules',
            'Update patient vitals',
            'Read medication lists'
        ],
        'admin': [
            'Full database access',
            'User management',
            'System configuration',
            'Audit log access',
            'Backup operations'
        ],
        'patient': [
            'Read own records only',
            'Read own appointments',
            'Update contact information'
        ]
    }
    return operations.get(role, [])

@app.before_request
def before_request():
    """Log all incoming requests for security analysis"""
    g.start_time = time.time()
    if request.endpoint not in ['health_check']:  # Don't log health checks
        logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def after_request(response):
    """Log response and execution time"""
    if hasattr(g, 'start_time') and request.endpoint not in ['health_check']:
        duration = time.time() - g.start_time
        logger.info(f"Response: {response.status_code} in {duration:.3f}s")
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler for security research logging"""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    if app.config['DEBUG']:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for all distributed components"""
    start_time = time.time()
    health_status = {
        'api': {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()},
        'database': {'status': 'unknown', 'response_time': None},
        'llm_service': {'status': 'unknown', 'response_time': None},
        'overall': 'healthy'
    }

    try:
        # Check database connection if manager exists
        if db_manager:
            db_start = time.time()
            db_manager.test_connection()
            health_status['database'] = {
                'status': 'healthy',
                'response_time': f"{(time.time() - db_start):.3f}s"
            }
        else:
            health_status['database'] = {'status': 'initializing', 'response_time': None}
            health_status['overall'] = 'degraded'

    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status['database'] = {'status': 'unhealthy', 'response_time': None}
        health_status['overall'] = 'degraded'

    try:
        # Check LLM service if client exists
        if llm_client:
            llm_start = time.time()
            llm_client.test_connection()
            health_status['llm_service'] = {
                'status': 'healthy',
                'response_time': f"{(time.time() - llm_start):.3f}s"
            }
        else:
            health_status['llm_service'] = {'status': 'initializing', 'response_time': None}
            health_status['overall'] = 'degraded'

    except Exception as e:
        logger.error(f"LLM service health check failed: {str(e)}")
        health_status['llm_service'] = {'status': 'unhealthy', 'response_time': None}
        health_status['overall'] = 'degraded'

    execution_time = time.time() - start_time
    health_status['api']['response_time'] = f"{execution_time:.3f}s"

    status_code = 200 if health_status['overall'] == 'healthy' else 503
    return jsonify(health_status), status_code

@app.route('/api/login', methods=['POST'])
def login():
    """User authentication endpoint"""
    try:
        data = validate_json_input(request, ['username', 'password'])
        if isinstance(data, tuple):
            return data

        username = data['username']
        password = data['password']

        user = db_manager.authenticate_user(username, password)

        if not user:
            return jsonify({
                'error': 'Invalid credentials',
                'message': 'Username or password is incorrect'
            }), 401

        # Update last login timestamp
        db_manager.update_last_login(user.user_id)

        # Generate JWT token
        token = jwt.encode({
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
        }, app.config['SECRET_KEY'], algorithm='HS256')

        logger.info(f"Successful login: {username} (role: {user.role})")

        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'role': user.role,
                'full_name': f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username
            },
            'message': 'Login successful'
        })

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/verify', methods=['GET'])
@token_required
def verify_token():
    """Verify JWT token and return user information"""
    try:
        user = g.current_user

        return jsonify({
            'success': True,
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'role': user.role,
                'full_name': f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username
            },
            'message': 'Token is valid'
        })

    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({'error': 'Verification failed'}), 401

@app.route('/api/logout', methods=['POST'])
@token_required
def logout():
    """Logout endpoint - adds token to blacklist"""
    try:
        token = getattr(g, 'token', None)
        if token:
            token_blacklist.add(token)
            return jsonify({
                'success': True,
                'message': 'Logout successful'
            })
        else:
            return jsonify({'error': 'No token provided'}), 400

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/api/query', methods=['POST'])
@token_required
def process_query():
    """Process natural language query and return SQL results"""
    try:
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400

        question = request.json.get('question')
        security_mode = request.json.get('security_mode', Config.SECURITY_MODE)
        user_role = getattr(g.current_user, 'role', 'patient')

        if not question:
            return jsonify({'error': 'Question is required'}), 400

        logger.info(f"Query request: user={g.current_user.username} role={user_role} mode={security_mode}")

        # Get database schema for LLM context
        schema_context = db_manager.get_schema_info()

        start_time = time.time()

        # Generate SQL using LLM
        sql_query = llm_client.generate_sql(
            question=question,
            schema_context=schema_context,
            user_role=user_role,
            security_mode=security_mode
        )

        llm_time = time.time() - start_time

        # Validate and execute query
        if security_mode == 'secure':
            validation = security_manager.validate_sql(sql_query, user_role)
            if not validation['valid']:
                return jsonify({
                    'success': False,
                    'blocked': True,
                    'reason': validation['reason'],
                    'warnings': validation.get('warnings', []),
                    'security_flags': {
                        'riskLevel': 'HIGH',
                        'blockedAttempts': 1,
                        'warnings': validation.get('warnings', []),
                        'authenticatedUser': g.current_user.username,
                        'userRole': user_role,
                        'allowedOperations': get_allowed_operations_for_role(user_role)
                    }
                })

        # Execute query
        query_start_time = time.time()
        results = db_manager.execute_query(sql_query)

        if results and isinstance(results, list) and len(results) > 0 and 'message' in results[0]:
            actual_results = []
            rows_affected = results[0].get('rows_affected', 0)
        else:
            actual_results = results if results else []
            rows_affected = len(actual_results)

        query_time = time.time() - query_start_time

        # Log audit entry
        db_manager.log_audit(
            user_id=g.current_user.user_id,
            username=g.current_user.username,
            query=sql_query,
            result_status='SUCCESS',
            security_mode=security_mode,
            execution_time=f"{query_time:.3f}s",
            rows_affected=rows_affected,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', 'Unknown')
        )

        security_flags = security_manager.analyze_query_security(sql_query, question, user_role)

        logger.success(f"Query executed successfully: user={g.current_user.username} rows={rows_affected}")

        return jsonify({
            'success': True,
            'sql': sql_query,
            'data': actual_results,
            'rowCount': rows_affected,
            'llmProcessingTime': int(llm_time * 1000),
            'executionTime': int(query_time * 1000),
            'securityFlags': {
                'riskLevel': security_flags['risk_level'],
                'blockedAttempts': 0,
                'warnings': security_flags.get('warnings', []),
                'authenticatedUser': g.current_user.username,
                'userRole': user_role,
                'allowedOperations': get_allowed_operations_for_role(user_role)
            }
        })

    except PermissionError as e:
        logger.warning(f"Query blocked: {str(e)}")
        return jsonify({
            'success': False,
            'blocked': True,
            'reason': str(e),
            'securityFlags': {
                'riskLevel': 'HIGH',
                'blockedAttempts': 1,
                'warnings': [str(e)],
                'authenticatedUser': g.current_user.username,
                'userRole': user_role,
                'allowedOperations': get_allowed_operations_for_role(user_role)
            }
        }), 403

    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Query processing failed',
            'details': str(e)
        }), 500

@app.route('/api/schema', methods=['GET'])
@token_required
def get_database_schema():
    """Return database schema information for LLM context"""
    try:
        user_role = getattr(g.current_user, 'role', 'patient')

        # Get full schema
        schema_info = db_manager.get_schema_info()

        # Filter schema based on user role (in secure mode)
        if Config.SECURITY_MODE == 'secure':
            filtered_schema = {}
            allowed_tables = Config.ROLE_PERMISSIONS.get(user_role, {}).get('tables', [])

            for table_name, table_info in schema_info.items():
                if table_name in allowed_tables:
                    filtered_schema[table_name] = table_info

            schema_info = filtered_schema

        return jsonify({
            'schema': schema_info,
            'security_mode': Config.SECURITY_MODE,
            'user_role': user_role
        })

    except Exception as e:
        logger.error(f"Schema retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve schema'}), 500

@app.route('/api/validate', methods=['POST'])
@token_required
def validate_question_only():
    """Validate question without executing SQL (testing endpoint)"""
    try:
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400

        question = request.json.get('question')
        user_role = request.json.get('user_role', getattr(g.current_user, 'role', 'patient'))
        security_mode = request.json.get('security_mode', Config.SECURITY_MODE)

        if not question:
            return jsonify({'error': 'Question is required'}), 400

        # Get schema for context
        schema_context = db_manager.get_schema_info()

        validation_results = {
            'question_validation': {'valid': True, 'warnings': []},
            'sql_validation': {'valid': True, 'warnings': []},
            'generated_sql': None
        }

        if security_mode == 'secure':
            validation_results['question_validation'] = security_manager.validate_question(question, user_role)

        if validation_results['question_validation']['valid']:
            try:
                sql_query = llm_client.generate_sql(question, schema_context, user_role, security_mode)
                validation_results['generated_sql'] = sql_query

                if security_mode == 'secure':
                    validation_results['sql_validation'] = security_manager.validate_sql(sql_query, user_role)

            except Exception as e:
                validation_results['sql_validation'] = {
                    'valid': False,
                    'warnings': [f"SQL generation failed: {str(e)}"]
                }

        return jsonify({
            'validation_results': validation_results,
            'security_mode': security_mode,
            'user_role': user_role
        })

    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': 'Validation failed'}), 500

@app.route('/api/audit', methods=['GET'])
@token_required
@admin_required
def get_audit_logs():
    """Security audit logs (admin only)"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        user_filter = request.args.get('user_id', type=int)
        status_filter = request.args.get('status')

        audit_logs = db_manager.get_audit_logs(
            limit=limit,
            offset=offset,
            user_id=user_filter,
            status=status_filter
        )

        return jsonify({
            'audit_logs': audit_logs,
            'total_count': db_manager.get_audit_log_count(user_filter, status_filter),
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"Audit log access error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve audit logs'}), 500

@app.route('/api/security/mode', methods=['POST'])
@token_required
@admin_required
def toggle_security_mode():
    """Toggle between vulnerable and secure modes (admin only)"""
    try:
        data = validate_json_input(request, ['mode'])
        if isinstance(data, tuple):
            return data

        mode = data['mode']
        if mode not in ['vulnerable', 'secure']:
            return jsonify({'error': 'Invalid security mode'}), 400

        security_manager.set_mode(SecurityMode.SECURE if mode == 'secure' else SecurityMode.VULNERABLE)

        logger.info(f"Security mode changed to {mode} by admin {g.current_user.username}")

        return jsonify({
            'message': f'Security mode set to {mode}',
            'mode': mode
        })

    except Exception as e:
        logger.error(f"Security mode toggle error: {str(e)}")
        return jsonify({'error': 'Failed to toggle security mode'}), 500

@app.route('/api/attack/scenarios', methods=['GET'])
@token_required
@admin_required
def list_attack_scenarios():
    """List available attack scenarios for testing (admin only)"""
    try:
        from attack_scenarios import AttackScenarioRunner

        runner = AttackScenarioRunner()
        scenarios = {
            'SQL Injection': runner.get_sql_injection_scenarios(),
            'Privilege Escalation': runner.get_privilege_escalation_scenarios(),
            'Prompt Injection': runner.get_prompt_injection_scenarios(),
            'Data Exfiltration': runner.get_data_exfiltration_scenarios()
        }

        return jsonify({
            'scenarios': scenarios,
            'total_count': sum(len(s) for s in scenarios.values())
        })

    except Exception as e:
        logger.error(f"Attack scenarios listing error: {str(e)}")
        return jsonify({'error': 'Failed to list attack scenarios'}), 500

if __name__ == '__main__':
    try:
        logger.info(f"Starting Healthcare Security API on {Config.HOST}:{Config.PORT}")
        logger.info(f"Security mode: {Config.SECURITY_MODE}")
        logger.info(f"LLM model: {Config.LLM_DEFAULT_MODEL}")

        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG
        )

    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise