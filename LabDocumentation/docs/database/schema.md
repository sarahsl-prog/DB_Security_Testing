<div align="center">
  <img src="../images/app-logo.jpg" alt="Healthcare Security Research Lab Logo" width="150"/>
</div>

# Healthcare Database Schema Documentation

## Overview

This PostgreSQL 17 database contains synthetic healthcare data designed for security vulnerability research. The schema includes patient health information (PHI), provider data, medical records, authentication systems, and comprehensive audit logging for security analysis.

**Database Name:** healthcare_research  
**DBMS:** PostgreSQL 17  
**Character Set:** UTF-8  
**Purpose:** Security research and SQL injection vulnerability testing

---

## Table: patients

**Purpose:** Stores patient demographic and contact information including Protected Health Information (PHI) for security testing scenarios.

| Column | Data Type | Constraints | Description | Security Classification |
|--------|-----------|-------------|-------------|------------------------|
| patient_id | SERIAL | PRIMARY KEY | Unique patient identifier, auto-incrementing | Public |
| first_name | VARCHAR(50) | NOT NULL | Patient's legal first name | PHI |
| last_name | VARCHAR(50) | NOT NULL | Patient's legal last name | PHI |
| date_of_birth | DATE | NOT NULL | Patient's date of birth | PHI |
| ssn | VARCHAR(11) | NOT NULL, UNIQUE | Social Security Number (format: XXX-XX-XXXX) | **HIGHLY SENSITIVE** |
| insurance_id | VARCHAR(20) | NOT NULL | Health insurance policy number | **SENSITIVE** |
| phone_number | VARCHAR(15) | NULL | Primary contact phone number | PHI |
| email | VARCHAR(100) | NULL | Email address for patient communications | PHI |
| address | TEXT | NULL | Full mailing address | PHI |
| emergency_contact | VARCHAR(100) | NULL | Emergency contact name and phone | PHI |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp | Metadata |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last modification timestamp | Metadata |

**Indexes:**
- `PRIMARY KEY` on patient_id
- `idx_patients_ssn` on ssn (UNIQUE)
- `idx_patients_name` on (last_name, first_name) - for name searches

**Foreign Key Relationships:**
- Referenced by: `medical_records.patient_id`
- Referenced by: `admin_users.patient_id`

**Security Considerations:**
- SSN field is primary target for SQL injection attacks in vulnerable mode
- Insurance ID should be masked for non-authorized roles
- All fields except patient_id are considered PHI under HIPAA
- Address field contains PII requiring protection

**Access Control:**
- Admin: Full access
- Doctor: Full read access
- Nurse: Limited read (no SSN, insurance)
- Patient: Own records only

---

## Table: doctors

**Purpose:** Stores healthcare provider information including credentials and contact details.

| Column | Data Type | Constraints | Description | Security Classification |
|--------|-----------|-------------|-------------|------------------------|
| doctor_id | SERIAL | PRIMARY KEY | Unique doctor identifier, auto-incrementing | Public |
| first_name | VARCHAR(50) | NOT NULL | Doctor's first name | Public |
| last_name | VARCHAR(50) | NOT NULL | Doctor's last name | Public |
| specialization | VARCHAR(100) | NOT NULL | Medical specialization (e.g., Cardiology, Oncology) | Public |
| license_number | VARCHAR(20) | NOT NULL, UNIQUE | State medical license number | **SENSITIVE** |
| phone_number | VARCHAR(15) | NULL | Office phone number | Public |
| email | VARCHAR(100) | NULL | Professional email address | Public |
| department | VARCHAR(50) | NULL | Hospital department assignment | Public |
| hire_date | DATE | NULL | Date of employment start | Internal |
| is_active | BOOLEAN | DEFAULT TRUE | Employment status flag | Internal |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp | Metadata |

**Indexes:**
- `PRIMARY KEY` on doctor_id
- `idx_doctors_license` on license_number (UNIQUE)
- `idx_doctors_specialization` on specialization - for specialty searches

**Foreign Key Relationships:**
- Referenced by: `medical_records.doctor_id`

