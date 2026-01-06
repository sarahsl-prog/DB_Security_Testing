#!/bin/bash
###############################################################################
# Healthcare Security Research Platform - Common Utilities
#
# This library provides shared functions for all installation modules:
# - Logging functions
# - Input validation
# - Color output
# - Error handling
# - System checks
#
# Usage: source common_utils.sh
###############################################################################

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
INSTALL_LOG="$LOG_DIR/install_$(date +%Y%m%d_%H%M%S).log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

###############################################################################
# Logging Functions
###############################################################################

# Log message to file and optionally to console
# Usage: log_message "INFO" "message text" [true|false]
log_message() {
    local level="$1"
    local message="$2"
    local to_console="${3:-true}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Write to log file
    echo "[$timestamp] [$level] $message" >> "$INSTALL_LOG"

    # Optionally write to console
    if [ "$to_console" = "true" ]; then
        case "$level" in
            "ERROR")
                echo -e "${RED}[$timestamp] [$level] $message${NC}"
                ;;
            "SUCCESS")
                echo -e "${GREEN}[$timestamp] [$level] $message${NC}"
                ;;
            "WARNING")
                echo -e "${YELLOW}[$timestamp] [$level] $message${NC}"
                ;;
            "INFO")
                echo -e "${BLUE}[$timestamp] [$level] $message${NC}"
                ;;
            *)
                echo "[$timestamp] [$level] $message"
                ;;
        esac
    fi
}

###############################################################################
# Display Functions
###############################################################################

print_banner() {
    clear
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}   Healthcare Security Research Platform - Installation${NC}"
    echo -e "${BLUE}   Modular Installation System${NC}"
    echo -e "${BLUE}================================================================${NC}\n"
    log_message "INFO" "Installation started" false
}

print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}\n"
    log_message "INFO" "$1" false
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    log_message "SUCCESS" "$1" false
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    log_message "ERROR" "$1" false
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
    log_message "WARNING" "$1" false
}

print_info() {
    echo -e "${BLUE}● $1${NC}"
    log_message "INFO" "$1" false
}

print_question() {
    echo -e "${MAGENTA}? $1${NC}"
}

###############################################################################
# Validation Functions
###############################################################################

# Validate IP address format
# Usage: validate_ip "192.168.1.1"
# Returns: 0 if valid, 1 if invalid
validate_ip() {
    local ip=$1
    local valid_ip_regex="^([0-9]{1,3}\.){3}[0-9]{1,3}$"

    if [[ ! $ip =~ $valid_ip_regex ]]; then
        return 1
    fi

    # Check each octet
    IFS='.' read -ra ADDR <<< "$ip"
    for i in "${ADDR[@]}"; do
        if [ "$i" -gt 255 ] || [ "$i" -lt 0 ]; then
            return 1
        fi
    done

    return 0
}

# Validate domain name
# Usage: validate_domain "example.com"
# Returns: 0 if valid, 1 if invalid
validate_domain() {
    local domain=$1
    local valid_domain_regex="^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"

    if [[ $domain =~ $valid_domain_regex ]]; then
        return 0
    else
        return 1
    fi
}

# Validate port number
# Usage: validate_port "5000"
# Returns: 0 if valid, 1 if invalid
validate_port() {
    local port=$1
    if [[ "$port" =~ ^[0-9]+$ ]] && [ "$port" -ge 1 ] && [ "$port" -le 65535 ]; then
        return 0
    else
        return 1
    fi
}

# Validate hostname or IP
# Usage: validate_host "192.168.1.1" or validate_host "localhost"
# Returns: 0 if valid, 1 if invalid
validate_host() {
    local host=$1

    # Check if it's localhost
    if [ "$host" = "localhost" ] || [ "$host" = "127.0.0.1" ] || [ "$host" = "0.0.0.0" ]; then
        return 0
    fi

    # Check if it's a valid IP
    if validate_ip "$host"; then
        return 0
    fi

    # Check if it's a valid domain
    if validate_domain "$host"; then
        return 0
    fi

    return 1
}

###############################################################################
# Input Functions
###############################################################################

# Prompt for input with validation
# Usage: result=$(prompt_with_validation "Enter IP" "192.168.1.1" validate_ip)
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

# Prompt for yes/no confirmation
# Usage: if confirm_action "Continue?"; then ... fi
# Returns: 0 for yes, 1 for no
confirm_action() {
    local prompt="${1:-Continue?}"
    local response

    while true; do
        read -p "$(echo -e "${YELLOW}${prompt} (y/n): ${NC}")" response
        case "$response" in
            [Yy]|[Yy][Ee][Ss])
                return 0
                ;;
            [Nn]|[Nn][Oo])
                return 1
                ;;
            *)
                print_error "Please answer yes or no."
                ;;
        esac
    done
}

###############################################################################
# System Check Functions
###############################################################################

# Check if command exists
# Usage: if command_exists "python3"; then ... fi
command_exists() {
    command -v "$1" &> /dev/null
}

