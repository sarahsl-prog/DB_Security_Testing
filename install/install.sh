#!/bin/bash
###############################################################################
# Healthcare Security Research Platform - Main Installation Script
#
# This is the main interactive installation script that orchestrates
# the complete installation process.
#
# Features:
# - Interactive service selection (Backend/Frontend, PostgreSQL, Ollama)
# - Local or remote service configuration
# - Modular installation with individual service scripts
# - Comprehensive error checking and logging
# - Installation validation
# - Detailed installation report generation
#
# Usage:
#   chmod +x install.sh
#   ./install.sh
#
# Author: Generated for Healthcare Security Research Platform
# Date: 2025
###############################################################################

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common_utils.sh"

# Installation flags
INSTALL_BACKEND_FRONTEND=false
INSTALL_POSTGRESQL=false
INSTALL_OLLAMA=false

# Service location flags
POSTGRESQL_LOCAL=false
OLLAMA_LOCAL=false

###############################################################################
# Service Selection
###############################################################################

select_services() {
    print_header "Service Selection"

    print_info "This installation wizard will help you set up the Healthcare Security"
    print_info "Research Platform. You can choose which services to install on this"
    print_info "machine and configure remote services."
    echo ""

    print_question "Which services would you like to install on THIS machine?"
    echo ""
    print_info "Available services:"
    print_info "  1. Backend/Frontend Applications (Flask API + Vite UI)"
    print_info "  2. PostgreSQL Database"
    print_info "  3. Ollama LLM Service"
    echo ""
    print_info "You can select one, two, or all three services."
    print_info "For services not installed locally, you'll be prompted for remote connection details."
    echo ""

    # Backend/Frontend selection
    if confirm_action "Install Backend/Frontend applications on this machine?"; then
        INSTALL_BACKEND_FRONTEND=true
        print_success "Backend/Frontend will be installed locally"
    else
        print_warning "Backend/Frontend will NOT be installed on this machine"
    fi

    # PostgreSQL selection
    if confirm_action "Install PostgreSQL database on this machine?"; then
        INSTALL_POSTGRESQL=true
        POSTGRESQL_LOCAL=true
        print_success "PostgreSQL will be installed locally"
    else
        print_info "PostgreSQL will be configured as a remote service"
        INSTALL_POSTGRESQL=true
        POSTGRESQL_LOCAL=false
    fi

    # Ollama selection
    if confirm_action "Install Ollama LLM service on this machine?"; then
        INSTALL_OLLAMA=true
        OLLAMA_LOCAL=true
        print_success "Ollama will be installed locally"
    else
        print_info "Ollama will be configured as a remote service"
        INSTALL_OLLAMA=true
        OLLAMA_LOCAL=false
    fi

    # Validate selection
    if [ "$INSTALL_BACKEND_FRONTEND" = false ] && \
       [ "$POSTGRESQL_LOCAL" = true ] && \
       [ "$OLLAMA_LOCAL" = true ]; then
        print_warning "You selected PostgreSQL and Ollama but not Backend/Frontend."
        print_warning "This configuration is unusual but valid."
        if ! confirm_action "Continue with this configuration?"; then
            print_info "Restarting service selection..."
            select_services
            return
        fi
    fi

    # Display summary
    print_header "Installation Summary"
    echo ""
    print_info "Services to install locally:"
    [ "$INSTALL_BACKEND_FRONTEND" = true ] && echo "  ✓ Backend/Frontend Applications"
    [ "$POSTGRESQL_LOCAL" = true ] && echo "  ✓ PostgreSQL Database"
    [ "$OLLAMA_LOCAL" = true ] && echo "  ✓ Ollama LLM Service"
    echo ""
    print_info "Services to configure remotely:"
    [ "$POSTGRESQL_LOCAL" = false ] && echo "  ○ PostgreSQL Database (remote)"
    [ "$OLLAMA_LOCAL" = false ] && echo "  ○ Ollama LLM Service (remote)"
    echo ""

    if ! confirm_action "Proceed with this configuration?"; then
        print_info "Restarting service selection..."
        select_services
        return
    fi
}

###############################################################################
# Prerequisites Check
###############################################################################

