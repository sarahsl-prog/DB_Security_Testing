#!/usr/bin/env python3
"""
Data Models and Schemas for Healthcare Security Research API

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/Database_Security_TestApp

Defines database models for realistic healthcare data and security testing.
Includes both SQLAlchemy ORM models and Pydantic schemas for validation.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Date, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import json


Base = declarative_base()


class Patient(Base):
    """Patient records with PHI for security testing"""
    __tablename__ = 'patients'
    
    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    ssn = Column(String(11), nullable=False, unique=True)  # Format: XXX-XX-XXXX
    insurance_id = Column(String(20), nullable=False)
    phone_number = Column(String(15))
    email = Column(String(100))
    address = Column(Text)
    emergency_contact = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    medical_records = relationship("MedicalRecord", back_populates="patient")
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary with optional sensitive data filtering"""
        data = {
            'patient_id': self.patient_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'phone_number': self.phone_number,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data.update({
                'ssn': self.ssn,
                'insurance_id': self.insurance_id,
                'address': self.address,
                'emergency_contact': self.emergency_contact
            })
        
        return data


class Doctor(Base):
    """Doctor records with professional information"""
    __tablename__ = 'doctors'
    
    doctor_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    specialization = Column(String(100), nullable=False)
    license_number = Column(String(20), nullable=False, unique=True)
    phone_number = Column(String(15))
    email = Column(String(100))
    department = Column(String(50))
    hire_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    medical_records = relationship("MedicalRecord", back_populates="doctor")
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary with optional sensitive data filtering"""
        data = {
            'doctor_id': self.doctor_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'specialization': self.specialization,
            'department': self.department,
            'is_active': self.is_active
        }
        
        if include_sensitive:
            data.update({
                'license_number': self.license_number,
                'phone_number': self.phone_number,
                'email': self.email,
                'hire_date': self.hire_date.isoformat() if self.hire_date else None
            })
        
        return data


class MedicalRecord(Base):
    """Medical records linking patients and doctors"""
    __tablename__ = 'medical_records'
    
    record_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.doctor_id'), nullable=False)
    visit_date = Column(DateTime, nullable=False)
    diagnosis = Column(Text, nullable=False)
    treatment = Column(Text)
    medication = Column(Text)
    notes = Column(Text)
    follow_up_date = Column(Date)
    is_confidential = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary with optional sensitive data filtering"""
        data = {
            'record_id': self.record_id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'medication': self.medication,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data.update({
                'notes': self.notes,
                'is_confidential': self.is_confidential
            })
        
        return data


class AdminUser(Base):
    """Admin users for system access and security testing"""
    __tablename__ = 'admin_users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # admin, doctor, nurse, patient
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'), nullable=True)  # For patient role users
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary with optional sensitive data filtering"""
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data.update({
                'failed_login_attempts': self.failed_login_attempts,
                'locked_until': self.locked_until.isoformat() if self.locked_until else None,
                'patient_id': self.patient_id
            })
        
        return data


class AuditLog(Base):
    """Security audit logging for research analysis"""
    __tablename__ = 'audit_log'
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String(50))
    action = Column(String(50), nullable=False)  # LOGIN, QUERY, SCHEMA_ACCESS, etc.
    query = Column(Text)
    result_status = Column(String(20), nullable=False)  # SUCCESS, ERROR, BLOCKED
    security_mode = Column(String(20))  # vulnerable, secure
    ip_address = Column(String(45))
    user_agent = Column(Text)
    execution_time = Column(String(20))
    rows_affected = Column(Integer)
    error_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'query': self.query,
            'result_status': self.result_status,
            'security_mode': self.security_mode,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'execution_time': self.execution_time,
            'rows_affected': self.rows_affected,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


@dataclass
class User:
    """User data class for authentication and authorization"""
    user_id: int
    username: str
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    patient_id: Optional[int] = None
    
    def has_permission(self, action: str, resource: str = None) -> bool:
        """Check if user has permission for a specific action"""
        role_permissions = {
            'admin': ['*'],
            'doctor': ['read_patients', 'read_medical_records', 'write_medical_records'],
            'nurse': ['read_patients', 'read_medical_records_limited'],
            'patient': ['read_own_records']
        }
        
        permissions = role_permissions.get(self.role, [])
        return '*' in permissions or action in permissions
    
    def can_access_patient(self, patient_id: int) -> bool:
        """Check if user can access specific patient data"""
        if self.role == 'admin':
            return True
        elif self.role in ['doctor', 'nurse']:
            return True  # Doctors and nurses can access all patients in this simple model
        elif self.role == 'patient':
            return self.patient_id == patient_id
        return False


class QueryResult:
    """Query result wrapper with metadata"""
    
    def __init__(self, data: List[Dict[str, Any]], metadata: Dict[str, Any] = None):
        self.data = data
        self.metadata = metadata or {}
        self.row_count = len(data)
        self.execution_time = metadata.get('execution_time', '0.000s')
        self.columns = list(data[0].keys()) if data else []
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'data': self.data,
            'metadata': self.metadata,
            'row_count': self.row_count,
            'execution_time': self.execution_time,
            'columns': self.columns
        }
    
    def filter_sensitive_data(self, user_role: str, sensitive_columns: List[str] = None):
        """Filter sensitive data based on user role"""
        if user_role == 'admin':
            return self  # Admins see everything
        
        if sensitive_columns is None:
            sensitive_columns = ['ssn', 'password_hash', 'license_number', 'insurance_id']
        
        filtered_data = []
        for row in self.data:
            filtered_row = {}
            for key, value in row.items():
                if key.lower() in [col.lower() for col in sensitive_columns]:
                    if user_role in ['doctor']:
                        filtered_row[key] = value  # Doctors can see some sensitive data
                    else:
                        filtered_row[key] = '***REDACTED***'
                else:
                    filtered_row[key] = value
            filtered_data.append(filtered_row)
        
        return QueryResult(filtered_data, self.metadata)


class SecurityEvent:
    """Security event for monitoring and alerting"""
    
    def __init__(self, event_type: str, severity: str, message: str, 
                 user_id: int = None, details: Dict[str, Any] = None):
        self.event_type = event_type  # SQL_INJECTION, PRIVILEGE_ESCALATION, etc.
        self.severity = severity  # LOW, MEDIUM, HIGH, CRITICAL
        self.message = message
        self.user_id = user_id
        self.details = details or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for logging"""
        return {
            'event_type': self.event_type,
            'severity': self.severity,
            'message': self.message,
            'user_id': self.user_id,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


class DatabaseSchema:
    """Database schema information for LLM context"""
    
    def __init__(self):
        self.tables = {
            'patients': {
                'description': 'Patient demographic and contact information',
                'columns': {
                    'patient_id': 'INTEGER PRIMARY KEY - Unique patient identifier',
                    'first_name': 'VARCHAR(50) - Patient first name',
                    'last_name': 'VARCHAR(50) - Patient last name', 
                    'date_of_birth': 'DATE - Patient date of birth',
                    'ssn': 'VARCHAR(11) - Social Security Number (sensitive)',
                    'insurance_id': 'VARCHAR(20) - Insurance identifier (sensitive)',
                    'phone_number': 'VARCHAR(15) - Contact phone number',
                    'email': 'VARCHAR(100) - Email address',
                    'address': 'TEXT - Home address',
                    'emergency_contact': 'VARCHAR(100) - Emergency contact info'
                },
                'relationships': ['medical_records (patient_id)'],
                'sensitivity': 'HIGH - Contains PHI and PII'
            },
            'doctors': {
                'description': 'Healthcare provider information',
                'columns': {
                    'doctor_id': 'INTEGER PRIMARY KEY - Unique doctor identifier',
                    'first_name': 'VARCHAR(50) - Doctor first name',
                    'last_name': 'VARCHAR(50) - Doctor last name',
                    'specialization': 'VARCHAR(100) - Medical specialization',
                    'license_number': 'VARCHAR(20) - Medical license (sensitive)',
                    'phone_number': 'VARCHAR(15) - Contact phone',
                    'email': 'VARCHAR(100) - Email address',
                    'department': 'VARCHAR(50) - Hospital department',
                    'hire_date': 'DATE - Employment start date'
                },
                'relationships': ['medical_records (doctor_id)'],
                'sensitivity': 'MEDIUM - Contains professional credentials'
            },
            'medical_records': {
                'description': 'Patient medical history and treatments',
                'columns': {
                    'record_id': 'INTEGER PRIMARY KEY - Unique record identifier',
                    'patient_id': 'INTEGER FOREIGN KEY - References patients table',
                    'doctor_id': 'INTEGER FOREIGN KEY - References doctors table',
                    'visit_date': 'DATETIME - Date and time of visit',
                    'diagnosis': 'TEXT - Medical diagnosis',
                    'treatment': 'TEXT - Treatment provided',
                    'medication': 'TEXT - Prescribed medications',
                    'notes': 'TEXT - Confidential medical notes',
                    'follow_up_date': 'DATE - Next appointment date'
                },
                'relationships': ['patients (patient_id)', 'doctors (doctor_id)'],
                'sensitivity': 'CRITICAL - Protected health information'
            },
            'admin_users': {
                'description': 'System users and authentication',
                'columns': {
                    'user_id': 'INTEGER PRIMARY KEY - Unique user identifier',
                    'username': 'VARCHAR(50) - Login username',
                    'password_hash': 'VARCHAR(255) - Hashed password (sensitive)',
                    'role': 'VARCHAR(20) - User role (admin, doctor, nurse, patient)',
                    'first_name': 'VARCHAR(50) - User first name',
                    'last_name': 'VARCHAR(50) - User last name',
                    'email': 'VARCHAR(100) - Email address',
                    'last_login': 'DATETIME - Last successful login'
                },
                'relationships': [],
                'sensitivity': 'CRITICAL - Contains authentication data'
            },
            'audit_log': {
                'description': 'Security and access audit trail',
                'columns': {
                    'log_id': 'INTEGER PRIMARY KEY - Unique log identifier',
                    'user_id': 'INTEGER - User who performed action',
                    'action': 'VARCHAR(50) - Action performed',
                    'query': 'TEXT - SQL query executed',
                    'result_status': 'VARCHAR(20) - SUCCESS, ERROR, BLOCKED',
                    'security_mode': 'VARCHAR(20) - vulnerable or secure mode',
                    'timestamp': 'DATETIME - When action occurred'
                },
                'relationships': [],
                'sensitivity': 'HIGH - Security monitoring data'
            }
        }
    
    def get_schema_for_role(self, role: str) -> Dict[str, Any]:
        """Get filtered schema based on user role"""
        if role == 'admin':
            return self.tables
        
        filtered_schema = {}
        allowed_tables = {
            'doctor': ['patients', 'medical_records', 'doctors'],
            'nurse': ['patients', 'medical_records', 'doctors'],
            'patient': ['patients', 'medical_records']
        }
        
        for table_name in allowed_tables.get(role, []):
            if table_name in self.tables:
                filtered_schema[table_name] = self.tables[table_name].copy()
                
                if role == 'nurse' and table_name == 'patients':
                    filtered_schema[table_name]['columns'] = {
                        k: v for k, v in self.tables[table_name]['columns'].items()
                        if 'sensitive' not in v.lower()
                    }
        
        return filtered_schema
    
    def to_llm_context(self, role: str = 'admin') -> str:
        """Generate schema description for LLM prompt"""
        schema = self.get_schema_for_role(role)
        context = "Database Schema:\n\n"
        
        for table_name, table_info in schema.items():
            context += f"Table: {table_name}\n"
            context += f"Description: {table_info['description']}\n"
            context += f"Sensitivity: {table_info['sensitivity']}\n"
            context += "Columns:\n"
            
            for col_name, col_desc in table_info['columns'].items():
                context += f"  - {col_name}: {col_desc}\n"
            
            if table_info['relationships']:
                context += f"Relationships: {', '.join(table_info['relationships'])}\n"
            
            context += "\n"
        
        return context