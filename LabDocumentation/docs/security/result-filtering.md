<div align="center">
  <img src="../images/logo-trnsp.png" alt="Healthcare Database Security Testing Lab Logo" width="150"/>
</div>

# Result Filtering

Role-based result filtering and data masking.

## Filtering by Role

### Admin Role
- No filtering
- All data visible
- All tables accessible

### Doctor Role
**Tables Accessible:**
- patients (full access)
- medical_records (own created records)
- doctors (own record + basic info)

**Filtered Fields:**
- password_hash (always masked)

### Nurse Role
**Tables Accessible:**
- patients (limited fields)
- medical_records (non-confidential only)
- doctors (basic info only)

**Filtered/Removed Fields:**
- ssn (masked: XXX-XX-6789)
- insurance_id (masked: ***-2345)
- diagnosis (removed)
- treatment (removed)
- medication (removed)
- password_hash (always masked)

### Patient Role
**Tables Accessible:**
- patients (own record only)
- medical_records (own records only)
- doctors (basic info only)

**Row Filtering:**
- WHERE patient_id = <user's patient_id>

## Data Masking

### SSN Masking
- Original: `123-45-6789`
- Masked: `XXX-XX-6789`

### Insurance ID Masking
- Original: `INS-001-2345`
- Masked: `***-2345`

### Password Hash Masking
- Original: `$2b$12$...`
- Masked: `[REDACTED]`

## Row-Level Security

Automatically injects WHERE clauses:

```sql
-- Patient query
SELECT * FROM medical_records

-- Becomes
SELECT * FROM medical_records WHERE patient_id = 5
```

## Column-Level Security

Removes sensitive columns from result set:

```python
def filter_results(results, role):
    if role == "nurse":
        for row in results:
            row.pop('ssn', None)
            row.pop('diagnosis', None)
    return results
```

## Related Documentation
- [Data Classification](../database/data-classification.md)
- [Security Overview](overview.md)

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
