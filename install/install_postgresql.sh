#!/bin/bash
###############################################################################
# Healthcare Security Research Platform - PostgreSQL Installation Module
#
# This module handles PostgreSQL installation and configuration:
# - Checks for existing PostgreSQL installation
# - Installs PostgreSQL if needed
# - Configures PostgreSQL for remote access
# - Creates database and user
# - Initializes schema and sample data
# - Validates installation
#
# Usage: ./install_postgresql.sh [--local|--remote]
###############################################################################

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common_utils.sh"

# PostgreSQL configuration variables
PG_VERSION="17"
PG_INSTALLED=false
PG_REMOTE=false
PG_HOST=""
PG_PORT="5432"
PG_DATABASE=""
PG_USER=""
PG_PASSWORD=""

###############################################################################
# PostgreSQL Detection Functions
###############################################################################

check_postgresql_installed() {
    print_header "Checking PostgreSQL Installation"

    if command_exists psql; then
        local version=$(psql --version | grep -oP '\d+' | head -1)
        print_success "PostgreSQL client installed (version $version)"
        PG_INSTALLED=true

        if service_running postgresql; then
            print_success "PostgreSQL service is running"
            return 0
        elif systemctl list-unit-files | grep -q "postgresql@"; then
            print_info "PostgreSQL service exists but not running"
            return 0
        else
            print_warning "PostgreSQL client found but service not detected"
        fi
    else
        print_warning "PostgreSQL not detected on this system"
        PG_INSTALLED=false
        return 1
    fi
}

###############################################################################
# PostgreSQL Installation Functions
###############################################################################

install_postgresql_ubuntu() {
    print_header "Installing PostgreSQL on Ubuntu/Debian"

    # Import PostgreSQL repository key
    print_info "Adding PostgreSQL repository..."
    if ! run_with_error_check \
        "sudo apt-get install -y wget ca-certificates" \
        "Failed to install prerequisites"; then
        return 1
    fi

    # Add PostgreSQL repository
    if ! run_with_error_check \
        "wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -" \
        "Failed to add PostgreSQL GPG key"; then
        # Try alternate method
        wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo tee /etc/apt/trusted.gpg.d/postgresql.asc > /dev/null
    fi

    local distro=$(lsb_release -cs 2>/dev/null || echo "jammy")
    echo "deb http://apt.postgresql.org/pub/repos/apt ${distro}-pgdg main" | \
        sudo tee /etc/apt/sources.list.d/pgdg.list > /dev/null

    # Install PostgreSQL
    print_info "Installing PostgreSQL $PG_VERSION..."
    sudo apt-get update >> "$INSTALL_LOG" 2>&1

    if install_package "postgresql-$PG_VERSION"; then
        install_package "postgresql-contrib-$PG_VERSION"
        install_package "postgresql-client-$PG_VERSION"
        print_success "PostgreSQL installed successfully"
        return 0
    else
        print_error "Failed to install PostgreSQL"
        return 1
    fi
}

install_postgresql_fedora() {
    print_header "Installing PostgreSQL on Fedora/RHEL"

    print_info "Installing PostgreSQL $PG_VERSION..."
    if install_package "postgresql$PG_VERSION-server"; then
        install_package "postgresql$PG_VERSION-contrib"
        install_package "postgresql$PG_VERSION"

        # Initialize database
        print_info "Initializing PostgreSQL database..."
        sudo /usr/pgsql-$PG_VERSION/bin/postgresql-$PG_VERSION-setup initdb >> "$INSTALL_LOG" 2>&1

        print_success "PostgreSQL installed successfully"
        return 0
    else
        print_error "Failed to install PostgreSQL"
        return 1
    fi
}

install_postgresql() {
    local distro=$(get_distro)

    case "$distro" in
        ubuntu|debian)
            install_postgresql_ubuntu
            ;;
        fedora|rhel|centos)
            install_postgresql_fedora
            ;;
        *)
            print_error "Unsupported distribution: $distro"
            print_info "Please install PostgreSQL manually:"
            print_info "  Ubuntu/Debian: sudo apt-get install postgresql"
            print_info "  Fedora/RHEL: sudo dnf install postgresql-server"
            return 1
            ;;
    esac
}

###############################################################################
# PostgreSQL Configuration Functions
###############################################################################