**Security Considerations:**
- License numbers should be restricted to admin/HR roles
- is_active flag prevents unauthorized access by former employees
- Personal contact information requires protection

**Access Control:**
- Admin: Full access
- Doctor: Read own record, read other doctors' basic info
- Nurse: Read basic info (no license numbers)
- Patient: Read basic info only

---

## Table: medical_records

**Purpose:** Stores clinical encounter data linking patients and doctors, including diagnoses, treatments, and medications. Core clinical data repository.

| Column | Data Type | Constraints | Description | Security Classification |
|--------|-----------|-------------|-------------|------------------------|
| record_id | SERIAL | PRIMARY KEY | Unique medical record identifier, auto-incrementing | Public |
| patient_id | INTEGER | NOT NULL, FK → patients | Reference to patient | Public |
| doctor_id | INTEGER | NOT NULL, FK → doctors | Reference to treating physician | Public |
| visit_date | TIMESTAMP | NOT NULL | Date and time of medical visit | PHI |
| diagnosis | TEXT | NOT NULL | Clinical diagnosis and findings | **HIGHLY SENSITIVE** |
| treatment | TEXT | NULL | Treatment plan and procedures performed | **HIGHLY SENSITIVE** |
| medication | TEXT | NULL | Prescribed medications and dosages | **HIGHLY SENSITIVE** |
| notes | TEXT | NULL | Additional clinical notes | **HIGHLY SENSITIVE** |
| follow_up_date | DATE | NULL | Scheduled follow-up appointment date | PHI |
| is_confidential | BOOLEAN | DEFAULT FALSE | Extra confidentiality flag for sensitive cases | Security Flag |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp | Metadata |

**Indexes:**
- `PRIMARY KEY` on record_id
- `idx_medical_records_patient` on patient_id - for patient record retrieval
- `idx_medical_records_doctor` on doctor_id - for doctor's patient list
- `idx_medical_records_date` on visit_date - for chronological queries

**Foreign Key Relationships:**
- `patient_id` → `patients.patient_id` (ON DELETE CASCADE)
- `doctor_id` → `doctors.doctor_id` (ON DELETE RESTRICT)

**Cascade Rules:**
- Patient deletion cascades to all medical records (CASCADE)
- Doctor deletion is restricted if records exist (RESTRICT)

**Security Considerations:**
- All clinical fields (diagnosis, treatment, medication, notes) are highly sensitive
- is_confidential flag indicates records requiring additional access restrictions
- This table is primary target for unauthorized data extraction attempts
- Text fields are vulnerable to SQL injection in vulnerable mode

**Access Control:**
- Admin: Full access to all records
- Doctor: Access to own patients' records and records they created
- Nurse: Limited access (basic info, no detailed diagnosis/treatment)
- Patient: Own records only, with potential restrictions on confidential records

---

## Table: admin_users

**Purpose:** User authentication and authorization system supporting role-based access control. Links system users to patient records where applicable.

| Column | Data Type | Constraints | Description | Security Classification |
|--------|-----------|-------------|-------------|------------------------|
| user_id | SERIAL | PRIMARY KEY | Unique user identifier, auto-incrementing | Public |
| username | VARCHAR(50) | NOT NULL, UNIQUE | Login username | Public |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password | **CRITICAL** |
| role | VARCHAR(20) | NOT NULL, CHECK | User role: admin, doctor, nurse, or patient | Security Critical |
| first_name | VARCHAR(50) | NULL | User's first name | Public |
| last_name | VARCHAR(50) | NULL | User's last name | Public |
| email | VARCHAR(100) | NULL | Contact email address | Public |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status | Security Flag |
| last_login | TIMESTAMP | NULL | Timestamp of most recent successful login | Audit Data |
| failed_login_attempts | INTEGER | DEFAULT 0 | Counter for failed login attempts | Security Metric |
| locked_until | TIMESTAMP | NULL | Account lockout expiration time | Security Control |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp | Metadata |
| patient_id | INTEGER | FK → patients | Optional link to patient record (for patient role users) | Sensitive Link |

