<div align="center">
  <img src="../images/logo-trnsp.png" alt="Healthcare Database Security Testing Lab Logo" width="150"/>
</div>

# SQL Validation

SQL query validation and sanitization controls.

## Validation Layers

### 1. Syntax Validation
- Parse SQL with sqlparse library
- Verify valid SQL syntax
- Check query structure

### 2. Operation Validation (Secure Mode)
**Allowed Operations:**
- SELECT statements only

**Blocked Operations:**
- DROP (tables, databases)
- DELETE (data removal)
- UPDATE (data modification)
- INSERT (data creation)
- ALTER (schema changes)
- TRUNCATE (data clearing)
- GRANT/REVOKE (permission changes)

### 3. Pattern Detection
**Dangerous Patterns:**
- `UNION` attacks
- Stacked queries (`;`)
- Comment injection (`--`, `/*`)
- Database functions (`LOAD_FILE`, `INTO OUTFILE`)
- System commands (`xp_cmdshell`)

### 4. Complexity Limits
- Maximum table joins: 5
- Maximum subqueries: 3
- Maximum WHERE clauses: 10

## Parameterized Queries (Secure Mode)

Instead of string concatenation:
```python
# Vulnerable
query = f"SELECT * FROM patients WHERE id = {user_input}"

# Secure
query = "SELECT * FROM patients WHERE id = %s"
cursor.execute(query, (user_input,))
```

## SQL Injection Prevention

### Common Attack Vectors Blocked:
1. String termination: `'; DROP TABLE--`
2. Boolean injection: `' OR '1'='1`
3. Union injection: `' UNION SELECT * FROM admin_users--`
4. Comment injection: `admin'--`
5. Stacked queries: `; DELETE FROM patients;`

## Related Documentation
- [Input Validation](input-validation.md)
- [Result Filtering](result-filtering.md)

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
