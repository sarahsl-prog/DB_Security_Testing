#!/bin/bash
###############################################################################
# Healthcare Security Research Platform - Backend/Frontend Installation Module
#
# This module handles backend and frontend installation and configuration:
# - Installs Python and Node.js if needed
# - Creates virtual environment
# - Installs Python dependencies
# - Installs Node.js dependencies
# - Configures nginx (optional)
# - Creates .env configuration files
# - Validates installation
#
# Usage: ./install_backend_frontend.sh
###############################################################################

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common_utils.sh"

# Configuration variables
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
VENV_DIR="$BACKEND_DIR/venv"
INSTALL_NGINX=false
NGINX_CONF_DIR="/etc/nginx/sites-available"
NGINX_ENABLED_DIR="/etc/nginx/sites-enabled"

# Application configuration
API_HOST="0.0.0.0"
API_PORT="5000"
BACKEND_PUBLIC_HOST=""
SECURITY_MODE="vulnerable"
EMAIL_DOMAIN="hospital.com"

# Import database and LLM config if available
if [ -f "$SCRIPT_DIR/.pg_config" ]; then
    source "$SCRIPT_DIR/.pg_config"
fi

if [ -f "$SCRIPT_DIR/.ollama_config" ]; then
    source "$SCRIPT_DIR/.ollama_config"
fi

###############################################################################
# Prerequisite Check Functions
###############################################################################

check_python_installation() {
    print_header "Checking Python Installation"

    if check_python_version "3.12"; then
        local version=$(python3 --version)
        print_success "Python installed: $version"
        return 0
    else
        print_warning "Python 3.12+ not found"
        return 1
    fi
}

install_python() {
    print_header "Installing Python"

    local distro=$(get_distro)

    case "$distro" in
        ubuntu|debian)
            if install_package "python3" && \
               install_package "python3-pip" && \
               install_package "python3-venv"; then
                print_success "Python installed successfully"
                return 0
            fi
            ;;
        fedora|rhel|centos)
            if install_package "python3" && \
               install_package "python3-pip"; then
                print_success "Python installed successfully"
                return 0
            fi
            ;;
    esac

    print_error "Failed to install Python"
    return 1
}

check_node_installation() {
    print_header "Checking Node.js Installation"

    if command_exists node && command_exists npm; then
        local node_version=$(node --version)
        local npm_version=$(npm --version)
        print_success "Node.js installed: $node_version"
        print_success "npm installed: $npm_version"
        return 0
    else
        print_warning "Node.js not found"
        return 1
    fi
}

install_nodejs() {
    print_header "Installing Node.js"

    local distro=$(get_distro)

    print_info "Installing Node.js via NodeSource repository..."

    # Download and run NodeSource setup script
    if curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - >> "$INSTALL_LOG" 2>&1; then
        if install_package "nodejs"; then
            print_success "Node.js installed successfully"
            return 0
        fi
    fi

    print_error "Failed to install Node.js"
    print_info "You can install manually from: https://nodejs.org/"
    return 1
}

###############################################################################
# Backend Installation Functions
###############################################################################

create_virtual_environment() {
    print_header "Creating Python Virtual Environment"

    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists"
        if confirm_action "Remove and recreate virtual environment?"; then
            rm -rf "$VENV_DIR"
        else
            print_info "Using existing virtual environment"
            return 0
        fi
    fi

    print_info "Creating virtual environment in: $VENV_DIR"

    if python3 -m venv "$VENV_DIR" >> "$INSTALL_LOG" 2>&1; then
        print_success "Virtual environment created"
        return 0
    else
        print_error "Failed to create virtual environment"
        return 1
    fi
}

install_backend_dependencies() {
    print_header "Installing Backend Dependencies"

    local requirements_file="$BACKEND_DIR/requirements.txt"

    if [ ! -f "$requirements_file" ]; then
        print_error "Requirements file not found: $requirements_file"
        return 1
    fi

    print_info "Installing Python packages..."
    print_info "This may take several minutes..."

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip >> "$INSTALL_LOG" 2>&1

    # Install requirements
    if pip install -r "$requirements_file" >> "$INSTALL_LOG" 2>&1; then
        print_success "Backend dependencies installed"
        deactivate
        return 0
    else
        print_error "Failed to install backend dependencies"
        deactivate
        return 1
    fi
}

