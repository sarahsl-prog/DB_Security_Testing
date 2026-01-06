#!/bin/bash
###############################################################################
# Healthcare Security Research Platform - Ollama Installation Module
#
# This module handles Ollama LLM service installation and configuration:
# - Checks for existing Ollama installation
# - Installs Ollama if needed
# - Configures Ollama for network access
# - Downloads required models
# - Validates installation
#
# Usage: ./install_ollama.sh [--local|--remote]
###############################################################################

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common_utils.sh"

# Ollama configuration variables
OLLAMA_INSTALLED=false
OLLAMA_REMOTE=false
OLLAMA_HOST=""
OLLAMA_PORT="11434"
OLLAMA_MODEL="llama3.1"
OLLAMA_SERVICE_FILE="/etc/systemd/system/ollama.service"

###############################################################################
# Ollama Detection Functions
###############################################################################

check_ollama_installed() {
    print_header "Checking Ollama Installation"

    if command_exists ollama; then
        local version=$(ollama --version 2>/dev/null | head -1)
        print_success "Ollama installed: $version"
        OLLAMA_INSTALLED=true
        return 0
    else
        print_warning "Ollama not detected on this system"
        OLLAMA_INSTALLED=false
        return 1
    fi
}

check_ollama_service() {
    if service_running ollama; then
        print_success "Ollama service is running"
        return 0
    else
        print_warning "Ollama service is not running"
        return 1
    fi
}

###############################################################################
# System Requirements Check
###############################################################################

