<div align="center">
  <img src="/images/logo-trnsp.png" alt="Healthcare Database Security Testing Lab Logo" width="150"/>
</div>

!!! warning "**DRAFT** - This documentation is a work in progress"

# Data Classification

Security classification guide for all data in the Healthcare Database Security Testing Lab.

---

## Classification Levels

| Level | Description | Examples | Access Control |
|-------|-------------|----------|----------------|
| **CRITICAL** | Data that would cause severe damage if exposed | Password hashes | Admin only, never displayed |
| **HIGHLY SENSITIVE** | PHI requiring maximum protection | SSN, diagnosis, treatment | Authorized clinicians only |
| **SENSITIVE** | Data requiring protection but not PHI | License numbers, insurance ID | Role-restricted |
| **PHI** | Protected Health Information under HIPAA | Patient demographics, visit dates | HIPAA-compliant access |
| **PUBLIC** | Non-sensitive identifiers | IDs, usernames, specializations | Standard access controls |
| **METADATA** | System-generated tracking data | Timestamps, audit logs | Available for system operations |

---

## Data Classification by Table

### PATIENTS Table

| Column | Classification | Justification |
|--------|---------------|---------------|
| patient_id | PUBLIC | Non-sensitive identifier |
| first_name | PHI | Patient identifier |
| last_name | PHI | Patient identifier |
| date_of_birth | PHI | Patient identifier |
| ssn | HIGHLY SENSITIVE | Can be used for identity theft |
| insurance_id | SENSITIVE | Financial information |
| phone_number | PHI | Contact information |
| email | PHI | Contact information |
| address | SENSITIVE | Location information, PII |
| emergency_contact | PHI | Related person information |
| created_at | METADATA | System tracking |
| updated_at | METADATA | System tracking |

### DOCTORS Table

| Column | Classification | Justification |
|--------|---------------|---------------|
| doctor_id | PUBLIC | Non-sensitive identifier |
| first_name | PUBLIC | Professional information |
| last_name | PUBLIC | Professional information |
| specialization | PUBLIC | Professional information |
| license_number | HIGHLY SENSITIVE | Professional credential, could be misused |
| phone_number | PUBLIC | Business contact |
| email | PUBLIC | Business contact |
| department | PUBLIC | Organizational information |
| hire_date | PUBLIC | Employment information |
| is_active | PUBLIC | Employment status |
| created_at | METADATA | System tracking |

### MEDICAL_RECORDS Table

| Column | Classification | Justification |
|--------|---------------|---------------|
| record_id | PUBLIC | Non-sensitive identifier |
| patient_id | PUBLIC | Reference only |
| doctor_id | PUBLIC | Reference only |
| visit_date | PHI | Part of medical record |
| diagnosis | HIGHLY SENSITIVE | Protected medical information |
| treatment | HIGHLY SENSITIVE | Protected medical information |
| medication | HIGHLY SENSITIVE | Protected medical information |
| notes | HIGHLY SENSITIVE | Protected medical information |
| follow_up_date | PHI | Medical scheduling |
| is_confidential | SENSITIVE | Security flag |
| created_at | METADATA | System tracking |

### ADMIN_USERS Table

| Column | Classification | Justification |
|--------|---------------|---------------|
| user_id | PUBLIC | Non-sensitive identifier |
| username | PUBLIC | Public identifier |
| password_hash | CRITICAL | Authentication credential |
| role | SENSITIVE | Authorization control |
| first_name | PUBLIC | User information |
| last_name | PUBLIC | User information |
| email | PUBLIC | Contact information |
| is_active | PUBLIC | Account status |
| last_login | METADATA | System tracking |
| failed_login_attempts | METADATA | Security tracking |
| locked_until | METADATA | Security tracking |
| created_at | METADATA | System tracking |
| patient_id | SENSITIVE | Links to patient data |

### AUDIT_LOG Table

| Column | Classification | Justification |
|--------|---------------|---------------|
| log_id | PUBLIC | Non-sensitive identifier |
| user_id | PUBLIC | Reference only |
| username | PUBLIC | Audit information |
| action | PUBLIC | Audit information |
| query | SENSITIVE | May contain sensitive data |
| result_status | PUBLIC | Audit information |
| security_mode | PUBLIC | System setting |
| ip_address | SENSITIVE | Network information |
| user_agent | PUBLIC | System information |
| execution_time | PUBLIC | Performance metric |
| rows_affected | PUBLIC | Query metric |
| error_message | PUBLIC | System information |
| timestamp | METADATA | System tracking |

---

## Access Control by Role

### Admin Role