create_backend_env_file() {
    print_header "Creating Backend .env File"

    local env_file="$BACKEND_DIR/.env"

    # Backup existing file
    backup_file "$env_file"

    # Generate secret keys
    print_info "Generating secure secret keys..."
    local secret_key=$(generate_secret_key)
    local jwt_secret_key=$(generate_secret_key)

    # Create .env file
    cat > "$env_file" << EOF
# Backend API Configuration
# Changed to 0.0.0.0 to bind to all network interfaces
API_HOST=$API_HOST
API_PORT=$API_PORT
FLASK_ENV=development
FLASK_DEBUG=False

# Database Configuration
DB_HOST=${PG_HOST:-localhost}
DB_PORT=${PG_PORT:-5432}
DB_NAME=${PG_DATABASE:-healthcare_security}
DB_USER=${PG_USER:-healthcare_user}
DB_PASSWORD=${PG_PASSWORD:-change_me}

# LLM Service Configuration
LLM_HOST=${OLLAMA_HOST:-localhost}
LLM_PORT=${OLLAMA_PORT:-11434}
LLM_MODEL=${OLLAMA_MODEL:-llama3.1}
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3

# Security Configuration
SECURITY_MODE=$SECURITY_MODE
SECRET_KEY=$secret_key
JWT_SECRET_KEY=$jwt_secret_key
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
EMAIL_DOMAIN=$EMAIL_DOMAIN
API_BASE_URL=http://${BACKEND_PUBLIC_HOST}:${API_PORT}

# Development Environment
DEVELOPMENT_DB_HOST=${PG_HOST:-localhost}
DEVELOPMENT_LLM_HOST=${OLLAMA_HOST:-localhost}

# Testing Environment
TESTING_DB_HOST=${PG_HOST:-localhost}
TESTING_LLM_HOST=${OLLAMA_HOST:-localhost}
TESTING_API_URL=http://localhost:${API_PORT}
EOF

    chmod 600 "$env_file"
    print_success "Backend .env file created"

    return 0
}

###############################################################################
# Frontend Installation Functions
###############################################################################

install_frontend_dependencies() {
    print_header "Installing Frontend Dependencies"

    local package_file="$FRONTEND_DIR/package.json"

    if [ ! -f "$package_file" ]; then
        print_error "package.json not found: $package_file"
        return 1
    fi

    print_info "Installing Node.js packages..."
    print_info "This may take several minutes..."

    cd "$FRONTEND_DIR"

    if npm install >> "$INSTALL_LOG" 2>&1; then
        print_success "Frontend dependencies installed"
        cd "$SCRIPT_DIR"
        return 0
    else
        print_error "Failed to install frontend dependencies"
        cd "$SCRIPT_DIR"
        return 1
    fi
}

create_frontend_env_file() {
    print_header "Creating Frontend .env File"

    local env_file="$FRONTEND_DIR/.env"

    # Backup existing file
    backup_file "$env_file"

    # Create .env file
    cat > "$env_file" << EOF
# Backend API Configuration
VITE_BACKEND_HOST=${BACKEND_PUBLIC_HOST}
VITE_BACKEND_PORT=${API_PORT}
BACKEND_HOST=${BACKEND_PUBLIC_HOST}
BACKEND_PORT=${API_PORT}

# Database Configuration (for reference only - frontend doesn't connect directly)
DB_HOST=${PG_HOST:-localhost}
DB_PORT=${PG_PORT:-5432}
DB_NAME=${PG_DATABASE:-healthcare_security}
DB_USER=${PG_USER:-healthcare_user}
DB_PASSWORD=${PG_PASSWORD:-change_me}

# LLM Service Configuration (for reference only - frontend doesn't connect directly)
LLM_HOST=${OLLAMA_HOST:-localhost}
LLM_PORT=${OLLAMA_PORT:-11434}
LLM_MODEL=${OLLAMA_MODEL:-llama3.1}

# Security Configuration
SECURITY_MODE=$SECURITY_MODE

# Domain Configuration
EMAIL_DOMAIN=$EMAIL_DOMAIN
EOF

    chmod 600 "$env_file"
    print_success "Frontend .env file created"

    return 0
}

###############################################################################
# Nginx Configuration Functions
###############################################################################

check_nginx_installed() {
    if command_exists nginx; then
        local version=$(nginx -v 2>&1 | grep -oP 'nginx/\K[0-9.]+')
        print_success "Nginx installed: $version"
        return 0
    else
        print_warning "Nginx not installed"
        return 1
    fi
}

install_nginx() {
    print_header "Installing Nginx"

    if install_package "nginx"; then
        print_success "Nginx installed successfully"
        return 0
    else
        print_error "Failed to install Nginx"
        return 1
    fi
}

