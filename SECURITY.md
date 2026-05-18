# Security Policy

## Security Notice

**This project is designed for educational and research purposes only.** It contains intentional security vulnerabilities for demonstrating SQL injection attacks and defense mechanisms. This application must NOT be used in production environments or exposed to public networks.

## Intentional Vulnerabilities

This project deliberately includes security vulnerabilities for educational purposes. These are documented so that users understand the scope of security testing and the pedagogical value of each vulnerability.

### Vulnerable Mode Features

When `SECURITY_MODE=vulnerable`, the following vulnerabilities are present:

1. **SQL Injection Vulnerabilities**
   - Raw SQL execution without parameterization
   - Direct concatenation of user input into queries
   - No input validation or sanitization
   - Database schema exposure to LLM queries

2. **Authentication Weaknesses**
   - Weak default passwords (`password123`)
   - No rate limiting on login attempts
   - Excessive token expiration times
   - Predictable JWT secrets

3. **Authorization Bypasses**
   - No role-based access control enforcement
   - Missing row-level security
   - Full database access for all authenticated users
   - No sensitive data filtering

4. **Data Exfiltration Risks**
   - Unlimited result set sizes
   - No query complexity limits
   - Exposed audit logs to non-admins
   - Full PHO access including SSNs

### Secure Mode Features

When `SECURITY_MODE=secure`, the following protections are in place:

1. **SQL Injection Prevention**
   - Parameterized queries
   - Input validation and sanitization  
   - Query complexity analysis
   - Schema access restrictions

2. **Strong Authentication**
   - Account lockout after failed attempts
   - Reasonable token expiration
   - Password complexity enforcement
   - Secure session management

3. **Role-Based Access Control**
   - Strict role validation
   - Row-level security for patients
   - Sensitive data redaction
   - Privilege escalation prevention

4. **Audit Logging**
   - Comprehensive query logging
   - Security event tracking
   - Failed attempt monitoring
   - Anomaly detection

## Secure Development Guidelines

### When Adding New Features

1. **Educational Value First**
   - Clearly demonstrate security principles
   - Provide both vulnerable and secure implementations
   - Document the security implications

2. **Sandbox Environment**
   - Use containerized or isolated environments
   - Restrict network access
   - Use development/test databases only

3. **No Real Data**
   - Generate synthetic patient/test data
   - Never use real PII or PHI in examples
   - Clearly label all test data

### Security Testing

The project includes comprehensive security tests:

```bash
# Test vulnerable mode capabilities
python backend/attack_scenarios.py --mode vulnerable

# Test secure mode defenses
python backend/attack_scenarios.py --mode secure

# Compare security effectiveness
python backend/attack_scenarios.py --mode compare
```

### Known Limitations

1. **Research Environment**
   - Not designed for real-world deployment
   - Simplified security models
   - Focused on SQL injection primarily

2. **Educational Scope**
   - Limited to database security concepts
   - Does not cover all OWASP Top 10 issues
   - Network security not comprehensively addressed

## Reporting Security Issues

If you discover **unintentional** security vulnerabilities (not part of the educational design):

1. **Do NOT create a public issue**
2. Email the project maintainers privately
3. Include details of the vulnerability
4. Describe how to reproduce the issue
5. Suggest a fix if possible

Unintentional vulnerabilities will be addressed promptly and credited appropriately.

## Vulnerability Classification

### Intentional (Educational)
- Marked with comments explaining pedagogical purpose
- Documented in code review reports
- Have both vulnerable/secure implementations
- Represent common security mistakes

### Unintentional (Bugs)  
- Not documented as educational examples
- Appear in secure mode as well as vulnerable
- Break the intended secure-mode demonstration
- Should be reported and fixed

## Security Best Practices in Development

When contributing to this project:

1. **Maintain the Dual-Mode Design**
   - Always implement features in both vulnerable/secure modes
   - Preserve the educational contrast between modes
   - Document security differences clearly

2. **Add Security Tests**
   - Include tests for both exploitation and defense
   - Document successful attack patterns
   - Validate security controls work correctly

3. **Update Documentation**
   - Reflect security design decisions
   - Update configuration examples
   - Maintain accurate security assessments

## Configuration Security

### Docker/Container Security
- Use non-root users when possible
- Limit container privileges
- Scan images for vulnerabilities
- Keep dependencies updated

### Database Security
- Strong database passwords
- Restricted database user permissions
- Network-level access controls
- Regular backup and restoration testing

### API Security
- HTTPS in production environments
- Proper CORS configuration
- Input validation and sanitization
- Rate limiting implementation

## Compliance and Ethics

### Research Ethics
- Use only for authorized security testing
- Never test on systems without permission
- Follow responsible disclosure practices
- Educate users about security risks

### Educational Use
- Clearly label as security research
- Document all intentional vulnerabilities
- Provide learning materials and explanations
- Emphasize real-world security practices

## Security Audits

This project undergoes regular security reviews:

1. **Code Review**
   - Regular vulnerability assessments
   - Peer review of security changes
   - Static analysis of code
   - Dependency security scanning

2. **Testing**
   - Automated security test suites
   - Manual penetration testing
   - Configuration security checks
   - Deployment security validation

## Monitoring and Logging

### Security Events Logged
- All authentication attempts
- SQL injection detection
- Privilege escalation attempts
- Data access violations
- System configuration changes

### Log Security
- Protect log files from unauthorized access
- Regular log rotation and archival
- Monitor for security event patterns
- Secure log storage and transmission

## Disclaimer

This project is provided "as is" for educational purposes only. The maintainers:

- Make no warranties about security or fitness for any purpose
- Assume no liability for any damages from misuse
- Expect users to understand the risks and use responsibly
- Require users to comply with applicable laws and regulations

By using this project, you acknowledge:
- Understanding of its educational purpose
- Acceptance of security risks
- Agreement to use responsibly
- Responsibility for any unauthorized use

---

**Remember: The security vulnerabilities in this project are intentional for education. Always follow ethical guidelines when conducting security research.**