configure_postgresql_network() {
    print_header "Configuring PostgreSQL for Network Access"

    local pg_data_dir=$(sudo -u postgres psql -t -P format=unaligned -c 'SHOW data_directory;' 2>/dev/null | tr -d ' ')

    if [ -z "$pg_data_dir" ]; then
        # Try common locations
        for dir in /var/lib/postgresql/$PG_VERSION/main /var/lib/pgsql/$PG_VERSION/data /etc/postgresql/$PG_VERSION/main; do
            if [ -d "$dir" ]; then
                pg_data_dir=$dir
                break
            fi
        done
    fi

    if [ -z "$pg_data_dir" ]; then
        print_error "Could not locate PostgreSQL data directory"
        return 1
    fi

    print_info "PostgreSQL data directory: $pg_data_dir"

    # Backup configuration files
    backup_file "$pg_data_dir/postgresql.conf"
    backup_file "$pg_data_dir/pg_hba.conf"

    # Configure postgresql.conf for network access
    print_info "Configuring postgresql.conf..."
    sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$pg_data_dir/postgresql.conf" 2>/dev/null || \
    sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '*'/" "$pg_data_dir/postgresql.conf"

    sudo sed -i "s/#port = 5432/port = $PG_PORT/" "$pg_data_dir/postgresql.conf" 2>/dev/null || \
    sudo sed -i "s/port = .*/port = $PG_PORT/" "$pg_data_dir/postgresql.conf"

    # Configure pg_hba.conf for remote access
    print_info "Configuring pg_hba.conf..."

    # Add host-based authentication for all networks (adjust for production)
    if ! sudo grep -q "host.*all.*all.*0.0.0.0/0.*md5" "$pg_data_dir/pg_hba.conf"; then
        echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a "$pg_data_dir/pg_hba.conf" > /dev/null
        echo "host    all             all             ::/0                    md5" | sudo tee -a "$pg_data_dir/pg_hba.conf" > /dev/null
    fi

    print_success "PostgreSQL configured for network access"

    # Restart PostgreSQL
    print_info "Restarting PostgreSQL service..."
    if sudo systemctl restart postgresql >> "$INSTALL_LOG" 2>&1; then
        print_success "PostgreSQL restarted successfully"
        sleep 2
        return 0
    else
        print_error "Failed to restart PostgreSQL"
        return 1
    fi
}

###############################################################################
# Database Setup Functions
###############################################################################

create_database_and_user() {
    print_header "Creating Database and User"

    print_info "Creating database: $PG_DATABASE"
    print_info "Creating user: $PG_USER"

    # Create user
    if sudo -u postgres psql -c "CREATE USER $PG_USER WITH PASSWORD '$PG_PASSWORD';" >> "$INSTALL_LOG" 2>&1; then
        print_success "User created: $PG_USER"
    else
        print_warning "User may already exist: $PG_USER"
    fi

    # Create database
    if sudo -u postgres psql -c "CREATE DATABASE $PG_DATABASE OWNER $PG_USER;" >> "$INSTALL_LOG" 2>&1; then
        print_success "Database created: $PG_DATABASE"
    else
        print_warning "Database may already exist: $PG_DATABASE"
    fi

    # Grant privileges
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $PG_DATABASE TO $PG_USER;" >> "$INSTALL_LOG" 2>&1
    sudo -u postgres psql -d "$PG_DATABASE" -c "GRANT ALL ON SCHEMA public TO $PG_USER;" >> "$INSTALL_LOG" 2>&1

    print_success "Database and user configured"
    return 0
}

initialize_database_schema() {
    print_header "Initializing Database Schema"

    local schema_file="$PROJECT_ROOT/backend/setup_database.sql"

    if [ ! -f "$schema_file" ]; then
        print_error "Schema file not found: $schema_file"
        return 1
    fi

    print_info "Executing schema file: $schema_file"

    # Set password for connection
    export PGPASSWORD="$PG_PASSWORD"

    if psql -h localhost -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -f "$schema_file" >> "$INSTALL_LOG" 2>&1; then
        print_success "Database schema initialized"
        unset PGPASSWORD
        return 0
    else
        print_error "Failed to initialize database schema"
        unset PGPASSWORD
        return 1
    fi
}

###############################################################################
# Validation Functions
###############################################################################

