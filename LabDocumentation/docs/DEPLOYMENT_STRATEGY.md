# Healthcare Security Research Platform - Deployment Strategy

**For Boston University CS 674 Database Security Fall 2025**

---

## Executive Summary

This document outlines three deployment approaches for the Healthcare Security Research Platform, ranging from easiest (Docker) to most flexible (manual installation).

**Target Users:** Students, researchers, and instructors with varying levels of technical experience.

**Architecture:**
- **Frontend + Backend:** Single host (combined deployment)
- **PostgreSQL Database:** Separate host or same host
- **Ollama LLM Service:** Separate host or same host
- **Documentation:** Static site (any host)

---

## Deployment Options

### Option 1: Docker Compose (RECOMMENDED for Beginners) ⭐

**Best for:** Users who want the simplest setup with minimal configuration.

**What it does:**
- Single command starts all services
- Automatically handles networking between containers
- No manual dependency installation
- Easy to tear down and restart

**Requirements:**
- Docker Engine + Docker Compose (any platform)
  - Docker Desktop, Colima, OrbStack, Rancher Desktop, or native Docker Engine
- 8GB RAM minimum
- 20GB disk space

**Time to deploy:** 5-10 minutes

**Pros:**
- ✅ Easiest to set up
- ✅ Consistent environment
- ✅ Easy to reset/restart
- ✅ Works on Windows, Mac, Linux

**Cons:**
- ⚠️ Requires Docker installation
- ⚠️ Limited access to logs initially
- ⚠️ May need to expose ports for external access

---

### Option 2: Automated Installation Scripts (CURRENT)

**Best for:** Users who prefer native installation or can't use Docker.

**What it does:**
- Interactive script walks through configuration
- Installs dependencies automatically
- Creates configuration files
- Validates installation

**Requirements:**
- Linux (Ubuntu/Debian recommended) or macOS
- Root/sudo access
- Internet connection

**Time to deploy:** 15-20 minutes

**Pros:**
- ✅ Native performance
- ✅ Full control over services
- ✅ Easier debugging
- ✅ No Docker overhead

**Cons:**
- ⚠️ More steps involved
- ⚠️ OS-specific differences
- ⚠️ Requires manual dependency installation
- ⚠️ Windows support limited

---

### Option 3: Manual Installation (ADVANCED)

**Best for:** Users who need full customization or are deploying to production.

**What it does:**
- Step-by-step manual installation
- Complete control over every component
- Custom configuration options
- Production-ready setup

**Requirements:**
- System administration experience
- Understanding of web servers, databases, and proxies
- Time for configuration and troubleshooting

**Time to deploy:** 30-60 minutes

**Pros:**
- ✅ Maximum flexibility
- ✅ Production-ready configuration
- ✅ Deep understanding of system
- ✅ Custom optimization

**Cons:**
- ⚠️ Complex setup
- ⚠️ Requires expertise
- ⚠️ Time-consuming
- ⚠️ More potential for errors

---

## Recommended Deployment Configurations

### Configuration A: All-in-One (Simplest)
**All services on one machine**

```
┌─────────────────────────────────────────┐
│         Single Host Machine             │
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │ Frontend │  │ Backend  │            │
│  │  (Vite)  │  │ (Flask)  │            │
│  └──────────┘  └──────────┘            │
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │PostgreSQL│  │  Ollama  │            │
│  │   DB     │  │   LLM    │            │
│  └──────────┘  └──────────┘            │
└─────────────────────────────────────────┘
```

**Best for:** Local development, testing, demos
**Requirements:** 16GB RAM, 4 CPU cores

---

### Configuration B: Split Services (Recommended for Research)
**Frontend/Backend on one machine, services on separate machines**

