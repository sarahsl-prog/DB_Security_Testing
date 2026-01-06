<div align="center">
  <img src="../images/app-logo.jpg" alt="Healthcare Security Research Lab Logo" width="150"/>
</div>

# Error Handling

API error codes and response formats.

## Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

## HTTP Status Codes

- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `423` - Locked (account locked)
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error
- `503` - Service Unavailable

## Common Error Codes

### Authentication Errors
- `INVALID_CREDENTIALS` - Username or password incorrect
- `ACCOUNT_LOCKED` - Too many failed login attempts
- `TOKEN_EXPIRED` - JWT token has expired
- `TOKEN_INVALID` - JWT token is malformed

### Query Errors
- `INVALID_QUERY` - Query format is invalid
- `SQL_INJECTION_DETECTED` - Malicious SQL pattern detected
- `PERMISSION_DENIED` - User lacks permission for operation
- `QUERY_TIMEOUT` - Query execution exceeded time limit

### System Errors
- `DATABASE_ERROR` - Database connection or query error
- `LLM_ERROR` - LLM service unavailable or error
- `INTERNAL_ERROR` - Unexpected server error

## Related Documentation
- [API Endpoints](endpoints.md)
- [Security Controls](../security/overview.md)

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
