#!/bin/bash
###############################################################################
# Healthcare Security Research API - Installation Script
#
# This script interactively configures the application by:
# - Collecting host IP addresses and configuration settings
# - Generating secure secret keys
# - Creating .env files for both backend and frontend
# - Setting up required directories
#
# Usage:
#   chmod +x install.sh
#   ./install.sh
###############################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

###############################################################################
# Helper Functions
###############################################################################

print_banner() {
    clear
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}   Healthcare Security Research Platform - Installation${NC}"
    echo -e "${BLUE}   Interactive Configuration Setup${NC}"
    echo -e "${BLUE}================================================================${NC}\n"
}

print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}● $1${NC}"
}

print_question() {
    echo -e "${MAGENTA}? $1${NC}"
}

# Function to validate IP address
validate_ip() {
    local ip=$1
    local valid_ip_regex="^([0-9]{1,3}\.){3}[0-9]{1,3}$"

    if [[ ! $ip =~ $valid_ip_regex ]]; then
        return 1
    fi

    # Check each octet
    IFS='.' read -ra ADDR <<< "$ip"
    for i in "${ADDR[@]}"; do
        if [ "$i" -gt 255 ]; then
            return 1
        fi
    done

    return 0
}

# Function to validate domain name
validate_domain() {
    local domain=$1
    local valid_domain_regex="^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"

    if [[ $domain =~ $valid_domain_regex ]]; then
        return 0
    else
        return 1
    fi
}

# Function to prompt for input with validation
prompt_with_validation() {
    local prompt=$1
    local default=$2
    local validator=$3
    local value=""

    while true; do
        if [ -n "$default" ]; then
            read -p "$(echo -e "${MAGENTA}? ${prompt} [${default}]: ${NC}")" value
            value=${value:-$default}
        else
            read -p "$(echo -e "${MAGENTA}? ${prompt}: ${NC}")" value
        fi

        if [ -z "$validator" ]; then
            echo "$value"
            return
        fi

        if $validator "$value"; then
            echo "$value"
            return
        else
            print_error "Invalid input. Please try again."
        fi
    done
}

# Function to generate secure random key
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || \
    openssl rand -base64 32 2>/dev/null || \
    head -c 32 /dev/urandom | base64
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"

    local all_good=true

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python installed: $PYTHON_VERSION"
    else
        print_error "Python 3 not found. Please install Python 3.12 or higher."
        all_good=false
    fi

    # Check for PostgreSQL client (optional)
    if command -v psql &> /dev/null; then
        PSQL_VERSION=$(psql --version | head -n 1)
        print_success "PostgreSQL client found: $PSQL_VERSION"
    else
        print_warning "PostgreSQL client not found (optional)"
    fi

    # Check if directories exist
    if [ -d "$BACKEND_DIR" ]; then
        print_success "Backend directory found"
    else
        print_error "Backend directory not found: $BACKEND_DIR"
        all_good=false
    fi

    if [ -d "$FRONTEND_DIR" ]; then
        print_success "Frontend directory found"
    else
        print_error "Frontend directory not found: $FRONTEND_DIR"
        all_good=false
    fi

    if [ "$all_good" = false ]; then
        print_error "Prerequisites check failed. Please fix the issues above."
        exit 1
    fi

    echo ""
}

