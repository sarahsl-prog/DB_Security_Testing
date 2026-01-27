!!! warning "**DRAFT** - This documentation is a work in progress"

# Database Host Setup

!!! info "Host Information"
    **Hostname:** database-01
    **IP Address:** 192.168.1.11
    **Operating System:** Ubuntu 25.04
    **Virtualization:** VMware Workstation 17.6.2 VM
    **Hardware:** 16GB RAM, 2 vCPU, 100GB Storage

    **Services:**

    - PostgreSQL 17 (Database Server)
    - Apache 2 (Web Server)

!!! note "Example IP Addresses"
    The IP addresses in this guide (192.168.1.11, 192.168.1.10, etc.) are **examples only**. For actual deployment:

    - **Docker (Recommended):** No manual IP configuration needed - see [Docker Deployment](../DOCKER_QUICKSTART.md)
    - **Manual Setup:** Replace example IPs with your actual network addresses
    - **Environment Variables:** Use `.env` files to configure your specific IPs

---

## Quick Links

- [Installation Steps](#installation-steps)
- [PostgreSQL Configuration](#postgresql-configuration)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Database Setup](#database-setup)
- [Verification](#verification)
- [Configuration Files](#configuration-files)

---

## Installation Steps

### 1. Initial System Setup

Update the system and install base dependencies:

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install base dependencies
sudo apt install -y build-essential curl git wget vim

# Install PostgreSQL repository
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh

# Verify repository
sudo apt update
```

### 2. Install PostgreSQL 17

```bash
# Install PostgreSQL 17
sudo apt install -y postgresql-17 postgresql-contrib-17

# Verify installation
psql --version

# Check PostgreSQL status
sudo systemctl status postgresql
```

### 3. Install Apache (Optional)

```bash
# Install Apache web server
sudo apt install -y apache2

# Verify Apache version
apache2 -v

# Start and enable Apache
sudo systemctl start apache2
sudo systemctl enable apache2

# Check status
sudo systemctl status apache2
```

---

## PostgreSQL Configuration

### 1. Configure PostgreSQL to Accept Remote Connections

Edit PostgreSQL configuration file:

```bash
sudo nano /etc/postgresql/17/main/postgresql.conf
```

Modify the following settings:

```conf
# Listen on all interfaces (vulnerable mode)
# For secure mode, specify only the frontend/backend IP
listen_addresses = '*'          # Vulnerable mode
# listen_addresses = '192.168.1.11,127.0.0.1'  # Secure mode

# Port configuration
port = 5432

# Connection settings
max_connections = 100

# Memory settings
shared_buffers = 4GB           # 25% of RAM
effective_cache_size = 12GB     # 75% of RAM
work_mem = 64MB
maintenance_work_mem = 1GB

# Logging (for research/audit)
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'all'           # Log all statements for research
log_duration = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### 2. Configure Client Authentication

Edit pg_hba.conf:

```bash
sudo nano /etc/postgresql/17/main/pg_hba.conf
```

Add connection rules:

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             postgres                                peer
local   all             all                                     peer

# IPv4 local connections
host    all             all             127.0.0.1/32            scram-sha-256

# Vulnerable mode - allow from frontend/backend without SSL
host    healthcare_research  healthcare_user  192.168.1.10/32   md5

# Secure mode - require SSL from frontend/backend (uncomment for secure mode)
# hostssl  healthcare_research  healthcare_user  192.168.1.10/32   md5

# Reject all other connections
host    all             all             0.0.0.0/0               reject
```

### 3. Restart PostgreSQL

```bash
# Restart PostgreSQL to apply changes
sudo systemctl restart postgresql

# Verify it's running
sudo systemctl status postgresql

# Check if listening on port 5432
sudo netstat -tulpn | grep 5432
```

---

## SSL/TLS Configuration

### 1. Generate SSL Certificates (Secure Mode)

```bash
# Create directory for certificates
sudo mkdir -p /var/lib/postgresql/17/main/ssl
cd /var/lib/postgresql/17/main/ssl

# Generate self-signed certificate
sudo openssl req -new -x509 -days 365 -nodes -text \
  -out server.crt \
  -keyout server.key \
  -subj "/CN=database-01"

# Set proper permissions
sudo chown postgres:postgres server.crt server.key
sudo chmod 600 server.key
sudo chmod 644 server.crt
```

### 2. Enable SSL in PostgreSQL

Edit postgresql.conf:

```bash
sudo nano /etc/postgresql/17/main/postgresql.conf
```

Add/modify SSL settings:

```conf
# SSL Configuration (for secure mode)
ssl = on
ssl_cert_file = '/var/lib/postgresql/17/main/ssl/server.crt'
ssl_key_file = '/var/lib/postgresql/17/main/ssl/server.key'
ssl_min_protocol_version = 'TLSv1.2'
ssl_prefer_server_ciphers = on
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
```

Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

---

## Database Setup

### 1. Create Database User

```bash
# Switch to postgres user
sudo -u postgres psql

# In psql prompt, create user
CREATE USER healthcare_user WITH PASSWORD 'your_secure_password_here';

# Grant privileges
ALTER USER healthcare_user CREATEDB;

# Exit psql
\q
```

### 2. Create Healthcare Database

```bash
# Create database
sudo -u postgres createdb -O healthcare_user healthcare_research

# Verify database creation
sudo -u postgres psql -l | grep healthcare
```

### 3. Load Database Schema

```bash
# Copy your schema file to the server
scp schema.sql user@192.168.1.11:/tmp/

# Load the schema
sudo -u postgres psql -d healthcare_research -f /tmp/schema.sql

# Verify tables were created
sudo -u postgres psql -d healthcare_research -c "\dt"
```

### 4. Create Tables and Seed Data

=== "Schema Creation"

    ```bash
    # Connect to database
    sudo -u postgres psql healthcare_research
    ```

    ```sql
    -- Create patients table
    CREATE TABLE patients (
        patient_id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        date_of_birth DATE NOT NULL,
        ssn VARCHAR(11) NOT NULL UNIQUE,
        insurance_id VARCHAR(20) NOT NULL,
        phone_number VARCHAR(15),
        email VARCHAR(100),
        address TEXT,
        emergency_contact VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create doctors table
    CREATE TABLE doctors (
        doctor_id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        specialization VARCHAR(100) NOT NULL,
        license_number VARCHAR(20) NOT NULL UNIQUE,
        phone_number VARCHAR(15),
        email VARCHAR(100),
        department VARCHAR(50),
        hire_date DATE,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create medical_records table
    CREATE TABLE medical_records (
        record_id SERIAL PRIMARY KEY,
        patient_id INTEGER NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
        doctor_id INTEGER NOT NULL REFERENCES doctors(doctor_id) ON DELETE RESTRICT,
        visit_date TIMESTAMP NOT NULL,
        diagnosis TEXT NOT NULL,
        treatment TEXT,
        medication TEXT,
        notes TEXT,
        follow_up_date DATE,
        is_confidential BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create admin_users table
    CREATE TABLE admin_users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'doctor', 'nurse', 'patient')),
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(100),
        is_active BOOLEAN DEFAULT TRUE,
        last_login TIMESTAMP,
        failed_login_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        patient_id INTEGER REFERENCES patients(patient_id)
    );

    -- Create audit_log table
    CREATE TABLE audit_log (
        log_id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        username VARCHAR(50),
        action VARCHAR(50) NOT NULL,
        query TEXT,
        result_status VARCHAR(20) NOT NULL CHECK (result_status IN ('SUCCESS', 'ERROR', 'BLOCKED')),
        security_mode VARCHAR(20) CHECK (security_mode IN ('vulnerable', 'secure')),
        ip_address VARCHAR(45),
        user_agent TEXT,
        execution_time VARCHAR(20),
        rows_affected INTEGER,
        error_message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    );

    -- Create indexes
    CREATE INDEX idx_patients_ssn ON patients(ssn);
    CREATE INDEX idx_patients_name ON patients(last_name, first_name);
    CREATE INDEX idx_doctors_license ON doctors(license_number);
    CREATE INDEX idx_doctors_specialization ON doctors(specialization);
    CREATE INDEX idx_medical_records_patient ON medical_records(patient_id);
    CREATE INDEX idx_medical_records_doctor ON medical_records(doctor_id);
    CREATE INDEX idx_medical_records_date ON medical_records(visit_date);
    CREATE INDEX idx_admin_users_username ON admin_users(username);
    CREATE INDEX idx_admin_users_role ON admin_users(role);
    CREATE INDEX idx_audit_log_user ON audit_log(user_id);
    CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
    CREATE INDEX idx_audit_log_action ON audit_log(action);
    ```

=== "Seed Test Data"

    ```bash
    # Create seed data script
    nano /tmp/seed_data.sql
    ```

    ```sql
    -- Insert test patients
    INSERT INTO patients (first_name, last_name, date_of_birth, ssn, insurance_id, phone_number, email, address) VALUES
    ('John', 'Doe', '1980-05-15', '123-45-6789', 'INS001', '555-0101', 'john.doe@email.com', '123 Main St'),
    ('Jane', 'Smith', '1992-08-22', '987-65-4321', 'INS002', '555-0102', 'jane.smith@email.com', '456 Oak Ave'),
    ('Bob', 'Johnson', '1975-12-10', '555-12-3456', 'INS003', '555-0103', 'bob.j@email.com', '789 Pine Rd');

    -- Insert test doctors
    INSERT INTO doctors (first_name, last_name, specialization, license_number, department, hire_date) VALUES
    ('Sarah', 'Wilson', 'Cardiology', 'MD123456', 'Cardiology', '2015-01-15'),
    ('Michael', 'Brown', 'Internal Medicine', 'MD789012', 'General Medicine', '2018-06-01'),
    ('Emily', 'Davis', 'Pediatrics', 'MD345678', 'Pediatrics', '2020-03-10');

    -- Insert test admin users (passwords are bcrypt hashed 'password123')
    INSERT INTO admin_users (username, password_hash, role, first_name, last_name, email) VALUES
    ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYBf5W8J7HW', 'admin', 'Admin', 'User', 'admin@hospital.com'),
    ('doctor1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYBf5W8J7HW', 'doctor', 'Sarah', 'Wilson', 'swilson@hospital.com'),
    ('nurse1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYBf5W8J7HW', 'nurse', 'Mary', 'Garcia', 'mgarcia@hospital.com');
    ```

    ```bash
    # Load seed data
    sudo -u postgres psql -d healthcare_research -f /tmp/seed_data.sql
    ```

---

## Verification

### Test Database Connectivity

**1. Local Connection Test:**

```bash
# Test local connection
sudo -u postgres psql -d healthcare_research

# In psql, run test query
SELECT COUNT(*) FROM patients;

# Exit
\q
```

**2. Remote Connection Test (from Frontend/Backend host):**

```bash
# Test from frontend/backend host
psql -h 192.168.1.11 -U healthcare_user -d healthcare_research

# If successful, you'll see the psql prompt
# Run a test query
SELECT * FROM admin_users WHERE role = 'admin';

# Exit
\q
```

**3. SSL Connection Test (Secure Mode):**

```bash
# Test SSL connection
psql "sslmode=require host=192.168.1.11 dbname=healthcare_research user=healthcare_user"

# Verify SSL is active
\conninfo
```

**4. Check PostgreSQL Logs:**

```bash
# View recent logs
sudo tail -f /var/log/postgresql/postgresql-17-main.log

# Check for connection attempts
sudo grep "connection" /var/log/postgresql/postgresql-17-main.log
```

---

## Configuration Files

### Download Configuration Files

- [:material-download: postgresql.conf](../config-files/postgresql.conf) - Main PostgreSQL configuration
- [:material-download: pg_hba.conf](../config-files/pg_hba.conf) - Client authentication configuration
- [:material-download: schema.sql](../config-files/schema.sql) - Complete database schema
- [:material-download: seed_data.sql](../config-files/seed_data.sql) - Test data for development

### View Configuration Files

=== "postgresql.conf"

    ```conf title="/etc/postgresql/17/main/postgresql.conf"
    # Connection Settings
    listen_addresses = '*'
    port = 5432
    max_connections = 100

    # Memory Settings
    shared_buffers = 4GB
    effective_cache_size = 12GB
    work_mem = 64MB
    maintenance_work_mem = 1GB

    # Logging
    logging_collector = on
    log_directory = 'log'
    log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
    log_statement = 'all'
    log_duration = on
    log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

    # SSL Configuration (Secure Mode)
    # ssl = on
    # ssl_cert_file = '/var/lib/postgresql/17/main/ssl/server.crt'
    # ssl_key_file = '/var/lib/postgresql/17/main/ssl/server.key'
    # ssl_min_protocol_version = 'TLSv1.2'
    ```

=== "pg_hba.conf"

    ```conf title="/etc/postgresql/17/main/pg_hba.conf"
    # TYPE  DATABASE        USER            ADDRESS                 METHOD
    
    # Local connections
    local   all             postgres                                peer
    local   all             all                                     peer
    
    # IPv4 local connections
    host    all             all             127.0.0.1/32            scram-sha-256
    
    # Vulnerable mode - allow from frontend/backend
    host    healthcare_research  healthcare_user  192.168.1.10/32   md5
    
    # Secure mode - require SSL (uncomment for secure mode)
    # hostssl  healthcare_research  healthcare_user  192.168.1.10/32   md5
    
    # Reject all other connections
    host    all             all             0.0.0.0/0               reject
    ```

---

## Firewall Configuration

### Vulnerable Mode

Allow PostgreSQL from any IP (for testing):

```bash
# Allow PostgreSQL port
sudo ufw allow 5432/tcp

# Allow Apache
sudo ufw allow 80/tcp

# Allow SSH
sudo ufw allow ssh

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Secure Mode

Restrict PostgreSQL to Frontend/Backend host only:

```bash
# Remove allow all rule
sudo ufw delete allow 5432/tcp

# Allow PostgreSQL only from frontend/backend
sudo ufw allow from 192.168.1.10 to any port 5432 proto tcp

# Allow Apache
sudo ufw allow 80/tcp

# Allow SSH
sudo ufw allow ssh

# Enable firewall
sudo ufw enable

# Verify rules
sudo ufw status numbered
```

---

## Troubleshooting

!!! bug "Common Issues"

    **Cannot connect remotely:**
    ```bash
    # Check if PostgreSQL is listening on all interfaces
    sudo netstat -tulpn | grep 5432
    
    # Should show 0.0.0.0:5432, not 127.0.0.1:5432
    
    # Verify postgresql.conf
    sudo grep "listen_addresses" /etc/postgresql/17/main/postgresql.conf
    
    # Check pg_hba.conf for correct IP
    sudo cat /etc/postgresql/17/main/pg_hba.conf | grep 192.168.1.10
    
    # Check firewall
    sudo ufw status
    ```

    **Authentication failed:**
    ```bash
    # Verify user exists
    sudo -u postgres psql -c "\du"
    
    # Reset password if needed
    sudo -u postgres psql -c "ALTER USER healthcare_user PASSWORD 'newpassword';"
    
    # Check pg_hba.conf authentication method
    sudo grep healthcare_user /etc/postgresql/17/main/pg_hba.conf
    ```

    **SSL connection fails:**
    ```bash
    # Verify SSL is enabled
    sudo -u postgres psql -c "SHOW ssl;"
    
    # Check certificate files exist
    ls -l /var/lib/postgresql/17/main/ssl/
    
    # Verify certificate permissions
    sudo ls -l /var/lib/postgresql/17/main/ssl/server.key
    # Should be: -rw------- postgres postgres
    
    # Check PostgreSQL logs
    sudo tail -f /var/log/postgresql/postgresql-17-main.log
    ```

    **Performance issues:**
    ```bash
    # Check current connections
    sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
    
    # Check slow queries
    sudo -u postgres psql -d healthcare_research -c "SELECT query, state, wait_event FROM pg_stat_activity WHERE state != 'idle';"
    
    # Analyze table statistics
    sudo -u postgres psql -d healthcare_research -c "ANALYZE VERBOSE;"
    ```

---

## Backup and Restore

### Create Backup

```bash
# Full database backup
sudo -u postgres pg_dump healthcare_research > healthcare_backup_$(date +%Y%m%d).sql

# Backup with compression
sudo -u postgres pg_dump healthcare_research | gzip > healthcare_backup_$(date +%Y%m%d).sql.gz

# Backup schema only
sudo -u postgres pg_dump -s healthcare_research > schema_backup.sql

# Backup data only
sudo -u postgres pg_dump -a healthcare_research > data_backup.sql
```

### Restore Backup

```bash
# Restore from backup
sudo -u postgres psql healthcare_research < healthcare_backup_20250101.sql

# Restore from compressed backup
gunzip -c healthcare_backup_20250101.sql.gz | sudo -u postgres psql healthcare_research
```

---

## Performance Tuning

### Monitor Database Performance

```bash
# Check database size
sudo -u postgres psql -d healthcare_research -c "SELECT pg_size_pretty(pg_database_size('healthcare_research'));"

# Check table sizes
sudo -u postgres psql -d healthcare_research -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Check index usage
sudo -u postgres psql -d healthcare_research -c "SELECT schemaname, tablename, indexname, idx_scan FROM pg_stat_user_indexes ORDER BY idx_scan;"

# View active queries
sudo -u postgres psql -c "SELECT pid, usename, application_name, client_addr, state, query FROM pg_stat_activity WHERE state != 'idle';"
```

---

## Security Hardening Checklist

- [x] PostgreSQL installed and configured
- [x] Database and user created
- [x] Schema loaded with indexes
- [ ] SSL/TLS certificates generated (secure mode)
- [ ] SSL enabled in postgresql.conf (secure mode)
- [ ] pg_hba.conf restricted to specific IP (secure mode)
- [ ] Firewall configured to allow only frontend/backend (secure mode)
- [ ] Strong password set for database user
- [ ] Logging enabled for audit purposes
- [ ] Regular backups scheduled
- [ ] Performance monitoring configured

---

## Related Documentation

- [Frontend/Backend Host Setup](frontend-backend.md)
- [LLM Host Setup](llm-host.md)
- [Database Schema Documentation](../database/schema.md)
- [Security Testing Guide](../security/security-testing.md)

---

*Last Updated: [Date]*  
*Lab Version: 1.0*
