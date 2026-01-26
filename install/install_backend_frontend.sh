#!/bin/bash
###############################################################################
# Healthcare Security Research Platform - Backend/Frontend Installation Module
#
# This module handles backend and frontend installation and configuration:
# - Installs Python, uv, and Node.js if needed
# - Copies project files to deployment directories
# - Creates virtual environment
# - Installs Python dependencies
# - Builds frontend and deploys static files
# - Configures nginx
# - Creates .env configuration files
# - Creates systemd service
# - Validates installation
#
# Usage: ./install_backend_frontend.sh
###############################################################################

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common_utils.sh"

# Fixed deployment directories
BACKEND_DIR="/opt/db_security"
FRONTEND_DIR="/var/www/healthcare-api"
FRONTEND_BUILD_DIR="$SCRIPT_DIR/../frontend_build"  # Temporary build location
VENV_DIR="$BACKEND_DIR/.venv"

# Nginx configuration
NGINX_CONF_DIR="/etc/nginx/sites-available"
NGINX_ENABLED_DIR="/etc/nginx/sites-enabled"

# Application configuration
API_HOST="0.0.0.0"
API_PORT="5000"
BACKEND_PUBLIC_HOST=""
SECURITY_MODE="vulnerable"
EMAIL_DOMAIN="healthcare.com"

# Node.js/nvm configuration
NVM_VERSION="v0.40.3"
NODE_VERSION="22"

# Import database and LLM config if available
if [ -f "$SCRIPT_DIR/.pg_config" ]; then
    source "$SCRIPT_DIR/.pg_config"
fi

if [ -f "$SCRIPT_DIR/.ollama_config" ]; then
    source "$SCRIPT_DIR/.ollama_config"
fi

###############################################################################
# System Detection Functions
###############################################################################

get_system_ip() {
    # Get primary non-localhost IP address
    local ip=""

    # Method 1: hostname -I (most reliable on Linux)
    if command_exists hostname; then
        ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    fi

    # Method 2: ip route (fallback)
    if [ -z "$ip" ] && command_exists ip; then
        ip=$(ip route get 1 2>/dev/null | awk '{print $7; exit}')
    fi

    # Method 3: ifconfig (older systems)
    if [ -z "$ip" ] && command_exists ifconfig; then
        ip=$(ifconfig 2>/dev/null | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n1)
    fi

    # Fallback to localhost if nothing found
    if [ -z "$ip" ]; then
        ip="127.0.0.1"
    fi

    echo "$ip"
}

###############################################################################
# Project File Functions
###############################################################################

copy_backend_files() {
    print_header "Setting Up Backend Directory"

    # Create backend directory
    if [ ! -d "$BACKEND_DIR" ]; then
        print_info "Creating backend directory: $BACKEND_DIR"
        if sudo mkdir -p "$BACKEND_DIR"; then
            sudo chown -R "$USER:$USER" "$BACKEND_DIR"
            print_success "Created backend directory"
        else
            print_error "Failed to create backend directory"
            return 1
        fi
    else
        print_info "Backend directory already exists"
        sudo chown -R "$USER:$USER" "$BACKEND_DIR"
    fi

    # Copy backend files from project
    print_info "Copying backend files to $BACKEND_DIR..."
    if cp -r "$PROJECT_ROOT/backend/"* "$BACKEND_DIR/" >> "$INSTALL_LOG" 2>&1; then
        print_success "Backend files copied"
    else
        print_error "Failed to copy backend files"
        return 1
    fi

    return 0
}

copy_frontend_files() {
    print_header "Setting Up Frontend Directory"

    # Create frontend directory for static files
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_info "Creating frontend directory: $FRONTEND_DIR"
        if sudo mkdir -p "$FRONTEND_DIR"; then
            sudo chown -R "$USER:$USER" "$FRONTEND_DIR"
            print_success "Created frontend directory"
        else
            print_error "Failed to create frontend directory"
            return 1
        fi
    else
        print_info "Frontend directory already exists"
        sudo chown -R "$USER:$USER" "$FRONTEND_DIR"
    fi

    return 0
}

