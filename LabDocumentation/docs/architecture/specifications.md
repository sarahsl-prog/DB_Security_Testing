<div align="center">
  <img src="../images/app-logo.jpg" alt="Healthcare Security Research Lab Logo" width="150"/>
</div>

# System Specifications

Complete technical specifications for all components in the Healthcare Database Security Research Lab.

---

## Host Specifications

See the detailed [Lab Specifications Table](lab-specs-table.md) for complete hardware and software specifications for all three hosts.

### Quick Reference

| Host | IP | OS | RAM | CPU | Storage | Key Software |
|------|----|----|-----|-----|---------|--------------|
| Frontend/Backend | 192.168.1.10 | Ubuntu 24.04 | 12GB | 2 vCPU | 100GB | Nginx 1.26, Flask 3.1.2, Python 3.12 |
| Database | 192.168.1.11 | Ubuntu 25.04 | 16GB | 2 vCPU | 100GB | PostgreSQL 17, Apache 2 |
| LLM | 192.168.1.12 | Ubuntu 24.04 | 32GB | Intel Core Ultra 5 | 1TB | Ollama 0.12.3, deepseek-coder:1.3b |

---

## Network Specifications

### IP Addressing

| Host | IP Address | Subnet | Gateway |
|------|-----------|--------|---------|
| Frontend/Backend | 192.168.1.10 | 255.255.255.0 | 192.168.1.1 |
| Database | 192.168.1.11 | 255.255.255.0 | 192.168.1.1 |
| LLM | 192.168.1.12 | 255.255.255.0 | 192.168.1.1 |

### Port Configuration

| Service | Port | Protocol | Access |
|---------|------|----------|--------|
| HTTP | 80 | TCP | External (Frontend only) |
| HTTPS | 443 | TCP | External (Frontend only) |
| Flask API | 5000 | TCP | Internal only |
| PostgreSQL | 5432 | TCP | Internal (from Frontend/Backend) |
| Ollama | 11434 | TCP | Internal (from Frontend/Backend) |
| SSH | 22 | TCP | Admin access |

---

## Software Versions

### Frontend/Backend Host

```yaml
Operating System: Ubuntu 24.04 LTS
Python: 3.12
Flask: 3.1.2
Nginx: 1.26
Node.js: 18.x
Vite (Vanilla JS): Latest
Key Libraries:
  - flask-cors: 4.0.0
  - PyJWT: 2.8.0
  - psycopg2-binary: 2.9.9
  - loguru: 0.7.2
  - requests: 2.31.0
```

### Database Host

```yaml
Operating System: Ubuntu 25.04
PostgreSQL: 17
Apache: 2
Extensions:
  - postgresql-contrib-17
```

### LLM Host

```yaml
Operating System: Ubuntu 24.04 LTS
Ollama: 0.12.3
Model: deepseek-coder:1.3b
Nginx: 1.26
```

---

## Virtualization

### VMware Configuration

| Parameter | Value |
|-----------|-------|
| Hypervisor | VMware Workstation 17.6.2 |
| Virtual Hardware | Version 19 |
| Network Adapter | NAT or Bridged |
| Disk Type | SCSI |
| Disk Provisioning | Thin provisioned |

### VM Resources

See [Lab Specifications Table](lab-specs-table.md) for detailed VM resource allocation.

---

## Database Specifications

### Schema Statistics

| Metric | Value |
|--------|-------|
| Total Tables | 5 |
| Total Indexes | 12 |
| Total Columns | ~60 |
| Estimated Data Size | ~100MB (with test data) |

### Table Sizes (Estimated)

| Table | Rows (Test Data) | Columns | Est. Size |
|-------|------------------|---------|-----------|
| patients | 100 | 12 | 10KB |
| doctors | 20 | 11 | 2KB |
| medical_records | 500 | 11 | 50KB |
| admin_users | 10 | 13 | 1KB |
| audit_log | 10,000+ | 13 | 5MB+ |

