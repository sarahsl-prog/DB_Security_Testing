#!/bin/bash
###############################################################################
# Healthcare Security Research Platform - Installation Report Generator
#
# This module generates a comprehensive installation report in markdown format
# with all relevant configuration information and next steps.
#
# Usage: ./generate_report.sh
###############################################################################

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common_utils.sh"

# Import configurations
[ -f "$SCRIPT_DIR/.pg_config" ] && source "$SCRIPT_DIR/.pg_config"
[ -f "$SCRIPT_DIR/.ollama_config" ] && source "$SCRIPT_DIR/.ollama_config"
[ -f "$SCRIPT_DIR/.app_config" ] && source "$SCRIPT_DIR/.app_config"

# Report file
REPORT_FILE="$PROJECT_ROOT/INSTALLATION_REPORT_$(date +%Y%m%d_%H%M%S).md"

###############################################################################
# Report Generation Functions
###############################################################################

generate_report_header() {
    cat >> "$REPORT_FILE" << 'EOF'
# Healthcare Security Research Platform
## Installation Report

---

EOF

    echo "**Installation Date:** $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
    echo "**System:** $(uname -a)" >> "$REPORT_FILE"
    echo "**User:** $(whoami)" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
}

generate_configuration_summary() {
    cat >> "$REPORT_FILE" << 'EOF'
## Configuration Summary

### Network Configuration

EOF

    cat >> "$REPORT_FILE" << EOF
| Component | Host | Port |
|-----------|------|------|
| Backend API | ${BACKEND_PUBLIC_HOST:-localhost} | ${API_PORT:-5000} |
| PostgreSQL Database | ${PG_HOST:-localhost} | ${PG_PORT:-5432} |
| Ollama LLM Service | ${OLLAMA_HOST:-localhost} | ${OLLAMA_PORT:-11434} |

### Database Configuration

| Setting | Value |
|---------|-------|
| Database Name | ${PG_DATABASE:-healthcare_security} |
| Database User | ${PG_USER:-healthcare_user} |
| Database Password | ***** (stored in .env) |

### Application Configuration

| Setting | Value |
|---------|-------|
| Security Mode | ${SECURITY_MODE:-vulnerable} |
| Email Domain | ${EMAIL_DOMAIN:-hospital.com} |
| LLM Model | ${OLLAMA_MODEL:-llama3.1} |

EOF
}

generate_directory_structure() {
    cat >> "$REPORT_FILE" << 'EOF'
## Directory Structure

```
Database_Security_TestApp/
├── backend/                   # Flask Python API server
│   ├── .env                   # Backend configuration (SENSITIVE)
│   ├── app.py                 # Main application entry point
│   ├── venv/                  # Python virtual environment
│   ├── logs/                  # Application and audit logs
│   └── tests/                 # Test suite
├── frontend/                  # Vite web interface
│   ├── .env                   # Frontend configuration
│   ├── node_modules/          # Node.js dependencies
│   └── tests/                 # Frontend tests
├── install/                   # Installation scripts (NEW)
│   ├── install.sh             # Main installation script
│   ├── common_utils.sh        # Shared utilities
│   ├── install_postgresql.sh  # PostgreSQL installer
│   ├── install_ollama.sh      # Ollama installer
│   ├── install_backend_frontend.sh  # App installer
│   ├── validate_installation.sh     # Validation tests
│   └── generate_report.sh     # This script
└── logs/                      # Installation logs
```

EOF
}