###############################################################################
# Systemd Service Function
###############################################################################

create_systemd_service() {
    print_header "Creating Systemd Service"

    local service_file="/etc/systemd/system/healthcare-api.service"

    print_info "Creating systemd service file..."

    sudo tee "$service_file" > /dev/null << EOF
[Unit]
Description=Healthcare Database Security Testing API
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    if [ $? -eq 0 ]; then
        print_success "Systemd service file created: $service_file"

        # Reload systemd
        sudo systemctl daemon-reload >> "$INSTALL_LOG" 2>&1

        # Enable and start the service
        print_info "Enabling and starting healthcare-api service..."
        sudo systemctl enable healthcare-api >> "$INSTALL_LOG" 2>&1
        sudo systemctl start healthcare-api >> "$INSTALL_LOG" 2>&1
        print_success "Service enabled and started"
        return 0
    else
        print_error "Failed to create systemd service file"
        return 1
    fi
}

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

check_uv_installation() {
    print_header "Checking uv Installation"

    # Check if uv is in PATH
    if command_exists uv; then
        local version=$(uv --version 2>/dev/null)
        print_success "uv installed: $version"
        return 0
    fi

    # Check common installation locations
    if [ -f "$HOME/.cargo/bin/uv" ]; then
        export PATH="$HOME/.cargo/bin:$PATH"
        local version=$(uv --version 2>/dev/null)
        print_success "uv installed: $version"
        return 0
    fi

    if [ -f "$HOME/.local/bin/uv" ]; then
        export PATH="$HOME/.local/bin:$PATH"
        local version=$(uv --version 2>/dev/null)
        print_success "uv installed: $version"
        return 0
    fi

    print_warning "uv not found"
    return 1
}

install_uv() {
    print_header "Installing uv"

    print_info "Downloading and installing uv..."

    if curl -LsSf https://astral.sh/uv/install.sh | sh >> "$INSTALL_LOG" 2>&1; then
        # Add to PATH for current session
        if [ -f "$HOME/.cargo/bin/uv" ]; then
            export PATH="$HOME/.cargo/bin:$PATH"
        elif [ -f "$HOME/.local/bin/uv" ]; then
            export PATH="$HOME/.local/bin:$PATH"
        fi

        local version=$(uv --version 2>/dev/null)
        print_success "uv installed successfully: $version"
        return 0
    else
        print_error "Failed to install uv"
        print_info "You can install manually from: https://github.com/astral-sh/uv"
        return 1
    fi
}

