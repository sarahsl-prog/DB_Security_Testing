<div align="center">
  <img src="../images/logo-trnsp.png" alt="Healthcare Database Security Testing Lab Logo" width="150"/>
</div>

!!! warning "**DRAFT** - This documentation is a work in progress"

# Architecture Diagrams

This page contains all architecture diagrams for the Healthcare Database Security Testing Lab.

---

## System Architecture

The following diagram shows the complete system architecture with all three hosts and their communication paths.
```
┌─────────────────┐
│   Frontend      │  Port: 5173
│   (Vite)        │
└────────┬────────┘
         │
         │ HTTP/HTTPS
         │
┌────────▼────────┐
│   Backend API   │  Port: 5000
│   (Flask)       │  Host: BACKEND_HOST
└────┬──────┬─────┘
     │      │
     │      └──────────┐
     │                 │
┌────▼────────┐  ┌────▼────────┐
│  PostgreSQL │  │   Ollama    │
│  Database   │  │   LLM       │
│             │  │             │
│ Port: 5432  │  │ Port: 11434 │
│ DB_HOST     │  │ LLM_HOST    │
└─────────────┘  └─────────────┘
```

---

## Authentication Flow

This diagram illustrates the complete authentication and query processing flow.

```mermaid
sequenceDiagram
    participant User
    participant Host as Frontend/Backend Host<br/>Nginx + Flask
    participant Database as Database Host<br/>PostgreSQL 17
    participant LLM as LLM Host<br/>Ollama :11434
    
    Note over User,Database: Initial Authentication
    User->>Host: Enter credentials (HTTP/HTTPS)
    Host->>Host: Nginx → Flask :5000
    Host->>Database: authenticate_user(username, password)
    Database-->>Host: User record (if valid)
    Host->>Host: Generate JWT token<br/>(user_id, username, role)<br/>exp: 24 hours
    Host->>Database: update_last_login(user_id)
    Database-->>Host: Success
    Host->>Host: Flask → Nginx
    Host-->>User: JWT + user info
    User->>User: Store JWT in localStorage
    
    Note over User,LLM: Authenticated Query Request Flow
    User->>Host: Submit natural language query
    Host->>Host: Nginx → Flask :5000<br/>Authorization: Bearer JWT
    Host->>Host: @token_required decorator:<br/>Decode & verify JWT
    Host->>Database: get_user_by_id(user_id)
    Database-->>Host: User object → g.current_user
    Host->>Database: get_schema_info()
    Database-->>Host: Schema context
    Host->>LLM: generate_sql(question, schema, role)
    LLM-->>Host: Generated SQL query
    Host->>Database: execute_query(sql)
    Database-->>Host: Query results
    Host->>Database: log_audit(user_id, query, status)
    Database-->>Host: Audit logged
    Host->>Host: Flask → Nginx
    Host-->>User: JSON response
    
    Note over Host: JWT expires after 24 hours
```

[View Full Mermaid Source](../reference/auth-flow-diagram.mermaid)

---

## Secure Mode Flow

This diagram shows the security validation layers in secure mode.

```mermaid
sequenceDiagram
    participant User
    participant Host as Frontend/Backend Host<br/>Nginx + Flask
    participant Security as SecurityManager<br/>Python (F/B Host)
    participant Database as Database Host<br/>PostgreSQL 17
    participant LLM as LLM Host<br/>Ollama :11434
    
    Note over User,LLM: Secure Mode Query Processing
    User->>Host: Submit natural language query
    Host->>Host: Nginx → Flask :5000
    Host->>Host: @token_required: Verify JWT
    Host->>Database: get_user_by_id(user_id)
    Database-->>Host: User object with role
    
    Note over Host,Security: Security Layer 1: Question Validation
    Host->>Security: validate_question(question, role)
    Security->>Security: Check malicious patterns
    alt Question Blocked
        Security-->>Host: {valid: false}
        Host-->>User: 400 Error: Query blocked
    else Question Valid
        Security-->>Host: {valid: true}
    end
    
    Note over Host,Database: Get Filtered Schema
    Host->>Database: get_schema_info()
    Database-->>Host: Full schema
    Host->>Security: filter_schema_by_role(schema, role)
    Security-->>Host: Filtered schema
    
    Note over Host,LLM: LLM SQL Generation
    Host->>LLM: generate_sql(question, filtered_schema, role)
    LLM-->>Host: Generated SQL query
    
    Note over Host,Security: Security Layer 2: SQL Validation
    Host->>Security: validate_sql(sql_query, role)
    Security->>Security: Check dangerous operations
    alt SQL Blocked
        Security-->>Host: {valid: false}
        Host->>Database: log_audit(BLOCKED)
        Host-->>User: 400 Error: SQL blocked
    else SQL Valid
        Security-->>Host: {valid: true}
    end
    
    Note over Host,Database: Execute Query
    Host->>Database: execute_query(sql)
    Database-->>Host: Raw results
    
    Note over Host,Security: Security Layer 3: Result Filtering
    Host->>Security: filter_results_by_role(results, role)
    Security->>Security: Remove unauthorized columns<br/>Filter sensitive data
    Security-->>Host: Filtered results
    
    Note over Host,Database: Audit Logging
    Host->>Database: log_audit(user_id, query, SUCCESS)
    Database-->>Host: Audit logged
    
    Host->>Host: Flask → Nginx
    Host-->>User: JSON response with warnings
```

[View Full Mermaid Source](../security/secure-mode-flow.mermaid)

---

## Network Topology

```mermaid
graph TB
    subgraph Internet
        User[End User]
    end
    
    subgraph "Lab Network (192.168.1.0/24)"
        subgraph "Frontend/Backend Host (192.168.1.10)"
            Nginx[Nginx :80/:443]
            Flask[Flask :5000]
            Nginx --> Flask
        end
        
        subgraph "Database Host (192.168.1.11)"
            PostgreSQL[PostgreSQL :5432]
            Apache[Apache :80]
        end
        
        subgraph "LLM Host (192.168.1.12)"
            Ollama[Ollama :11434]
            Nginx2[Nginx :80]
        end
    end
    
    User -->|HTTP/HTTPS| Nginx
    Flask -->|SQL| PostgreSQL
    Flask -->|API| Ollama
```

---

## Database Entity-Relationship Diagram

See the [Database ERD page](../database/erd.md) for the complete healthcare database schema diagram.

---

## Related Documentation

- [System Overview](overview.md)
- [Authentication Flow](authentication.md)
- [Security Layers](security-layers.md)
- [System Specifications](specifications.md)

---

*Last Updated: [Date]*  
*Lab Version: 1.0*
