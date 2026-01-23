<div align="center">
  <img src="LabDocumentation\docs\images\logo-trnsp.png" alt="Healthcare Database Security Testing Logo" width="200"/>

</div>

# Docker Quick Start - Healthcare Database Security Testing Platform

**The easiest way to get started!** ⭐

This guide will help you deploy the entire Healthcare Database Security Testing Platform with just a few commands using Docker.

---

## What You'll Get

After following this guide, you'll have:
- ✅ Backend API running on http://localhost:5000
- ✅ Frontend web interface on http://localhost:5173
- ✅ PostgreSQL database automatically configured
- ✅ Ollama LLM service ready to use
- ✅ (Optional) Documentation site on http://localhost:8080

All with **one command!**

---

## Compose Layout

If you want to bring up all the containers at once, use this docker-compose file:

- `docker-compose-all.yml` - starts all containers - postgres, ollama, backend & frontend

```bash
docker compose -f docker-compose-all.yml -d
```

This project now includes two Compose descriptors if you want to isolate the infrastructure containers:

- `docker-compose.yml` — infrastructure services (PostgreSQL + Ollama)
- `docker-compose.app.yml` — application services (Flask backend + Vite/NGINX frontend)

Always run them together so every container shares the same Docker network:

```bash
docker compose -f docker-compose.yml -f docker-compose.app.yml up -d
```

All subsequent examples assume you are passing both files in this order.

---

## Prerequisites

### 1. Install Docker

You need Docker Engine and Docker Compose. You have several options:

**Option A: Docker Desktop (Easiest for Windows/Mac)**
1. Download from https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Verify: `docker --version && docker compose version`

**Option B: Docker Engine (Linux, or WSL2 on Windows)**
```bash
# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose plugin
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Add your user to docker group (avoids sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version && docker compose version
```