generate_installed_components() {
    cat >> "$REPORT_FILE" << 'EOF'
## Installed Components

### Backend (Python/Flask)

EOF

    if [ -d "$PROJECT_ROOT/backend/venv" ]; then
        echo "- ✅ Virtual environment created" >> "$REPORT_FILE"

        if [ -f "$PROJECT_ROOT/backend/venv/bin/python" ]; then
            local python_version=$("$PROJECT_ROOT/backend/venv/bin/python" --version 2>&1)
            echo "- Python version: $python_version" >> "$REPORT_FILE"
        fi
    else
        echo "- ❌ Virtual environment not found" >> "$REPORT_FILE"
    fi

    if [ -f "$PROJECT_ROOT/backend/.env" ]; then
        echo "- ✅ Configuration file (.env) created" >> "$REPORT_FILE"
    else
        echo "- ❌ Configuration file (.env) not found" >> "$REPORT_FILE"
    fi

    cat >> "$REPORT_FILE" << 'EOF'

### Frontend (Node.js/Vite)

EOF

    if [ -d "$PROJECT_ROOT/frontend/node_modules" ]; then
        echo "- ✅ Node.js dependencies installed" >> "$REPORT_FILE"

        if command_exists node; then
            local node_version=$(node --version)
            echo "- Node.js version: $node_version" >> "$REPORT_FILE"
        fi
    else
        echo "- ❌ Node.js dependencies not installed" >> "$REPORT_FILE"
    fi

    if [ -f "$PROJECT_ROOT/frontend/.env" ]; then
        echo "- ✅ Configuration file (.env) created" >> "$REPORT_FILE"
    else
        echo "- ❌ Configuration file (.env) not found" >> "$REPORT_FILE"
    fi

    cat >> "$REPORT_FILE" << 'EOF'

### PostgreSQL Database

EOF

    if command_exists psql; then
        local pg_version=$(psql --version)
        echo "- ✅ PostgreSQL client: $pg_version" >> "$REPORT_FILE"
    else
        echo "- ❌ PostgreSQL client not found" >> "$REPORT_FILE"
    fi

    cat >> "$REPORT_FILE" << 'EOF'

### Ollama LLM Service

EOF

    if command_exists ollama; then
        local ollama_version=$(ollama --version 2>/dev/null)
        echo "- ✅ Ollama: $ollama_version" >> "$REPORT_FILE"
    else
        echo "- ❌ Ollama not found" >> "$REPORT_FILE"
    fi
}

