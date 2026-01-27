<div align="center">
  <img src="../images/logo-trnsp.png" alt="Healthcare Database Security Testing Lab Logo" width="150"/>
</div>

!!! warning "**DRAFT** - This documentation is a work in progress"

# Port Reference

Network ports used by the Healthcare Database Security Testing Platform.

## Service Ports

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| Frontend | 5173 | HTTP/HTTPS | Vite development server |
| Backend API | 5000 | HTTP/HTTPS | Flask REST API |
| PostgreSQL | 5432 | TCP | Database server |
| Ollama LLM | 11434 | HTTP | LLM inference service |

## Docker Internal Networking

Services communicate using container names:
- Frontend → Backend: `http://backend:5000`
- Backend → Database: `postgres:5432`
- Backend → LLM: `http://ollama:11434`

## Host Access

From your host machine, use localhost:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:5000`
- PostgreSQL: `localhost:5432`
- Ollama: `http://localhost:11434`

## Firewall Rules

### Development
All ports accessible from localhost

### Production (Secure Mode)
- 5173: Accessible from allowed origins only
- 5000: Accessible from frontend only
- 5432: Accessible from backend only (no public access)
- 11434: Accessible from backend only (no public access)

## Port Conflicts

If ports are in use, check with:
```bash
# Linux/Mac
sudo lsof -i :5173
sudo lsof -i :5000
sudo lsof -i :5432
sudo lsof -i :11434

# Windows
netstat -ano | findstr :5173
netstat -ano | findstr :5000
```

## Related Documentation
- [Network Configuration](../hosts/network-config.md)
- [Docker Quickstart](../DOCKER_QUICKSTART.md)

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
