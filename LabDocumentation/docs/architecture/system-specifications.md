!!! warning "**DRAFT** - This documentation is a work in progress"

## Test Lab System Specifications

| Component | Operating System | Virtualization | Hardware | Storage | Key Software | Network Ports | Role |
|-----------|-----------------|----------------|----------|---------|--------------|---------------|------|
| **Frontend/Backend Host** | Ubuntu 24.04 LTS | Virtual Machine | 12 GB RAM<br/>2 vCPUs | 100 GB | Python 3.12<br/>Flask 3.1.2<br/>Nginx 1.26<br/>Vite (Vanilla JS) | 80 (HTTP)<br/>443 (HTTPS)<br/>5000 (Flask) | Web interface and API server:<br/>- User authentication<br/>- Query processing<br/>- Security controls<br/>- Session management |
| **Database Host** | Ubuntu 25.04 | Virtual Machine | 16 GB RAM<br/>2 vCPUs | 100 GB | PostgreSQL 17<br/>Apache 2 | 5432 (PostgreSQL)<br/>80 (Apache) | Data persistence:<br/>- Healthcare records<br/>- User credentials<br/>- Audit logs<br/>- Schema storage |
| **LLM Host** | Ubuntu 24.04 LTS | Physical Machine | 32 GB RAM<br/>Intel Core Ultra 5 | 1 TB | Ollama 0.12.3<br/>qwen2.5-coder<br/>Nginx 1.26 | 11434 (Ollama) | Natural language processing:<br/>- SQL generation<br/>- Query interpretation<br/>- LLM inference |

### Network Configuration

**Internal Network Topology:**
```
[Frontend/Backend Host] :80 :5000
         ↓
    [Database Host] :5432
         ↓
    [LLM Host] :11434
```

**External Access:**
- User access via HTTP/HTTPS (ports 80/443) to Frontend/Backend Host
- All other communication occurs on internal network
- No direct external access to Database or LLM hosts

### Software Versions

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.12 | Backend application runtime |
| Flask | 3.1.2 | REST API framework |
| PostgreSQL | 17 | Relational database |
| Nginx | 1.26 | Web server and reverse proxy |
| Ollama | 0.12.3 | LLM inference engine |
| qwen2.5-coder | 1.3b | Natural language to SQL generation |
| JWT | PyJWT library | Authentication tokens |
| Apache | 2 | Database host web services |

### Virtual Machine Specifications

Virtual machines (Frontend/Backend and Database hosts) are running on **VMware Workstation 17.6.2**. The LLM host is a physical machine for optimal inference performance.

**Resource Allocation Rationale:**
- Frontend/Backend: Moderate resources for API processing and web serving
- Database: Higher memory for query caching and concurrent connections
- LLM: Physical host with highest resources for model inference (32GB RAM, 1TB for model storage)

### Network Security

- All inter-host communication uses internal network
- JWT tokens for API authentication (HS256 algorithm)
- 24-hour token expiration
- Role-based access control (Admin, Doctor, Nurse, Patient)
- Audit logging of all queries

---

**Note:** This is a research test environment. All systems are isolated from production networks and contain only synthetic test data.

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
