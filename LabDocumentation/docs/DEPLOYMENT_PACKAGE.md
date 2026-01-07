<div align="center">
  <img src="images/logo-trnsp.png" alt="Healthcare Database Security Testing Lab Logo" width="150"/>
</div>

# Healthcare Database Security Testing Platform - Deployment Package

**Complete Deployment Solution for All User Types**

---

## Overview

This repository now includes a comprehensive deployment package designed for users with varying levels of technical expertise. All deployment materials have been created and tested.

---

## Package Contents

### 🚀 Quick Start Files

| File | Purpose | Audience |
|------|---------|----------|
| **START_HERE.md** | Master deployment guide | Everyone |
| **deploy.sh** | Interactive deployment script | Linux/Mac users |
| **DOCKER_QUICKSTART.md** | Docker deployment guide | Beginners |
| **QUICKSTART.md** | Traditional quick start | Intermediate |
| **DEPLOYMENT_STRATEGY.md** | Comprehensive strategy | All levels |

### 🐳 Docker Configuration

| File | Purpose |
|------|---------|
| **docker-compose.yml** | Multi-service orchestration |
| **.env.docker** | Docker environment template |
| **backend/Dockerfile** | Backend container definition |
| **frontend/Dockerfile** | Frontend container definition |
| **backend/.dockerignore** | Build optimization |
| **frontend/.dockerignore** | Build optimization |
| **frontend/nginx.conf** | Production web server config |
| **docs-nginx.conf** | Documentation server config |

### 📜 Installation Scripts

| File | Location | Purpose |
|------|----------|---------|
| **install.sh** | install/ | Main installation wizard |
| **install_backend_frontend.sh** | install/ | App deployment |
| **install_postgresql.sh** | install/ | Database setup |
| **install_ollama.sh** | install/ | LLM service setup |
| **validate_installation.sh** | install/ | Validation tests |
| **generate_report.sh** | install/ | Installation report |

### 📚 Documentation

