<div align="center">
  <img src="../images/app-logo.jpg" alt="Healthcare Security Research Lab Logo" width="150"/>
</div>

# Security Controls Overview

Comprehensive security architecture for the Healthcare Database Security Research Platform.

## Security Modes

The system operates in two modes for research purposes:

### Vulnerable Mode
Intentionally insecure for demonstrating vulnerabilities:
- No SQL injection protection
- Minimal input validation
- No parameterized queries
- Full data exposure
- HTTP allowed

### Secure Mode
Production-grade security controls:
- SQL injection prevention
- Strict input validation
- Parameterized queries only
- Role-based access control (RBAC)
- Data masking for sensitive fields
- HTTPS required
- Rate limiting

## Security Layers

1. **Network Security**
   - HTTPS/TLS in secure mode
   - Firewall rules
   - Network segmentation

2. **Authentication & Authorization**
   - JWT-based authentication
   - Role-based access control
   - Account lockout protection

3. **Input Validation**
   - Query length limits
   - Character whitelist/blacklist
   - SQL pattern detection

4. **SQL Validation**
   - Dangerous operation detection
   - Query complexity limits
   - Parameterized queries

5. **Result Filtering**
   - Role-based data masking
   - Sensitive field redaction
   - Row-level security

6. **Audit Logging**
   - All queries logged
   - Authentication attempts tracked
   - Security violations recorded

## Related Documentation
- [Input Validation](input-validation.md)
- [SQL Validation](sql-validation.md)
- [Result Filtering](result-filtering.md)
- [Authentication](../api/authentication.md)

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
