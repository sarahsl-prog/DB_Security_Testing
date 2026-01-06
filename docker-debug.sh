#!/bin/bash
###############################################################################
# Docker Deployment Troubleshooting Script
# Healthcare Security Research Platform
#
# This script helps diagnose Docker deployment issues
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Determine docker compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

clear
print_header "Docker Deployment Troubleshooting"

echo "This script will help diagnose issues with your Docker deployment."
echo ""

# 1. Check Docker is running
print_header "1. Checking Docker Status"

if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running!"
    echo ""
    echo "Solutions:"
    echo "  • Docker Desktop: Start the application"
    echo "  • Linux: sudo systemctl start docker"
    echo "  • Colima: colima start"
    echo ""
    exit 1
else
    print_success "Docker daemon is running"
    docker --version
fi

# 2. Check docker-compose.yml
print_header "2. Checking Configuration Files"

if [ ! -f docker-compose.yml ]; then
    print_error "docker-compose.yml not found!"
    exit 1
else
    print_success "docker-compose.yml found"
fi

if [ ! -f .env ]; then
    print_warning ".env file not found"
    echo "Creating from .env.docker template..."
    if [ -f .env.docker ]; then
        cp .env.docker .env
        print_success "Created .env from template"
    else
        print_error ".env.docker template not found!"
    fi
else
    print_success ".env file found"
fi

# 3. Validate docker-compose.yml
print_header "3. Validating Docker Compose Configuration"

if $DOCKER_COMPOSE config &> /dev/null; then
    print_success "docker-compose.yml is valid"
else
    print_error "docker-compose.yml has errors:"
    $DOCKER_COMPOSE config
    exit 1
fi

# 4. Check container status
print_header "4. Checking Container Status"

echo "Running containers:"
echo ""
$DOCKER_COMPOSE ps
echo ""

# Check if containers are running
RUNNING_CONTAINERS=$($DOCKER_COMPOSE ps --services --filter "status=running" 2>/dev/null | wc -l)
EXPECTED_CONTAINERS=4  # postgres, ollama, backend, frontend

echo ""
if [ "$RUNNING_CONTAINERS" -eq "$EXPECTED_CONTAINERS" ]; then
    print_success "All $EXPECTED_CONTAINERS containers are running"
else
    print_warning "Only $RUNNING_CONTAINERS of $EXPECTED_CONTAINERS containers are running"
fi

# 5. Check individual services
print_header "5. Checking Individual Services"

check_service() {
    local service=$1
    local container=$2

    echo ""
    echo -e "${BLUE}Checking $service...${NC}"

    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        print_success "$service container is running"

        # Check health status
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null || echo "no-healthcheck")

        if [ "$HEALTH" = "healthy" ]; then
            print_success "$service is healthy"
        elif [ "$HEALTH" = "no-healthcheck" ]; then
            print_info "$service has no health check configured"
        else
            print_warning "$service health: $HEALTH"
        fi
    else
        print_error "$service container is not running"

        echo ""
        echo "Last 20 lines of logs:"
        $DOCKER_COMPOSE logs --tail=20 $service
    fi
}

check_service "PostgreSQL" "healthcare_db"
check_service "Ollama LLM" "healthcare_llm"
check_service "Backend API" "healthcare_backend"
check_service "Frontend" "healthcare_frontend"

# 6. Check ports
print_header "6. Checking Port Availability"

check_port() {
    local port=$1
    local service=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":$port "; then
        print_success "Port $port ($service) is in use"
    else
        print_warning "Port $port ($service) is not listening"
    fi
}

if command -v lsof >/dev/null 2>&1 || command -v netstat >/dev/null 2>&1; then
    check_port 5432 "PostgreSQL"
    check_port 11434 "Ollama"
    check_port 5000 "Backend"
    check_port 5173 "Frontend"
else
    print_info "lsof/netstat not available, skipping port check"
fi

# 7. Test connectivity
print_header "7. Testing Service Connectivity"

test_endpoint() {
    local url=$1
    local name=$2

    if curl -sf "$url" > /dev/null 2>&1; then
        print_success "$name is responding"
    else
        print_error "$name is not responding at $url"
    fi
}

test_endpoint "http://localhost:5000/api/health" "Backend API"
test_endpoint "http://localhost:5173" "Frontend"
test_endpoint "http://localhost:11434" "Ollama"

# 8. Check Docker resources
print_header "8. Checking Docker Resources"

echo "Docker system info:"
docker system df
echo ""

# 9. Show recent logs
print_header "9. Recent Logs from Each Service"

show_logs() {
    local service=$1
    echo ""
    echo -e "${BLUE}Last 10 lines from $service:${NC}"
    $DOCKER_COMPOSE logs --tail=10 $service 2>&1 | sed 's/^/  /'
}

show_logs "postgres"
show_logs "ollama"
show_logs "backend"
show_logs "frontend"

# 10. Recommendations
print_header "10. Troubleshooting Recommendations"

echo "Based on the checks above, here are common solutions:"
echo ""
echo "🔧 If containers aren't starting:"
echo "   1. Check logs: $DOCKER_COMPOSE logs -f <service-name>"
echo "   2. Rebuild: $DOCKER_COMPOSE up -d --build"
echo "   3. Fresh start: $DOCKER_COMPOSE down -v && $DOCKER_COMPOSE up -d"
echo ""
echo "🔧 If services are unhealthy:"
echo "   1. Wait longer (Ollama needs ~60 seconds, backend needs ~40 seconds)"
echo "   2. Check dependencies: postgres and ollama must be healthy first"
echo "   3. Restart: $DOCKER_COMPOSE restart <service-name>"
echo ""
echo "🔧 If ports are in use:"
echo "   1. Stop conflicting services"
echo "   2. Change ports in .env file (BACKEND_PORT, FRONTEND_PORT, etc.)"
echo "   3. Restart: $DOCKER_COMPOSE down && $DOCKER_COMPOSE up -d"
echo ""
echo "🔧 To view detailed logs:"
echo "   $DOCKER_COMPOSE logs -f <service-name>"
echo ""
echo "🔧 To restart everything:"
echo "   $DOCKER_COMPOSE down && $DOCKER_COMPOSE up -d"
echo ""
echo "🔧 To completely reset (WARNING: deletes data):"
echo "   $DOCKER_COMPOSE down -v && $DOCKER_COMPOSE up -d"
echo ""

print_header "Troubleshooting Complete"

echo "For more help:"
echo "  • Documentation: DOCKER_QUICKSTART.md"
echo "  • View logs: $DOCKER_COMPOSE logs -f"
echo "  • Check status: $DOCKER_COMPOSE ps"
echo ""
