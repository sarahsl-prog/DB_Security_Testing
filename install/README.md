# Healthcare Security Research Platform - Installation Scripts

This directory contains modular installation scripts for the Healthcare Security Research Platform.

## Overview

The installation system is designed to be flexible, modular, and well-documented. It supports installing services locally or configuring remote connections to existing services.

## Directory Contents

| File | Description |
|------|-------------|
| `install.sh` | **Main installation script** - Interactive installer that orchestrates the entire installation process |
| `common_utils.sh` | Shared utility library with logging, validation, and helper functions |
| `install_postgresql.sh` | PostgreSQL installation and configuration module |
| `install_ollama.sh` | Ollama LLM service installation and configuration module |
| `install_backend_frontend.sh` | Backend/Frontend application installation module |
| `validate_installation.sh` | Installation validation and testing module |
| `generate_report.sh` | Installation report generator in markdown format |
| `install_original.sh` | Original installation script (backup) |
| `install_original.bat` | Original Windows installation script (backup) |

## Quick Start

### Run the Main Installer

```bash
cd install
chmod +x install.sh
./install.sh
```

The installer will interactively guide you through:
1. Service selection (Backend/Frontend, PostgreSQL, Ollama)
2. Local vs remote installation choices
3. Configuration setup
4. Installation execution
5. Validation testing
6. Report generation

## Installation Modules

### Main Installation Script (`install.sh`)

The primary entry point for installation. Features:
- Interactive service selection
- Support for local and remote services
- Comprehensive error checking
- Progress tracking and logging
- Post-installation validation
- Report generation

**Usage:**
```bash
./install.sh
```

### Common Utilities (`common_utils.sh`)

Shared library providing:
- Color-coded console output
- Logging functions (file and console)
- Input validation (IP, domain, port, host)
- System checks (OS detection, package management)
- Network connectivity tests
- Security functions (key generation)
- Error handling

**Usage:** (sourced by other scripts)
```bash
source common_utils.sh
```

### PostgreSQL Module (`install_postgresql.sh`)

Handles PostgreSQL installation and configuration:
- Detects existing PostgreSQL installations
- Installs PostgreSQL 15 if needed
- Configures network access
- Creates database and user
- Initializes schema from `backend/setup_database.sql`
- Validates installation

**Usage:**
```bash
# Local installation
./install_postgresql.sh --local

# Remote configuration
./install_postgresql.sh --remote
```

**What it does:**
- Checks system requirements
- Installs PostgreSQL (Ubuntu/Debian or Fedora/RHEL)
- Configures `postgresql.conf` for network access
- Updates `pg_hba.conf` for remote connections
- Creates database and user with proper permissions
- Runs schema initialization
- Tests connectivity and validates installation

### Ollama Module (`install_ollama.sh`)

Handles Ollama LLM service installation and configuration:
- Checks system requirements (CPU, RAM, disk space)
- Installs Ollama using official installer
- Configures systemd service for network access
- Downloads specified LLM model
- Validates installation and API

**Usage:**
```bash
# Local installation
./install_ollama.sh --local

# Remote configuration
./install_ollama.sh --remote
```

**What it does:**
- Checks system resources (CPU cores, RAM, disk space)
- Downloads and installs Ollama
- Creates/updates systemd service file
- Configures `OLLAMA_HOST=0.0.0.0` for network access
- Downloads requested model (e.g., llama3.1)
- Tests API connectivity
- Optional: runs test generation

### Backend/Frontend Module (`install_backend_frontend.sh`)

Handles application installation:
- Checks for Python 3.8+ and Node.js 16+
- Creates Python virtual environment
- Installs Python dependencies from `requirements.txt`
- Installs Node.js dependencies from `package.json`
- Creates `.env` configuration files
- Optional: Installs and configures nginx

**Usage:**
```bash
./install_backend_frontend.sh
```

**What it does:**
- Validates Python and Node.js versions
- Installs missing dependencies
- Creates virtual environment in `backend/venv`
- Installs 150+ Python packages
- Installs Node.js packages
- Generates secure secret keys
- Creates backend and frontend `.env` files
- Creates required log directories
- Optional: configures nginx as reverse proxy

### Validation Module (`validate_installation.sh`)

Comprehensive installation validation:
- Tests database connectivity
- Tests LLM service connectivity
- Tests backend API endpoints
- Runs backend test suite
- Checks system resources
- Validates configuration files

**Usage:**
```bash
./validate_installation.sh
```

**What it tests:**
- PostgreSQL connection and schema
- Ollama API and model availability
- Backend health and authentication endpoints
- Configuration file presence and content
- System resources (disk, memory, CPU)
- Optional: Full test suite execution

### Report Generator (`generate_report.sh`)

Generates comprehensive installation report:
- Configuration summary
- Directory structure
- Installed components
- Next steps and quick start commands
- Default credentials
- Security considerations
- Troubleshooting guide

**Usage:**
```bash
./generate_report.sh
```

**Output:** Markdown report saved to `INSTALLATION_REPORT_YYYYMMDD_HHMMSS.md`

## Installation Scenarios

### Scenario 1: All Services on One Machine

Install everything on a single machine (e.g., for development):

```bash
./install.sh
# Select: Yes to all services
```

This installs:
- PostgreSQL locally
- Ollama locally
- Backend/Frontend locally

### Scenario 2: Distributed Installation