---

## API Specifications

### Endpoints

Total Endpoints: 10

See [API Endpoints](../api/endpoints.md) for complete documentation.

### Request/Response Format

**Content-Type:** `application/json`

**Authentication:** JWT Bearer Token

**Rate Limiting:** None (research environment)

---

## Security Specifications

### Authentication

| Feature | Specification |
|---------|--------------|
| Method | JWT (JSON Web Token) |
| Algorithm | HS256 |
| Token Lifetime | 24 hours |
| Storage | localStorage (client-side) |

### Encryption

| Component | Vulnerable Mode | Secure Mode |
|-----------|----------------|-------------|
| HTTP Transport | Unencrypted (HTTP) | Encrypted (HTTPS/TLS 1.2+) |
| Database Connection | Unencrypted | SSL/TLS |
| Password Storage | bcrypt (rounds=12) | bcrypt (rounds=12) |

---

## Performance Specifications

### Expected Response Times

| Operation | Vulnerable Mode | Secure Mode | Notes |
|-----------|----------------|-------------|-------|
| Login | ~50ms | ~50ms | No difference |
| Simple Query | ~200ms | ~220ms | +20ms for validation |
| Complex Query | ~500ms | ~550ms | +50ms for validation |
| LLM Generation | ~1-3s | ~1-3s | LLM processing dominates |

### Concurrent Users

**Supported:** 5-10 concurrent users (test environment)

**Bottleneck:** LLM host (single model instance)

---

## Storage Specifications

### Disk Space Requirements

| Component | Space Required | Notes |
|-----------|----------------|-------|
| Frontend/Backend | 20GB | Application + logs |
| Database | 30GB | Database + logs + backups |
| LLM | 10GB | Model files + logs |
| **Total** | **60GB** | Minimum recommended |

### Backup Requirements

**Estimated Backup Size:** 5-10GB (database + configs)

**Backup Frequency:** Daily (for active research)

---

## Monitoring & Logging

### Log Locations

| Host | Log Location | Size Limit |
|------|-------------|------------|
| Frontend/Backend | `/var/log/nginx/` | 100MB rotating |
| Frontend/Backend | `journalctl -u healthcare-api` | Systemd managed |
| Database | `/var/log/postgresql/` | 500MB rotating |
| LLM | `journalctl -u ollama` | Systemd managed |

### Audit Logging

**Database:** `audit_log` table

**Retention:** Unlimited (for research)

**Average Size:** ~500 bytes per entry

---

## Capacity Planning

### Database Growth

| Period | Estimated audit_log Rows | Estimated Size |
|--------|-------------------------|----------------|
| 1 day | 1,000 | 500KB |
| 1 week | 7,000 | 3.5MB |
| 1 month | 30,000 | 15MB |
| Research Period | 100,000+ | 50MB+ |

### LLM Model Storage

**Current Model:** deepseek-coder:1.3b = 1.3GB

**Alternative Models:** 
- codellama:7b = 3.8GB
- llama3:8b = 4.7GB

---

## System Requirements Summary

### Minimum Requirements

- **Total RAM:** 60GB (12 + 16 + 32)
- **Total Storage:** 1.2TB (100 + 100 + 1000)
- **Total vCPUs:** 4 (2 + 2, plus physical for LLM)
- **Network:** 1 Gbps LAN

### Recommended Requirements

- **Total RAM:** 64GB+ (allows for OS overhead)
- **Total Storage:** 1.5TB (extra space for logs and backups)
- **Network:** Isolated lab network segment
- **Hypervisor:** VMware Workstation Pro 17+

---

## Related Documentation

- [Lab Specifications Table (Detailed)](lab-specs-table.md)
- [Architecture Overview](overview.md)
- [Host Setup Guides](../hosts/frontend-backend.md)
- [Network Configuration](../hosts/network-config.md)

---

*Last Updated: [November 1, 2025]*  
*Lab Version: 1.0*