check_system_prerequisites() {
    print_header "Checking System Prerequisites"

    local os_type=$(get_os_type)
    local distro=$(get_distro)

    print_success "Operating System: $os_type"
    print_success "Distribution: $distro"

    # Check if running on WSL or Linux
    if [ "$os_type" != "Linux" ] && [ "$os_type" != "WSL" ]; then
        print_error "This script is designed for Linux or WSL environments"
        exit_error "Unsupported operating system: $os_type"
    fi

    # Check for sudo access
    if sudo -n true 2>/dev/null; then
        print_success "Sudo access available"
    else
        print_warning "Sudo access may require password"
        sudo -v || exit_error "Sudo access is required for installation"
    fi

    # Check internet connectivity
    if ping -c 1 8.8.8.8 &> /dev/null; then
        print_success "Internet connectivity available"
    else
        print_warning "Internet connectivity check failed"
        if ! confirm_action "Continue without internet connectivity?"; then
            exit_error "Internet connectivity is required for installation"
        fi
    fi

    return 0
}

###############################################################################
# Installation Execution
###############################################################################

install_services() {
    local install_failed=false

    # Install PostgreSQL
    if [ "$INSTALL_POSTGRESQL" = true ]; then
        print_header "PostgreSQL Installation"

        if [ "$POSTGRESQL_LOCAL" = true ]; then
            print_info "Installing PostgreSQL locally..."
            if bash "$SCRIPT_DIR/install_postgresql.sh" --local; then
                print_success "PostgreSQL installation completed"
            else
                print_error "PostgreSQL installation failed"
                install_failed=true
            fi
        else
            print_info "Configuring remote PostgreSQL connection..."
            if bash "$SCRIPT_DIR/install_postgresql.sh" --remote; then
                print_success "PostgreSQL configuration completed"
            else
                print_error "PostgreSQL configuration failed"
                install_failed=true
            fi
        fi
    fi

    # Install Ollama
    if [ "$INSTALL_OLLAMA" = true ]; then
        print_header "Ollama Installation"

        if [ "$OLLAMA_LOCAL" = true ]; then
            print_info "Installing Ollama locally..."
            if bash "$SCRIPT_DIR/install_ollama.sh" --local; then
                print_success "Ollama installation completed"
            else
                print_error "Ollama installation failed"
                install_failed=true
            fi
        else
            print_info "Configuring remote Ollama connection..."
            if bash "$SCRIPT_DIR/install_ollama.sh" --remote; then
                print_success "Ollama configuration completed"
            else
                print_error "Ollama configuration failed"
                install_failed=true
            fi
        fi
    fi

    # Install Backend/Frontend
    if [ "$INSTALL_BACKEND_FRONTEND" = true ]; then
        print_header "Backend/Frontend Installation"

        print_info "Installing Backend and Frontend applications..."
        if bash "$SCRIPT_DIR/install_backend_frontend.sh"; then
            print_success "Backend/Frontend installation completed"
        else
            print_error "Backend/Frontend installation failed"
            install_failed=true
        fi
    fi

    if [ "$install_failed" = true ]; then
        print_warning "Some installations failed or had warnings"
        if ! confirm_action "Continue to validation anyway?"; then
            exit_error "Installation aborted due to failures"
        fi
    fi

    return 0
}

###############################################################################
# Post-Installation
###############################################################################

run_validation() {
    print_header "Installation Validation"

    if confirm_action "Would you like to validate the installation?"; then
        if bash "$SCRIPT_DIR/validate_installation.sh"; then
            print_success "Validation completed successfully"
        else
            print_warning "Validation completed with warnings or failures"
        fi
    else
        print_info "Skipping validation"
    fi
}

generate_installation_report() {
    print_header "Installation Report"

    if confirm_action "Would you like to generate an installation report?"; then
        if bash "$SCRIPT_DIR/generate_report.sh"; then
            print_success "Installation report generated"
        else
            print_warning "Failed to generate installation report"
        fi
    else
        print_info "Skipping report generation"
    fi
}

###############################################################################
# Display Final Summary
###############################################################################

