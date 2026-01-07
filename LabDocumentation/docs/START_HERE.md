<div align="center">
  <img src="images/logo-trnsp.png" alt="Healthcare Database Security Testing Lab Logo" width="150"/>
</div>

# 🏥 Healthcare Database Security Testing Platform - START HERE

**Welcome!** This guide will help you choose the best way to deploy this application based on your experience level.

---

## Choose Your Path

### 🌟 Option 1: Docker (RECOMMENDED) - **Easiest!**

**Best for:** Beginners, quick setup, consistent environment

**Time:** 10-15 minutes
**Difficulty:** ⭐ Easy

**What you need:**
- Docker Desktop installed
- 8GB RAM minimum

**Get started:**
```bash
# 1. Install Docker Desktop from docker.com
# 2. Copy environment file
cp .env.docker .env

# 3. Start everything
docker-compose up -d

# 4. Open browser to http://localhost:5173
```

📖 **[Read Docker Quick Start Guide](DOCKER_QUICKSTART.md)**

---

### 🔧 Option 2: Automated Scripts - **Recommended for Linux**

**Best for:** Linux users, those who can't use Docker, learning experience

**Time:** 20-30 minutes
**Difficulty:** ⭐⭐ Moderate

**What you need:**
- Linux or macOS
- Sudo access
- Internet connection

**Get started:**
```bash
# Run the installation wizard
cd install
./install.sh
```

📖 **[Read Installation Guide](INSTALL.md)** | **[Quick Start](QUICKSTART.md)**

---

### 🎓 Option 3: Manual Installation - **Full Control**

**Best for:** Advanced users, production deployment, custom configuration

**Time:** 45-60 minutes
**Difficulty:** ⭐⭐⭐ Advanced

**What you need:**
- System administration experience
- Understanding of web servers and databases

**Get started:**

📖 **[Read Deployment Strategy](DEPLOYMENT_STRATEGY.md)** | **[Read Installation Guide](INSTALL.md)**

---

## Quick Comparison

| Feature | Docker | Automated Scripts | Manual |
|---------|--------|-------------------|--------|
| Time to deploy | 10-15 min | 20-30 min | 45-60 min |
| Difficulty | Easy | Moderate | Advanced |
| Windows support | ✅ Yes | ❌ Limited | ⚠️ Complex |
| Mac support | ✅ Yes | ✅ Yes | ✅ Yes |
| Linux support | ✅ Yes | ✅ Yes | ✅ Yes |
| Isolation | ✅ Full | ⚠️ Partial | ❌ None |
| Easy reset | ✅ Yes | ⚠️ Moderate | ❌ Manual |
| Production ready | ✅ Yes | ✅ Yes | ✅ Yes |
| Learning curve | Low | Medium | High |

---

## System Requirements

### Minimum (All Options)
- **RAM:** 8GB
- **Disk:** 20GB free
- **CPU:** 2 cores

### Recommended
- **RAM:** 16GB
- **Disk:** 50GB free
- **CPU:** 4 cores
- **GPU:** Optional (improves LLM performance)

---

## What Gets Installed?

All deployment options install these components:

```
┌─────────────────────────────────────────┐
│         Your Computer                   │
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │ Frontend │  │ Backend  │            │
│  │  (Vite)  │  │ (Flask)  │            │
│  │  :5173   │  │  :5000   │            │
│  └──────────┘  └──────────┘            │
│       │              │                  │
│       └──────┬───────┘                  │
│              │                          │
│  ┌───────────┴──────────┐              │
│  │                      │              │
│  │   ┌──────────┐  ┌───▼──────┐       │
│  │   │PostgreSQL│  │  Ollama  │       │
│  │   │    DB    │  │   LLM    │       │
│  │   │  :5432   │  │  :11434  │       │
│  │   └──────────┘  └──────────┘       │
│  │                                     │
└──┴─────────────────────────────────────┘
```

---

## After Installation

Once installed, you'll be able to:

1. **Access the web interface:** http://localhost:5173
2. **Use test accounts:**
   - Username: `doctor1` / Password: `doctor123`
   - Username: `admin` / Password: `password123`
3. **Test SQL injection vulnerabilities** (in vulnerable mode)
4. **Switch to secure mode** and see the difference
5. **Run automated tests** to validate the installation

---

## Default Ports

Make sure these ports are available:

| Service | Port | Can Change? |
|---------|------|-------------|
| Frontend | 5173 | ✅ Yes (.env) |
| Backend | 5000 | ✅ Yes (.env) |
| PostgreSQL | 5432 | ✅ Yes (.env) |
| Ollama LLM | 11434 | ✅ Yes (.env) |
| Docs (optional) | 8080 | ✅ Yes (.env) |

