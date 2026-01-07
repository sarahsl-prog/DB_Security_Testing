#!/bin/bash
###############################################################################
# Healthcare Security Research Platform - Simple Deployment Script
#
# This script helps you choose and execute the best deployment option
# for your environment.
#
# Usage: ./deploy.sh
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
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

check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_warning "$1 is not installed"
        return 1
    fi
}

# Detect OS type
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        OS="rhel"
    elif [ "$(uname)" == "Darwin" ]; then
        OS="macos"
    else
        OS="unknown"
    fi
    echo $OS
}

# Install Python and pip
install_python() {
    local os=$(detect_os)

    print_info "Attempting to install Python..."
    echo ""

    case $os in
        ubuntu|debian)
            print_info "Detected Ubuntu/Debian - installing Python..."
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        fedora|rhel|centos)
            print_info "Detected Fedora/RHEL/CentOS - installing Python..."
            sudo dnf install -y python3 python3-pip
            ;;
        arch|manjaro)
            print_info "Detected Arch/Manjaro - installing Python..."
            sudo pacman -S --noconfirm python python-pip
            ;;
        macos)
            if command -v brew &> /dev/null; then
                print_info "Detected macOS with Homebrew - installing Python..."
                brew install python3
            else
                print_error "Homebrew not found. Please install from https://brew.sh"
                return 1
            fi
            ;;
        *)
            print_error "Unsupported OS. Please install Python 3.12+ manually."
            return 1
            ;;
    esac

    # Verify installation
    if command -v python3 &> /dev/null; then
        print_success "Python installed successfully!"
        python3 --version
        return 0
    else
        print_error "Python installation failed"
        return 1
    fi
}

# Main script
clear
print_header "Healthcare Security Research Platform"
echo ""
echo "Welcome! This script will help you deploy the application."
echo ""

# Check what's available
print_header "Checking Your System"
echo ""

HAS_DOCKER=false
HAS_PYTHON=false
HAS_NODE=false
HAS_POSTGRES=false

if check_command docker && check_command docker-compose; then
    HAS_DOCKER=true
fi

if check_command python3 || check_command python; then
    HAS_PYTHON=true
else
    # Offer to install Python
    echo ""
    read -p "Python is not installed. Would you like to install it now? [y/N]: " install_py
    if [ "$install_py" = "y" ] || [ "$install_py" = "Y" ]; then
        if install_python; then
            HAS_PYTHON=true
        fi
    fi
fi

if check_command node && check_command npm; then
    HAS_NODE=true
fi

if check_command psql; then
    HAS_POSTGRES=true
fi

echo ""

# Recommend deployment option
print_header "Recommended Deployment Option"
echo ""

if [ "$HAS_DOCKER" = true ]; then
    print_success "Docker is available - RECOMMENDED!"
    echo ""
    echo "Docker deployment is the easiest option:"
    echo "  • Single command setup"
    echo "  • All dependencies included"
    echo "  • Easy to reset and restart"
    echo "  • Works on all platforms"
    echo ""
    RECOMMENDED="docker"
elif [ "$HAS_PYTHON" = true ]; then
    print_info "Python is available - Script installation recommended"
    echo ""
    echo "Automated script installation is a good option:"
    echo "  • Interactive setup wizard"
    echo "  • Automatic dependency installation"
    echo "  • Native performance"
    echo ""
    RECOMMENDED="script"
else
    print_warning "Limited dependencies available"
    echo ""
    echo "You'll need to install dependencies first."
    echo "See INSTALL.md for manual installation guide."
    echo ""
    RECOMMENDED="manual"
fi

# Show options
print_header "Deployment Options"
echo ""
echo "1) Docker Deployment (EASIEST) ⭐"
echo "   - Requires: Docker Engine + Docker Compose"
echo "   - Time: ~10 minutes"
echo "   - Difficulty: Easy"
echo ""
echo "2) Automated Script Installation"
echo "   - Requires: Python, PostgreSQL, Ollama"
echo "   - Time: ~20 minutes"
echo "   - Difficulty: Moderate"
echo ""
echo "3) Manual Installation"
echo "   - Requires: System admin skills"
echo "   - Time: ~45 minutes"
echo "   - Difficulty: Advanced"
echo ""
echo "4) View Documentation"
echo "   - Read deployment guides"
echo ""
echo "5) Exit"
echo ""

# Get user choice
read -p "Choose an option [1-5]: " choice

