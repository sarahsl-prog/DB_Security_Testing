#!/bin/bash
###############################################################################
# Healthcare Security Research Platform - Installation Validation Module
#
# This module validates the complete installation:
# - Tests database connectivity
# - Tests LLM service connectivity
# - Tests backend API
# - Runs backend test suite
# - Generates validation report
#
# Usage: ./validate_installation.sh
###############################################################################

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common_utils.sh"

# Import configurations
[ -f "$SCRIPT_DIR/.pg_config" ] && source "$SCRIPT_DIR/.pg_config"
[ -f "$SCRIPT_DIR/.ollama_config" ] && source "$SCRIPT_DIR/.ollama_config"
[ -f "$SCRIPT_DIR/.app_config" ] && source "$SCRIPT_DIR/.app_config"

# Validation results
VALIDATION_RESULTS=()

###############################################################################
# Test Result Tracking
###############################################################################

add_test_result() {
    local test_name="$1"
    local status="$2"
    local message="$3"

    VALIDATION_RESULTS+=("$test_name|$status|$message")

    if [ "$status" = "PASS" ]; then
        print_success "$test_name: $message"
    elif [ "$status" = "FAIL" ]; then
        print_error "$test_name: $message"
    else
        print_warning "$test_name: $message"
    fi
}

###############################################################################
# Database Validation
###############################################################################