```
┌──────────────────────┐     ┌──────────────┐
│   Application Host   │────▶│ PostgreSQL   │
│                      │     │   Server     │
│  ┌────────────────┐  │     └──────────────┘
│  │  Frontend +    │  │
│  │  Backend       │  │     ┌──────────────┐
│  │  (Combined)    │  │────▶│   Ollama     │
│  └────────────────┘  │     │   LLM Host   │
└──────────────────────┘     └──────────────┘
```

**Best for:** Research labs, performance testing
**Requirements:**
- App Host: 8GB RAM, 2 CPU cores
- DB Host: 8GB RAM, 2 CPU cores
- LLM Host: 16GB RAM, 4 CPU cores (GPU optional but recommended)

---

### Configuration C: Full Production (Advanced)
**All services separated with load balancing**

```
┌─────────────┐
│   Nginx     │
│  Reverse    │
│   Proxy     │
└──────┬──────┘
       │
       ├─────────────┬───────────────┐
       │             │               │
┌──────▼─────┐ ┌────▼─────┐  ┌──────▼──────┐
│  Frontend  │ │ Backend  │  │  Backend    │
│   Server   │ │ Server 1 │  │  Server 2   │
└────────────┘ └──────────┘  └─────────────┘
                     │               │
                     └───────┬───────┘
                             │
                   ┌─────────▼─────────┐
                   │   PostgreSQL      │
                   │   (Replicated)    │
                   └───────────────────┘
                             │
                   ┌─────────▼─────────┐
                   │   Ollama LLM      │
                   │   Cluster         │
                   └───────────────────┘
```

**Best for:** Production deployment, high availability
**Requirements:** Multiple servers, load balancer, monitoring

---

## Component Installation Guides

### PostgreSQL Installation

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
1. Download installer from postgresql.org
2. Run installer, accept defaults
3. Set password for postgres user
4. Port 5432 will be configured automatically

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Post-installation:**
```bash
# Create database and user
sudo -u postgres psql
postgres=# CREATE DATABASE healthcare_security;
postgres=# CREATE USER healthcare_user WITH PASSWORD 'your_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE healthcare_security TO healthcare_user;
postgres=# \q
```

---

### Ollama LLM Installation

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
```

**Windows/Mac:**
1. Download from https://ollama.com/download
2. Run installer
3. Ollama starts automatically

**Pull required models:**
```bash
ollama pull llama3.1-sql:latest
# OR
ollama pull codellama:7b
# OR
ollama pull deepseek-coder
```

**Configure for network access:**
```bash
# Set environment variable
export OLLAMA_HOST=0.0.0.0:11434

# Or create systemd service override (Linux)
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo cat > /etc/systemd/system/ollama.service.d/override.conf <<EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

---

## Documentation Deployment

### Option 1: GitHub Pages (Easiest)

1. **Push to GitHub:**
   ```bash
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Go to repository Settings
   - Navigate to Pages
   - Source: Deploy from branch
   - Branch: main
   - Folder: /LabDocumentation
   - Save

3. **Access documentation:**
   - URL: `https://<username>.github.io/<repo-name>/`

### Option 2: Static File Server

**Using Python:**
```bash
cd LabDocumentation
python -m http.server 8000
```
Access at: `http://localhost:8000`

**Using nginx:**
```nginx
server {
    listen 80;
    server_name docs.yourdomain.com;
    root /path/to/LabDocumentation;
    index index.html README.md;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

### Option 3: Documentation Portal

Use MkDocs or similar:
```bash
pip install mkdocs mkdocs-material
cd LabDocumentation
mkdocs serve
```

---

## Quick Start Scripts

### deploy.sh (All-in-One Deployment)

```bash
#!/bin/bash
# Simple deployment script for all-in-one setup

# Run the installation
cd install
./install.sh

# Start PostgreSQL (if needed)
sudo systemctl start postgresql

# Start Ollama (if needed)
ollama serve &

# Start backend
cd ../backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python database.py
python app.py &

