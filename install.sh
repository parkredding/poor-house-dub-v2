#!/bin/bash
# One-line installer for Dub Siren V2
# Usage: curl -sSL https://raw.githubusercontent.com/yourusername/poor-house-dub-v2/main/install.sh | bash

set -e

REPO_URL="https://github.com/parkredding/poor-house-dub-v2.git"
INSTALL_DIR="$HOME/poor-house-dub-v2"
SERVICE_USER="${USER:-pi}"

echo "========================================"
echo "  Dub Siren V2 - One-Line Installer"
echo "  Raspberry Pi Zero 2 + PCM5102 DAC"
echo "========================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "WARNING: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Clone or update repository
if [ -d "$INSTALL_DIR" ]; then
    echo "Directory exists. Updating..."
    cd "$INSTALL_DIR"
    git pull
else
    echo "Cloning repository..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Update system
echo "Updating system packages..."
sudo apt-get update -qq

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-dev \
    python3-numpy \
    libasound2-dev \
    libportaudio2 \
    git \
    2>&1 | grep -v "^Reading" || true

# Install Python packages
echo "Installing Python packages..."
pip3 install -q -r requirements.txt

# Configure I2S for PCM5102
echo "Configuring I2S audio interface..."

# Backup config if it exists
if [ -f /boot/config.txt ]; then
    sudo cp /boot/config.txt /boot/config.txt.backup.$(date +%Y%m%d_%H%M%S)
elif [ -f /boot/firmware/config.txt ]; then
    sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup.$(date +%Y%m%d_%H%M%S)
fi

# Determine config file location (handles both old and new Pi OS)
CONFIG_FILE="/boot/config.txt"
if [ ! -f "$CONFIG_FILE" ] && [ -f "/boot/firmware/config.txt" ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
fi

# Add I2S configuration if not present
if ! sudo grep -q "dtparam=i2s=on" "$CONFIG_FILE"; then
    echo "Adding I2S configuration..."
    echo "" | sudo tee -a "$CONFIG_FILE" > /dev/null
    echo "# I2S Audio for PCM5102 DAC" | sudo tee -a "$CONFIG_FILE" > /dev/null
    echo "dtparam=i2s=on" | sudo tee -a "$CONFIG_FILE" > /dev/null
    echo "dtoverlay=hifiberry-dac" | sudo tee -a "$CONFIG_FILE" > /dev/null
else
    echo "I2S configuration already present"
fi

# Disable onboard audio
if ! sudo grep -q "dtparam=audio=off" "$CONFIG_FILE"; then
    echo "Disabling onboard audio..."
    sudo sed -i 's/dtparam=audio=on/dtparam=audio=off/' "$CONFIG_FILE"
fi

# Configure ALSA
echo "Configuring ALSA..."
cat > /tmp/asound.conf << 'EOF'
pcm.!default {
    type hw
    card 0
}

ctl.!default {
    type hw
    card 0
}
EOF
sudo mv /tmp/asound.conf /etc/asound.conf

# Make scripts executable
echo "Making scripts executable..."
chmod +x main.py synthesizer.py gpio_controller.py audio_output.py setup.sh

# Add user to necessary groups
echo "Adding user to gpio and audio groups..."
sudo usermod -a -G gpio,audio "$SERVICE_USER" 2>/dev/null || true

# Create systemd service
echo "Creating systemd service..."
cat > /tmp/dubsiren.service << EOF
[Unit]
Description=Dub Siren V2 Synthesizer
After=sound.target network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/main.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/dubsiren.service /etc/systemd/system/dubsiren.service
sudo systemctl daemon-reload

# Enable and start service
echo "Enabling service to start on boot..."
sudo systemctl enable dubsiren.service

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "PCM5102 Wiring (Quick Reference):"
echo "  VIN → Pin 1 (3.3V)"
echo "  GND → Pin 6 (GND)"
echo "  LCK → Pin 12 (GPIO 18)"
echo "  BCK → Pin 35 (GPIO 19)"
echo "  DIN → Pin 40 (GPIO 21)"
echo ""
echo "Next Steps:"
echo "  1. Reboot: sudo reboot"
echo "  2. After reboot, service will start automatically"
echo "  3. Check status: sudo systemctl status dubsiren.service"
echo "  4. View logs: journalctl -u dubsiren.service -f"
echo "  5. Stop service: sudo systemctl stop dubsiren.service"
echo "  6. Disable autostart: sudo systemctl disable dubsiren.service"
echo ""
echo "Manual Testing:"
echo "  cd $INSTALL_DIR"
echo "  python3 main.py --simulate --interactive"
echo ""
echo "Documentation:"
echo "  README: $INSTALL_DIR/README.md"
echo "  Hardware Guide: $INSTALL_DIR/HARDWARE.md"
echo "  Quick Start: $INSTALL_DIR/QUICKSTART.md"
echo ""
echo "IMPORTANT: You must reboot for I2S audio to work!"
echo ""
read -p "Reboot now? (Y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "Rebooting in 3 seconds..."
    sleep 3
    sudo reboot
else
    echo "Remember to reboot before using the dub siren!"
fi
