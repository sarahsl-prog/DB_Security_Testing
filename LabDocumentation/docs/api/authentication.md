<div align="center">
  <img src="../images/app-logo.jpg" alt="Healthcare Security Research Lab Logo" width="150"/>
</div>

# API Authentication

Authentication and authorization system for the Healthcare Database Security Research API.

## Overview
The API uses JWT (JSON Web Tokens) for authentication with role-based access control (RBAC).

## Authentication Flow

1. User sends credentials to `/api/login`
2. Server validates credentials against `admin_users` table
3. Server generates JWT token with user info and role
4. Client includes token in `Authorization` header for subsequent requests

## JWT Token Structure

```json
{
  "user_id": 1,
  "username": "dr.johnson",
  "role": "doctor",
  "patient_id": null,
  "exp": 1672531200
}
```

## Roles

- **admin** - Full system access
- **doctor** - Access to patient records and medical data
- **nurse** - Limited patient data access (no SSN, diagnosis)
- **patient** - Access to own records only

## Token Usage

Include token in Authorization header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Security Features

- Password hashing with bcrypt
- Account lockout after 5 failed attempts
- Token expiration (24 hours)
- Secure mode enforces HTTPS only

## Related Documentation
- [API Endpoints](endpoints.md)
- [Security Overview](../security/overview.md)

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
