# Healthcare Database Application - Deployment Checklist

## Overview
This checklist covers all requirements for deploying the Healthcare Database Application across three hosts:
- **PostgreSQL Database Server** (192.168.100.30)
- **Ollama LLM Service** (192.168.100.1) 
- **Backend API Server** (192.168.100.20)

---

## 🐘 PostgreSQL Database Host (192.168.100.30:5432)

### System Requirements
- [ ] PostgreSQL 12+ installed and running
- [ ] Port 5432 accessible from Backend API host (192.168.100.20)
- [ ] Sufficient disk space for healthcare data
- [ ] Memory: Minimum 4GB RAM recommended

### Database Setup
- [ ] Create database: `health`
- [ ] Set database encoding to UTF-8
- [ ] Configure postgresql.conf for network connections
- [ ] Update pg_hba.conf for authentication

### Required Database Users
- [ ] **healthcare_app** - Main application user
  - Password: (generate secure password)
  - Privileges: SELECT, INSERT, UPDATE, DELETE on application tables
  - Connection limit: 20
- [ ] **healthcare_readonly** - Read-only user for reports
  - Password: (generate secure password)  
  - Privileges: SELECT only on patient tables
  - Connection limit: 10
- [ ] **healthcare_admin** - Administrative user
  - Password: (generate secure password)
  - Privileges: ALL on health database
  - Connection limit: 5

### Required Database Schema
```sql
-- Core application tables
- [ ] patients (patient_id, first_name, last_name, birth_date, user_id, created_at)
- [ ] diagnoses (diagnosis_id, patient_id, diagnosis_name, diagnosis_date, icd_code)
- [ ] doctors (doctor_id, first_name, last_name, department, email, phone, created_at)
- [ ] appointments (appointment_id, patient_id, doctor_id, appointment_date, appointment_time, status)
- [ ] users (user_id, username, password_hash, email, role, created_at, last_login)
- [ ] audit_logs (log_id, user_id, action, table_name, record_id, timestamp, ip_address)
```

### Indexes and Performance
- [ ] Primary keys on all tables
- [ ] Index on patients.user_id
- [ ] Index on diagnoses.patient_id
- [ ] Index on appointments.patient_id, appointments.doctor_id
- [ ] Index on users.username
- [ ] Index on audit_logs.timestamp

### Security Configuration
- [ ] SSL/TLS enabled for connections
- [ ] Row-level security (RLS) policies for patient data
- [ ] Audit logging enabled
- [ ] Regular backup schedule configured
- [ ] Password policies enforced

### Sample Data (Optional for Testing)
- [ ] Insert demo patients, doctors, appointments
- [ ] Create test user accounts matching application demo credentials

---

## 🤖 Ollama LLM Host (192.168.100.1:11434)

### System Requirements
- [ ] Linux/macOS/Windows host with GPU support (recommended)
- [ ] Minimum 8GB RAM (16GB+ for larger models)
- [ ] 20GB+ disk space for models
- [ ] Port 11434 accessible from Backend API host (192.168.100.20)

### Ollama Installation
- [ ] Install Ollama from https://ollama.ai/download
- [ ] Verify installation: `ollama --version`
- [ ] Configure Ollama to listen on all interfaces: `export OLLAMA_HOST=0.0.0.0:11434`
- [ ] Start Ollama service: `ollama serve`

### Required Models
- [ ] **Code/SQL Generation Model**:
  - `ollama pull codellama:7b` OR `ollama pull llama2:7b`
  - Verify: `ollama list`
- [ ] **Text Analysis Model** (for security scanning):
  - `ollama pull llama2:7b` OR another suitable model
- [ ] Test model functionality: `ollama run codellama:7b "SELECT * FROM patients;"`

### Service Configuration
- [ ] Create systemd service file (Linux) or equivalent
- [ ] Configure auto-start on boot
- [ ] Set up log rotation
- [ ] Configure memory limits if needed

### API Endpoints Verification
- [ ] Health check: `curl http://192.168.100.1:11434/health`
- [ ] Model list: `curl http://192.168.100.1:11434/api/tags`
- [ ] Text generation: Test POST to `/api/generate`

### Performance Tuning
- [ ] GPU configuration (if available)
- [ ] Memory allocation settings
- [ ] Concurrent request limits
- [ ] Model loading optimization

---

## 🖥️ Backend API Host (192.168.100.20:5000)

### System Requirements
- [ ] Node.js 16+ OR Python 3.8+ (depending on implementation choice)
- [ ] Port 5000 accessible from frontend clients
- [ ] Network access to PostgreSQL (192.168.100.30:5432)
- [ ] Network access to Ollama (192.168.100.1:11434)

### Application Dependencies
**If Node.js:**
- [ ] Express.js framework
- [ ] PostgreSQL client (pg)
- [ ] JWT for authentication
- [ ] CORS middleware
- [ ] Helmet for security headers

