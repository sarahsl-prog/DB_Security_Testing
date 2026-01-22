#!/usr/bin/env python3
"""
Configuration Management for Healthcare Security Research API

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing

Handles environment-specific settings for dockered services:
- Flask API Server - backend
- NGINX Reverse Proxy - frontend
- LLM Service  - ollama
- PostgreSQL Database - postgres
- Security mode toggles
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with security research settings"""

   
    # Load environment variables with required validation
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        SECRET_KEY = 'dev-key-change-in-production'
        print("WARNING: Using default SECRET_KEY. Set SECRET_KEY environment variable for production!")

    HOST = os.environ.get('API_HOST', '0.0.0.0')
    PORT = int(os.environ.get('API_PORT', 5000))
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Try DATABASE_URL first (for Docker), fall back to individual vars (for local)
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    else:
        # Database configuration - require environment variables
        DATABASE_HOST = os.environ.get('DB_HOST')
        if not DATABASE_HOST:
            raise ValueError("DB_HOST environment variable must be set. Check your .env file.")

        DATABASE_PORT = int(os.environ.get('DB_PORT', 5432))
        DATABASE_NAME = os.environ.get('DB_NAME', 'healthcare_security')
        DATABASE_USER = os.environ.get('DB_USER', 'healthcare_user')
        DATABASE_PASSWORD = os.environ.get('DB_PASSWORD')
        if not DATABASE_PASSWORD:
            raise ValueError("DB_PASSWORD environment variable must be set. Check your .env file.")

        DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"


    
    # LLM configuration - require environment variables
    LLM_HOST = os.environ.get('LLM_HOST','ollama')
    if not LLM_HOST:
        raise ValueError("LLM_HOST environment variable must be set. Check your .env file.")

    LLM_PORT = int(os.environ.get('LLM_PORT', 11434))
    LLM_BASE_URL = f"http://{LLM_HOST}:{LLM_PORT}"
    LLM_DEFAULT_MODEL = os.environ.get('LLM_MODEL', 'llama-sql:latest')
    LLM_TIMEOUT = int(os.environ.get('LLM_TIMEOUT', 30))
    LLM_MAX_RETRIES = int(os.environ.get('LLM_MAX_RETRIES', 3))
    
    SECURITY_MODE = os.environ.get('SECURITY_MODE', 'vulnerable')
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY','dev-key-change-in-production') 
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_EXPIRES_HOURS', 24)))
    
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/healthcare_security.log')
    AUDIT_LOG_FILE = os.environ.get('AUDIT_LOG_FILE', 'logs/security_audit.log')

    # Domain configuration
    EMAIL_DOMAIN = os.environ.get('EMAIL_DOMAIN', 'hospital.com')
    API_BASE_URL = os.environ.get('API_BASE_URL', f"http://{HOST}:{PORT}")
    
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    MAX_QUERY_RESULTS = int(os.environ.get('MAX_QUERY_RESULTS', 1000))
    QUERY_TIMEOUT = int(os.environ.get('QUERY_TIMEOUT', 30))
    
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 60))
    
    CACHE_TTL = int(os.environ.get('CACHE_TTL', 300))
    
    VULNERABLE_MODE_FEATURES = {
        'sql_injection_protection': False,
        'input_validation': False,
        'role_based_filtering': False,
        'comprehensive_logging': False,
        'query_analysis': False,
        'schema_protection': False
    }
    
    SECURE_MODE_FEATURES = {
        'sql_injection_protection': True,
        'input_validation': True,
        'role_based_filtering': True,
        'comprehensive_logging': True,
        'query_analysis': True,
        'schema_protection': True
    }
    
    SQL_INJECTION_PATTERNS = [
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
        r"(--|#|/\*|\*/)",
        r"(\bor\b\s+\d+\s*=\s*\d+)",
        r"(\band\b\s+\d+\s*=\s*\d+)",
        r"(\bwhere\b\s+\d+\s*=\s*\d+)",
        r"(char\s*\(\s*\d+\s*\))",
        r"(concat\s*\()",
        r"(0x[0-9a-f]+)",
        r"(\bxp_cmdshell\b)",
        r"(\bsp_executesql\b)"
    ]
    
    SENSITIVE_COLUMNS = [
        'ssn', 'social_security_number', 'password', 'password_hash',
        'credit_card', 'card_number', 'license_number', 'insurance_id'
    ]
    
    ROLE_PERMISSIONS = {
        'patient': {
            'tables': ['patients', 'medical_records'],
            'columns': {
                'patients': ['first_name', 'last_name', 'date_of_birth'],
                'medical_records': ['diagnosis', 'treatment', 'visit_date']
            },
            'filters': ['WHERE patients.patient_id = {user_patient_id}']
        },
        'nurse': {
            'tables': ['patients', 'medical_records', 'doctors'],
            'columns': {
                'patients': ['first_name', 'last_name', 'date_of_birth'],
                'medical_records': ['diagnosis', 'treatment', 'visit_date', 'medication'],
                'doctors': ['first_name', 'last_name', 'specialization']
            },
            'filters': []
        },
        'doctor': {
            'tables': ['patients', 'medical_records', 'doctors'],
            'columns': {
                'patients': ['first_name', 'last_name', 'date_of_birth', 'insurance_id'],
                'medical_records': ['diagnosis', 'treatment', 'visit_date', 'medication', 'patient_id', 'doctor_id'],
                'doctors': ['first_name', 'last_name', 'specialization', 'doctor_id']
            },
            'filters': []
        },
        'admin': {
            'tables': ['patients', 'medical_records', 'doctors', 'admin_users', 'audit_log'],
            'columns': '*',
            'filters': []
        }
    }
    
    @classmethod
    def get_current_mode_features(cls):
        """Get features for current security mode"""
        if cls.SECURITY_MODE.lower() == 'secure':
            return cls.SECURE_MODE_FEATURES
        return cls.VULNERABLE_MODE_FEATURES
    
    @classmethod
    def is_feature_enabled(cls, feature_name):
        """Check if a specific security feature is enabled"""
        features = cls.get_current_mode_features()
        return features.get(feature_name, False)