**Indexes:**
- `PRIMARY KEY` on user_id
- `idx_admin_users_username` on username (UNIQUE) - for login lookups
- `idx_admin_users_role` on role - for role-based queries

**Foreign Key Relationships:**
- `patient_id` → `patients.patient_id` (optional, for patient role only)
- Referenced by: `audit_log.user_id` (logical reference, no FK constraint)

**Check Constraints:**
- `role` IN ('admin', 'doctor', 'nurse', 'patient')

**Security Considerations:**
- Password hashes use bcrypt algorithm - never store plaintext passwords
- Username is target for authentication bypass attempts in vulnerable mode
- Role field is critical for authorization - modification attempts should be logged
- failed_login_attempts and locked_until implement brute force protection
- is_active flag enables account suspension without deletion
- patient_id link allows patient users to access their own records

**Access Control:**
- Admin: Full access to all user accounts
- Doctor/Nurse/Patient: Read own profile only
- Password changes require current password verification
- Role changes restricted to admin only

**Authentication Flow:**
- Login validates username and password_hash
- Updates last_login on successful authentication
- Increments failed_login_attempts on failure
- Locks account after threshold exceeded
- Generates JWT token with user_id, username, and role

---

## Table: audit_log

**Purpose:** Comprehensive security audit trail capturing all database queries and access attempts for security research and compliance. Critical for analyzing attack patterns and security control effectiveness.

| Column | Data Type | Constraints | Description | Security Classification |
|--------|-----------|-------------|-------------|------------------------|
| log_id | SERIAL | PRIMARY KEY | Unique audit log entry identifier | Public |
| user_id | INTEGER | NOT NULL | User ID from admin_users (no FK constraint) | Audit Data |
| username | VARCHAR(50) | NULL | Username at time of action (denormalized) | Audit Data |
| action | VARCHAR(50) | NOT NULL | Type of action performed (e.g., SCHEMA_ACCESS, QUERY) | Audit Data |
| query | TEXT | NULL | Full SQL query executed (for research analysis) | **SENSITIVE** |
| result_status | VARCHAR(20) | NOT NULL, CHECK | Execution result: SUCCESS, ERROR, or BLOCKED | Audit Data |
| security_mode | VARCHAR(20) | CHECK | Testing mode: vulnerable or secure | Research Data |
| ip_address | VARCHAR(45) | NULL | Client IP address (supports IPv4 and IPv6) | Audit Data |
| user_agent | TEXT | NULL | Client browser/application user agent string | Audit Data |
| execution_time | VARCHAR(20) | NULL | Query execution duration | Performance Data |
| rows_affected | INTEGER | NULL | Number of rows returned or modified | Audit Data |
| error_message | TEXT | NULL | Error details if result_status is ERROR | Debug Data |
| timestamp | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Time of action | Audit Data |

**Indexes:**
- `PRIMARY KEY` on log_id
- `idx_audit_log_user` on user_id - for user activity queries
- `idx_audit_log_timestamp` on timestamp - for chronological analysis
- `idx_audit_log_action` on action - for action type filtering

**Check Constraints:**
- `result_status` IN ('SUCCESS', 'ERROR', 'BLOCKED')
- `security_mode` IN ('vulnerable', 'secure')

**Foreign Key Relationships:**
- None (intentionally no FK constraint to prevent cascading issues)
- Logically references `admin_users.user_id`

**Security Considerations:**
- query field stores potentially malicious SQL for research analysis
- No FK constraint prevents audit log loss if user accounts are deleted
- timestamp and ip_address enable forensic analysis
- result_status='BLOCKED' indicates security control effectiveness
- All entries are append-only - updates should never occur
- Stores both successful and failed attempts for comprehensive analysis

**Access Control:**
- Admin: Full read access
- Doctor/Nurse/Patient: No access (admin only)
- No delete permissions for any role (audit integrity)

**Research Usage:**
- Compare success rates between vulnerable and secure modes
- Analyze blocked query patterns
- Measure security control effectiveness
- Identify attack vectors and exploitation attempts
- Generate metrics for research paper:
  - Attack detection rate
  - False positive/negative rates
  - Query execution times by security mode
  - Most common attack patterns

