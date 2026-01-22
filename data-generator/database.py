#!/usr/bin/env python3
"""
Database Manager for Healthcare Security Research API

Healthcare Security Research Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing

Handles PostgreSQL connections, query execution, and data management
for both vulnerable and secure modes of operation.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import bcrypt
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
from loguru import logger

from config import Config
from models import Base, Patient, MedicalRecord, AdminUser, AuditLog, User, QueryResult, DatabaseSchema


class DatabaseManager:
    """Manages database connections and operations for security research"""
    
    def __init__(self):
        self.engine = None
        self.Session = None
        self.schema = DatabaseSchema()
        self._connection_pool = None
        self._setup_database()
    
    def _setup_database(self):
        """Initialize database connection and session factory"""
        try:
            logger.info(f"Attempting to connect to database at {Config.DB_HOST}:{Config.DB_PORT}")
            logger.debug(f"Database connection parameters: host={Config.DB_HOST}, port={Config.DB_PORT}, db={Config.DB_NAME}")

            self.engine = create_engine(
                Config.DATABASE_URL,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=Config.DEBUG
            )

            self.Session = sessionmaker(bind=self.engine)

            Base.metadata.bind = self.engine

            logger.success(f"Database connection established successfully to {Config.DB_NAME}")
            logger.info("Connection pool configured: pool_size=10, max_overflow=20")

        except Exception as e:
            logger.error(f"Database setup failed: {str(e)}")
            logger.exception("Full database connection error details")
            raise
    
    def test_connection(self):
        """Test database connectivity for health checks"""
        try:
            logger.debug("Testing database connection...")
            start_time = time.time()

            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                connection_result = result.fetchone()[0] == 1

            elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

            if connection_result:
                logger.success(f"Database connection test successful ({elapsed_time:.2f}ms)")
            else:
                logger.warning("Database connection test returned unexpected result")

            return connection_result
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            logger.exception("Database connectivity error details")
            raise
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Table creation failed: {str(e)}")
            raise
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        session = self.get_session()
        try:
            logger.info(f"Authentication attempt for user: {username}")
            logger.debug(f"Querying database for user: {username}")

            admin_user = session.query(AdminUser).filter(
                AdminUser.username == username,
                AdminUser.is_active
            ).first()

            if not admin_user:
                logger.warning(f"Authentication failed - User not found: {username}")
                return None

            if admin_user.locked_until and admin_user.locked_until > datetime.utcnow():
                time_remaining = (admin_user.locked_until - datetime.utcnow()).seconds // 60
                logger.warning(f"Authentication failed - User account locked: {username} (locked for {time_remaining} more minutes)")
                return None

            logger.debug(f"Validating password for user: {username}")

            if bcrypt.checkpw(password.encode('utf-8'), admin_user.password_hash.encode('utf-8')):
                admin_user.failed_login_attempts = 0
                admin_user.locked_until = None
                session.commit()

                logger.success(f"Authentication successful for user: {username} (role: {admin_user.role})")
                logger.info(f"User {username} logged in with role {admin_user.role} (user_id: {admin_user.user_id})")

                return User(
                    user_id=admin_user.user_id,
                    username=admin_user.username,
                    role=admin_user.role,
                    first_name=admin_user.first_name,
                    last_name=admin_user.last_name,
                    email=admin_user.email,
                    is_active=admin_user.is_active,
                    patient_id=admin_user.patient_id
                )
            else:
                admin_user.failed_login_attempts += 1
                if admin_user.failed_login_attempts >= 5:
                    admin_user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                    logger.error(f"User account locked due to failed attempts: {username} (attempts: {admin_user.failed_login_attempts})")
                else:
                    logger.warning(f"Invalid password for user: {username} (failed attempts: {admin_user.failed_login_attempts}/5)")

                session.commit()
                return None

        except Exception as e:
            logger.error(f"Authentication error for user {username}: {str(e)}")
            logger.exception("Full authentication error details")
            session.rollback()
            return None
        finally:
            session.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID for token validation"""
        session = self.get_session()
        try:
            admin_user = session.query(AdminUser).filter(
                AdminUser.user_id == user_id,
                AdminUser.is_active
            ).first()
            
            if not admin_user:
                return None
            
            return User(
                user_id=admin_user.user_id,
                username=admin_user.username,
                role=admin_user.role,
                first_name=admin_user.first_name,
                last_name=admin_user.last_name,
                email=admin_user.email,
                is_active=admin_user.is_active,
                patient_id=admin_user.patient_id
            )
            
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return None
        finally:
            session.close()
    
    def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        session = self.get_session()
        try:
            admin_user = session.query(AdminUser).filter(
                AdminUser.user_id == user_id
            ).first()
            
            if admin_user:
                admin_user.last_login = datetime.utcnow()
                session.commit()
                
        except Exception as e:
            logger.error(f"Update last login error: {str(e)}")
            session.rollback()
        finally:
            session.close()
    
    def execute_query(self, sql_query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute SQL query with timing and error handling"""
        start_time = time.time()
        results = []
        
        try:
            with self.engine.connect() as conn:
                # CRITICAL FIX: Add query timeout enforcement to prevent DoS
                # Use execution_options to set timeout at application level
                if parameters:
                    result = conn.execute(
                        text(sql_query).execution_options(timeout=Config.QUERY_TIMEOUT),
                        parameters
                    )
                else:
                    result = conn.execute(
                        text(sql_query).execution_options(timeout=Config.QUERY_TIMEOUT)
                    )
                
                if result.returns_rows:
                    columns = result.keys()
                    rows = result.fetchall()
                    
                    for row in rows:
                        results.append(dict(zip(columns, row)))
                else:
                    results = [{"message": "Query executed successfully", "rows_affected": result.rowcount}]
                
                execution_time = time.time() - start_time
                logger.info(f"Query executed in {execution_time:.3f}s, returned {len(results)} rows")
                
                return results
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query execution failed in {execution_time:.3f}s: {str(e)}")
            raise
    
    def execute_safe_query(self, sql_query: str, user_role: str, user_id: int = None, user_patient_id: int = None) -> QueryResult:
        """Execute query with role-based security controls

        Args:
            sql_query: The SQL query to execute
            user_role: The role of the user executing the query
            user_id: The user's ID (optional)
            user_patient_id: For patient role, the patient_id to restrict access to (optional)
        """
        start_time = time.time()

        try:
            if not self._validate_query_permissions(sql_query, user_role, user_patient_id):
                raise PermissionError(f"Query not allowed for role: {user_role}")

            raw_results = self.execute_query(sql_query)

            execution_time = time.time() - start_time
            metadata = {
                'execution_time': f"{execution_time:.3f}s",
                'user_role': user_role,
                'security_mode': 'secure'
            }

            result = QueryResult(raw_results, metadata)

            if user_role != 'admin':
                result = result.filter_sensitive_data(user_role, Config.SENSITIVE_COLUMNS)

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Safe query execution failed: {str(e)}")
            raise
    
    def _validate_query_permissions(self, sql_query: str, user_role: str, user_patient_id: int = None) -> bool:
        """Validate if user role can execute the query

        Args:
            sql_query: The SQL query to validate
            user_role: The role of the user executing the query
            user_patient_id: For patient role, the patient_id to restrict access to
        """
        query_upper = sql_query.upper().strip()

        if user_role == 'admin':
            return True

        role_permissions = Config.ROLE_PERMISSIONS.get(user_role, {})
        allowed_tables = role_permissions.get('tables', [])

        # Block highly dangerous operations for all non-admin users
        if any(dangerous in query_upper for dangerous in ['DROP', 'ALTER', 'TRUNCATE']):
            return False

        # Patient role restrictions: can only SELECT, UPDATE, INSERT (no DELETE)
        if user_role == 'patient':
            if 'DELETE' in query_upper:
                return False

            # CRITICAL: For UPDATE/INSERT on patients/medical_records tables,
            # verify the query includes patient_id restriction in WHERE clause
            if 'UPDATE' in query_upper or 'INSERT' in query_upper:
                # For UPDATE, must have WHERE patient_id = <user_patient_id>
                if 'UPDATE' in query_upper and ('PATIENTS' in query_upper or 'MEDICAL_RECORDS' in query_upper):
                    # Check for WHERE clause with patient_id restriction
                    if 'WHERE' not in query_upper:
                        logger.warning("Patient UPDATE query blocked: missing WHERE clause")
                        return False

                    # Verify patient_id is in the WHERE clause
                    if 'PATIENT_ID' not in query_upper:
                        logger.warning("Patient UPDATE query blocked: missing patient_id in WHERE clause")
                        return False

                    # If user_patient_id is provided, verify it matches
                    if user_patient_id:
                        # Look for patient_id = <number> in the query
                        where_pattern = r'WHERE.*PATIENT_ID\s*=\s*(\d+)'
                        match = re.search(where_pattern, query_upper)
                        if match:
                            query_patient_id = int(match.group(1))
                            if query_patient_id != user_patient_id:
                                logger.warning(f"Patient UPDATE query blocked: patient_id {query_patient_id} does not match user's patient_id {user_patient_id}")
                                return False

        # Extract all table names from the query (SELECT, UPDATE, INSERT, DELETE)
        table_pattern = r'\bFROM\s+(\w+)|\bJOIN\s+(\w+)|\bUPDATE\s+(\w+)|\bINTO\s+(\w+)|\bDELETE\s+FROM\s+(\w+)'
        table_matches = re.findall(table_pattern, query_upper)

        # Check if all referenced tables are in the user's allowed list
        for match_group in table_matches:
            for table in match_group:
                if table and table.lower() not in [t.lower() for t in allowed_tables]:
                    return False

        return True
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get database schema information for LLM context"""
        try:
            schema_info = {}
            
            with self.engine.connect() as conn:
                tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                """
                
                tables_result = conn.execute(text(tables_query))
                
                for table_row in tables_result:
                    table_name = table_row[0]
                    
                    columns_query = """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = :table_name
                    ORDER BY ordinal_position
                    """
                    
                    columns_result = conn.execute(text(columns_query), {"table_name": table_name})
                    
                    columns = []
                    for col_row in columns_result:
                        columns.append({
                            'name': col_row[0],
                            'type': col_row[1],
                            'nullable': col_row[2] == 'YES',
                            'default': col_row[3]
                        })
                    
                    schema_info[table_name] = {
                        'columns': columns,
                        'description': self._get_table_description(table_name)
                    }
            
            return schema_info
            
        except Exception as e:
            logger.error(f"Schema info retrieval failed: {str(e)}")
            return {}
    
    def _get_table_description(self, table_name: str) -> str:
        """Get human-readable table description"""
        descriptions = {
            'patients': 'Patient demographic and contact information',
            'doctors': 'Healthcare provider information',
            'medical_records': 'Patient medical history and treatments',
            'admin_users': 'System users and authentication',
            'audit_log': 'Security and access audit trail'
        }
        return descriptions.get(table_name, f'Table: {table_name}')
    
    def log_audit(self, user_id: int, query: str, result_status: str, 
                  security_mode: str = None, username: str = None, 
                  execution_time: str = None, rows_affected: int = None,
                  error_message: str = None, ip_address: str = None,
                  user_agent: str = None):
        """Log security audit entry"""
        session = self.get_session()
        try:
            audit_entry = AuditLog(
                user_id=user_id,
                username=username,
                action='QUERY',
                query=query,
                result_status=result_status,
                security_mode=security_mode,
                ip_address=ip_address,
                user_agent=user_agent,
                execution_time=execution_time,
                rows_affected=rows_affected,
                error_message=error_message
            )
            
            session.add(audit_entry)
            session.commit()
            
            logger.info(f"Audit log entry created for user {user_id}")
            
        except Exception as e:
            logger.error(f"Audit logging failed: {str(e)}")
            session.rollback()
        finally:
            session.close()
    
    def get_audit_logs(self, limit: int = 100, offset: int = 0, 
                       user_id: int = None, status: str = None) -> List[Dict[str, Any]]:
        """Retrieve audit logs with filtering"""
        session = self.get_session()
        try:
            query = session.query(AuditLog)
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            if status:
                query = query.filter(AuditLog.result_status == status)
            
            query = query.order_by(AuditLog.timestamp.desc())
            query = query.offset(offset).limit(limit)
            
            audit_logs = query.all()
            
            return [log.to_dict() for log in audit_logs]
            
        except Exception as e:
            logger.error(f"Audit log retrieval failed: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_patients_for_user(self, user: User, limit: int = None) -> List[Dict[str, Any]]:
        """Get patients accessible to user based on role"""
        session = self.get_session()
        try:
            query = session.query(Patient)
            
            if user.role == 'patient':
                if user.patient_id:
                    query = query.filter(Patient.patient_id == user.patient_id)
                else:
                    return []
            
            if limit:
                query = query.limit(limit)
            
            patients = query.all()
            
            include_sensitive = user.role in ['admin', 'doctor']
            return [patient.to_dict(include_sensitive) for patient in patients]
            
        except Exception as e:
            logger.error(f"Patient retrieval failed: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_medical_records_for_user(self, user: User, patient_id: int = None, 
                                   limit: int = None) -> List[Dict[str, Any]]:
        """Get medical records accessible to user"""
        session = self.get_session()
        try:
            query = session.query(MedicalRecord)
            
            if user.role == 'patient':
                if user.patient_id:
                    query = query.filter(MedicalRecord.patient_id == user.patient_id)
                else:
                    return []
            elif patient_id:
                query = query.filter(MedicalRecord.patient_id == patient_id)
            
            if limit:
                query = query.limit(limit)
            
            records = query.all()
            
            include_sensitive = user.role in ['admin', 'doctor']
            return [record.to_dict(include_sensitive) for record in records]
            
        except Exception as e:
            logger.error(f"Medical records retrieval failed: {str(e)}")
            return []
        finally:
            session.close()
    
    def create_sample_data(self):
        """Create sample data for testing (if not exists)"""
        session = self.get_session()
        try:
            existing_patients = session.query(Patient).count()
            if existing_patients > 0:
                logger.info("Sample data already exists, skipping creation")
                return
            
            logger.info("Creating sample data...")
            
            password_hash = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            email_domain = Config.EMAIL_DOMAIN

            admin_user = AdminUser(
                username='admin',
                password_hash=password_hash,
                role='admin',
                first_name='System',
                last_name='Administrator',
                email=f'admin@{email_domain}'
            )
            session.add(admin_user)

            doctor_user = AdminUser(
                username='doctor',
                password_hash=password_hash,
                role='doctor',
                first_name='Test',
                last_name='Doctor',
                email=f'doctor@{email_domain}'
            )
            session.add(doctor_user)

            nurse_user = AdminUser(
                username='nurse',
                password_hash=password_hash,
                role='nurse',
                first_name='Test',
                last_name='Nurse',
                email=f'nurse@{email_domain}'
            )
            session.add(nurse_user)
            
            session.commit()
            logger.info("Sample admin users created")
            
        except Exception as e:
            logger.error(f"Sample data creation failed: {str(e)}")
            session.rollback()
        finally:
            session.close()
    
    def backup_database(self, backup_path: str = None) -> str:
        """Create database backup for testing"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"healthcare_security_backup_{timestamp}.sql"
        
        try:
            import subprocess
            
            cmd = [
                'pg_dump',
                '--host', Config.DATABASE_HOST,
                '--port', str(Config.DATABASE_PORT),
                '--username', Config.DATABASE_USER,
                '--dbname', Config.DATABASE_NAME,
                '--file', backup_path,
                '--verbose'
            ]
            
            env = {'PGPASSWORD': Config.DATABASE_PASSWORD}
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Database backup created: {backup_path}")
                return backup_path
            else:
                logger.error(f"Backup failed: {result.stderr}")
                raise Exception(f"Backup failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Database backup error: {str(e)}")
            raise
    
    def restore_database(self, backup_path: str):
        """Restore database from backup"""
        try:
            import subprocess
            
            cmd = [
                'psql',
                '--host', Config.DATABASE_HOST,
                '--port', str(Config.DATABASE_PORT),
                '--username', Config.DATABASE_USER,
                '--dbname', Config.DATABASE_NAME,
                '--file', backup_path
            ]
            
            env = {'PGPASSWORD': Config.DATABASE_PASSWORD}
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Database restored from: {backup_path}")
            else:
                logger.error(f"Restore failed: {result.stderr}")
                raise Exception(f"Restore failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Database restore error: {str(e)}")
            raise
    
    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")