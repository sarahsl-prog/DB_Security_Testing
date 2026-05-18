# Quick Start - Installation System

## 1-Minute Quick Start

```bash
cd install
./install.sh
```

Follow the interactive prompts to install your desired components.

## What Gets Installed?

The installer will ask you to choose which services to install on this machine:

### Option 1: Backend/Frontend Applications
- Flask Python API server
- Vite-based web frontend
- Python virtual environment
- All dependencies (150+ Python packages, Node.js packages)
- Configuration files (.env)

### Option 2: PostgreSQL Database
- PostgreSQL 15 database server
- Database and user creation
- Schema initialization with sample data
- Network configuration for remote access

### Option 3: Ollama LLM Service
- Ollama installation
- LLM model download (llama3.1 by default)
- Systemd service configuration
- Network configuration for remote access

## Installation Scenarios

### Scenario A: Everything on One Machine (Development)

```bash
./install.sh

# Answer:
# Backend/Frontend? yes
# PostgreSQL? yes (local)
# Ollama? yes (local)
```

**Result:** Complete development environment ready to go.

### Scenario B: Distributed Production Setup

**Database Server:**
```bash
./install.sh
# PostgreSQL only (local)
```

**LLM Server:**
```bash
./install.sh
# Ollama only (local)
```

**Application Server:**
```bash
./install.sh
# Backend/Frontend only
# PostgreSQL remote (provide DB server IP)
# Ollama remote (provide LLM server IP)
```

**Result:** Production-ready distributed architecture.

### Scenario C: Use Existing Services

```bash
./install.sh

# Backend/Frontend? yes
# PostgreSQL? no (provide remote IP)
# Ollama? no (provide remote IP)
```

**Result:** Applications only, connecting to existing database and LLM services.

## After Installation

### Start Backend

```bash
cd backend
source venv/bin/activate
python app.py
```

Access at: http://localhost:5000

### Start Frontend

```bash
cd frontend
npm run dev
```

Access at: http://localhost:5173

### Test Installation

```bash
# Health check
curl http://localhost:5000/api/health

# Login test
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'
```

### Run Tests

```bash
cd backend/tests
./run_tests.sh
```

## Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | password123 | Admin |
| dr.johnson | password123 | Doctor |
| nurse.smith | password123 | Nurse |
| patient.john | password123 | Patient |

⚠️ **Change these passwords before production use!**

## Configuration Files

Created during installation:

- `backend/.env` - Backend configuration (database, LLM, secrets)
- `frontend/.env` - Frontend configuration
- `logs/install_*.log` - Installation log

## Need Help?

- **Installation Issues:** Check `logs/install_*.log`
- **Detailed Documentation:** See `install/README.md`
- **Full Overview:** See `INSTALLATION_SYSTEM_OVERVIEW.md`
- **Project Documentation:** See `LabDocumentation/`

## What the Installer Does

1. ✅ Checks system prerequisites
2. ✅ Interactively selects services to install
3. ✅ Installs PostgreSQL (if selected)
4. ✅ Installs Ollama (if selected)
5. ✅ Installs Backend/Frontend (if selected)
6. ✅ Generates secure secret keys
7. ✅ Creates configuration files
8. ✅ Validates installation (optional)
9. ✅ Generates detailed report (optional)
10. ✅ Displays next steps

## Safety Features

- Comprehensive error checking
- Detailed logging
- Backup of existing configuration files
- Validation before proceeding
- Rollback capability
- Clear error messages

## Time Estimate

- **Prerequisites check:** 1 minute
- **PostgreSQL installation:** 5-10 minutes
- **Ollama installation:** 10-20 minutes (model download)
- **Backend/Frontend installation:** 5-10 minutes
- **Validation:** 2-5 minutes

**Total:** 20-45 minutes depending on selections and download speeds

## Advanced Usage

### Run Individual Modules

```bash
# Install only PostgreSQL
./install_postgresql.sh --local

# Install only Ollama
./install_ollama.sh --local

# Install only apps
./install_backend_frontend.sh

# Validate installation
./validate_installation.sh

# Generate report
./generate_report.sh
```

### Non-Interactive Installation

For automated deployments, pre-configure:

1. Create `.pg_config`, `.ollama_config`, `.app_config` files
2. Run individual modules
3. Skip validation prompts

## Support

Questions? Issues?

1. Check installation log
2. Review `install/README.md`
3. Consult project documentation
4. Review generated installation report

---

**Ready to install?**

```bash
cd install
./install.sh
```

Let's get started! 🚀