display_completion_summary() {
    print_header "Installation Complete!"

    echo ""
    print_success "The Healthcare Security Research Platform has been installed successfully!"
    echo ""

    print_info "Installation log: $INSTALL_LOG"
    echo ""

    # Load app config if available to get deployment mode
    local backend_dir="$PROJECT_ROOT/backend"
    local frontend_dir="$PROJECT_ROOT/frontend"
    local deployment_mode="development"

    if [ -f "$SCRIPT_DIR/.app_config" ]; then
        source "$SCRIPT_DIR/.app_config"
        backend_dir="${BACKEND_DIR:-$PROJECT_ROOT/backend}"
        frontend_dir="${FRONTEND_DIR:-$PROJECT_ROOT/frontend}"
        deployment_mode="${DEPLOYMENT_MODE:-development}"
    fi

    print_header "Quick Start Commands"
    echo ""

    if [ "$INSTALL_BACKEND_FRONTEND" = true ]; then
        if [ "$deployment_mode" = "production" ]; then
            echo -e "${CYAN}Backend Service (Production):${NC}"
            echo "  sudo systemctl start healthcare-api"
            echo "  sudo systemctl status healthcare-api"
            echo "  sudo journalctl -u healthcare-api -f"
            echo ""
        else
            echo -e "${CYAN}Start Backend:${NC}"
            echo "  cd $backend_dir"
            echo "  source .venv/bin/activate"
            echo "  python app.py"
            echo ""

            echo -e "${CYAN}Start Frontend:${NC}"
            echo "  cd $frontend_dir"
            echo "  npm run dev"
            echo ""
        fi
    fi

    if [ "$POSTGRESQL_LOCAL" = true ]; then
        echo -e "${CYAN}PostgreSQL Service:${NC}"
        echo "  sudo systemctl status postgresql"
        echo "  sudo systemctl start postgresql"
        echo ""
    fi

    if [ "$OLLAMA_LOCAL" = true ]; then
        echo -e "${CYAN}Ollama Service:${NC}"
        echo "  sudo systemctl status ollama"
        echo "  ollama list"
        echo ""
    fi

    echo -e "${CYAN}Run Tests:${NC}"
    echo "  cd $backend_dir/tests"
    echo "  ./run_tests.sh"
    echo ""

    print_warning "Important Security Notes:"
    echo "  • Default passwords are set to 'password123' - CHANGE THEM!"
    echo "  • .env files contain sensitive data - keep them secure"
    echo "  • Review CORS settings before production deployment"
    echo "  • Consider enabling HTTPS/SSL for production"
    echo ""

    print_info "For detailed information, see:"
    echo "  • Installation report (if generated)"
    echo "  • README.md"
    echo "  • QUICKSTART.md"
    echo "  • LabDocumentation/"
    echo ""

    log_message "SUCCESS" "Installation completed successfully"
}

###############################################################################
# Cleanup Function
###############################################################################

cleanup() {
    # Clean up temporary config files if desired
    if confirm_action "Would you like to remove temporary configuration files?"; then
        rm -f "$SCRIPT_DIR/.pg_config" \
              "$SCRIPT_DIR/.ollama_config" \
              "$SCRIPT_DIR/.app_config" 2>/dev/null
        print_info "Temporary configuration files removed"
        print_warning "Configuration is stored in .env files in backend/ and frontend/"
    else
        print_info "Temporary configuration files kept in: $SCRIPT_DIR/"
    fi
}

###############################################################################
# Main Installation Flow
###############################################################################

main() {
    # Display banner
    print_banner

    log_message "INFO" "=== Healthcare Security Research Platform Installation Started ==="
    log_message "INFO" "Installation initiated by: $(whoami)"
    log_message "INFO" "Installation directory: $PROJECT_ROOT"

    # Check system prerequisites
    if ! check_system_prerequisites; then
        exit_error "System prerequisites check failed"
    fi

    # Select services to install
    select_services

    # Execute installations
    if ! install_services; then
        exit_error "Service installation failed"
    fi

    # Run validation
    run_validation

    # Generate report
    generate_installation_report

    # Display completion summary
    display_completion_summary

    # Optional cleanup
    cleanup

    # Final message
    echo ""
    print_success "Thank you for installing the Healthcare Security Research Platform!"
    print_info "For support, consult the documentation in the LabDocumentation/ directory"
    echo ""

    log_message "INFO" "=== Installation Process Completed ==="

    return 0
}

###############################################################################
# Error Handling
###############################################################################

# Set up error handling
set -e
trap 'echo -e "\n${RED}Installation interrupted${NC}"; exit 1' INT TERM

###############################################################################
# Script Entry Point
###############################################################################

# Check if being sourced or executed
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    # Check for help flag
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        cat << EOF
Healthcare Security Research Platform - Installation Script

Usage: ./install.sh [OPTIONS]

This interactive installation script will guide you through installing:
  - Backend/Frontend Applications (Flask API + Vite UI)
  - PostgreSQL Database
  - Ollama LLM Service

You can choose to install services locally or configure remote connections.

Options:
  -h, --help     Display this help message

The installer will:
  1. Check system prerequisites
  2. Guide you through service selection
  3. Install selected services
  4. Validate the installation
  5. Generate a comprehensive installation report

For more information, see INSTALL.md

EOF
        exit 0
    fi

    # Run main installation
    main "$@"
fi
