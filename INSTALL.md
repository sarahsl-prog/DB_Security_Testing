<!--
Healthcare Database Security Testing Project
Created for Boston University CS 674 Database Security Fall 2025
Author: Sarah Sund-Lussier (SarahSL@bu.edu)
GitHub: https://github.com/sarahsl-prog/DB_Security_Testing
-->

# Healthcare Database Security Testing Platform - Installation Guide

This guide will help you install and configure the Healthcare Database Security Testing Platform using the interactive installation scripts.

## Prerequisites

Before running the installation scripts, ensure you have the following:

### Required Software

- **Python 3.12+** - Backend application runtime
- **PostgreSQL 17+** - Database server
- **Node.js 22+** - Frontend build tools (required >=22.12.0)
- **Ollama** - LLM service for SQL generation

### Network Requirements

You'll need to know the IP addresses of:
1. The machine running the backend API server
2. The PostgreSQL database server
3. The Ollama LLM service

### Database Setup

Ensure your PostgreSQL server is running and you have:
- A database created (or the script will create one)
- A database user with appropriate permissions
- The database password

---

## Quick Start

### For Windows Users

1. Open Command Prompt or PowerShell
2. Navigate to the DB_Security_Testing directory
3. Run the installation script:
   ```cmd
   install.bat
   ```

### For Linux/Mac Users

1. Open Terminal
2. Navigate to the DB_Security_Testing directory
3. Make the script executable (if not already):
   ```bash
   chmod +x install.sh
   ```
4. Run the installation script:
   ```bash
   ./install.sh
   ```

---

## Installation Process

The installation script will guide you through the following steps:

### 1. Prerequisites Check

The script will verify:
- Python is installed
- Required directories exist
- PostgreSQL client is available (optional)

### 2. Configuration Collection

You'll be prompted to provide:

#### Network Configuration
- **Backend API Host**: IP address where Flask backend will run
  - Default: `192.168.100.20`
  - Use `0.0.0.0` to bind to all interfaces
  - Use `127.0.0.1` for localhost only

- **Backend API Port**: Port for Flask backend
  - Default: `5000`

- **Database Host**: PostgreSQL server IP address
  - Default: `192.168.100.30`

- **Database Port**: PostgreSQL server port
  - Default: `5432`

- **LLM Service Host**: Ollama server IP address
  - Default: `192.168.100.1`

- **LLM Service Port**: Ollama server port
  - Default: `11434`

#### Database Configuration
- **Database Name**: Name of the PostgreSQL database
  - Default: `healthcare_security`

- **Database User**: PostgreSQL username
  - Default: `healthcare_user`

- **Database Password**: PostgreSQL password
  - No default - you must provide this

#### Application Configuration
- **Email Domain**: Domain for user email addresses
  - Default: `hospital.com`
  - Example: `admin@hospital.com`

- **LLM Model**: Ollama model to use
  - Default: `deepseek-r1:latest`

- **Security Mode**: Choose between:
  - `vulnerable` - Demonstrates security vulnerabilities (for research)
  - `secure` - All security features enabled

### 3. Configuration Summary

The script will display a summary of your configuration. Review it carefully and confirm to proceed.

### 4. File Creation

The script will create:
- `backend/.env` - Backend environment configuration
- `frontend/.env` - Frontend environment configuration
- Required directories:
  - `backend/logs/` - Application logs
  - `backend/tests/test_reports/` - Test reports
  - `frontend/tests/reports/` - Frontend test reports

### 5. Secure Key Generation

The script automatically generates secure random keys for:
- `SECRET_KEY` - Flask session security
- `JWT_SECRET_KEY` - JWT token signing

---

## Post-Installation Steps

After the installation script completes, follow these steps:

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
# For Linux/Mac:
uv venv .venv
source .venv/bin/activate

# For Windows:
uv venv .venv
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Initialize database (creates tables and sample data)
python database.py

# Start the backend server
python app.py
```

The backend will be available at `http://<BACKEND_HOST>:<BACKEND_PORT>`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173` (or Vite's assigned port)

### 3. Verify Installation

#### Test Backend Health
```bash
curl http://<BACKEND_HOST>:<BACKEND_PORT>/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "services": {
    "database": "connected",
    "llm": "available"
  }
}
```

#### Test Login
Open your browser and navigate to the frontend URL. Try logging in with:
- **Username**: `admin`
- **Password**: `password123`

### 4. Run Tests (Optional)

#### Backend Tests
```bash
cd backend/tests

# Run all tests (Linux/Mac)
./run_tests.sh

# Run all tests (Windows)
run_tests.bat
```

#### Frontend Tests
```bash
cd frontend/tests
python testing.py
```

---

## Configuration Files

### Backend .env File

Located at `backend/.env`, contains:
- API server configuration
- Database connection details
- LLM service configuration
- Security settings
- Logging configuration