- ✅ ALL TABLES - Full access
- ✅ CRITICAL data - Can view (except raw passwords)
- ✅ HIGHLY SENSITIVE - Full access
- ✅ SENSITIVE - Full access
- ✅ PHI - Full access

### Doctor Role

- ✅ PATIENTS - Full read access
- ✅ MEDICAL_RECORDS - Own patients + created records
- ✅ DOCTORS - Own record + basic info of others
- ❌ ADMIN_USERS - No access
- ❌ AUDIT_LOG - No access
- ✅ HIGHLY SENSITIVE - For own patients only
- ❌ Password hashes - Never

### Nurse Role

- ⚠️ PATIENTS - Limited fields (no SSN, no insurance_id)
- ⚠️ MEDICAL_RECORDS - Limited (no confidential records)
- ✅ DOCTORS - Basic info only
- ❌ ADMIN_USERS - No access
- ❌ AUDIT_LOG - No access
- ❌ HIGHLY SENSITIVE - Filtered out
- ❌ License numbers - No access

### Patient Role

- ⚠️ PATIENTS - Own record only
- ⚠️ MEDICAL_RECORDS - Own records only
- ⚠️ DOCTORS - Basic info only
- ❌ ADMIN_USERS - No access
- ❌ AUDIT_LOG - No access
- ⚠️ Own HIGHLY SENSITIVE data - Yes
- ❌ Other patients' data - No

---

## HIPAA Considerations

### HIPAA Identifiers in Database

All 18 HIPAA identifiers present in this database:

1. ✅ Names (first_name, last_name)
2. ✅ Geographic subdivisions (address)
3. ✅ Dates (date_of_birth, visit_date)
4. ✅ Telephone numbers (phone_number)
5. ✅ Email addresses (email)
6. ✅ Social Security Numbers (ssn)
7. ✅ Medical record numbers (patient_id, record_id)
8. ✅ Health plan beneficiary numbers (insurance_id)

### HIPAA Compliance Requirements

- **Minimum Necessary:** Role-based access ensures minimum necessary access
- **Audit Trail:** All access logged in audit_log table
- **Encryption:** HTTPS in secure mode, database SSL
- **Access Controls:** Role-based restrictions enforced
- **Data Integrity:** Foreign key constraints, data validation

---

## Data Masking Rules

### Vulnerable Mode

No masking applied - all data visible

### Secure Mode

| Field | Masking Rule | Example |
|-------|-------------|---------|
| ssn | Show last 4 digits only | 123-45-6789 → XXX-XX-6789 |
| insurance_id | Show last 4 characters | INS-001-2345 → ***-2345 |
| password_hash | Always redact | $2b$12$... → [REDACTED] |
| diagnosis (nurse) | Remove entirely | - |
| treatment (nurse) | Remove entirely | - |

---

## Encryption Requirements

### Data at Rest

| Component | Vulnerable Mode | Secure Mode |
|-----------|----------------|-------------|
| Database files | Unencrypted | Recommended: LUKS encryption |
| Backup files | Unencrypted | Should be encrypted |
| Log files | Unencrypted | Should be encrypted |

### Data in Transit

| Connection | Vulnerable Mode | Secure Mode |
|------------|----------------|-------------|
| Client → Frontend | HTTP (unencrypted) | HTTPS (TLS 1.2+) |
| Frontend → Database | PostgreSQL (no SSL) | PostgreSQL with SSL |
| Frontend → LLM | HTTP (unencrypted) | HTTP (internal network) |

---

## Data Retention Policy

### Production Recommendations

| Data Type | Retention Period | Justification |
|-----------|-----------------|---------------|
| Patient Records | 7-10 years | Legal requirement |
| Audit Logs | 7 years | HIPAA requirement |
| Authentication Logs | 90 days | Security monitoring |
| Query Logs | 30 days | Performance monitoring |

### Research Environment

| Data Type | Retention Period | Justification |
|-----------|-----------------|---------------|
| All Data | Duration of research | Research needs |
| Audit Logs | Unlimited | Research analysis |

---

## Research Considerations

!!! warning "Research Use Only"
    This classification applies to synthetic test data only. Never use this database with real patient information.

### Synthetic Data Requirements

- All SSNs are fake (generated)
- All names are synthetic
- All addresses are fictional
- All medical data is invented
- No real PHI should ever be used

---

## Related Documentation

- [Database Schema](schema.md)
- [Entity-Relationship Diagram](erd.md)
- [Security Controls](../security/overview.md)
- [HIPAA Compliance Guide](https://www.hhs.gov/hipaa)

---

*Last Updated: [Date]*  
*Lab Version: 1.0*
