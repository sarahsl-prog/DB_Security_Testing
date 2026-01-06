<div align="center">
  <img src="../images/app-logo.jpg" alt="Healthcare Security Research Lab Logo" width="150"/>
</div>

# API Endpoints

Complete reference for all REST API endpoints in the Healthcare Database Security Research API.

## Base URL
- Development: `http://localhost:5000`
- Docker: `http://localhost:5000`

## Health Endpoints

### GET /api/health
Health check endpoint.

**Response:**
```json
{"status": "healthy", "timestamp": "2025-01-01T12:00:00Z"}
```

### GET /api/status
Detailed system status including database and LLM connectivity.

## Authentication Endpoints

### POST /api/login
Authenticate user and receive JWT token.

**Request:**
```json
{"username": "dr.johnson", "password": "password123"}
```

### POST /api/logout
Invalidate current session.

## Query Endpoints

### POST /api/query
Execute natural language query against the database.

**Headers:** `Authorization: Bearer <token>`

### GET /api/schema
Retrieve database schema information (filtered by role).

## Audit Endpoints

### GET /api/audit
Retrieve audit log entries (admin only).

## Related Documentation
- [Authentication](authentication.md)
- [Query Processing](query-processing.md)
- [Error Handling](errors.md)

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