**Important**: This file contains sensitive information. Never commit it to version control!

### Frontend .env File

Located at `frontend/.env`, contains:
- Backend API endpoint
- Reference copies of database/LLM settings (for display only)
- Security mode settings

---

## Troubleshooting

### Issue: "Python not found"

**Solution**: Install Python 3.12+ or higher from [python.org](https://www.python.org/downloads/)

### Issue: "Failed to connect to database"

**Possible causes**:
1. PostgreSQL is not running
2. Incorrect IP address or port
3. Firewall blocking connection
4. Incorrect credentials

**Solution**:
```bash
# Test database connection
psql -h <DB_HOST> -p <DB_PORT> -U <DB_USER> -d <DB_NAME>
```

### Issue: "LLM service not available"

**Possible causes**:
1. Ollama is not running
2. Incorrect IP address or port
3. Model not downloaded

**Solution**:
```bash
# Test Ollama service
curl http://<LLM_HOST>:<LLM_PORT>/api/version

# List available models
curl http://<LLM_HOST>:<LLM_PORT>/api/tags

# Pull the model if not available
ollama pull deepseek-r1:latest
```

### Issue: "Port already in use"

**Solution**: Change the port in your `.env` file:
```bash
# Edit backend/.env
API_PORT=5001  # Use a different port
```

### Issue: "CORS errors in browser"

**Solution**: Update CORS settings in `backend/.env`:
```bash
# Allow specific origins
CORS_ORIGINS=http://localhost:5173,http://192.168.100.20

# Or allow all (development only)
CORS_ORIGINS=*
```

---

## Security Considerations

### Development vs Production

The installation script sets up a **development environment**. For production:

1. **Change default passwords**:
   - Database password
   - User account passwords
   - SECRET_KEY and JWT_SECRET_KEY (regenerate)

2. **Enable HTTPS**:
   - Use a reverse proxy (nginx, Apache)
   - Obtain SSL certificates

3. **Restrict CORS**:
   - Set specific allowed origins
   - Remove wildcard (`*`) setting

4. **Set security mode**:
   ```bash
   SECURITY_MODE=secure
   ```

5. **Review firewall rules**:
   - Only expose necessary ports
   - Restrict database/LLM access

6. **Enable production logging**:
   ```bash
   LOG_LEVEL=WARNING
   FLASK_DEBUG=False
   FLASK_ENV=production
   ```

### Protecting .env Files

The `.env` files contain sensitive information:
- Database passwords
- Secret keys
- Internal IP addresses

**Important**:
- Never commit `.env` files to version control
- Set appropriate file permissions:
  ```bash
  # Linux/Mac
  chmod 600 backend/.env frontend/.env
  ```
- Back up `.env` files securely
- Use different credentials for each environment

---

## Network Architecture

```
┌─────────────────┐
│   Frontend      │  Port: 5173
│   (Vite)        │
└────────┬────────┘
         │
         │ HTTP/HTTPS
         │
┌────────▼────────┐
│   Backend API   │  Port: 5000
│   (Flask)       │  Host: BACKEND_HOST
└────┬──────┬─────┘
     │      │
     │      └──────────┐
     │                 │
┌────▼────────┐  ┌────▼────────┐
│  PostgreSQL │  │   Ollama    │
│  Database   │  │   LLM       │
│             │  │             │
│ Port: 5432  │  │ Port: 11434 │
│ DB_HOST     │  │ LLM_HOST    │
└─────────────┘  └─────────────┘
```

---

## Re-running Installation

If you need to reconfigure the application:

1. The installation script will **overwrite** existing `.env` files
2. Back up your current configuration if needed:
   ```bash
   cp backend/.env backend/.env.backup
   cp frontend/.env frontend/.env.backup
   ```
3. Run the installation script again
4. Your existing database and logs will not be affected

---

## Getting Help

If you encounter issues:

1. Check the logs:
   - Backend: `backend/logs/healthcare_security.log`
   - Connectivity: `backend/logs/connectivity_debug.log`
   - Login audit: `backend/logs/login_audit.log`

2. Review the configuration:
   - `backend/.env`
   - `frontend/.env`

3. Run diagnostic tests:
   ```bash
   cd backend
   python -c "from config import Config; print(Config.DATABASE_URL)"
   ```

4. Check network connectivity:
   ```bash
   # Test database
   telnet <DB_HOST> <DB_PORT>

   # Test LLM service
   telnet <LLM_HOST> <LLM_PORT>
   ```

---

## Additional Resources

- **Project Documentation**: See main `README.md`
- **Backend API Documentation**: `backend/README.md` (if available)
- **Frontend Documentation**: `frontend/README.md` (if available)
- **Security Research Guide**: Documentation on using vulnerable vs secure modes

---

## License

**MIT License**: `LICENSE`

---

## Support

For issues, questions, or contributions, please **contact** sarahsl@bu.edu