check_ollama_requirements() {
    print_header "Checking Ollama System Requirements"

    local all_good=true

    # Check CPU
    local cpu_cores=$(nproc 2>/dev/null || echo "0")
    if [ "$cpu_cores" -ge 2 ]; then
        print_success "CPU cores: $cpu_cores (minimum 2)"
    else
        print_warning "CPU cores: $cpu_cores (recommended: 4+)"
        all_good=false
    fi

    # Check RAM
    local total_ram=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$total_ram" -ge 8 ]; then
        print_success "RAM: ${total_ram}GB (minimum 8GB)"
    else
        print_warning "RAM: ${total_ram}GB (recommended: 8GB+ for llama3.1)"
        all_good=false
    fi

    # Check disk space
    local free_space=$(df -BG "$HOME" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$free_space" -ge 10 ]; then
        print_success "Disk space: ${free_space}GB available (minimum 10GB)"
    else
        print_warning "Disk space: ${free_space}GB (recommended: 20GB+ for models)"
        all_good=false
    fi

    # Check for GPU (optional)
    if command_exists nvidia-smi; then
        local gpu_info=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
        print_success "GPU detected: $gpu_info"
    else
        print_info "No NVIDIA GPU detected (will use CPU)"
    fi

    # Check curl (required for installation)
    if command_exists curl; then
        print_success "curl is installed"
    else
        print_warning "curl not found, installing..."
        install_package "curl" || all_good=false
    fi

    if [ "$all_good" = false ]; then
        print_warning "System may not meet recommended requirements"
        if ! confirm_action "Continue anyway?"; then
            return 1
        fi
    fi

    return 0
}

###############################################################################
# Ollama Installation Functions
###############################################################################

install_ollama() {
    print_header "Installing Ollama"

    print_info "Downloading and installing Ollama..."
    print_info "This may take several minutes..."

    # Download and run the official installation script
    if curl -fsSL https://ollama.ai/install.sh | sh >> "$INSTALL_LOG" 2>&1; then
        print_success "Ollama installed successfully"
        OLLAMA_INSTALLED=true
        return 0
    else
        print_error "Ollama installation failed"
        print_info "You can install manually from: https://ollama.ai/download"
        return 1
    fi
}

###############################################################################
# Ollama Configuration Functions
###############################################################################

configure_ollama_network() {
    print_header "Configuring Ollama for Network Access"

    # Check if systemd service exists
    if [ ! -f "$OLLAMA_SERVICE_FILE" ]; then
        print_info "Creating Ollama systemd service..."

        sudo tee "$OLLAMA_SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
Environment="OLLAMA_HOST=0.0.0.0:${OLLAMA_PORT}"
User=$(whoami)
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

        sudo systemctl daemon-reload
        print_success "Ollama service created"
    else
        print_info "Ollama service already exists"

        # Update environment to listen on all interfaces
        if ! sudo grep -q "Environment.*OLLAMA_HOST" "$OLLAMA_SERVICE_FILE"; then
            backup_file "$OLLAMA_SERVICE_FILE"

            # Add environment variable to service file
            sudo sed -i "/\[Service\]/a Environment=\"OLLAMA_HOST=0.0.0.0:${OLLAMA_PORT}\"" "$OLLAMA_SERVICE_FILE"
            sudo systemctl daemon-reload
            print_success "Updated Ollama service configuration"
        fi
    fi

    # Enable and start service
    print_info "Enabling Ollama service..."
    sudo systemctl enable ollama >> "$INSTALL_LOG" 2>&1

    print_info "Starting Ollama service..."
    if sudo systemctl restart ollama >> "$INSTALL_LOG" 2>&1; then
        print_success "Ollama service started"
        sleep 3
        return 0
    else
        print_error "Failed to start Ollama service"
        return 1
    fi
}

###############################################################################
# Model Management Functions
###############################################################################

download_ollama_model() {
    local model=$1

    print_header "Downloading Ollama Model: $model"

    print_info "This may take several minutes depending on model size..."
    print_info "Model: $model"

    # Pull the model
    if timeout 600 ollama pull "$model" >> "$INSTALL_LOG" 2>&1; then
        print_success "Model downloaded: $model"
        return 0
    else
        print_error "Failed to download model: $model"
        print_info "You can download it manually later with: ollama pull $model"
        return 1
    fi
}

list_available_models() {
    print_header "Available Ollama Models"

    if command_exists ollama; then
        print_info "Currently downloaded models:"
        ollama list 2>/dev/null || print_warning "No models downloaded yet"
    fi
}

###############################################################################
# Validation Functions
###############################################################################

validate_ollama_installation() {
    print_header "Validating Ollama Installation"

    # Check if Ollama is running
    if ! check_ollama_service; then
        print_error "Ollama service is not running"
        return 1
    fi

    # Check network connectivity
    if check_connectivity "localhost" "$OLLAMA_PORT"; then
        print_success "Ollama is listening on port $OLLAMA_PORT"
    else
        print_error "Cannot connect to Ollama on port $OLLAMA_PORT"
        return 1
    fi

    # Test API endpoint
    print_info "Testing Ollama API..."
    local api_response=$(curl -s http://localhost:$OLLAMA_PORT/api/tags 2>/dev/null)

    if [ -n "$api_response" ]; then
        print_success "Ollama API is responding"

        # Check if model exists
        if echo "$api_response" | grep -q "\"name\":\"$OLLAMA_MODEL\""; then
            print_success "Model available: $OLLAMA_MODEL"
            return 0
        else
            print_warning "Model not found: $OLLAMA_MODEL"
            if confirm_action "Download $OLLAMA_MODEL now?"; then
                download_ollama_model "$OLLAMA_MODEL"
            fi
        fi
    else
        print_error "Ollama API is not responding"
        return 1
    fi
}

test_ollama_generation() {
    print_header "Testing Ollama Text Generation"

    print_info "Running a simple test query..."

    local test_prompt="SELECT * FROM patients WHERE patient_id = 1"
    local response=$(curl -s http://localhost:$OLLAMA_PORT/api/generate -d "{
        \"model\": \"$OLLAMA_MODEL\",
        \"prompt\": \"$test_prompt\",
        \"stream\": false
    }" 2>/dev/null)

    if [ -n "$response" ] && echo "$response" | grep -q "response"; then
        print_success "Ollama is generating responses correctly"
        return 0
    else
        print_warning "Ollama test generation failed"
        return 1
    fi
}

###############################################################################
# Remote Ollama Configuration
###############################################################################

configure_remote_ollama() {
    print_header "Configuring Remote Ollama Connection"

    print_info "Testing connection to remote Ollama..."

    if curl -s --max-time 5 "http://$OLLAMA_HOST:$OLLAMA_PORT/api/tags" > /dev/null 2>&1; then
        print_success "Successfully connected to remote Ollama"

        # Check for required model
        local api_response=$(curl -s "http://$OLLAMA_HOST:$OLLAMA_PORT/api/tags" 2>/dev/null)
        if echo "$api_response" | grep -q "\"name\":\"$OLLAMA_MODEL\""; then
            print_success "Model available on remote: $OLLAMA_MODEL"
        else
            print_warning "Model $OLLAMA_MODEL not found on remote server"
            print_info "Please install it on the remote server with:"
            print_info "  ollama pull $OLLAMA_MODEL"
        fi

        return 0
    else
        print_warning "Cannot connect to remote Ollama"
        print_info "Please ensure:"
        print_info "  1. Ollama is running on $OLLAMA_HOST:$OLLAMA_PORT"
        print_info "  2. Firewall allows connections"
        print_info "  3. Ollama is configured to listen on 0.0.0.0"

        if confirm_action "Would you like to continue anyway?"; then
            return 0
        else
            return 1
        fi
    fi
}

###############################################################################
# Main Installation Flow
###############################################################################

main() {
    print_banner
    log_message "INFO" "Ollama installation module started"

    # Determine if local or remote installation
    if [ "$1" = "--remote" ]; then
        OLLAMA_REMOTE=true
        print_info "Configuring for remote Ollama server"
    else
        print_info "Configuring for local Ollama installation"
    fi

    # Get Ollama configuration
    print_header "Ollama Configuration"

    if [ "$OLLAMA_REMOTE" = true ]; then
        OLLAMA_HOST=$(prompt_with_validation "Ollama server IP address" "192.168.100.1" validate_ip)
    else
        OLLAMA_HOST="localhost"
    fi

    OLLAMA_PORT=$(prompt_with_validation "Ollama port" "11434" validate_port)

    print_question "Which Ollama model would you like to use?"
    print_info "Recommended: llama3.1 (general purpose, good for SQL)"
    print_info "Alternative: codellama (code-focused)"
    OLLAMA_MODEL=$(prompt_with_validation "Ollama model" "llama3.1")

    # Save configuration for later use
    cat > "$SCRIPT_DIR/.ollama_config" << EOF
OLLAMA_HOST=$OLLAMA_HOST
OLLAMA_PORT=$OLLAMA_PORT
OLLAMA_MODEL=$OLLAMA_MODEL
EOF
    chmod 600 "$SCRIPT_DIR/.ollama_config"

    # Execute installation steps
    if [ "$OLLAMA_REMOTE" = false ]; then
        # Local installation
        if ! check_ollama_requirements; then
            exit_error "System requirements not met"
        fi

        if ! check_ollama_installed; then
            if confirm_action "Ollama not found. Install it now?"; then
                if ! install_ollama; then
                    exit_error "Ollama installation failed"
                fi
            else
                exit_error "Ollama installation cancelled by user"
            fi
        fi

        # Configure Ollama for network access
        if ! configure_ollama_network; then
            print_warning "Failed to configure network access"
        fi

        # Download required model
        list_available_models

        if ! validate_ollama_installation; then
            print_warning "Ollama validation incomplete"
        fi

        # Optional: test generation
        if confirm_action "Would you like to test text generation?"; then
            test_ollama_generation
        fi
    else
        # Remote installation - just test connection
        if ! configure_remote_ollama; then
            exit_error "Failed to configure remote Ollama"
        fi
    fi

    print_header "Ollama Installation Complete"
    print_success "Ollama is configured and ready"
    print_info "Host: $OLLAMA_HOST"
    print_info "Port: $OLLAMA_PORT"
    print_info "Model: $OLLAMA_MODEL"

    log_message "SUCCESS" "Ollama installation completed successfully"

    return 0
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    main "$@"
fi