validate_postgresql_installation() {
    print_header "Validating PostgreSQL Installation"

    # Check if PostgreSQL is running
    if ! service_running postgresql; then
        print_error "PostgreSQL service is not running"
        return 1
    fi
    print_success "PostgreSQL service is running"

    # Check network connectivity
    if check_connectivity "localhost" "$PG_PORT"; then
        print_success "PostgreSQL is listening on port $PG_PORT"
    else
        print_error "Cannot connect to PostgreSQL on port $PG_PORT"
        return 1
    fi

    # Test database connection
    export PGPASSWORD="$PG_PASSWORD"
    if psql -h localhost -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -c "SELECT version();" >> "$INSTALL_LOG" 2>&1; then
        print_success "Database connection successful"

        # Check table count
        local table_count=$(psql -h localhost -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
        print_success "Database contains $table_count tables"

        unset PGPASSWORD
        return 0
    else
        print_error "Failed to connect to database"
        unset PGPASSWORD
        return 1
    fi
}

###############################################################################
# Remote PostgreSQL Configuration
###############################################################################

configure_remote_postgresql() {
    print_header "Configuring Remote PostgreSQL Connection"

    print_info "Testing connection to remote PostgreSQL..."

    export PGPASSWORD="$PG_PASSWORD"
    if psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -c "SELECT 1;" >> "$INSTALL_LOG" 2>&1; then
        print_success "Successfully connected to remote PostgreSQL"
        unset PGPASSWORD
        return 0
    else
        print_warning "Cannot connect to remote PostgreSQL"
        print_info "Please ensure:"
        print_info "  1. PostgreSQL is running on $PG_HOST:$PG_PORT"
        print_info "  2. Database $PG_DATABASE exists"
        print_info "  3. User $PG_USER has access"
        print_info "  4. Firewall allows connections"
        print_info "  5. pg_hba.conf allows remote connections"
        unset PGPASSWORD

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
    log_message "INFO" "PostgreSQL installation module started"

    # Determine if local or remote installation
    if [ "$1" = "--remote" ]; then
        PG_REMOTE=true
        print_info "Configuring for remote PostgreSQL server"
    else
        print_info "Configuring for local PostgreSQL installation"
    fi

    # Get PostgreSQL configuration
    print_header "PostgreSQL Configuration"

    if [ "$PG_REMOTE" = true ]; then
        PG_HOST=$(prompt_with_validation "PostgreSQL server IP address" "192.168.100.30" validate_ip)
    else
        PG_HOST="localhost"
    fi

    PG_PORT=$(prompt_with_validation "PostgreSQL port" "5432" validate_port)
    PG_DATABASE=$(prompt_with_validation "Database name" "healthcare_security")
    PG_USER=$(prompt_with_validation "Database user" "healthcare_user")

    print_question "Database password (will not echo):"
    read -s PG_PASSWORD
    echo ""

    if [ -z "$PG_PASSWORD" ]; then
        print_warning "No password provided, generating secure password..."
        PG_PASSWORD=$(generate_password 16)
        print_success "Generated password: $PG_PASSWORD"
        print_warning "Please save this password securely!"
    fi

    # Save configuration for later use
    cat > "$SCRIPT_DIR/.pg_config" << EOF
PG_HOST=$PG_HOST
PG_PORT=$PG_PORT
PG_DATABASE=$PG_DATABASE
PG_USER=$PG_USER
PG_PASSWORD=$PG_PASSWORD
EOF
    chmod 600 "$SCRIPT_DIR/.pg_config"

    # Execute installation steps
    if [ "$PG_REMOTE" = false ]; then
        # Local installation
        if ! check_postgresql_installed; then
            if confirm_action "PostgreSQL not found. Install it now?"; then
                if ! install_postgresql; then
                    exit_error "PostgreSQL installation failed"
                fi
            else
                exit_error "PostgreSQL installation cancelled by user"
            fi
        fi

        # Configure PostgreSQL for network access
        if ! configure_postgresql_network; then
            print_warning "Failed to configure network access"
        fi

        # Create database and user
        if ! create_database_and_user; then
            exit_error "Failed to create database and user"
        fi

        # Initialize schema
        if ! initialize_database_schema; then
            exit_error "Failed to initialize database schema"
        fi

        # Validate installation
        if ! validate_postgresql_installation; then
            exit_error "PostgreSQL validation failed"
        fi
    else
        # Remote installation - just test connection
        if ! configure_remote_postgresql; then
            exit_error "Failed to configure remote PostgreSQL"
        fi
    fi

    print_header "PostgreSQL Installation Complete"
    print_success "PostgreSQL is configured and ready"
    print_info "Host: $PG_HOST"
    print_info "Port: $PG_PORT"
    print_info "Database: $PG_DATABASE"
    print_info "User: $PG_USER"

    log_message "SUCCESS" "PostgreSQL installation completed successfully"

    return 0
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    main "$@"
fi
