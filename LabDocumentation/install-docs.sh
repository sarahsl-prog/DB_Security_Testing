#!/bin/bash
# Documentation Installation Script
# Healthcare Database Security Research Lab
#
# This script installs MkDocs and dependencies for serving documentation
# Usage: ./install-docs.sh [OPTIONS]
#
# Options:
#   --global    Install globally (requires sudo)
#   --user      Install for current user only (default)
#   --venv      Create virtual environment for docs

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_NAME="docs-venv"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Parse command line arguments
INSTALL_MODE="user"

for arg in "$@"; do
    case $arg in
        --global)
            INSTALL_MODE="global"
            shift
            ;;
        --user)
            INSTALL_MODE="user"
            shift
            ;;
        --venv)
            INSTALL_MODE="venv"
            shift
            ;;
        --help|-h)
            echo "Documentation Installation Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --global    Install globally (requires sudo)"
            echo "  --user      Install for current user only (default)"
            echo "  --venv      Create virtual environment for docs"
            echo "  --help      Show this help message"
            echo ""
            echo "After installation, you can:"
            echo "  mkdocs serve              # Start development server"
            echo "  mkdocs build              # Build static site"
            exit 0
            ;;
        *)
            print_error "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_header "MkDocs Documentation Setup"

# Check Python
print_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

# Check pip
print_info "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed"
    exit 1
fi

PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
print_success "pip $PIP_VERSION found"

# Install based on mode
case $INSTALL_MODE in
    global)
        print_header "Installing MkDocs Globally (requires sudo)"
        print_warning "This will install packages system-wide"
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Installation cancelled"
            exit 0
        fi

        print_info "Installing MkDocs dependencies..."
        sudo pip3 install -r "$SCRIPT_DIR/requirements-docs.txt"

        print_success "Global installation complete!"
        print_info "You can now run: mkdocs serve"
        ;;

    user)
        print_header "Installing MkDocs for Current User"

        print_info "Installing MkDocs dependencies..."
        pip3 install --user -r "$SCRIPT_DIR/requirements-docs.txt"

        print_success "User installation complete!"
        print_info "You can now run: mkdocs serve"

        # Check if ~/.local/bin is in PATH
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            print_warning "~/.local/bin is not in your PATH"
            print_info "Add this to your ~/.bashrc or ~/.zshrc:"
            echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
        fi
        ;;

    venv)
        print_header "Creating Virtual Environment for Documentation"

        VENV_PATH="$SCRIPT_DIR/$VENV_NAME"

        if [ -d "$VENV_PATH" ]; then
            print_warning "Virtual environment already exists at: $VENV_PATH"
            read -p "Remove and recreate? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -rf "$VENV_PATH"
                print_info "Removed existing virtual environment"
            else
                print_info "Using existing virtual environment"
            fi
        fi

        if [ ! -d "$VENV_PATH" ]; then
            print_info "Creating virtual environment..."
            uv venv "$VENV_PATH"
            print_success "Virtual environment created"
        fi

        print_info "Activating virtual environment..."
        source "$VENV_PATH/bin/activate"

        print_info "Upgrading pip..."
        uv pip install --upgrade pip

        print_info "Installing MkDocs dependencies..."
        uv pip install -r "$SCRIPT_DIR/requirements-docs.txt"

        print_success "Virtual environment installation complete!"
        echo ""
        print_header "How to Use the Documentation Environment"
        echo ""
        echo "Activate the environment:"
        echo "  ${GREEN}source $VENV_PATH/bin/activate${NC}"
        echo ""
        echo "Serve documentation:"
        echo "  ${GREEN}mkdocs serve${NC}"
        echo ""
        echo "Build documentation:"
        echo "  ${GREEN}mkdocs build${NC}"
        echo ""
        echo "Deactivate environment:"
        echo "  ${GREEN}deactivate${NC}"
        echo ""

        # Create activation helper script
        cat > "$SCRIPT_DIR/activate-docs.sh" << 'EOF'
#!/bin/bash
# Quick activation script for docs virtual environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/docs-venv/bin/activate"
echo "✓ Documentation environment activated"
echo "Run 'mkdocs serve' to start the development server"
EOF
        chmod +x "$SCRIPT_DIR/activate-docs.sh"

        print_success "Created activation helper: ./activate-docs.sh"
        ;;
esac

# Verify installation
echo ""
print_header "Verifying Installation"

if command -v mkdocs &> /dev/null; then
    MKDOCS_VERSION=$(mkdocs --version | head -n 1)
    print_success "MkDocs installed: $MKDOCS_VERSION"
else
    print_error "MkDocs not found in PATH"
    exit 1
fi

# Test build
print_info "Testing documentation build..."
cd "$SCRIPT_DIR"
if mkdocs build --quiet 2>&1 | grep -q "Error"; then
    print_error "Documentation build failed"
    mkdocs build 2>&1 | tail -20
    exit 1
else
    print_success "Documentation builds successfully"
fi

# Clean up test build
if [ -d "$SCRIPT_DIR/site" ]; then
    rm -rf "$SCRIPT_DIR/site"
fi

echo ""
print_header "Installation Complete!"
echo ""
print_info "Documentation is ready to use"
echo ""
echo "Quick Start:"
echo "  ${GREEN}cd $(basename $SCRIPT_DIR)${NC}"
echo "  ${GREEN}mkdocs serve${NC}"
echo ""
echo "Then open: ${BLUE}http://localhost:8000${NC}"
echo ""
print_info "For more information, see README.md"