configure_nginx() {
    print_header "Configuring Nginx"

    local nginx_conf="$NGINX_CONF_DIR/healthcare_security"

    # Create nginx configuration
    sudo tee "$nginx_conf" > /dev/null << EOF
server {
    listen 80;
    server_name ${BACKEND_PUBLIC_HOST};

    # Frontend (Vite dev server proxy)
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:${API_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

    # Enable site
    if [ ! -L "$NGINX_ENABLED_DIR/healthcare_security" ]; then
        sudo ln -s "$nginx_conf" "$NGINX_ENABLED_DIR/healthcare_security"
    fi

    # Test configuration
    if sudo nginx -t >> "$INSTALL_LOG" 2>&1; then
        print_success "Nginx configuration is valid"

        # Restart nginx
        if sudo systemctl restart nginx >> "$INSTALL_LOG" 2>&1; then
            print_success "Nginx restarted successfully"
            return 0
        fi
    else
        print_error "Nginx configuration test failed"
        return 1
    fi
}

###############################################################################
# Validation Functions
###############################################################################

validate_backend_installation() {
    print_header "Validating Backend Installation"

    # Check virtual environment
    if [ -d "$VENV_DIR" ]; then
        print_success "Virtual environment exists"
    else
        print_error "Virtual environment not found"
        return 1
    fi

    # Check .env file
    if [ -f "$BACKEND_DIR/.env" ]; then
        print_success "Backend .env file exists"
    else
        print_error "Backend .env file not found"
        return 1
    fi

    # Check if Flask can be imported
    source "$VENV_DIR/bin/activate"
    if python3 -c "import flask" 2>/dev/null; then
        print_success "Flask installed correctly"
    else
        print_error "Flask import failed"
        deactivate
        return 1
    fi
    deactivate

    print_success "Backend validation complete"
    return 0
}

validate_frontend_installation() {
    print_header "Validating Frontend Installation"

    # Check node_modules
    if [ -d "$FRONTEND_DIR/node_modules" ]; then
        print_success "Node modules installed"
    else
        print_error "Node modules not found"
        return 1
    fi

    # Check .env file
    if [ -f "$FRONTEND_DIR/.env" ]; then
        print_success "Frontend .env file exists"
    else
        print_error "Frontend .env file not found"
        return 1
    fi

    print_success "Frontend validation complete"
    return 0
}

###############################################################################
# Main Installation Flow
###############################################################################

main() {
    print_banner
    log_message "INFO" "Backend/Frontend installation module started"

    # Get configuration
    print_header "Backend/Frontend Configuration"

    BACKEND_PUBLIC_HOST=$(prompt_with_validation "Backend server IP address" "192.168.100.20" validate_ip)
    API_PORT=$(prompt_with_validation "Backend API port" "5000" validate_port)

    print_question "Which security mode would you like to start with?"
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

    EMAIL_DOMAIN=$(prompt_with_validation "Email domain for user accounts" "hospital.com" validate_domain)

    if confirm_action "Would you like to install and configure Nginx?"; then
        INSTALL_NGINX=true
    fi

    # Save configuration
    cat > "$SCRIPT_DIR/.app_config" << EOF
BACKEND_PUBLIC_HOST=$BACKEND_PUBLIC_HOST
API_PORT=$API_PORT
SECURITY_MODE=$SECURITY_MODE
EMAIL_DOMAIN=$EMAIL_DOMAIN
EOF
    chmod 600 "$SCRIPT_DIR/.app_config"

    # Check and install Python
    if ! check_python_installation; then
        if confirm_action "Python 3.8+ not found. Install it now?"; then
            if ! install_python; then
                exit_error "Python installation failed"
            fi
        else
            exit_error "Python is required for backend"
        fi
    fi

    # Check and install Node.js
    if ! check_node_installation; then
        if confirm_action "Node.js not found. Install it now?"; then
            if ! install_nodejs; then
                exit_error "Node.js installation failed"
            fi
        else
            exit_error "Node.js is required for frontend"
        fi
    fi

    # Install backend
    print_header "Backend Installation"

    if ! create_virtual_environment; then
        exit_error "Failed to create virtual environment"
    fi

    if ! install_backend_dependencies; then
        exit_error "Failed to install backend dependencies"
    fi

    # Create backend directories
    ensure_directory "$BACKEND_DIR/logs"
    ensure_directory "$BACKEND_DIR/tests/test_reports"

    if ! create_backend_env_file; then
        exit_error "Failed to create backend .env file"
    fi

    # Install frontend
    print_header "Frontend Installation"

    if ! install_frontend_dependencies; then
        exit_error "Failed to install frontend dependencies"
    fi

    ensure_directory "$FRONTEND_DIR/tests/reports"

    if ! create_frontend_env_file; then
        exit_error "Failed to create frontend .env file"
    fi

    # Install Nginx if requested
    if [ "$INSTALL_NGINX" = true ]; then
        if ! check_nginx_installed; then
            if ! install_nginx; then
                print_warning "Nginx installation failed (optional)"
            else
                configure_nginx
            fi
        else
            configure_nginx
        fi
    fi

    # Validate installations
    if ! validate_backend_installation; then
        exit_error "Backend validation failed"
    fi

    if ! validate_frontend_installation; then
        exit_error "Frontend validation failed"
    fi

    print_header "Backend/Frontend Installation Complete"
    print_success "Applications are configured and ready"
    print_info "Backend: http://${BACKEND_PUBLIC_HOST}:${API_PORT}"
    print_info "Security Mode: $SECURITY_MODE"

    log_message "SUCCESS" "Backend/Frontend installation completed successfully"

    return 0
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    main "$@"
fi