# Start frontend
cd ../frontend
npm install
npm run dev
```

---

## Pre-deployment Checklist

### All Deployments
- [ ] Servers have sufficient resources (see Configuration requirements)
- [ ] Network connectivity between all services
- [ ] Firewall rules configured appropriately
- [ ] All required ports available (5000, 5432, 11434, 5173)

### Security Checklist
- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY and JWT_SECRET_KEY
  ```bash
  # Generate secure keys
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] Configure CORS appropriately (not `*` in production)
- [ ] Enable HTTPS for production
- [ ] Review firewall rules
- [ ] Set appropriate LOG_LEVEL
- [ ] Back up `.env` files securely

### Database
- [ ] PostgreSQL installed and running
- [ ] Database created
- [ ] User created with appropriate permissions
- [ ] Network access configured (pg_hba.conf)
- [ ] Backup strategy in place

### LLM Service
- [ ] Ollama installed
- [ ] Required model downloaded
- [ ] Service accessible over network
- [ ] Sufficient resources (8GB+ RAM, GPU optional)

### Application
- [ ] Python 3.8+ installed
- [ ] Node.js 22+ installed (required >=22.12.0)
- [ ] Dependencies installed
- [ ] .env files configured
- [ ] Logs directory created

---

## Post-deployment Validation

### 1. Test Database Connectivity
```bash
cd backend
python tests/test_connectivity.py
```

### 2. Test Backend API
```bash
cd backend
python tests/test_api_endpoints.py
```

### 3. Test Frontend Setup
```bash
cd frontend
python tests/test_frontend_setup.py
```

### 4. Verify Logging
```bash
cd backend
python tests/test_logging.py
```

### 5. Manual Health Checks
```bash
# Backend health
curl http://localhost:5000/api/health

# Database connection
psql -h localhost -U healthcare_user -d healthcare_security -c "SELECT version();"

# LLM service
curl http://localhost:11434/api/tags
```

---

## Troubleshooting

### Common Issues

**"Cannot connect to database"**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check pg_hba.conf allows connections
sudo nano /etc/postgresql/*/main/pg_hba.conf
# Add: host healthcare_security healthcare_user 0.0.0.0/0 md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

**"LLM service not responding"**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Check if model is downloaded
ollama list

# Pull model if missing
ollama pull llama3.1-sql:latest
```

**"Port already in use"**
```bash
# Find what's using the port
sudo lsof -i :5000

# Kill the process or change port in .env
```

**"Frontend can't connect to backend"**
```bash
# Check CORS settings in backend/.env
CORS_ORIGINS=http://localhost:5173

# Check BACKEND_HOST in frontend/.env
VITE_BACKEND_HOST=localhost
VITE_BACKEND_PORT=5000
```

---

## Maintenance

### Regular Tasks
- Check logs weekly: `tail -f backend/logs/healthcare_security.log`
- Back up database regularly
- Update dependencies: `pip install -U -r requirements.txt`
- Review security logs: `backend/logs/security_audit.log`

### Updates
```bash
# Pull latest code
git pull origin main

# Update backend dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend dependencies
cd frontend
npm install
```

---

## Support Resources

- **Installation Guide:** `INSTALL.md`
- **Quick Start:** `QUICKSTART.md`
- **Migration Guide:** `working/CONFIGURATION_MIGRATION_GUIDE.md`
- **Testing Guide:** `QUICK_START_TESTING.md`
- **Lab Documentation:** `LabDocumentation/`
- **Test Reports:** `backend/tests/CONNECTIVITY_TEST_RESULTS.md`

---

## Next Steps

1. **Choose your deployment option** (Docker, Scripts, or Manual)
2. **Review the appropriate configuration** (A, B, or C)
3. **Follow the component installation guides**
4. **Run the deployment checklist**
5. **Validate with test scripts**
6. **Deploy documentation**

---

**Created:** 2025-12-29
**For:** Healthcare Security Research Platform
**Branch:** claude/frontend-migration-checklist-DSMzl
