<div align="center">
  <img src="/images/logo-trnsp.png" alt="Healthcare Database Security Testing Lab Logo" width="150"/>
</div>

!!! warning "**DRAFT** - This documentation is a work in progress"

# Command Reference

Common commands for managing the Healthcare Database Security Testing Platform.

## Docker Commands

### Start Services
```bash
# Using deploy script
./deploy.sh

# Manual start
docker compose up -d

# View logs while starting
docker compose up
```

### Stop Services
```bash
docker compose down

# Stop and remove volumes
docker compose down -v
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f postgres
docker compose logs -f ollama

# Save logs to file
docker compose logs -f 2>&1 | tee logs/runtime.log
```

### Check Status
```bash
docker compose ps

# Detailed status
docker compose ps --services --filter "status=running"
```

### Restart Services
```bash
# All services
docker compose restart

# Specific service
docker compose restart backend
```

### Rebuild
```bash
# Rebuild and restart
docker compose up -d --build

# Rebuild specific service
docker compose build backend
docker compose up -d backend
```

## Database Commands

### Connect to PostgreSQL
```bash
# From host
psql -h localhost -p 5432 -U healthcare_admin -d healthcare_security

# From Docker
docker compose exec postgres psql -U healthcare_admin -d healthcare_security
```

### Run SQL File
```bash
psql -h localhost -U healthcare_admin -d healthcare_security -f script.sql
```

### Database Backup
```bash
pg_dump -h localhost -U healthcare_admin healthcare_security > backup.sql
```

### Database Restore
```bash
psql -h localhost -U healthcare_admin -d healthcare_security < backup.sql
```

## Ollama Commands

### Pull LLM Model
```bash
# From host (if Ollama installed)
ollama pull qwen-coder-sql:latest

# From Docker
docker compose exec ollama ollama pull qwen-coder-sql:latest
```

### List Models
```bash
docker compose exec ollama ollama list
```

### Test LLM
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen-coder-sql:latest",
  "prompt": "Convert to SQL: show all patients"
}'
```

## Frontend Commands

### Development Server
```bash
cd frontend
npm run dev
```

### Build for Production
```bash
cd frontend
npm run build
```

### Run Tests
```bash
cd frontend
npm test
```

## Backend Commands

### Run Development Server
```bash
cd backend
python app.py
```

### Run with Gunicorn
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Run Tests
```bash
cd backend
pytest
```

## Troubleshooting Commands

### Debug Container
```bash
# Execute shell in container
docker compose exec backend /bin/bash
docker compose exec postgres /bin/bash

# Check container logs
docker compose logs --tail=100 backend

# Inspect container
docker inspect healthcare_backend
```

### Check Connectivity
```bash
# Test backend API
curl http://localhost:5000/api/health

# Test database from backend
docker compose exec backend psql -h postgres -U healthcare_admin -d healthcare_security -c "SELECT 1"

# Test LLM
curl http://localhost:11434/api/version
```

## Related Documentation
- [Docker Quickstart](../DOCKER_QUICKSTART.md)
- [Troubleshooting](../troubleshooting/common-issues.md)

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
