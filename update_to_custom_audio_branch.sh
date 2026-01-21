#!/bin/bash
# Update Dub Siren to Custom Audio Branch
# Run this on your Raspberry Pi to update to the custom audio feature branch

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

BRANCH="claude/add-secret-mode-audio-JPSOr"
INSTALL_DIR="$HOME/poor-house-dub-v2"

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Dub Siren V2 - Custom Audio Branch Update${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}❌ Error: Dub Siren installation not found at $INSTALL_DIR${NC}"
    echo "   Please install first or adjust INSTALL_DIR in this script"
    exit 1
fi

cd "$INSTALL_DIR"

# Stop the service if it's running
echo -e "${YELLOW}⏸️  Stopping dubsiren-cpp service...${NC}"
if sudo systemctl is-active --quiet dubsiren-cpp.service; then
    sudo systemctl stop dubsiren-cpp.service
    echo -e "${GREEN}✓ Service stopped${NC}"
else
    echo -e "${YELLOW}  (Service was not running)${NC}"
fi

echo ""
echo -e "${CYAN}📥 Fetching latest changes...${NC}"
git fetch origin

echo ""
echo -e "${CYAN}🔀 Switching to branch: $BRANCH${NC}"
git checkout "$BRANCH"

echo ""
echo -e "${CYAN}⬇️  Pulling latest changes from branch...${NC}"
git pull origin "$BRANCH"

echo ""
echo -e "${GREEN}✓ Git update complete${NC}"

# Build the project
echo ""
echo -e "${CYAN}🔨 Building C++ project...${NC}"
cd "$INSTALL_DIR/cpp"

# Clean build recommended when switching branches
echo -e "${YELLOW}  Cleaning previous build...${NC}"
rm -rf build

# Run build script
./build.sh

echo ""
echo -e "${GREEN}✓ Build complete!${NC}"

# Restart the service
echo ""
echo -e "${CYAN}▶️  Starting dubsiren-cpp service...${NC}"
sudo systemctl start dubsiren-cpp.service

echo ""
echo -e "${GREEN}✓ Service started${NC}"

# Show status
echo ""
echo -e "${CYAN}📊 Service Status:${NC}"
sudo systemctl status dubsiren-cpp.service --no-pager -l

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Update Complete!${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}🎵 Custom Audio Secret Mode is now available!${NC}"
echo ""
echo -e "To use the new feature:"
echo -e "  1️⃣  Upload your MP3 file to:"
echo -e "     ${CYAN}$INSTALL_DIR/assets/audio/custom.mp3${NC}"
echo ""
echo -e "  2️⃣  Press SHIFT button 4 times rapidly"
echo ""
echo -e "  3️⃣  Press TRIGGER to play your custom audio"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  View logs:     ${CYAN}journalctl -u dubsiren-cpp.service -f${NC}"
echo -e "  Stop service:  ${CYAN}sudo systemctl stop dubsiren-cpp.service${NC}"
echo -e "  Start service: ${CYAN}sudo systemctl start dubsiren-cpp.service${NC}"
echo -e "  Check status:  ${CYAN}sudo systemctl status dubsiren-cpp.service${NC}"
echo ""
echo -e "For help uploading your MP3, see:"
echo -e "  ${CYAN}$INSTALL_DIR/assets/audio/README.md${NC}"
echo ""