# Function to collect configuration
collect_configuration() {
    print_header "Configuration Wizard"

    print_info "This wizard will guide you through configuring the application."
    print_info "Press Enter to accept default values shown in brackets [default].\n"

    # Backend/Frontend Host
    print_question "What is the IP address where the backend API will run?"
    print_info "This is typically the IP of the machine running the Flask backend."
    BACKEND_HOST=$(prompt_with_validation "Backend API Host" "192.168.100.20" validate_ip)

    # Backend Port
    print_question "\nWhat port should the backend API listen on?"
    BACKEND_PORT=$(prompt_with_validation "Backend API Port" "5000")

    # Database Host
    print_question "\nWhat is the IP address of your PostgreSQL database server?"
    DB_HOST=$(prompt_with_validation "Database Host" "192.168.100.30" validate_ip)

    # Database Port
    print_question "\nWhat port is PostgreSQL running on?"
    DB_PORT=$(prompt_with_validation "Database Port" "5432")

    # Database Name
    print_question "\nWhat is the name of your PostgreSQL database?"
    DB_NAME=$(prompt_with_validation "Database Name" "healthcare_security")

    # Database User
    print_question "\nWhat is the PostgreSQL username?"
    DB_USER=$(prompt_with_validation "Database User" "healthcare_user")

    # Database Password
    print_question "\nWhat is the PostgreSQL password?"
    read -s -p "$(echo -e "${MAGENTA}? Database Password: ${NC}")" DB_PASSWORD
    echo ""

    # LLM Host
    print_question "\nWhat is the IP address of your Ollama LLM service?"
    LLM_HOST=$(prompt_with_validation "LLM Service Host" "192.168.100.1" validate_ip)

    # LLM Port
    print_question "\nWhat port is Ollama running on?"
    LLM_PORT=$(prompt_with_validation "LLM Service Port" "11434")

    # LLM Model
    print_question "\nWhat Ollama model should be used?"
    LLM_MODEL=$(prompt_with_validation "LLM Model" "llama3.1-sql:latest")

    # Email Domain
    print_question "\nWhat domain should be used for user email addresses?"
    print_info "Example: hospital.com will create emails like admin@hospital.com"
    EMAIL_DOMAIN=$(prompt_with_validation "Email Domain" "hospital.com" validate_domain)

    # Security Mode
    print_question "\nWhich security mode would you like to start with?"
    print_info "  vulnerable - Demonstrates security vulnerabilities (for research)"
    print_info "  secure     - All security features enabled"
    PS3="$(echo -e "${MAGENTA}? Select mode (1-2): ${NC}")"
    options=("vulnerable" "secure")
    select opt in "${options[@]}"; do
        case $opt in
            "vulnerable")
                SECURITY_MODE="vulnerable"
                break
                ;;
            "secure")
                SECURITY_MODE="secure"
                break
                ;;
            *)
                print_error "Invalid option. Please select 1 or 2."
                ;;
        esac
    done

    # Generate secret keys
    print_info "\nGenerating secure secret keys..."
    SECRET_KEY=$(generate_secret_key)
    JWT_SECRET_KEY=$(generate_secret_key)

    if [ -z "$SECRET_KEY" ] || [ -z "$JWT_SECRET_KEY" ]; then
        print_warning "Failed to generate secure keys automatically."
        print_warning "Using default keys. CHANGE THESE IN PRODUCTION!"
        SECRET_KEY="change_this_in_production_$(date +%s)"
        JWT_SECRET_KEY="change_this_in_production_$(date +%s)"
    else
        print_success "Secure keys generated"
    fi
}

# Function to display configuration summary
display_summary() {
    print_header "Configuration Summary"

    echo -e "${CYAN}Network Configuration:${NC}"
    echo -e "  Backend API:        ${GREEN}${BACKEND_HOST}:${BACKEND_PORT}${NC}"
    echo -e "  Database Server:    ${GREEN}${DB_HOST}:${DB_PORT}${NC}"
    echo -e "  LLM Service:        ${GREEN}${LLM_HOST}:${LLM_PORT}${NC}"
    echo ""
    echo -e "${CYAN}Database Configuration:${NC}"
    echo -e "  Database Name:      ${GREEN}${DB_NAME}${NC}"
    echo -e "  Database User:      ${GREEN}${DB_USER}${NC}"
    echo -e "  Database Password:  ${GREEN}***********${NC}"
    echo ""
    echo -e "${CYAN}Application Configuration:${NC}"
    echo -e "  Email Domain:       ${GREEN}${EMAIL_DOMAIN}${NC}"
    echo -e "  LLM Model:          ${GREEN}${LLM_MODEL}${NC}"
    echo -e "  Security Mode:      ${GREEN}${SECURITY_MODE}${NC}"
    echo ""

    read -p "$(echo -e "${YELLOW}Continue with this configuration? (y/n): ${NC}")" confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_warning "Installation cancelled by user."
        exit 0
    fi
}

# Function to create backend .env file
create_backend_env() {
    print_info "Creating backend/.env file..."

    cat > "$BACKEND_DIR/.env" << EOF
# Backend API Configuration
# Changed to 0.0.0.0 to bind to all network interfaces
# Use 127.0.0.1 for localhost only, or specific IP if needed
API_HOST=0.0.0.0
API_PORT=${BACKEND_PORT}
FLASK_ENV=development
FLASK_DEBUG=False

# Database Configuration
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

# LLM Service Configuration
LLM_HOST=${LLM_HOST}
LLM_PORT=${LLM_PORT}
LLM_MODEL=${LLM_MODEL}
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3

# Security Configuration
SECURITY_MODE=${SECURITY_MODE}
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_EXPIRES_HOURS=24

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/healthcare_security.log
AUDIT_LOG_FILE=logs/security_audit.log

# CORS Configuration
CORS_ORIGINS=*

# Query and Rate Limiting
MAX_QUERY_RESULTS=1000
QUERY_TIMEOUT=30
RATE_LIMIT_PER_MINUTE=60
CACHE_TTL=300

# Domain Configuration
EMAIL_DOMAIN=${EMAIL_DOMAIN}
API_BASE_URL=http://${BACKEND_HOST}:${BACKEND_PORT}

# Development Environment
DEVELOPMENT_DB_HOST=${DB_HOST}
DEVELOPMENT_LLM_HOST=${LLM_HOST}

# Testing Environment
TESTING_DB_HOST=${DB_HOST}
TESTING_LLM_HOST=${LLM_HOST}
TESTING_API_URL=http://localhost:${BACKEND_PORT}
EOF

    if [ $? -eq 0 ]; then
        print_success "Backend .env file created"
    else
        print_error "Failed to create backend .env file"
        exit 1
    fi
}

