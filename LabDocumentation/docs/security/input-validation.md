<div align="center">
  <img src="../images/app-logo.jpg" alt="Healthcare Security Research Lab Logo" width="150"/>
</div>

# Input Validation

Input validation controls for query processing.

## Validation Rules

### Query Length
- Maximum: 1000 characters
- Minimum: 3 characters

### Allowed Characters (Secure Mode)
- Alphanumeric: a-z, A-Z, 0-9
- Whitespace: space, tab, newline
- Punctuation: . , ? ! ' " ( ) - _
- SQL keywords: SELECT, FROM, WHERE, etc.

### Blocked Patterns (Secure Mode)
- SQL comments: `--`, `/*`, `*/`
- Command separators: `;` (except at end)
- Union attacks: `UNION`, `UNION ALL`
- Stacked queries: Multiple statements
- Database functions: `LOAD_FILE`, `INTO OUTFILE`

## Implementation

```python
def validate_input(query, mode):
    if len(query) > 1000:
        raise ValidationError("Query too long")
    
    if mode == "secure":
        # Check for dangerous patterns
        if re.search(r'(DROP|DELETE|UPDATE|INSERT)', query, re.I):
            raise SecurityViolation("Dangerous operation detected")
```

## Bypass Techniques (Vulnerable Mode)
For research purposes, vulnerable mode allows:
- SQL injection via string concatenation
- Comment-based injection
- Union-based data extraction
- Boolean-based blind injection

## Related Documentation
- [SQL Validation](sql-validation.md)
- [Security Overview](overview.md)