check_node_installation() {
    print_header "Checking Node.js Installation"

    # Try to load nvm if installed (nvm-installed node won't be in PATH otherwise)
    if [ -s "$HOME/.nvm/nvm.sh" ]; then
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    fi

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
    local nvm_version="$NVM_VERSION"
    local node_version="$NODE_VERSION"

    print_info "Installing Node.js via nvm (Node Version Manager)..."

    # Check if nvm is already installed
    if [ -s "$HOME/.nvm/nvm.sh" ]; then
        print_info "nvm already installed, loading..."
        source "$HOME/.nvm/nvm.sh"
    else
        print_info "Downloading and installing nvm $nvm_version..."
        if curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/${nvm_version}/install.sh" | bash >> "$INSTALL_LOG" 2>&1; then
            # Load nvm into current shell
            export NVM_DIR="$HOME/.nvm"
            [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
            print_success "nvm installed successfully"
        else
            print_error "Failed to install nvm"
            print_info "You can install manually from: https://github.com/nvm-sh/nvm"
            return 1
        fi
    fi

    # Install Node.js using nvm
    print_info "Installing Node.js $node_version..."
    if nvm install $node_version >> "$INSTALL_LOG" 2>&1; then
        nvm use $node_version >> "$INSTALL_LOG" 2>&1
        nvm alias default $node_version >> "$INSTALL_LOG" 2>&1

        local installed_node_version=$(node -v 2>/dev/null)
        local installed_npm_version=$(npm -v 2>/dev/null)
        print_success "Node.js installed: $installed_node_version"
        print_success "npm installed: $installed_npm_version"
        return 0
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

    if uv venv "$VENV_DIR" >> "$INSTALL_LOG" 2>&1; then
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

    # Install requirements using uv
    if uv pip install -r "$requirements_file" >> "$INSTALL_LOG" 2>&1; then
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
API_HOST=$API_HOST
API_PORT=$API_PORT
FLASK_ENV=production
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
EOF

    chmod 600 "$env_file"
    print_success "Backend .env file created"

    return 0
}

###############################################################################
# Frontend Installation Functions
###############################################################################

build_frontend() {
    print_header "Building Frontend"

    # Ensure nvm is loaded for npm commands
    if [ -s "$HOME/.nvm/nvm.sh" ]; then
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    fi

    local frontend_src="$PROJECT_ROOT/frontend"
    local package_file="$frontend_src/package.json"

    if [ ! -f "$package_file" ]; then
        print_error "package.json not found: $package_file"
        return 1
    fi

    print_info "Installing Node.js packages..."
    print_info "This may take several minutes..."

    cd "$frontend_src"

    # Install dependencies
    if ! npm install >> "$INSTALL_LOG" 2>&1; then
        print_error "Failed to install frontend dependencies"
        cd "$SCRIPT_DIR"
        return 1
    fi
    print_success "Frontend dependencies installed"

    # Create .env file for build with backend host
    cat > "$frontend_src/.env" << EOF
VITE_BACKEND_HOST=${BACKEND_PUBLIC_HOST}
VITE_BACKEND_PORT=${API_PORT}
EOF

    # Build the frontend
    print_info "Building frontend for production..."
    if npm run build >> "$INSTALL_LOG" 2>&1; then
        print_success "Frontend built successfully"
    else
        print_error "Failed to build frontend"
        cd "$SCRIPT_DIR"
        return 1
    fi

    # Copy built files to deployment directory
    print_info "Copying built files to $FRONTEND_DIR..."

    # Determine build output directory (could be 'dist' or 'build')
    local build_output=""
    if [ -d "$frontend_src/dist" ]; then
        build_output="$frontend_src/dist"
    elif [ -d "$frontend_src/build" ]; then
        build_output="$frontend_src/build"
    else
        print_error "Build output directory not found (expected 'dist' or 'build')"
        cd "$SCRIPT_DIR"
        return 1
    fi

    # Clear existing files and copy new build
    sudo rm -rf "$FRONTEND_DIR"/* 2>/dev/null
    if sudo cp -r "$build_output"/* "$FRONTEND_DIR/" >> "$INSTALL_LOG" 2>&1; then
        sudo chown -R www-data:www-data "$FRONTEND_DIR"
        print_success "Built files deployed to $FRONTEND_DIR"
    else
        print_error "Failed to copy built files"
        cd "$SCRIPT_DIR"
        return 1
    fi

    cd "$SCRIPT_DIR"
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

    # Remove default site if it exists
    if [ -L "$NGINX_ENABLED_DIR/default" ]; then
        sudo rm "$NGINX_ENABLED_DIR/default" 2>/dev/null
    fi

    # Create nginx configuration for static files
    sudo tee "$nginx_conf" > /dev/null << EOF
server {
    listen 80;
    server_name ${BACKEND_PUBLIC_HOST} _;

    # Serve static frontend files
    root $FRONTEND_DIR;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:${API_PORT};
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

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
EOF

    # Enable site
    if [ -L "$NGINX_ENABLED_DIR/healthcare_security" ]; then
        sudo rm "$NGINX_ENABLED_DIR/healthcare_security"
    fi
    sudo ln -s "$nginx_conf" "$NGINX_ENABLED_DIR/healthcare_security"

    # Test configuration
    if sudo nginx -t >> "$INSTALL_LOG" 2>&1; then
        print_success "Nginx configuration is valid"

        # Restart nginx
        if sudo systemctl restart nginx >> "$INSTALL_LOG" 2>&1; then
            sudo systemctl enable nginx >> "$INSTALL_LOG" 2>&1
            print_success "Nginx restarted and enabled"
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

    # Check if index.html exists in deployment directory
    if [ -f "$FRONTEND_DIR/index.html" ]; then
        print_success "Frontend index.html exists"
    else
        print_error "Frontend index.html not found"
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

    # Detect system IP address
    print_header "System Configuration"
    BACKEND_PUBLIC_HOST=$(get_system_ip)
    print_success "Detected system IP: $BACKEND_PUBLIC_HOST"

    # Display installation paths
    print_info "Backend will be installed to: $BACKEND_DIR"
    print_info "Frontend will be installed to: $FRONTEND_DIR"

    # Get remaining configuration
    print_header "Application Configuration"

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

    EMAIL_DOMAIN=$(prompt_with_validation "Email domain for user accounts" "healthcare.com" validate_domain)

    # Save configuration
    cat > "$SCRIPT_DIR/.app_config" << EOF
BACKEND_DIR=$BACKEND_DIR
FRONTEND_DIR=$FRONTEND_DIR
BACKEND_PUBLIC_HOST=$BACKEND_PUBLIC_HOST
API_PORT=$API_PORT
SECURITY_MODE=$SECURITY_MODE
EMAIL_DOMAIN=$EMAIL_DOMAIN
NVM_VERSION=$NVM_VERSION
NODE_VERSION=$NODE_VERSION
EOF
    chmod 600 "$SCRIPT_DIR/.app_config"

    # Check and install Python
    if ! check_python_installation; then
        print_info "Python 3.12+ not found. Installing..."
        if ! install_python; then
            exit_error "Python installation failed"
        fi
    fi

    # Check and install uv
    if ! check_uv_installation; then
        print_info "uv not found. Installing..."
        if ! install_uv; then
            exit_error "uv installation failed"
        fi
    fi

    # Check and install Node.js
    if ! check_node_installation; then
        print_info "Node.js not found. Installing..."
        if ! install_nodejs; then
            exit_error "Node.js installation failed"
        fi
    fi

    # Copy backend files first
    if ! copy_backend_files; then
        exit_error "Failed to copy backend files"
    fi

    # Setup frontend directory
    if ! copy_frontend_files; then
        exit_error "Failed to setup frontend directory"
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

    # Build and deploy frontend
    print_header "Frontend Installation"

    if ! build_frontend; then
        exit_error "Failed to build frontend"
    fi

    # Install and configure Nginx
    print_header "Nginx Installation"
    if ! check_nginx_installed; then
        if ! install_nginx; then
            exit_error "Nginx installation failed"
        fi
    fi

    if ! configure_nginx; then
        exit_error "Nginx configuration failed"
    fi

    # Validate installations
    if ! validate_backend_installation; then
        exit_error "Backend validation failed"
    fi

    if ! validate_frontend_installation; then
        exit_error "Frontend validation failed"
    fi

    # Create systemd service
    if ! create_systemd_service; then
        print_warning "Systemd service creation failed (non-fatal)"
    fi

    print_header "Installation Complete"
    print_success "Healthcare Security Research Platform is installed and running!"
    echo ""
    print_info "Backend Directory: $BACKEND_DIR"
    print_info "Frontend Directory: $FRONTEND_DIR"
    print_info "Server IP: $BACKEND_PUBLIC_HOST"
    print_info "Security Mode: $SECURITY_MODE"
    echo ""
    print_info "Access the application at: http://${BACKEND_PUBLIC_HOST}"
    echo ""
    print_info "Service management commands:"
    echo "  Backend:  sudo systemctl {start|stop|restart|status} healthcare-api"
    echo "  Nginx:    sudo systemctl {start|stop|restart|status} nginx"
    echo "  Logs:     sudo journalctl -u healthcare-api -f"

    log_message "SUCCESS" "Backend/Frontend installation completed successfully"

    return 0
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    main "$@"
fi