case $choice in
    1)
        # Docker deployment
        print_header "Docker Deployment"
        echo ""

        if [ "$HAS_DOCKER" = false ]; then
            print_error "Docker is not installed!"
            echo ""
            echo "Please install Docker (any of these options):"
            echo "  • Docker Desktop: https://www.docker.com/products/docker-desktop"
            echo "  • Docker Engine (Linux): curl -fsSL https://get.docker.com | sh"
            echo "  • Colima (Mac): brew install colima"
            echo "  • OrbStack (Mac): https://orbstack.dev/"
            echo ""
            echo "Then run this script again."
            exit 1
        fi

        print_info "Starting Docker deployment..."
        echo ""

        # Check for .env file
        if [ ! -f .env ]; then
            print_info "Creating .env file from template..."
            cp .env.docker .env
            print_success "Created .env file"
            echo ""
            print_warning "IMPORTANT: Edit .env file to change default passwords!"
            echo ""
            read -p "Press Enter to continue or Ctrl+C to edit .env first..."
        fi

        # Determine which docker compose command to use
        if docker compose version &> /dev/null; then
            DOCKER_COMPOSE="docker compose"
        else
            DOCKER_COMPOSE="docker-compose"
        fi

        # Create logs directory
        mkdir -p logs

        # Generate log filename with timestamp
        DEPLOY_LOG="logs/docker-deploy-$(date +%Y%m%d_%H%M%S).log"

        # Start services
        print_info "Starting Docker containers..."
        print_info "Logging to: $DEPLOY_LOG"
        echo ""
        $DOCKER_COMPOSE up -d 2>&1 | tee "$DEPLOY_LOG"

        echo ""
        print_success "Docker deployment started!"
        echo ""

        # Wait for services
        print_info "Waiting for services to start (30 seconds)..."
        sleep 30

        # Check status
        echo ""
        print_header "Service Status"
        $DOCKER_COMPOSE ps

        echo ""
        print_success "Deployment complete!"
        echo ""
        print_info "Deployment log saved to: $DEPLOY_LOG"
        echo ""
        print_info "Access the application:"
        echo "  • Frontend: http://localhost:5173"
        echo "  • Backend API: http://localhost:5000/api/health"
        echo "  • Default login: doctor1 / doctor123"
        echo ""
        print_info "Useful commands:"
        echo "  • View logs: $DOCKER_COMPOSE logs -f"
        echo "  • View logs + save to file: $DOCKER_COMPOSE logs -f 2>&1 | tee logs/runtime.log"
        echo "  • Stop: $DOCKER_COMPOSE down"
        echo "  • Restart: $DOCKER_COMPOSE restart"
        echo ""
        print_info "Next steps:"
        echo "  1. Open http://localhost:5173 in your browser"
        echo "  2. Download LLM model: $DOCKER_COMPOSE exec ollama ollama pull llama3.1-sql:latest"
        echo "  3. Read DOCKER_QUICKSTART.md for more info"
        ;;

    2)
        # Script installation
        print_header "Automated Script Installation"
        echo ""

        if [ "$HAS_PYTHON" = false ]; then
            print_warning "Python is not installed!"
            echo ""
            read -p "Would you like to install Python now? [y/N]: " install_py
            if [ "$install_py" = "y" ] || [ "$install_py" = "Y" ]; then
                if install_python; then
                    HAS_PYTHON=true
                else
                    print_error "Failed to install Python. Please install Python 3.12+ manually."
                    exit 1
                fi
            else
                print_error "Python is required for script installation."
                echo "Please install Python 3.12+ and run this script again."
                exit 1
            fi
        fi

        print_info "Starting automated installation..."
        echo ""

        cd install
        ./install.sh
        ;;

    3)
        # Manual installation
        print_header "Manual Installation"
        echo ""

        print_info "For manual installation, please read:"
        echo "  • DEPLOYMENT_STRATEGY.md"
        echo "  • INSTALL.md"
        echo ""

        read -p "Open DEPLOYMENT_STRATEGY.md now? [y/N]: " open_docs
        if [ "$open_docs" = "y" ] || [ "$open_docs" = "Y" ]; then
            if command -v less &> /dev/null; then
                less DEPLOYMENT_STRATEGY.md
            else
                cat DEPLOYMENT_STRATEGY.md
            fi
        fi
        ;;

    4)
        # View documentation
        print_header "Documentation"
        echo ""

        echo "Available documentation:"
        echo ""
        echo "  1) START_HERE.md - Quick start guide"
        echo "  2) DOCKER_QUICKSTART.md - Docker deployment"
        echo "  3) QUICKSTART.md - Manual quick start"
        echo "  4) INSTALL.md - Detailed installation"
        echo "  5) DEPLOYMENT_STRATEGY.md - All deployment options"
        echo "  6) Back to main menu"
        echo ""

        read -p "Choose a document [1-6]: " doc_choice

        case $doc_choice in
            1) less START_HERE.md 2>/dev/null || cat START_HERE.md ;;
            2) less DOCKER_QUICKSTART.md 2>/dev/null || cat DOCKER_QUICKSTART.md ;;
            3) less QUICKSTART.md 2>/dev/null || cat QUICKSTART.md ;;
            4) less INSTALL.md 2>/dev/null || cat INSTALL.md ;;
            5) less DEPLOYMENT_STRATEGY.md 2>/dev/null || cat DEPLOYMENT_STRATEGY.md ;;
            6) exec $0 ;;
            *) print_error "Invalid choice" ;;
        esac
        ;;

    5)
        # Exit
        print_info "Goodbye!"
        exit 0
        ;;

    *)
        print_error "Invalid choice!"
        exit 1
        ;;
esac