# Check if service is running
# Usage: if service_running "postgresql"; then ... fi
service_running() {
    local service=$1
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Check network connectivity to host:port
# Usage: if check_connectivity "192.168.1.1" "5432"; then ... fi
check_connectivity() {
    local host=$1
    local port=$2
    local timeout=5

    log_message "INFO" "Checking connectivity to $host:$port" false

    if timeout "$timeout" bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Get OS type
# Usage: os_type=$(get_os_type)
get_os_type() {
    if [[ -f /proc/version ]]; then
        if grep -qi microsoft /proc/version; then
            echo "WSL"
        else
            echo "Linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macOS"
    else
        echo "Unknown"
    fi
}

# Get OS distribution (for Linux)
# Usage: distro=$(get_distro)
get_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    else
        echo "unknown"
    fi
}

# Check minimum Python version
# Usage: if check_python_version "3.8"; then ... fi
check_python_version() {
    local required_version=$1

    if ! command_exists python3; then
        return 1
    fi

    local python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
        return 0
    else
        return 1
    fi
}

###############################################################################
# Security Functions
###############################################################################

# Generate secure random key
# Usage: secret=$(generate_secret_key)
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || \
    openssl rand -base64 32 2>/dev/null || \
    head -c 32 /dev/urandom | base64
}

# Generate secure password
# Usage: password=$(generate_password 16)
generate_password() {
    local length=${1:-16}
    python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range($length)))" 2>/dev/null || \
    openssl rand -base64 $length 2>/dev/null || \
    head -c $length /dev/urandom | base64 | tr -d '=' | head -c $length
}

###############################################################################
# Error Handling Functions
###############################################################################

# Exit with error message
# Usage: exit_error "Failed to install package"
exit_error() {
    local message=$1
    print_error "$message"
    log_message "ERROR" "Installation failed: $message" false
    echo -e "\n${RED}Installation failed. Check log file: $INSTALL_LOG${NC}"
    exit 1
}

# Handle errors in functions
# Usage: run_with_error_check "command" "Error message"
run_with_error_check() {
    local command=$1
    local error_msg=$2

    log_message "INFO" "Executing: $command" false

    if eval "$command" >> "$INSTALL_LOG" 2>&1; then
        return 0
    else
        local exit_code=$?
        print_error "$error_msg (Exit code: $exit_code)"
        log_message "ERROR" "$error_msg (Exit code: $exit_code)" false
        return $exit_code
    fi
}

###############################################################################
# File Operations
###############################################################################

# Create directory if it doesn't exist
# Usage: ensure_directory "/path/to/dir"
ensure_directory() {
    local dir=$1

    if [ ! -d "$dir" ]; then
        log_message "INFO" "Creating directory: $dir" false
        if mkdir -p "$dir"; then
            print_success "Created directory: $dir"
            return 0
        else
            print_error "Failed to create directory: $dir"
            return 1
        fi
    fi
    return 0
}

# Backup file if it exists
# Usage: backup_file "/path/to/file"
backup_file() {
    local file=$1

    if [ -f "$file" ]; then
        local backup="${file}.backup.$(date +%Y%m%d_%H%M%S)"
        log_message "INFO" "Backing up $file to $backup" false
        if cp "$file" "$backup"; then
            print_success "Backed up: $file"
            return 0
        else
            print_warning "Failed to backup: $file"
            return 1
        fi
    fi
    return 0
}

###############################################################################
# Package Management Functions
###############################################################################

# Install system package (auto-detects package manager)
# Usage: install_package "postgresql"
install_package() {
    local package=$1
    local distro=$(get_distro)

    print_info "Installing package: $package"
    log_message "INFO" "Installing package: $package on $distro" false

    case "$distro" in
        ubuntu|debian)
            if sudo apt-get update >> "$INSTALL_LOG" 2>&1 && \
               sudo apt-get install -y "$package" >> "$INSTALL_LOG" 2>&1; then
                print_success "Installed: $package"
                return 0
            fi
            ;;
        fedora|rhel|centos)
            if sudo dnf install -y "$package" >> "$INSTALL_LOG" 2>&1; then
                print_success "Installed: $package"
                return 0
            fi
            ;;
        arch)
            if sudo pacman -S --noconfirm "$package" >> "$INSTALL_LOG" 2>&1; then
                print_success "Installed: $package"
                return 0
            fi
            ;;
        *)
            print_warning "Unknown distribution. Please install $package manually."
            return 1
            ;;
    esac

    print_error "Failed to install: $package"
    return 1
}

###############################################################################
# Version Comparison
###############################################################################

# Compare versions
# Usage: if version_gt "2.0" "1.5"; then ... fi
version_gt() {
    test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"
}

version_ge() {
    test "$(printf '%s\n' "$@" | sort -V | head -n 1)" = "$2"
}

###############################################################################
# Initialization
###############################################################################

log_message "INFO" "Common utilities library loaded" false
log_message "INFO" "OS Type: $(get_os_type)" false
log_message "INFO" "Distribution: $(get_distro)" false
log_message "INFO" "Log file: $INSTALL_LOG" false