**Option C: Alternative Runtimes (Mac/Windows)**
- **Mac**: [Colima](https://github.com/abiosoft/colima), [OrbStack](https://orbstack.dev/), [Rancher Desktop](https://rancherdesktop.io/)
- **Windows**: Docker Engine in WSL2 (Ubuntu), [Rancher Desktop](https://rancherdesktop.io/)

All you need is the ability to run `docker` and `docker compose` commands.

### 2. System Requirements

- **RAM:** 8GB minimum (16GB recommended)
- **Disk Space:** 20GB free
- **CPU:** 2 cores minimum (4 recommended)
- **GPU:** Optional (NVIDIA GPU with nvidia-docker for faster LLM inference)

---

## Quick Start (3 Steps)

### Step 1: Configure Environment

```bash
# Copy the example environment file
cp .env.docker .env

# Edit .env with your preferred settings (optional)
nano .env
```

**Important settings to change:**
```bash
DB_PASSWORD=your_secure_password_here
SECRET_KEY=generate_random_key_here
JWT_SECRET_KEY=generate_random_jwt_key_here
DB_HOST=postgres          # matches the postgres service name
DB_NAME=healthcare_security
DB_USER=healthcare_user
LLM_HOST=ollama           # matches the ollama service name
BACKEND_HOST=0.0.0.0      # ensure Flask listens on all interfaces in the container
FRONTEND_BACKEND_HOST=localhost  # what the browser will use to reach the API
```

**How to generate secure keys:**
```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it into your `.env` file.

---

### Step 2: Start Everything!

```bash
# Start all services (infrastructure + app)
docker compose -f docker-compose-all.yml up -d

# Watch the logs (optional)
docker compose -f docker-compose-all.yml logs -f

# Or check specific service logs
docker compose -f docker-compose-all.yml  logs -f backend
```



---

### Step 3: Seed Sample Data

The database only contains schemas after the containers start. Run the data generator once so the default accounts exist:

```bash
docker compose -f docker-compose.yml -f docker-compose.app.yml exec backend \
   python generate_sample_data.py
```

This seeds doctors, patients, records, and admin accounts. Re-run the command anytime you want a fresh dataset.
**That's it!** 🎉

---

### Optional - Pull other LLM Models
The Ollama service will download three AI models. This happens automatically, you can download other models manually:

```bash
# Start just the Ollama service
docker compose up -d ollama

# Wait for it to start (about 30 seconds)
sleep 30

# Pull the model (this may take 5-10 minutes)
docker compose exec ollama ollama pull ds2-coder:latest

# Or use a smaller model (faster download)
docker compose exec ollama ollama pull codellama:7b
```

**Both `docker compose` (modern) and `docker-compose` (legacy) commands work. We use `docker compose` in this guide.**
---

## Access the Application

### Web Interface
Open your browser to: **http://localhost:5173**

**Default Login (after Step 4):**
- `security_admin` / `password123` (system administrator)
- `nurse.wilson` / `password123` (security administrator)
- `dr.johnson` / `password123` (doctor role)

The generator produces additional doctor and nurse accounts, all using `password123` by default.

### API
- Health Check: http://localhost:5000/api/health
- API Documentation: http://localhost:5000/api/

### Database (if needed)
```bash
docker compose exec postgres psql -U healthcare_user -d healthcare_security
```

### Documentation (optional)
```bash
# Start documentation server
docker compose --profile docs up -d docs

# Access at http://localhost:8080
```

---

## Common Commands

### Check Status
```bash
# See all running containers
docker compose ps

# Check health of services
docker compose ps --services --filter "status=running"
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
docker compose logs -f ollama

# View logs AND save to file simultaneously
docker compose logs -f 2>&1 | tee logs/runtime.log

# View specific service logs + save to file
docker compose logs -f backend 2>&1 | tee logs/backend.log
```

### Stop Everything
```bash
# Stop all services (data persists)
docker compose -f docker-compose-all.yml down

# Stop and remove ALL data (fresh start)
docker compose -f docker-compose-all.yml down -v
```

### Restart a Service
```bash
# Restart backend
docker compose -f docker-compose-all.yml restart backend

# Restart all
docker compose -f docker-compose-all.yml restart
```

### Update Code
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose -f docker-compose-all.yml up -d --build
```

---

## Troubleshooting

**Quick Diagnosis Tool** 🔍

If things aren't working, run the troubleshooting script:
```bash
./docker-debug.sh
```

This script will:
- Check if Docker is running
- Verify all containers are healthy
- Test connectivity to each service
- Show recent logs from each container
- Provide specific recommendations based on issues found

### "Port already in use"

**Problem:** Another service is using ports 5000, 5173, or 5432

**Solution:** Edit `.env` file:
```bash
BACKEND_PORT=5001
FRONTEND_PORT=5174
DB_PORT=5433
```

Then restart:
```bash
docker compose -f docker-compose-all.yml down
docker compose -f docker-compose-all.yml up -d
```

### "Cannot connect to Docker daemon"

**Problem:** Docker service is not running

**Solution:**
- **Docker Desktop**: Start the Docker Desktop application
- **Docker Engine (Linux/WSL2)**: `sudo systemctl start docker`
- **Colima (Mac)**: `colima start`
- **OrbStack (Mac)**: Start OrbStack application
- **Rancher Desktop**: Start Rancher Desktop application

### "Service unhealthy"

**Problem:** Service failed health check

**Solution:**
```bash
# Check logs for the failing service
docker compose -f docker-compose-all.yml logs <service-name>

# Common fixes:
# 1. Restart the service
docker compose -f docker-compose-all.yml restart <service-name>

# 2. Rebuild the service
docker compose -f docker-compose-all.yml up -d --build <service-name>

# 3. Check resource usage
docker stats
```

### "Ollama model not found"

**Problem:** LLM model not downloaded

**Solution:**
```bash
# Download the model
docker compose exec ollama ollama pull ds2-coder:latest

# Verify it's available
docker compose exec ollama ollama list
```

### "Database connection refused"

**Problem:** Database not ready when backend starts

**Solution:**
```bash
# Wait a bit longer and restart backend
sleep 10
docker compose restart backend
```

### "Frontend shows blank page"

**Problem:** Build issue or backend not reachable

**Solution:**
```bash
# Rebuild frontend
docker compose -f docker-compose-all.yml up -d --build frontend

# Check browser console for errors
# Verify VITE_BACKEND_HOST in .env matches your setup
```

---

## Testing the Deployment

Run the automated tests:

```bash
# Test database connectivity
docker compose exec backend python tests/test_connectivity.py

# Test API endpoints
docker compose exec backend python tests/test_api_endpoints.py

# Test logging
docker compose exec backend python tests/test_logging.py
```

---

## Production Deployment

For production use, update `.env`:

```bash
# Security
SECURITY_MODE=secure
FLASK_ENV=production
FLASK_DEBUG=False

# Secrets (generate new ones!)
SECRET_KEY=<generate-strong-random-key>
JWT_SECRET_KEY=<generate-strong-random-jwt-key>
DB_PASSWORD=<strong-database-password>

# CORS (replace with your domain)
CORS_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=WARNING
```

**Generate production secrets:**
```bash
# Generate new SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate new JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Alternative: Use OpenSSL
openssl rand -base64 32
```

Then restart:
```bash
docker compose -f docker-compose-all.yml down
docker compose -f docker-compose-all.yml up -d
```

---

## Advanced: Custom Configuration

### Using Different Models

Edit `.env`:
```bash
# Use CodeLlama instead
LLM_MODEL=codellama:7b

# Or DeepSeek Coder
LLM_MODEL=deepseek-coder
```

Download the model:
```bash
docker compose exec ollama ollama pull codellama:7b
```

### Persistent Logs

Logs are already persisted in `backend/logs/`. To view:
```bash
# On host machine
tail -f backend/logs/healthcare_security.log
tail -f backend/logs/security_audit.log
```

### Database Backups

```bash
# Create backup
docker compose exec postgres pg_dump -U healthcare_user healthcare_security > backup.sql

# Restore backup
docker compose exec -T postgres psql -U healthcare_user healthcare_security < backup.sql
```

### GPU Support (For Ollama)

**GPU is NOT required** - Ollama works fine on CPU, it's just slower for large models.

**To enable GPU acceleration (optional):**

If you have an NVIDIA GPU and want faster LLM inference:

1. **Install nvidia-docker**:
   ```bash
   # Ubuntu/Debian
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

2. **Enable GPU in docker-compose.yml**:
   - Open `docker-compose.yml`
   - Find the `ollama` service
   - Uncomment the `deploy` section (lines 48-54)

3. **Restart services**:
   ```bash
   docker compose down
   docker compose up -d
   ```

4. **Verify GPU is being used**:
   ```bash
   docker compose exec ollama nvidia-smi
   ```

**Performance comparison:**
- **CPU only**: Slower inference, works everywhere
- **With GPU**: 5-10x faster inference, requires NVIDIA GPU + nvidia-docker

---

## Cleanup

### Remove Everything (Including Data)

```bash
# Stop containers
docker compose -f docker-compose-all.yml down

# Remove volumes (THIS DELETES ALL DATA!)
docker compose -f docker-compose-all.yml down -v

# Remove images
docker compose -f docker-compose-all.yml down --rmi all

# Full cleanup (careful!)
docker system -f docker-compose-all.yml prune -a --volumes
```

---

## Understanding Docker Networking

Docker creates an isolated network for your containers. Understanding how this works is important for troubleshooting:

### Container-to-Container Communication

**Inside containers**, services communicate using **container names** (not localhost):
- Backend connects to database using `postgres:5432` (not localhost:5432)
- Backend connects to LLM using `ollama:11434` (not localhost:11434)
- These names are defined in docker-compose.yml as service names

### Host-to-Container Communication

**From your host machine**, use **localhost** or **127.0.0.1**:
- Access frontend: `http://localhost:5173`
- Access backend: `http://localhost:5000`
- Access database: `localhost:5432`

### External Machine Access

**From other machines on your network**, use the **host's IP address**:
- Frontend: `http://192.168.x.x:5173`
- Backend: `http://192.168.x.x:5000`

### Example Configuration

```yaml
# docker-compose.yml shows:
backend:
  environment:
    DB_HOST: postgres        # ← Container name (inside Docker network)
    DB_PORT: 5432
  ports:
    - "5000:5000"           # ← Maps host:5000 to container:5000
```

When backend container runs, it uses `postgres:5432` to connect to the database.
When you access the backend from your browser, you use `localhost:5000`.

---

## Network Configuration

### Access from Other Machines

By default, services are only accessible from localhost. To allow access from other machines:

1. **Edit `.env`:**
   ```bash
   BACKEND_HOST=0.0.0.0
   ```

2. **Restart services:**
   ```bash
   docker compose -f docker-compose-all.yml down
   docker compose -f docker-compose-all.yml up -d
   ```

3. **Configure firewall** to allow ports 5000, 5173

4. **Access from other machines:**
   - Frontend: http://<your-ip>:5173
   - Backend: http://<your-ip>:5000

---

## What's Running?

After `docker compose up -d`, you have:

| Service | Container Name | Port | Purpose |
|---------|---------------|------|---------|
| PostgreSQL | healthcare_db | 5432 | Database storage |
| Ollama | healthcare_llm | 11434 | AI/LLM service |
| Backend | healthcare_backend | 5000 | Flask API |
| Frontend | healthcare_frontend | 5173 | Web UI |
| Docs (optional) | healthcare_docs | 8080 | Documentation |

---

## Next Steps

1. **Change default passwords** in the database
2. **Generate sample data:**
   ```bash
   docker compose exec backend python generate_sample_data.py
   ```
3. **Explore the application** at http://localhost:5173
4. **Read the documentation** at http://localhost:8080 (if enabled)
5. **Run security tests** in vulnerable mode
6. **Switch to secure mode** and compare behavior

---

## Help & Support

- **Logs:** `docker compose logs -f [service]`
- **Exec into container:** `docker compose exec [service] bash`
- **Check health:** `docker compose ps`
- **Full documentation:** See `INSTALL.md` and `DEPLOYMENT_STRATEGY.md`

---

## Why Docker?

- ✅ **Consistent environment** - Works the same on Windows, Mac, Linux
- ✅ **No dependency conflicts** - Each service isolated
- ✅ **Easy cleanup** - Remove everything with one command
- ✅ **Quick reset** - Fresh start in seconds
- ✅ **Production-ready** - Same setup for dev and prod
- ✅ **Beginner-friendly** - No complex installation steps

---

**Enjoy your Healthcare Database Security Testing Platform!** 🏥🔐

For traditional installation (without Docker), see `INSTALL.md` or `QUICKSTART.md`.