---

## Component Installation Guides

If you want to install components on separate machines:

### PostgreSQL Database
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb healthcare_security
sudo -u postgres createuser healthcare_user
```

📖 **[Full PostgreSQL Guide](DEPLOYMENT_STRATEGY.md#postgresql-installation)**

### Ollama LLM Service
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull ds2-coder:latest
```

📖 **[Full Ollama Guide](DEPLOYMENT_STRATEGY.md#ollama-llm-installation)**

---

## Documentation Deployment

The `LabDocumentation/` folder contains all project documentation.

**Option 1: GitHub Pages (Free)**
1. Push repo to GitHub
2. Settings → Pages → Enable Pages
3. Source: `/LabDocumentation`

**Option 2: Simple Web Server**
```bash
cd LabDocumentation
python -m http.server 8080
```
Access at: http://localhost:8080

**Option 3: With Docker**
```bash
docker-compose --profile docs up -d docs
```
Access at: http://localhost:8080

---

## Testing Your Installation

After deployment, run these tests:

```bash
# Option 1: With Docker
docker-compose exec backend python tests/test_connectivity.py
docker-compose exec backend python tests/test_api_endpoints.py

# Option 2: Without Docker
cd backend
python tests/test_connectivity.py
python tests/test_api_endpoints.py
```

---

## Security Modes

This platform has two modes for research:

### 🔓 Vulnerable Mode (Default)
- Demonstrates SQL injection
- No input validation
- Educational purposes
- **Never use in production!**

### 🔐 Secure Mode
- SQL injection protection
- Input validation
- Role-based access control
- Production-ready

**Switch modes:**
```bash
# Edit .env file
SECURITY_MODE=secure  # or 'vulnerable'

# Restart application
docker-compose restart backend  # Docker
# OR
# Restart manually
```

---

## Common Issues

### "Port already in use"
**Solution:** Change port in `.env` file
```bash
BACKEND_PORT=5001  # Instead of 5000
```

### "Cannot connect to database"
**Solution:** Check PostgreSQL is running
```bash
# Docker
docker-compose ps postgres

# Manual
sudo systemctl status postgresql
```

### "LLM model not found"
**Solution:** Download the model
```bash
# Docker
docker-compose exec ollama ollama pull ds2-coder:latest

# Manual
ollama pull ds2-coder:latest
```

---

## Need Help?

### Documentation
- 📘 **[Docker Quick Start](DOCKER_QUICKSTART.md)** - Easiest option
- 📗 **[Installation Guide](INSTALL.md)** - Detailed installation
- 📙 **[Quick Start](QUICKSTART.md)** - Fast manual setup
- 📕 **[Deployment Strategy](DEPLOYMENT_STRATEGY.md)** - All deployment options
- 📓 **[Testing Guide](QUICK_START_TESTING.md)** - Running tests

### Troubleshooting
- Check logs: `docker-compose logs -f` (Docker) or `tail -f backend/logs/*.log`
- Test connectivity: `python backend/tests/test_connectivity.py`
- Validate configuration: `python backend/tests/test_api_endpoints.py`

### Support
- Check existing documentation in `LabDocumentation/`
- Review installation logs
- Verify `.env` configuration
- Run validation tests

---

## Recommended: Start with Docker

**For most users, we recommend starting with Docker because:**

1. ✅ Works on all operating systems
2. ✅ Simplest setup process
3. ✅ Easy to reset and try again
4. ✅ No dependency conflicts
5. ✅ Production-ready configuration

**Get started now:**
```bash
# 1. Install Docker Desktop from docker.com
# 2. Clone or download this repository
# 3. Run these commands:

cp .env.docker .env
docker-compose up -d

# 4. Open http://localhost:5173
```

📖 **[Continue with Docker Quick Start →](DOCKER_QUICKSTART.md)**

---

## Production Deployment

Before deploying to production:

- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY and JWT_SECRET_KEY
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] Set `SECURITY_MODE=secure`
- [ ] Configure CORS properly (not `*`)
- [ ] Enable HTTPS
- [ ] Review firewall rules
- [ ] Set up database backups
- [ ] Configure monitoring and logging
- [ ] Test all functionality
- [ ] Review security checklist

📖 **[Production Checklist →](DEPLOYMENT_STRATEGY.md#pre-deployment-checklist)**

---

## Next Steps

1. **Choose your deployment option** above
2. **Follow the appropriate guide**
3. **Test the installation** with provided test scripts
4. **Explore the application** and documentation
5. **Try vulnerable mode** to see SQL injection in action
6. **Switch to secure mode** to see protection working

---

**Ready? Pick your deployment option above and get started!** 🚀

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