**If Python:**
- [ ] Flask/FastAPI framework
- [ ] psycopg2 for PostgreSQL
- [ ] PyJWT for authentication
- [ ] flask-cors
- [ ] requests library for Ollama integration

### Required API Endpoints
- [ ] `POST /api/login` - User authentication
- [ ] `GET /api/verify` - JWT token verification
- [ ] `POST /api/query` - Natural language query processing
- [ ] `GET /health` - Backend health check
- [ ] `GET /api/db-status` - Database connectivity check

### Environment Configuration
```bash
# Database connection
- [ ] DB_HOST=192.168.100.30
- [ ] DB_PORT=5432
- [ ] DB_NAME=health
- [ ] DB_USER=healthcare_app
- [ ] DB_PASSWORD=(secure password)

# Ollama LLM service
- [ ] LLM_HOST=192.168.100.1
- [ ] LLM_PORT=11434
- [ ] LLM_MODEL=codellama:7b

# API configuration
- [ ] JWT_SECRET=(generate random secret)
- [ ] API_PORT=5000
- [ ] CORS_ORIGINS=http://frontend-host
```

### Security Implementation
- [ ] JWT token validation
- [ ] SQL injection prevention
- [ ] Input sanitization and validation
- [ ] Rate limiting
- [ ] HTTPS configuration (recommended)
- [ ] Security headers (CORS, CSP, etc.)

### User Authentication System
- [ ] Password hashing (bcrypt/scrypt)
- [ ] Session management
- [ ] Role-based access control (RBAC)
- [ ] Account lockout protection
- [ ] Password complexity requirements

### Integration Logic
- [ ] PostgreSQL connection pooling
- [ ] Ollama API client integration
- [ ] Natural language to SQL conversion
- [ ] Query result formatting
- [ ] Error handling and logging
- [ ] Audit trail implementation

---

## 🌐 Network and Security Requirements

### Firewall Configuration
**PostgreSQL Host (192.168.100.30):**
- [ ] Allow inbound on port 5432 from 192.168.100.20 only
- [ ] Block all other inbound database connections
- [ ] Allow outbound for updates/monitoring

**Ollama Host (192.168.100.1):**
- [ ] Allow inbound on port 11434 from 192.168.100.20 only
- [ ] Allow outbound for model downloads
- [ ] Block unnecessary ports

**Backend API Host (192.168.100.20):**
- [ ] Allow inbound on port 5000 from frontend clients
- [ ] Allow outbound to 192.168.100.30:5432 (PostgreSQL)
- [ ] Allow outbound to 192.168.100.1:11434 (Ollama)

### SSL/TLS Configuration
- [ ] Database connections use SSL
- [ ] API endpoints use HTTPS (recommended)
- [ ] Valid certificates configured
- [ ] TLS version 1.2+ only

### Monitoring and Logging
- [ ] Application logs configured
- [ ] Database query logging
- [ ] Failed authentication logging
- [ ] Health check monitoring
- [ ] Disk space monitoring
- [ ] Performance metrics collection

### Backup and Recovery
- [ ] PostgreSQL automated backups
- [ ] Application configuration backups
- [ ] Disaster recovery procedures documented
- [ ] Recovery testing performed

---

## 🧪 Testing and Validation

### Connectivity Testing
- [ ] Run `python testing.py` from application directory
- [ ] Verify all health checks pass
- [ ] Test authentication flow
- [ ] Test query processing end-to-end

### Functional Testing
- [ ] User login with all demo accounts
- [ ] Natural language query processing
- [ ] SQL generation and execution
- [ ] Role-based access control
- [ ] Error handling scenarios

### Security Testing
- [ ] SQL injection attempts blocked
- [ ] Malicious query detection working
- [ ] Authentication bypass attempts fail
- [ ] Audit logging captures events

### Performance Testing
- [ ] Concurrent user load testing
- [ ] Database query performance
- [ ] LLM response times acceptable
- [ ] Memory usage within limits

---

## 📋 Pre-Production Checklist

### Documentation
- [ ] API documentation complete
- [ ] Database schema documented
- [ ] Deployment procedures written
- [ ] Troubleshooting guide created
- [ ] User manual updated

### Security Review
- [ ] Penetration testing completed
- [ ] Security policies reviewed
- [ ] Access controls verified
- [ ] Vulnerability scan performed

### Final Validation
- [ ] All hosts communicating properly
- [ ] Application functionality verified
- [ ] Performance meets requirements
- [ ] Security measures active
- [ ] Monitoring systems operational
- [ ] Backup/recovery tested

---

## 🚀 Go-Live Preparation

- [ ] All checklist items completed
- [ ] Stakeholders notified
- [ ] Support team briefed
- [ ] Rollback plan prepared
- [ ] Maintenance window scheduled

---

**Note:** This checklist should be customized based on your specific environment, security requirements, and organizational policies. Always follow your institution's security and deployment guidelines.