class DevelopmentConfig(Config):
    """Development configuration with enhanced debugging"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

    DATABASE_HOST = os.environ.get('DEVELOPMENT_DB_HOST', os.environ.get('DB_HOST'))
    DATABASE_NAME = 'healthcare_security'

    LLM_HOST = os.environ.get('DEVELOPMENT_LLM_HOST', os.environ.get('LLM_HOST'))

    SECURITY_MODE = 'vulnerable'


class ProductionConfig(Config):
    """Production configuration with security hardening"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    SECRET_KEY = os.environ.get('SECRET_KEY','dev-key-change-in-production')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
     # Try DATABASE_URL first (for Docker), fall back to individual vars (for local)
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    else:
        # Database configuration - require environment variables
        DATABASE_HOST = os.environ.get('DB_HOST')
        if not DATABASE_HOST:
            raise ValueError("DB_HOST environment variable must be set. Check your .env file.")

        DATABASE_PORT = int(os.environ.get('DB_PORT', 5432))
        DATABASE_NAME = os.environ.get('DB_NAME', 'healthcare_security')
        DATABASE_USER = os.environ.get('DB_USER', 'healthcare_user')
        DATABASE_PASSWORD = os.environ.get('DB_PASSWORD')
        if not DATABASE_PASSWORD:
            raise ValueError("DB_PASSWORD environment variable must be set in production")

        DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

       
    SECURITY_MODE = 'secure'
    
    RATE_LIMIT_PER_MINUTE = 30


class TestingConfig(Config):
    """Testing configuration for automated security tests"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

    DATABASE_NAME = 'Testing'
    DATABASE_HOST = os.environ.get('TESTING_DB_HOST', os.environ.get('DB_HOST', 'localhost'))

    LLM_HOST = os.environ.get('TESTING_LLM_HOST', os.environ.get('LLM_HOST','localhost'))
    LLM_TIMEOUT = 5
    
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    
    MAX_QUERY_RESULTS = 100


class SecurityTestConfig(Config):
    """Special configuration for penetration testing"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    SECURITY_MODE = 'vulnerable'
    
    VULNERABLE_MODE_FEATURES = {
        'sql_injection_protection': False,
        'input_validation': False,
        'role_based_filtering': False,
        'comprehensive_logging': True,  # Keep logging for analysis
        'query_analysis': False,
        'schema_protection': False
    }
    
    MAX_QUERY_RESULTS = 10000  # Allow large data extraction for testing
    QUERY_TIMEOUT = 60


config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'security_test': SecurityTestConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config_dict.get(config_name, DevelopmentConfig)