<!--
Healthcare Database Security Testing Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing
-->
<div align="center">
  <img src="LabDocumentation\docs\images\logo-trnsp.png" alt="Healthcare Database Security Testing Logo" width="200"/>

</div>

# Healthcare Database Security Testing Platform - Quick Start Guide
## Installation (5 minutes)

### Step 1: Run Installation Script

**Windows:**
```cmd
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

### Step 2: Provide Configuration

When prompted, enter:

| Setting | Example | Description |
|---------|---------|-------------|
| Backend API Host | `192.168.1.100` | IP where Flask runs |
| Backend API Port | `5000` | Backend port |
| Database Host | `192.168.1.101` | PostgreSQL server IP |
| Database Port | `5432` | PostgreSQL port |
| Database Name | `healthcare_security` | Database name |
| Database User | `healthcare_user` | PostgreSQL username |
| Database Password | `yourpassword` | PostgreSQL password |
| LLM Service Host | `192.168.1.102` | Ollama server IP |
| LLM Service Port | `11434` | Ollama port |
| LLM Model | `ds2-coder:latest` | Model name |
| Email Domain | `hospital.com` | Email domain |
| Security Mode | `vulnerable` or `secure` | Research mode |

Press Enter to accept defaults shown in brackets `[default]`.

---

## Setup (5 minutes)

### Backend

```bash
cd backend
uv venv venv

# Activate virtual environment
source venv/bin/activate        # Linux/Mac
# OR
venv\Scripts\activate           # Windows

uv pip install -r requirements.txt
python database.py              # Initialize database
python app.py                   # Start backend
```

### Frontend (in new terminal)

```bash
cd frontend
npm install
npm run dev                     # Start frontend
```

---

## Access Application

1. **Open browser**: `http://localhost:5173`
2. **Login**:
   - Username: `admin`
   - Password: `password123`

---

## Default Test Accounts

| Username | Password | Role |
|----------|----------|------|
| admin | password123 | Administrator |
| doctor | password123 | Doctor |
| nurse | password123 | Nurse |

---

## Quick Tests

### Test Backend Health
```bash
curl http://<BACKEND_HOST>:<BACKEND_PORT>/api/health
```

### Test Database Connection
```bash
psql -h <DB_HOST> -p <DB_PORT> -U <DB_USER> -d <DB_NAME>
```

### Test LLM Service
```bash
curl http://<LLM_HOST>:<LLM_PORT>/api/version
```

---

## Common Issues

### "Python not found"
**Fix**: Install Python 3.12+ from python.org

### "Database connection failed"
**Fix**:
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql    # Linux
# OR
net start postgresql-x64-12         # Windows

# Verify credentials in backend/.env
```

### "LLM service not available"
**Fix**:
```bash
# Start Ollama
ollama serve

# Download model (if needed)
ollama pull ds2-coder:latest
```

### "Port already in use"
**Fix**: Edit `backend/.env` and change `API_PORT=5001`

---

## Security Modes

### Vulnerable Mode (Research)
- Demonstrates SQL injection vulnerabilities
- No input validation
- No role-based access control
- For security research and education

### Secure Mode (Production)
- SQL injection protection enabled
- Input validation enforced
- Role-based access control
- Comprehensive logging
- Query analysis

**Switch modes**: Edit `backend/.env` and set `SECURITY_MODE=secure`

---

## Directory Structure After Installation

```
TestLabApp/
├── install.sh              # Linux/Mac installer
├── install.bat             # Windows installer
├── INSTALL.md              # Full installation guide
├── QUICKSTART.md           # This file
│
├── backend/
│   ├── .env               # ✅ Created by installer
│   ├── logs/              # ✅ Created by installer
│   │   ├── healthcare_security.log
│   │   ├── connectivity_debug.log
│   │   └── login_audit.log
│   ├── tests/
│   │   └── test_reports/  # ✅ Created by installer
│   └── venv/              # Created during setup
│
└── frontend/
    ├── .env               # ✅ Created by installer
    └── tests/
        └── reports/       # ✅ Created by installer
```

---

## Next Steps

1. **Change default passwords** (see `INSTALL.md`)
2. **Generate sample data**: `python backend/generate_sample_data.py`
3. **Run tests**: `cd backend/tests && ./run_tests.sh`
4. **Read security documentation**
5. **Configure for production** (if deploying)

---

## Need Help?

- **Full documentation**: See `INSTALL.md`
- **Check logs**: `backend/logs/healthcare_security.log`
- **Test connectivity**: Use diagnostic commands above
- **Review configuration**: Check `backend/.env` and `frontend/.env`

---

## Reconfigure

To change configuration:
```bash
# Backup current config
cp backend/.env backend/.env.backup

# Run installer again
./install.sh        # Linux/Mac
install.bat         # Windows
```

---

## Architecture Overview

```
Browser (localhost:5173)
    ↓
Frontend (Vite Dev Server)
    ↓ HTTP API calls
Backend (Flask) @ BACKEND_HOST:5000
    ↓                     ↓
PostgreSQL             Ollama LLM
@ DB_HOST:5432        @ LLM_HOST:11434
```

---

## Important Files

- `backend/.env` - Backend configuration (**sensitive**)
- `frontend/.env` - Frontend configuration (**sensitive**)
- `backend/logs/` - Application logs
- `backend/database.py` - Database initialization
- `backend/app.py` - Flask application
- `backend/tests/run_tests.sh` - Test runner

---

## Production Checklist

Before deploying to production:

- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY and JWT_SECRET_KEY
- [ ] Set `SECURITY_MODE=secure`
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Configure CORS properly (not `*`)
- [ ] Enable HTTPS
- [ ] Review firewall rules
- [ ] Set appropriate LOG_LEVEL
- [ ] Back up `.env` files securely
- [ ] Test all functionality
- [ ] Review security settings

---

For complete installation instructions and troubleshooting, see **INSTALL.md**.