generate_next_steps() {
    cat >> "$REPORT_FILE" << EOF
## Next Steps

### 1. Start the Backend Server

\`\`\`bash
cd backend
source venv/bin/activate
python app.py
\`\`\`

The backend will be available at: **http://${BACKEND_PUBLIC_HOST:-localhost}:${API_PORT:-5000}**

### 2. Start the Frontend Development Server

\`\`\`bash
cd frontend
npm run dev
\`\`\`

The frontend will typically be available at: **http://localhost:5173**

### 3. Test the Installation

#### Test Backend Health

\`\`\`bash
curl http://${BACKEND_PUBLIC_HOST:-localhost}:${API_PORT:-5000}/api/health
\`\`\`

Expected response:
\`\`\`json
{
  "status": "healthy",
  "timestamp": "...",
  "services": {
    "database": "connected",
    "llm": "available"
  }
}
\`\`\`

#### Test Login

\`\`\`bash
curl -X POST http://${BACKEND_PUBLIC_HOST:-localhost}:${API_PORT:-5000}/api/login \\
  -H "Content-Type: application/json" \\
  -d '{"username":"admin","password":"password123"}'
\`\`\`

### 4. Run Test Suite

\`\`\`bash
cd backend/tests
./run_tests.sh
\`\`\`

Or run specific tests:

\`\`\`bash
cd backend
source venv/bin/activate
pytest tests/test_database.py -v
pytest tests/test_llm_client.py -v
pytest tests/test_healthcare_security.py -v
\`\`\`

## Default User Accounts

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| admin | password123 | Admin | Full system access |
| dr.johnson | password123 | Doctor | Doctor access |
| nurse.smith | password123 | Nurse | Nurse access |
| patient.john | password123 | Patient | Patient access |

**⚠️ IMPORTANT:** Change these passwords before deploying to production!

## Security Considerations

### Current Security Mode: **${SECURITY_MODE:-vulnerable}**

EOF

    if [ "$SECURITY_MODE" = "vulnerable" ]; then
        cat >> "$REPORT_FILE" << 'EOF'
**WARNING:** The system is currently in VULNERABLE mode for research purposes.

This mode:
- ❌ Minimal input validation
- ❌ Direct SQL execution
- ❌ Limited security controls
- ✅ Useful for security research and testing

**To switch to secure mode:**

1. Edit `backend/.env`
2. Change `SECURITY_MODE=vulnerable` to `SECURITY_MODE=secure`
3. Restart the backend server

EOF
    else
        cat >> "$REPORT_FILE" << 'EOF'
**GOOD:** The system is in SECURE mode.

This mode:
- ✅ Input sanitization and validation
- ✅ SQL injection prevention
- ✅ Role-based access controls
- ✅ Comprehensive audit logging
- ✅ Result filtering and redaction

EOF
    fi

    cat >> "$REPORT_FILE" << 'EOF'
### Production Deployment Checklist

Before deploying to production:

- [ ] Change all default passwords (database, user accounts)
- [ ] Regenerate SECRET_KEY and JWT_SECRET_KEY
- [ ] Set `SECURITY_MODE=secure`
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Configure CORS to specific origins (not wildcard)
- [ ] Enable HTTPS/SSL
- [ ] Review and restrict firewall rules
- [ ] Set appropriate log levels (WARNING or ERROR)
- [ ] Secure .env files (chmod 600)
- [ ] Back up database and configuration
- [ ] Review all security settings

## Configuration Files

### Backend .env Location

```
backend/.env
```

**⚠️ SENSITIVE FILE** - Contains database passwords and secret keys

### Frontend .env Location

```
frontend/.env
```

## Log Files

### Installation Logs

EOF

    echo "\`\`\`" >> "$REPORT_FILE"
    echo "$INSTALL_LOG" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"

    cat >> "$REPORT_FILE" << 'EOF'

### Application Logs

- Backend: `backend/logs/healthcare_security.log`
- Security Audit: `backend/logs/security_audit.log`

## Troubleshooting

### Database Connection Issues

1. Check PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

2. Test database connection:
   ```bash
   psql -h <DB_HOST> -p <DB_PORT> -U <DB_USER> -d <DB_NAME>
   ```

3. Check firewall rules:
   ```bash
   sudo ufw status
   ```

### LLM Service Issues

1. Check Ollama is running:
   ```bash
   sudo systemctl status ollama
   ```

2. Test Ollama API:
   ```bash
   curl http://<LLM_HOST>:<LLM_PORT>/api/tags
   ```

3. List available models:
   ```bash
   ollama list
   ```

### Backend API Issues

1. Check if port is in use:
   ```bash
   sudo netstat -tlnp | grep <API_PORT>
   ```

2. Check backend logs:
   ```bash
   tail -f backend/logs/healthcare_security.log
   ```

3. Test Flask can import:
   ```bash
   cd backend
   source venv/bin/activate
   python -c "import flask; print(flask.__version__)"
   ```

## Additional Resources

- **Main README:** `README.md`
- **Quick Start Guide:** `QUICKSTART.md`
- **Testing Guide:** `QUICK_START_TESTING.md`
- **Backend Test Documentation:** `backend/tests/README.md`
- **Comprehensive Documentation:** `LabDocumentation/`

## Support

For issues, questions, or contributions:
- Review the troubleshooting section above
- Check the installation log file
- Consult the comprehensive documentation in `LabDocumentation/`

---

**Installation completed at:**
EOF

    date '+%Y-%m-%d %H:%M:%S' >> "$REPORT_FILE"

    echo "" >> "$REPORT_FILE"
    echo "**Report generated by:** Healthcare Security Research Platform Installer" >> "$REPORT_FILE"
}

###############################################################################
# Main Report Generation
###############################################################################

main() {
    print_header "Generating Installation Report"

    # Create report file
    touch "$REPORT_FILE"

    print_info "Generating report sections..."

    generate_report_header
    generate_configuration_summary
    generate_directory_structure
    generate_installed_components
    generate_next_steps

    print_success "Installation report generated"
    print_info "Report location: $REPORT_FILE"

    echo ""
    print_question "Would you like to view the report now?"
    if confirm_action "View report?"; then
        if command_exists less; then
            less "$REPORT_FILE"
        else
            cat "$REPORT_FILE"
        fi
    fi

    return 0
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    main "$@"
fi