# Function to create frontend .env file
create_frontend_env() {
    print_info "Creating frontend/.env file..."

    cat > "$FRONTEND_DIR/.env" << EOF
# Backend API Configuration
VITE_BACKEND_HOST=${BACKEND_HOST}
VITE_BACKEND_PORT=${BACKEND_PORT}
BACKEND_HOST=${BACKEND_HOST}
BACKEND_PORT=${BACKEND_PORT}

# Database Configuration (for reference only - frontend doesn't connect directly)
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

# LLM Service Configuration (for reference only - frontend doesn't connect directly)
LLM_HOST=${LLM_HOST}
LLM_PORT=${LLM_PORT}
LLM_MODEL=${LLM_MODEL}

# Security Configuration
SECURITY_MODE=${SECURITY_MODE}
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}

# Logging (for reference only - actual logs are in backend)
LOG_LEVEL=INFO
LOG_FILE=logs/healthcare_security.log
AUDIT_LOG_FILE=logs/security_audit.log

# Domain Configuration
EMAIL_DOMAIN=${EMAIL_DOMAIN}
EOF

    if [ $? -eq 0 ]; then
        print_success "Frontend .env file created"
    else
        print_error "Failed to create frontend .env file"
        exit 1
    fi
}

# Function to create required directories
create_directories() {
    print_info "Creating required directories..."

    # Backend directories
    mkdir -p "$BACKEND_DIR/logs"
    mkdir -p "$BACKEND_DIR/tests/test_reports"

    # Frontend directories
    mkdir -p "$FRONTEND_DIR/tests/reports"

    print_success "Directories created"
}

# Function to display next steps
display_next_steps() {
    print_header "Installation Complete!"

    print_success "Configuration files have been created successfully.\n"

    echo -e "${CYAN}Next Steps:${NC}\n"

    echo -e "${YELLOW}1. Set up the PostgreSQL database:${NC}"
    echo -e "   cd backend"
    echo -e "   python3 -m venv venv"
    echo -e "   source venv/bin/activate"
    echo -e "   pip install -r requirements.txt"
    echo -e "   python database.py  # Initialize database and create tables"
    echo ""

    echo -e "${YELLOW}2. Start the backend server:${NC}"
    echo -e "   cd backend"
    echo -e "   source venv/bin/activate"
    echo -e "   python app.py"
    echo ""

    echo -e "${YELLOW}3. Set up the frontend:${NC}"
    echo -e "   cd frontend"
    echo -e "   npm install"
    echo -e "   npm run dev"
    echo ""

    echo -e "${YELLOW}4. Access the application:${NC}"
    echo -e "   Frontend: http://localhost:5173 (or Vite's assigned port)"
    echo -e "   Backend:  http://${BACKEND_HOST}:${BACKEND_PORT}"
    echo ""

    echo -e "${YELLOW}5. Default login credentials:${NC}"
    echo -e "   Username: admin"
    echo -e "   Password: password123"
    echo ""

    print_warning "IMPORTANT SECURITY NOTES:"
    echo -e "   • Change default passwords in production"
    echo -e "   • Secure your .env files (they contain sensitive data)"
    echo -e "   • Review CORS settings for production deployment"
    echo -e "   • Consider using HTTPS in production"
    echo ""

    print_info "For more information, see the README.md file."
}

###############################################################################
# Main Installation Flow
###############################################################################

main() {
    print_banner

    # Check prerequisites
    check_prerequisites

    # Collect configuration from user
    collect_configuration

    # Display summary and confirm
    display_summary

    # Create configuration files
    print_header "Creating Configuration Files"
    create_backend_env
    create_frontend_env

    # Create directories
    create_directories

    # Display next steps
    display_next_steps
}

# Run main function
main
