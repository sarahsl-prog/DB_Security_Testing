#!/bin/bash
# Quick activation script for docs virtual environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/docs-venv/bin/activate"
echo "✓ Documentation environment activated"
echo "Run 'mkdocs serve' to start the development server"