Install services across multiple machines:

**On Database Server:**
```bash
./install.sh
# Select: PostgreSQL only
```

**On LLM Server:**
```bash
./install.sh
# Select: Ollama only
```

**On Application Server:**
```bash
./install.sh
# Select: Backend/Frontend
# Configure remote PostgreSQL
# Configure remote Ollama
```

### Scenario 3: Backend/Frontend Only

Use existing PostgreSQL and Ollama services:

```bash
./install.sh
# Select: Backend/Frontend only
# Provide remote PostgreSQL details
# Provide remote Ollama details
```

## Configuration Files

The installation creates configuration files in `.env` format:

### Backend Configuration
**Location:** `backend/.env`

Contains:
- API host and port
- Database connection details
- LLM service configuration
- Security settings (mode, secret keys)
- Logging configuration

### Frontend Configuration
**Location:** `frontend/.env`

Contains:
- Backend API endpoint
- Reference copies of service settings
- Security mode

### Temporary Config Files
**Location:** `install/` directory

- `.pg_config` - PostgreSQL configuration
- `.ollama_config` - Ollama configuration
- `.app_config` - Application configuration

These files are used to pass configuration between installation modules and can be safely deleted after installation.

## Logging

All installation activities are logged to:

```
logs/install_YYYYMMDD_HHMMSS.log
```

The log includes:
- Timestamp for each operation
- Success/failure status
- Error messages and stack traces
- Command output

## Error Handling

Each module includes comprehensive error handling:
- Validates prerequisites before installation
- Checks command success/failure
- Provides clear error messages
- Logs all errors to install log
- Allows user to continue or abort on errors

## Security Features

The installation system includes several security features:

1. **Secure Key Generation**
   - Generates cryptographically secure random keys
   - Uses Python `secrets` module or OpenSSL

2. **Configuration File Permissions**
   - Sets `.env` files to mode 600 (owner read/write only)
   - Protects sensitive credentials

3. **Input Validation**
   - Validates IP addresses, ports, domains
   - Prevents injection attacks

4. **Logging**
   - Comprehensive audit trail
   - Sensitive data (passwords) not logged in plaintext

## System Requirements

### Minimum Requirements
- **OS:** Linux or WSL (Ubuntu, Debian, Fedora, RHEL, CentOS)
- **CPU:** 2+ cores (4+ recommended for Ollama)
- **RAM:** 8GB+ (for Ollama model)
- **Disk:** 20GB+ free space
- **Network:** Internet connection for package downloads

### Software Prerequisites
- `bash` 4.0+
- `curl` or `wget`
- `sudo` access
- Package manager (`apt`, `dnf`, or `pacman`)

The installer will check for and install missing prerequisites.

## Troubleshooting

### Installation Fails with "Permission Denied"

**Solution:** Run with sudo or ensure user has appropriate permissions
```bash
sudo ./install.sh
```

### PostgreSQL Installation Fails

**Common causes:**
- Conflicting PostgreSQL version already installed
- Port 5432 already in use
- Insufficient disk space

**Solution:** Check system logs and install log file

### Ollama Installation Fails

**Common causes:**
- Insufficient RAM (need 8GB+)
- Limited disk space
- Network connectivity issues

**Solution:** Check system resources and internet connection

### Backend Dependencies Installation Fails

**Common causes:**
- Python version too old (<3.8)
- Missing system libraries
- Network issues

**Solution:**
```bash
# Check Python version
python3 --version

# Install system libraries
sudo apt-get install python3-dev libpq-dev
```

### Script Doesn't Start

**Solution:** Make sure scripts are executable
```bash
chmod +x install/*.sh
```

## Advanced Usage

### Running Individual Modules

You can run installation modules independently:

```bash
# Install only PostgreSQL
./install_postgresql.sh --local

# Install only Ollama
./install_ollama.sh --local

# Install only backend/frontend
./install_backend_frontend.sh
```

### Skip Validation

If you want to skip validation:
- Answer "No" when prompted during main installation
- Or simply don't run `validate_installation.sh`

### Regenerate Report

You can regenerate the installation report anytime:

```bash
./generate_report.sh
```

### Rerun Installation

To reinstall components:
1. Backup your `.env` files
2. Run the installer again
3. It will detect existing installations and offer to:
   - Skip
   - Upgrade
   - Reinstall

## Development and Customization

### Adding New Modules

To add a new installation module:

1. Create a new script in `install/`
2. Source `common_utils.sh`
3. Use common utility functions
4. Follow the existing module pattern
5. Update `install.sh` to call your module
6. Update this README

### Modifying Configuration

To change default values:
- Edit the configuration prompts in each module
- Modify default values in `prompt_with_validation` calls
- Update `.env.example` files

### Custom Logging

The logging system can be customized by modifying `common_utils.sh`:
- Change log format in `log_message` function
- Add new log levels
- Modify console output formatting

## Support

For issues or questions:
1. Check the installation log: `logs/install_*.log`
2. Review this README
3. Consult the main project documentation
4. Check individual module documentation

## License

Part of the Healthcare Security Research Platform
Boston University CS 674 Database Security Fall 2025

## Version History

- **v1.0** (2025-12) - Initial modular installation system
  - Interactive service selection
  - Local and remote installation support
  - Comprehensive validation and reporting
  - Modular architecture with individual service installers