| File | Type | Purpose |
|------|------|---------|
| **INSTALL.md** | Guide | Detailed installation |
| **QUICKSTART.md** | Guide | Fast setup |
| **README.md** | Overview | Project introduction |
| **QUICK_START_TESTING.md** | Guide | Testing procedures |
| **LabDocumentation/** | Directory | Full documentation |

### 🧪 Test Suite

| File | Location | Tests |
|------|----------|-------|
| **test_connectivity.py** | backend/tests/ | DB & LLM connectivity |
| **test_api_endpoints.py** | backend/tests/ | Backend API validation |
| **test_frontend_setup.py** | frontend/tests/ | Frontend configuration |
| **test_logging.py** | backend/tests/ | Logging system |

### 📋 Configuration

| File | Purpose |
|------|---------|
| **backend/.env** | Backend configuration |
| **backend/.env.example** | Backend template |
| **frontend/.env** | Frontend configuration |
| **frontend/.env.example** | Frontend template |
| **.env.docker** | Docker environment template |

---

## Deployment Options Summary

### Option 1: Docker (RECOMMENDED) ⭐

**For:** Beginners, quick setup, consistent environment

**Steps:**
```bash
./deploy.sh  # Choose option 1
# OR
cp .env.docker .env
docker-compose up -d
```

**Time:** 10-15 minutes
**Docs:** `DOCKER_QUICKSTART.md`

---

### Option 2: Automated Scripts

**For:** Linux users, learning experience

**Steps:**
```bash
./deploy.sh  # Choose option 2
# OR
cd install
./install.sh
```

**Time:** 20-30 minutes
**Docs:** `INSTALL.md`, `QUICKSTART.md`

---

### Option 3: Manual Installation

**For:** Advanced users, custom setups

**Steps:**
1. Install PostgreSQL
2. Install Ollama
3. Setup backend
4. Setup frontend
5. Configure services

**Time:** 45-60 minutes
**Docs:** `DEPLOYMENT_STRATEGY.md`

---

## Target Audiences

### Students (Beginners)
- **Recommended:** Docker
- **Guide:** START_HERE.md → DOCKER_QUICKSTART.md
- **Time:** 15 minutes
- **Support Level:** Full

### Researchers (Intermediate)
- **Recommended:** Automated Scripts or Docker
- **Guide:** START_HERE.md → QUICKSTART.md or DOCKER_QUICKSTART.md
- **Time:** 20-30 minutes
- **Support Level:** Moderate

### System Administrators (Advanced)
- **Recommended:** Manual Installation
- **Guide:** DEPLOYMENT_STRATEGY.md
- **Time:** 45-60 minutes
- **Support Level:** Documentation only

### Instructors (Varies)
- **Recommended:** Docker for demos, Scripts for labs
- **Guide:** All documentation available
- **Time:** Varies
- **Support Level:** Full

---

## Component Separation

### Frontend + Backend (Same Host)

Both services deploy together on one machine for simplicity.

**Docker:**
- Services in docker-compose.yml already configured together
- Access frontend at http://localhost:5173
- Access backend at http://localhost:5000

**Manual:**
- Run backend: `cd backend && python app.py`
- Run frontend: `cd frontend && npm run dev`

---

### PostgreSQL Database

Can be deployed separately or with application.

**Installation Guides:**
- Docker: Included in docker-compose.yml
- Ubuntu: `install/install_postgresql.sh`
- Manual: See `DEPLOYMENT_STRATEGY.md#postgresql-installation`

**Requirements:**
- PostgreSQL 12+
- Network accessible from application host
- User with appropriate permissions

---

### Ollama LLM Service

Can be deployed separately or with application.

**Installation Guides:**
- Docker: Included in docker-compose.yml
- Linux: `install/install_ollama.sh`
- Manual: See `DEPLOYMENT_STRATEGY.md#ollama-llm-installation`

**Requirements:**
- 8GB+ RAM (16GB recommended)
- GPU optional but recommended
- Network accessible from application host

**Model Download:**
```bash
ollama pull ds2-coder:latest
# OR
ollama pull codellama:7b
```

---

### Documentation Deployment

Multiple options for hosting documentation:

**Option 1: GitHub Pages (Free)**
- Enable Pages in repository settings
- Source: main branch / LabDocumentation folder
- Automatic updates with git push

**Option 2: Docker Container**
```bash
docker-compose --profile docs up -d docs
# Access at http://localhost:8080
```

**Option 3: Simple HTTP Server**
```bash
cd LabDocumentation
python -m http.server 8000
```

**Option 4: Static Site Generator**
```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

---

## File Organization

```
DB_Security_Testing/
│
├── START_HERE.md                 ← BEGIN HERE!
├── deploy.sh                     ← Interactive deployment
│
├── 🐳 Docker Files
│   ├── docker-compose.yml
│   ├── .env.docker
│   ├── DOCKER_QUICKSTART.md
│   ├── backend/Dockerfile
│   ├── frontend/Dockerfile
│   └── docs-nginx.conf
│
├── 📚 Documentation
│   ├── DEPLOYMENT_STRATEGY.md    ← Comprehensive guide
│   ├── INSTALL.md                ← Detailed installation
│   ├── QUICKSTART.md             ← Fast manual setup
│   ├── README.md
│   └── LabDocumentation/         ← Full docs
│
├── 📜 Installation Scripts
│   └── install/
│       ├── install.sh            ← Main installer
│       ├── install_backend_frontend.sh
│       ├── install_postgresql.sh
│       └── install_ollama.sh
│
├── 🧪 Test Suite
│   ├── backend/tests/
│   │   ├── test_connectivity.py
│   │   ├── test_api_endpoints.py
│   │   └── test_logging.py
│   └── frontend/tests/
│       └── test_frontend_setup.py
│
├── 🔧 Application
│   ├── backend/                  ← Flask API
│   │   ├── app.py
│   │   ├── database.py
│   │   ├── .env
│   │   └── requirements.txt
│   └── frontend/                 ← Vite UI
│       ├── index.html
│       ├── config.js
│       ├── .env
│       └── package.json
│
└── 📋 Configuration
    ├── .env.docker               ← Docker template
    ├── backend/.env.example
    └── frontend/.env.example
```

---

## User Journey

### Complete Beginner
1. Read START_HERE.md
2. Install Docker Desktop
3. Run `./deploy.sh` (choose option 1)
4. Open http://localhost:5173
5. Login and explore

**Time:** 15 minutes

---

### Intermediate User
1. Read START_HERE.md
2. Choose deployment option
3. Follow appropriate guide
4. Run validation tests
5. Customize configuration

**Time:** 20-30 minutes

---

### Advanced User
1. Read DEPLOYMENT_STRATEGY.md
2. Plan architecture
3. Install components separately
4. Custom configuration
5. Production hardening

**Time:** 45-60 minutes

---

## Validation

All deployments can be validated with:

```bash
# Database connectivity
cd backend
python tests/test_connectivity.py

# API endpoints
python tests/test_api_endpoints.py

# Frontend setup
cd ../frontend
python tests/test_frontend_setup.py

# Logging system
cd ../backend
python tests/test_logging.py
```

**Expected Results:** All tests should pass or show expected connection states.

---

## Support Matrix

| Component | Docker | Scripts | Manual |
|-----------|--------|---------|--------|
| Windows | ✅ Full | ⚠️ Limited | ⚠️ Complex |
| macOS | ✅ Full | ✅ Full | ✅ Full |
| Linux | ✅ Full | ✅ Full | ✅ Full |
| Beginner | ✅ Yes | ⚠️ Moderate | ❌ No |
| Intermediate | ✅ Yes | ✅ Yes | ✅ Yes |
| Advanced | ✅ Yes | ✅ Yes | ✅ Yes |

---

## Key Features

### For Beginners
- ✅ Single command deployment (Docker)
- ✅ Interactive helper script (deploy.sh)
- ✅ Clear, step-by-step guides
- ✅ Automatic validation
- ✅ Easy troubleshooting

### For All Users
- ✅ Multiple deployment options
- ✅ Comprehensive documentation
- ✅ Test suite included
- ✅ Environment-based configuration
- ✅ Production-ready setup

### For Production
- ✅ Security hardening guide
- ✅ Separate service deployment
- ✅ Monitoring and logging
- ✅ Backup procedures
- ✅ Performance optimization

---

## Quick Reference

### Start Deployment
```bash
./deploy.sh
```

### Docker Commands
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build
```

### Script Installation
```bash
cd install
./install.sh
```

### Manual Start
```bash
# Backend
cd backend
python app.py &

# Frontend
cd frontend
npm run dev &
```

---

## Next Steps

1. **Choose deployment option** from START_HERE.md
2. **Follow the guide** for your chosen method
3. **Run validation tests**
4. **Explore the application**
5. **Read security documentation**
6. **Customize for your needs**

---

## Package Completeness

### ✅ Deployment Methods
- [x] Docker Compose
- [x] Automated scripts
- [x] Manual installation
- [x] Interactive wizard

### ✅ Documentation
- [x] Quick start guide
- [x] Docker guide
- [x] Installation guide
- [x] Deployment strategy
- [x] Component guides

### ✅ Configuration
- [x] Environment templates
- [x] Docker configuration
- [x] Service definitions
- [x] Example files

### ✅ Testing
- [x] Connectivity tests
- [x] API endpoint tests
- [x] Frontend tests
- [x] Logging tests

### ✅ Support
- [x] Troubleshooting guides
- [x] Common issues documented
- [x] Multiple difficulty levels
- [x] Clear error messages

---

**This deployment package is complete and ready for use by users of all experience levels.**

---

*Last Updated: January 6, 2026*
*Documentation Version: 1.1*
*Lab Version: 1.0*
