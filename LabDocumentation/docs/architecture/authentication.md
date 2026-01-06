<div align="center">
  <img src="../images/app-logo.jpg" alt="Healthcare Security Research Lab Logo" width="150"/>
</div>

# Authentication Flow

This page details the complete authentication and authorization flow in the Healthcare Database Security Research Lab.

---

## Overview

The system uses **JWT (JSON Web Token)** based authentication with role-based access control (RBAC). The authentication flow consists of:

1. User login with credentials
2. JWT token generation and distribution
3. Token validation on subsequent requests
4. Role-based authorization
5. Audit logging

---

## JWT Token Structure

### Token Payload

```json
{
  "user_id": 1,
  "username": "admin",
  "role": "admin",
  "exp": 1735689600
}
```

### Token Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| Algorithm | HS256 | HMAC with SHA-256 |
| Expiration | 24 hours | Token lifetime |
| Secret Key | Configured in `.env` | HMAC signing key |
| Storage | localStorage (client) | Browser storage |

---

## Authentication Endpoints

### POST /api/login

Authenticates user and returns JWT token.

**Request:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "username": "admin",
    "role": "admin",
    "user_id": 1,
    "full_name": "Admin User"
  },
  "expires_in": "24 hours"
}
```

**Response (Failure):**
```json
{
  "error": "Invalid credentials"
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid credentials
- `400` - Missing required fields
- `500` - Server error

---

### GET /api/verify

Verifies JWT token validity and returns user information.

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (Success):**
```json
{
  "success": true,
  "user": {
    "username": "admin",
    "role": "admin",
    "user_id": 1,
    "full_name": "Admin User"
  }
}
```

**Response (Failure):**
```json
{
  "success": false,
  "error": "Token expired"
}
```

---

## Authentication Flow Diagram

See the [Architecture Diagrams](diagrams.md#authentication-flow) page for the complete authentication sequence diagram.

---

## Token Validation Process

### @token_required Decorator

All protected endpoints use the `@token_required` decorator:

```python
@app.route('/api/query', methods=['POST'])
@token_required
def process_query():
    # g.current_user is now available
    user = g.current_user
    # Process request...
```

### Validation Steps

1. **Extract Token** - Get token from Authorization header
2. **Decode Token** - Decode JWT using secret key and HS256
3. **Verify Expiration** - Check if token has expired
4. **Fetch User** - Query database for user by user_id
5. **Store in Context** - Store user object in Flask's `g.current_user`

### Error Handling

| Error | HTTP Status | Description |
|-------|-------------|-------------|
| Token missing | 401 | No Authorization header provided |
| Token expired | 401 | exp claim is in the past |
| Invalid token | 401 | Token signature invalid or malformed |
| User not found | 401 | user_id doesn't exist in database |

---

## Role-Based Access Control

### Available Roles

| Role | Level | Permissions |
|------|-------|-------------|
| admin | 4 | Full database access, user management, audit logs |
| doctor | 3 | Patient records, medical data, own patients |
| nurse | 2 | Limited patient info, no SSN/insurance |
| patient | 1 | Own records only |

### Role Verification

Endpoints can require specific roles using the `@admin_required` decorator:

```python
@app.route('/api/audit', methods=['GET'])
@token_required
@admin_required
def get_audit_logs():
    # Only admin users can access
    pass
```

---

## Security Considerations

### Vulnerable Mode

In vulnerable mode, authentication is basic:

- ✅ JWT token generation
- ✅ Token expiration
- ❌ No password hashing verification (demo purposes)
- ❌ No rate limiting
- ❌ No account lockout
- ❌ Token transmitted over HTTP

### Secure Mode

In secure mode, authentication is hardened:

- ✅ JWT token generation with secure secret
- ✅ Token expiration (24 hours)
- ✅ Password hashing with bcrypt
- ✅ Failed login attempt tracking
- ✅ Account lockout after threshold
- ✅ Token transmitted over HTTPS only
- ✅ CORS restrictions
- ✅ All auth attempts logged

---

## Password Security

### Hashing Algorithm

Passwords are hashed using **bcrypt** with a work factor of 12:

```python
password_hash = bcrypt.hashpw(
    password.encode('utf-8'), 
    bcrypt.gensalt(rounds=12)
)
```

### Password Requirements

For production deployment:
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- No common passwords
- Password history (last 5 passwords)

---

## Session Management

### Token Storage (Frontend)

```javascript
// Store token after login
localStorage.setItem('token', response.token);
localStorage.setItem('user', JSON.stringify(response.user));

// Include token in requests
const token = localStorage.getItem('token');
fetch('/api/query', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

// Clear on logout
localStorage.removeItem('token');
localStorage.removeItem('user');
```

### Token Refresh

Currently, the system uses a 24-hour token lifetime without refresh. For production:

- Implement refresh tokens
- Short-lived access tokens (15 minutes)
- Long-lived refresh tokens (30 days)
- Rotate refresh tokens on use

---

## Audit Logging

All authentication attempts are logged to the `audit_log` table:

```sql
INSERT INTO audit_log (
    user_id,
    username,
    action,
    result_status,
    ip_address,
    timestamp
) VALUES (
    1,
    'admin',
    'LOGIN',
    'SUCCESS',
    '192.168.1.100',
    NOW()
);
```

### Logged Events

- Login attempts (success and failure)
- Token verification failures
- Token expiration
- Account lockouts
- Password changes
- Role changes

---

## Testing Authentication

### Test Login

```bash
# Valid credentials
curl -X POST http://192.168.1.10/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'

# Invalid credentials
curl -X POST http://192.168.1.10/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "wrong"}'
```

### Test Token Verification

```bash
# With valid token
curl http://192.168.1.10/api/verify \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Without token
curl http://192.168.1.10/api/verify
# Returns 401
```

### Test Protected Endpoint

```bash
# With authentication
curl -X POST http://192.168.1.10/api/query \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"question": "Show all patients"}'
```

---

## Related Documentation

- [Architecture Overview](overview.md)
- [API Endpoints](../api/endpoints.md)
- [Security Controls](../security/overview.md)
- [Testing Guide](../testing/methodology.md)

---

*Last Updated: [Date]*  
*Lab Version: 1.0*
