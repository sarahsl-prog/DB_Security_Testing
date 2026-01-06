<div align="center">
  <img src="../images/app-logo.jpg" alt="Healthcare Security Research Lab Logo" width="150"/>
</div>

# Common Issues

Troubleshooting guide for common problems with the Healthcare Database Security Research Platform.

## Docker Issues

### Container Won't Start

**Symptoms:** Container exits immediately or fails to start

**Solutions:**
1. Check logs:
   ```bash
   docker compose logs backend
   docker compose logs postgres
   ```

2. Verify configuration:
   ```bash
   docker compose config
   ```

3. Check port conflicts:
   ```bash
   sudo lsof -i :5173
   sudo lsof -i :5000
   sudo lsof -i :5432
   ```

4. Rebuild containers:
   ```bash
   docker compose down
   docker compose up -d --build
   ```

### Database Connection Errors

**Symptoms:** `could not connect to server`, `connection refused`

**Solutions:**
1. Check if PostgreSQL is running:
   ```bash
   docker compose ps postgres
   ```

2. Verify database credentials in `.env`
   ```bash
   cat .env | grep DB_
   ```

3. Wait for database to be ready (health check):
   ```bash
   docker compose logs postgres | grep "ready to accept connections"
   ```

4. Test connection:
   ```bash
   docker compose exec backend psql -h postgres -U healthcare_admin -d healthcare_security -c "SELECT 1"
   ```

### LLM Service Not Responding

**Symptoms:** `Failed to connect to LLM service`, timeout errors

**Solutions:**
1. Check Ollama status:
   ```bash
   docker compose logs ollama
   curl http://localhost:11434/api/version
   ```

2. Verify model is pulled:
   ```bash
   docker compose exec ollama ollama list
   ```

3. Pull model if missing:
   ```bash
   docker compose exec ollama ollama pull llama3.1-sql:latest
   ```

4. Check memory/CPU usage (Ollama is resource-intensive):
   ```bash
   docker stats
   ```

## Frontend Issues

### Frontend Not Loading

**Symptoms:** Blank page, connection refused

**Solutions:**
1. Check if Vite server is running:
   ```bash
   docker compose logs frontend
   ```

2. Verify port 5173 is accessible:
   ```bash
   curl http://localhost:5173
   ```

3. Check browser console for errors (F12)

4. Clear browser cache and reload

### API Connection Errors

**Symptoms:** `Failed to fetch`, CORS errors

**Solutions:**
1. Verify backend is running:
   ```bash
   curl http://localhost:5000/api/health
   ```

2. Check CORS configuration in `.env`:
   ```bash
   cat .env | grep CORS
   ```

3. Verify `config.js` has correct backend URL:
   ```bash
   cat frontend/public/config.js | grep BACKEND_HOST
   ```

## Backend Issues

### Authentication Failures

**Symptoms:** Login fails with valid credentials

**Solutions:**
1. Check database connection:
   ```bash
   docker compose logs backend | grep "database"
   ```

2. Verify user exists in database:
   ```bash
   docker compose exec postgres psql -U healthcare_admin -d healthcare_security -c "SELECT username, role FROM admin_users"
   ```

3. Check for account lockout:
   ```bash
   docker compose exec postgres psql -U healthcare_admin -d healthcare_security -c "SELECT username, locked_until, failed_login_attempts FROM admin_users WHERE username='dr.johnson'"
   ```

### Query Execution Errors

**Symptoms:** Queries fail, security violations

**Solutions:**
1. Check security mode:
   ```bash
   cat .env | grep SECURITY_MODE
   ```

2. Review audit logs:
   ```bash
   docker compose exec postgres psql -U healthcare_admin -d healthcare_security -c "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 10"
   ```

3. Verify LLM is generating valid SQL:
   ```bash
   docker compose logs backend | grep "Generated SQL"
   ```

## Permission Issues

### Docker Permission Denied

**Symptoms:** `permission denied while trying to connect to Docker daemon`

**Solutions:**
1. Add user to docker group:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. Restart Docker daemon:
   ```bash
   sudo systemctl restart docker
   ```

### File Permission Errors

**Symptoms:** Cannot write logs, cannot create files

**Solutions:**
1. Check file ownership:
   ```bash
   ls -la logs/
   ```

2. Fix permissions:
   ```bash
   sudo chown -R $USER:$USER logs/
   chmod -R 755 logs/
   ```

## Performance Issues

### Slow Query Execution

**Solutions:**
1. Check database indexes
2. Review query complexity
3. Monitor resource usage:
   ```bash
   docker stats
   ```

### High Memory Usage (Ollama)

**Solutions:**
1. Use smaller LLM model
2. Increase Docker memory limit
3. Run Ollama on dedicated machine

## Network Issues

### Container Name Resolution Fails

**Symptoms:** `could not resolve host: postgres`

**Solutions:**
1. Verify all containers are on same network:
   ```bash
   docker network inspect healthcare-network
   ```

2. Restart containers:
   ```bash
   docker compose down
   docker compose up -d
   ```

## Getting Help

1. Check logs: `./docker-debug.sh`
2. Review documentation: `docs/`
3. Check GitHub issues
4. Contact: SarahSL@bu.edu

## Related Documentation
- [Docker Quickstart](../DOCKER_QUICKSTART.md)
- [Frontend-Backend Troubleshooting](frontend-backend.md)
- [Database Troubleshooting](database.md)
- [Network Troubleshooting](network.md)

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
