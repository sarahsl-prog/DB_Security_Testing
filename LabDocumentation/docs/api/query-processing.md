!!! warning "**DRAFT** - This documentation is a work in progress"

# Query Processing

Natural language to SQL query processing system using LLM.

## Overview
The system converts natural language queries to SQL using Ollama LLM (qwen-coder-sql model).

## Processing Pipeline

1. **Input Validation** - Check query format and length
2. **LLM Generation** - Convert natural language to SQL
3. **SQL Validation** - Check for malicious patterns
4. **Permission Filtering** - Apply role-based restrictions
5. **Execution** - Run query against PostgreSQL
6. **Result Filtering** - Filter sensitive data by role
7. **Audit Logging** - Log all queries and results

## Role-Based Filtering

### Doctor Role
- Full access to patients table
- Access to own created medical_records
- No access to admin_users or audit_log

### Nurse Role
- Limited patient data (no SSN, insurance_id)
- No access to confidential medical records
- Read-only access

### Patient Role
- Own records only (WHERE patient_id = <user's patient_id>)
- No access to other patients

## Security Modes

### Vulnerable Mode
- Minimal SQL validation
- No parameterized queries
- Direct SQL execution
- All data visible

### Secure Mode
- Strict SQL validation
- Parameterized queries only
- Blocked dangerous operations (DROP, DELETE, UPDATE)
- Data masking for sensitive fields

## Related Documentation
- [SQL Validation](../security/sql-validation.md)
- [Result Filtering](../security/result-filtering.md)

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
