#!/bin/bash
# Clean Install Script for Poor House Dub V2
# This script completely removes the current build and installs from main branch

set -e  # Exit on error

echo "================================================"
echo "Poor House Dub V2 - Clean Install from Main"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}Step 1: Stopping dubsiren service (if running)...${NC}"
if systemctl is-active --quiet dubsiren-cpp.service 2>/dev/null; then
    echo "Stopping dubsiren-cpp.service..."
    sudo systemctl stop dubsiren-cpp.service
    echo -e "${GREEN}✓ Service stopped${NC}"
else
    echo "Service not running or not installed"
fi

echo ""
echo -e "${YELLOW}Step 2: Disabling service auto-start...${NC}"
if systemctl is-enabled --quiet dubsiren-cpp.service 2>/dev/null; then
    echo "Disabling dubsiren-cpp.service..."
    sudo systemctl disable dubsiren-cpp.service
    echo -e "${GREEN}✓ Service disabled${NC}"
else
    echo "Service not enabled"
fi

echo ""
echo -e "${YELLOW}Step 3: Removing build artifacts...${NC}"
if [ -d "cpp/build" ]; then
    echo "Removing cpp/build directory..."
    rm -rf cpp/build
    echo -e "${GREEN}✓ Build directory removed${NC}"
else
    echo "No build directory found"
fi

# Also remove node_modules if present
if [ -d "node_modules" ]; then
    echo "Removing node_modules directory..."
    rm -rf node_modules
    echo -e "${GREEN}✓ node_modules removed${NC}"
fi

echo ""
echo -e "${YELLOW}Step 4: Checking out main branch...${NC}"
# Stash any local changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "Stashing local changes..."
    git stash push -m "Clean install backup $(date +%Y%m%d_%H%M%S)"
fi

# Fetch latest from remote
echo "Fetching latest from origin..."
git fetch origin

# Check if main branch exists locally
if git show-ref --verify --quiet refs/heads/main; then
    echo "Checking out main branch..."
    git checkout main
else
    echo "Creating and checking out main branch from origin/main..."
    git checkout -b main origin/main
fi

# Pull latest changes
echo "Pulling latest changes from origin/main..."
git pull origin main

echo -e "${GREEN}✓ On main branch with latest changes${NC}"

echo ""
echo -e "${YELLOW}Step 5: Running setup script...${NC}"
if [ -f "cpp/setup.sh" ]; then
    echo "Running cpp/setup.sh..."
    cd cpp
    bash setup.sh
    cd ..
    echo -e "${GREEN}✓ Setup complete${NC}"
else
    echo -e "${RED}Error: cpp/setup.sh not found!${NC}"
    exit 1
fi

echo ""
echo "================================================"
echo -e "${GREEN}Clean install complete!${NC}"
echo "================================================"
echo ""
echo "Service status:"
sudo systemctl status dubsiren-cpp.service --no-pager || true
echo ""
echo "To view logs:"
echo "  journalctl -u dubsiren-cpp.service -f"
echo ""
echo "To manually control the service:"
echo "  sudo systemctl start dubsiren-cpp.service"
echo "  sudo systemctl stop dubsiren-cpp.service"
echo "  sudo systemctl restart dubsiren-cpp.service"
echo ""