test_database_connectivity() {
    print_header "Testing Database Connectivity"

    local host=${PG_HOST:-localhost}
    local port=${PG_PORT:-5432}
    local database=${PG_DATABASE:-healthcare_security}
    local user=${PG_USER:-healthcare_user}
    local password=${PG_PASSWORD}

    print_info "Testing connection to PostgreSQL..."
    print_info "Host: $host:$port"
    print_info "Database: $database"

    export PGPASSWORD="$password"

    if psql -h "$host" -p "$port" -U "$user" -d "$database" -c "SELECT 1;" >> "$INSTALL_LOG" 2>&1; then
        add_test_result "Database Connection" "PASS" "Connected to $host:$port"

        # Check tables
        local table_count=$(psql -h "$host" -p "$port" -U "$user" -d "$database" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

        if [ "$table_count" -ge 5 ]; then
            add_test_result "Database Schema" "PASS" "$table_count tables found"
        else
            add_test_result "Database Schema" "WARN" "Only $table_count tables found (expected 5+)"
        fi

        # Check sample data
        local patient_count=$(psql -h "$host" -p "$port" -U "$user" -d "$database" -t -c "SELECT COUNT(*) FROM patients;" 2>/dev/null | tr -d ' ')
        if [ "$patient_count" -ge 10 ]; then
            add_test_result "Sample Data" "PASS" "$patient_count patients in database"
        else
            add_test_result "Sample Data" "WARN" "Only $patient_count patients found"
        fi
    else
        add_test_result "Database Connection" "FAIL" "Cannot connect to $host:$port"
    fi

    unset PGPASSWORD
}

###############################################################################
# LLM Service Validation
###############################################################################

test_llm_connectivity() {
    print_header "Testing LLM Service Connectivity"

    local host=${OLLAMA_HOST:-localhost}
    local port=${OLLAMA_PORT:-11434}
    local model=${OLLAMA_MODEL:-llama3.1}

    print_info "Testing connection to Ollama..."
    print_info "Host: $host:$port"
    print_info "Model: $model"

    # Test API endpoint
    if curl -s --max-time 5 "http://$host:$port/api/tags" > /dev/null 2>&1; then
        add_test_result "LLM Service" "PASS" "Ollama is responding at $host:$port"

        # Check if model is available
        local api_response=$(curl -s "http://$host:$port/api/tags" 2>/dev/null)
        if echo "$api_response" | grep -q "\"name\":\"$model\""; then
            add_test_result "LLM Model" "PASS" "Model $model is available"
        else
            add_test_result "LLM Model" "WARN" "Model $model not found"
        fi
    else
        add_test_result "LLM Service" "FAIL" "Cannot connect to Ollama at $host:$port"
    fi
}

###############################################################################
# Backend API Validation
###############################################################################

test_backend_api() {
    print_header "Testing Backend API"

    local host=${BACKEND_PUBLIC_HOST:-localhost}
    local port=${API_PORT:-5000}

    print_info "Starting backend server for testing..."

    # Start backend in background
    cd "$PROJECT_ROOT/backend"
    source venv/bin/activate

    # Start Flask app in background
    python3 app.py >> "$INSTALL_LOG" 2>&1 &
    local backend_pid=$!

    # Wait for backend to start
    print_info "Waiting for backend to start..."
    sleep 5

    # Test health endpoint
    print_info "Testing /api/health endpoint..."
    local health_response=$(curl -s "http://$host:$port/api/health" 2>/dev/null)

    if echo "$health_response" | grep -q "healthy"; then
        add_test_result "Backend Health" "PASS" "Backend is healthy"

        # Test login endpoint
        print_info "Testing /api/login endpoint..."
        local login_response=$(curl -s -X POST "http://$host:$port/api/login" \
            -H "Content-Type: application/json" \
            -d '{"username":"admin","password":"password123"}' 2>/dev/null)

        if echo "$login_response" | grep -q "token"; then
            add_test_result "Backend Auth" "PASS" "Authentication working"
        else
            add_test_result "Backend Auth" "FAIL" "Authentication failed"
        fi
    else
        add_test_result "Backend Health" "FAIL" "Backend not responding"
    fi

    # Stop backend
    kill $backend_pid 2>/dev/null
    deactivate
    cd "$SCRIPT_DIR"
}

###############################################################################
# Test Suite Execution
###############################################################################

run_backend_tests() {
    print_header "Running Backend Test Suite"

    cd "$PROJECT_ROOT/backend"
    source venv/bin/activate

    print_info "Running pytest..."

    # Run a subset of critical tests
    if pytest tests/test_database.py -v >> "$INSTALL_LOG" 2>&1; then
        add_test_result "Database Tests" "PASS" "All database tests passed"
    else
        add_test_result "Database Tests" "FAIL" "Some database tests failed"
    fi

    if pytest tests/test_llm_client.py -v >> "$INSTALL_LOG" 2>&1; then
        add_test_result "LLM Tests" "PASS" "All LLM tests passed"
    else
        add_test_result "LLM Tests" "WARN" "Some LLM tests failed"
    fi

    deactivate
    cd "$SCRIPT_DIR"
}

###############################################################################
# System Resource Check
###############################################################################

check_system_resources() {
    print_header "Checking System Resources"

    # Check disk space
    local free_space=$(df -BG "$PROJECT_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$free_space" -ge 5 ]; then
        add_test_result "Disk Space" "PASS" "${free_space}GB available"
    else
        add_test_result "Disk Space" "WARN" "Only ${free_space}GB available"
    fi

    # Check memory
    local free_ram=$(free -g | awk '/^Mem:/{print $7}')
    if [ "$free_ram" -ge 2 ]; then
        add_test_result "Memory" "PASS" "${free_ram}GB free"
    else
        add_test_result "Memory" "WARN" "Only ${free_ram}GB free"
    fi

    # Check CPU load
    local cpu_load=$(uptime | awk -F'load average:' '{print $2}' | cut -d, -f1 | tr -d ' ')
    add_test_result "CPU Load" "INFO" "Load average: $cpu_load"
}

###############################################################################
# Configuration Validation
###############################################################################

validate_configuration() {
    print_header "Validating Configuration Files"

    # Check backend .env
    if [ -f "$PROJECT_ROOT/backend/.env" ]; then
        add_test_result "Backend Config" "PASS" ".env file exists"

        # Check for required variables
        if grep -q "SECRET_KEY" "$PROJECT_ROOT/backend/.env" && \
           grep -q "DB_HOST" "$PROJECT_ROOT/backend/.env" && \
           grep -q "LLM_HOST" "$PROJECT_ROOT/backend/.env"; then
            add_test_result "Backend Config Content" "PASS" "Required variables present"
        else
            add_test_result "Backend Config Content" "WARN" "Some variables may be missing"
        fi
    else
        add_test_result "Backend Config" "FAIL" ".env file not found"
    fi

    # Check frontend .env
    if [ -f "$PROJECT_ROOT/frontend/.env" ]; then
        add_test_result "Frontend Config" "PASS" ".env file exists"
    else
        add_test_result "Frontend Config" "FAIL" ".env file not found"
    fi

    # Check log directories
    if [ -d "$PROJECT_ROOT/backend/logs" ]; then
        add_test_result "Log Directory" "PASS" "Backend logs directory exists"
    else
        add_test_result "Log Directory" "WARN" "Backend logs directory not found"
    fi
}

###############################################################################
# Generate Validation Summary
###############################################################################

generate_validation_summary() {
    print_header "Validation Summary"

    local pass_count=0
    local fail_count=0
    local warn_count=0
    local total_count=${#VALIDATION_RESULTS[@]}

    echo ""
    echo "Test Results:"
    echo "============================================"

    for result in "${VALIDATION_RESULTS[@]}"; do
        IFS='|' read -r test_name status message <<< "$result"

        case "$status" in
            PASS)
                echo -e "${GREEN}[✓] $test_name${NC}: $message"
                ((pass_count++))
                ;;
            FAIL)
                echo -e "${RED}[✗] $test_name${NC}: $message"
                ((fail_count++))
                ;;
            WARN)
                echo -e "${YELLOW}[!] $test_name${NC}: $message"
                ((warn_count++))
                ;;
            INFO)
                echo -e "${BLUE}[i] $test_name${NC}: $message"
                ;;
        esac
    done

    echo ""
    echo "============================================"
    echo -e "${GREEN}Passed:${NC} $pass_count"
    echo -e "${RED}Failed:${NC} $fail_count"
    echo -e "${YELLOW}Warnings:${NC} $warn_count"
    echo -e "Total Tests: $total_count"
    echo ""

    if [ $fail_count -eq 0 ]; then
        print_success "Validation completed successfully!"
        return 0
    else
        print_warning "Validation completed with $fail_count failures"
        return 1
    fi
}

###############################################################################
# Main Validation Flow
###############################################################################

main() {
    print_banner
    log_message "INFO" "Installation validation started"

    print_info "This will validate all installed components..."
    echo ""

    # Run all validation tests
    test_database_connectivity
    test_llm_connectivity
    check_system_resources
    validate_configuration

    # Optional: Run backend tests
    if confirm_action "Would you like to run the backend test suite? (may take a few minutes)"; then
        run_backend_tests
    fi

    # Optional: Test backend API (starts server temporarily)
    if confirm_action "Would you like to test the backend API? (will start server temporarily)"; then
        test_backend_api
    fi

    # Generate summary
    if generate_validation_summary; then
        log_message "SUCCESS" "Validation completed successfully"
        return 0
    else
        log_message "WARNING" "Validation completed with failures"
        return 1
    fi
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    main "$@"
fi