---

## Database Relationships Summary

```
patients (1) ----< (many) medical_records (many) >---- (1) doctors
    |                                                       
    | (optional)
    |
    v (0 or 1)
admin_users (1) ----< (many) audit_log
```

**Key Relationship Rules:**
1. Each medical record belongs to exactly one patient and one doctor
2. Patients can have zero or one admin_users account (for patient portal access)
3. Doctors, nurses, and admins have admin_users accounts but no patient_id link
4. All authenticated actions generate audit_log entries
5. Deleting a patient cascades to their medical records
6. Deleting a doctor is restricted if they have associated medical records

---

## Security Testing Considerations

### Vulnerable Mode Targets
- `patients.ssn` - SQL injection to extract Social Security Numbers
- `admin_users.password_hash` - Attempts to extract credential data
- `medical_records.diagnosis` - Unauthorized access to medical data
- WHERE clause bypasses to access unauthorized records

### Secure Mode Controls
- Input validation on all user queries
- Parameterized queries to prevent SQL injection
- Role-based result filtering
- Schema information filtering by role
- Column-level access restrictions

### Audit Analysis Metrics
- Query success rate by security_mode
- Blocked attempts by user role
- Most frequently attempted attack vectors
- Average query execution time
- Rows accessed per query type

---

## Indexes Summary

All indexes are created for query performance optimization and security pattern analysis:

| Index Name | Table | Column(s) | Purpose |
|------------|-------|-----------|---------|
| idx_patients_ssn | patients | ssn | Unique constraint enforcement, login lookups |
| idx_patients_name | patients | last_name, first_name | Patient search optimization |
| idx_doctors_license | doctors | license_number | Unique constraint, credential verification |
| idx_doctors_specialization | doctors | specialization | Specialty-based queries |
| idx_medical_records_patient | medical_records | patient_id | Patient history retrieval |
| idx_medical_records_doctor | medical_records | doctor_id | Doctor's patient list |
| idx_medical_records_date | medical_records | visit_date | Chronological queries |
| idx_admin_users_username | admin_users | username | Authentication lookups |
| idx_admin_users_role | admin_users | role | Role-based queries |
| idx_audit_log_user | audit_log | user_id | User activity analysis |
| idx_audit_log_timestamp | audit_log | timestamp | Temporal analysis |
| idx_audit_log_action | audit_log | action | Action type filtering |

---

## Data Classification Summary

| Classification Level | Tables/Fields | Access Requirements |
|---------------------|---------------|---------------------|
| **CRITICAL** | admin_users.password_hash | Admin only, never displayed |
| **HIGHLY SENSITIVE** | patients.ssn, patients.insurance_id, medical_records.diagnosis, medical_records.treatment, medical_records.medication, medical_records.notes | Authorized clinicians only, audit all access |
| **SENSITIVE** | doctors.license_number, admin_users.patient_id, audit_log.query | Restricted access, role-based filtering |
| **PHI** | All patient demographic fields, medical_records.visit_date | HIPAA compliance required, audit logging |
| **PUBLIC** | doctor_id, patient_id, specialization | Standard access controls |
| **METADATA** | created_at, updated_at, timestamp | Available for audit purposes |

---

## Compliance Notes

**HIPAA Considerations:**
- All patient data is Protected Health Information (PHI)
- Audit logging satisfies HIPAA requirements for access tracking
- Role-based access control implements minimum necessary principle
- is_confidential flag enables additional protection for sensitive cases

**Research Use Only:**
This database contains synthetic data only. It is designed for:
- SQL injection vulnerability research
- Security control effectiveness testing
- Attack pattern analysis
- Role-based access control evaluation

**NOT suitable for:**
- Production healthcare systems
- Real patient data storage
- Clinical decision support
- Actual patient care

---

*Generated for MET CS 674 Database Security Research Paper*  
*Schema Version: 1.0*  
*PostgreSQL 17*