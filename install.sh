#!/bin/bash
# Dub Siren V2 - One-line Installer for Raspberry Pi Zero 2W
# Usage: curl -sSL https://raw.githubusercontent.com/parkredding/poor-house-dub-v2/main/install.sh | bash

set -e

REPO_URL="https://github.com/parkredding/poor-house-dub-v2.git"
INSTALL_DIR="$HOME/poor-house-dub-v2"
BRANCH="${1:-main}"

echo "========================================"
echo "  Dub Siren V2 Installer"
echo "  Raspberry Pi Zero 2W + PCM5102 DAC"
echo "========================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/cpuinfo ] || ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  WARNING: Not running on Raspberry Pi!"
    echo "   This installer is designed for Raspberry Pi Zero 2W"
    echo "   GPIO and I2S features may not work correctly"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r </dev/tty
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if directory already exists and remove for fresh install
if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️  Directory $INSTALL_DIR already exists!"
    echo "🗑️  Removing for fresh installation..."
    # Change to home directory first to avoid "current working directory" issues
    cd "$HOME"
    rm -rf "$INSTALL_DIR"
    echo "✓ Old installation removed"
    echo ""
fi

# Update system
echo "📦 Updating system packages..."
sudo apt-get update -qq

# Install git if not present
if ! command -v git &> /dev/null; then
    echo "📦 Installing git..."
    sudo apt-get install -y git >/dev/null 2>&1
fi

echo "✓ System updated"

# Clone repository
echo ""
echo "📥 Cloning Dub Siren V2 repository..."
git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR" 2>&1 | grep -v "Cloning into" || true

# Change to install directory
cd "$INSTALL_DIR"

# Make setup script executable
chmod +x setup.sh

# Run setup
echo ""
echo "🔧 Running setup script..."
echo ""
./setup.sh

echo ""
echo "========================================"
echo "✅ Installation Complete!"
echo "========================================"
echo ""
echo "📍 Installation directory: $INSTALL_DIR"
echo ""
echo "Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  Wire up your PCM5102 DAC (see wiring guide below)"
echo "2️⃣  Wire up your rotary encoders and switches"
echo "3️⃣  Reboot your Raspberry Pi:"
echo "    sudo reboot"
echo ""
echo "4️⃣  After reboot, test in simulation mode:"
echo "    ~/poor-house-dub-v2-venv/bin/python3 ~/poor-house-dub-v2/main.py --simulate --interactive"
echo ""
echo "5️⃣  Run on hardware:"
echo "    ~/poor-house-dub-v2-venv/bin/python3 ~/poor-house-dub-v2/main.py"
echo ""
echo "6️⃣  Enable auto-start on boot:"
echo "    sudo systemctl enable dubsiren.service"
echo "    sudo systemctl start dubsiren.service"
echo ""
echo "PCM5102 Wiring Guide:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PCM5102 Pin    →  Raspberry Pi Zero 2W"
echo "  ───────────────────────────────────────"
echo "  VIN            →  3.3V (Pin 1)"
echo "  GND            →  GND (Pin 6)"
echo "  LCK            →  GPIO 18 (Pin 12) - I2S LRCLK"
echo "  BCK            →  GPIO 19 (Pin 35) - I2S BCLK"
echo "  DIN            →  GPIO 21 (Pin 40) - I2S DOUT"
echo "  SCK            →  GND (for 48kHz)"
echo "  FLT            →  GND (normal filter)"
echo "  FMT            →  GND (I2S format)"
echo ""
echo "Documentation:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📖 Full guide:    ~/poor-house-dub-v2/README.md"
echo "  🔧 Hardware:      ~/poor-house-dub-v2/HARDWARE.md"
echo "  🚀 Quick start:   ~/poor-house-dub-v2/QUICKSTART.md"
echo "  🎛️  GPIO wiring:  ~/poor-house-dub-v2/GPIO_WIRING_GUIDE.md"
echo ""
echo "Need help? Visit: https://github.com/parkredding/poor-house-dub-v2"
echo ""
