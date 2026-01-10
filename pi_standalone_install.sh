#!/bin/bash
# Standalone GPIO/I2C test installer for Raspberry Pi
# Installs dependencies without needing to clone the full repo

set -e

echo "========================================"
echo "  GPIO/I2C Test Setup for Pi Zero 2W"
echo "  2 Encoders + 1 Switch"
echo "========================================"
echo ""

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-numpy \
    libasound2-dev \
    libportaudio2 \
    git

# Install Python packages
echo "Installing Python packages..."
pip3 install --user numpy>=1.21.0 sounddevice>=0.4.5 RPi.GPIO>=0.7.1

# Configure I2S for PCM5102
echo "Configuring I2S audio interface for PCM5102..."

# Backup config if it exists
if [ -f /boot/config.txt ]; then
    sudo cp /boot/config.txt /boot/config.txt.backup
fi

# Add dtoverlay for I2S if not already present
if ! grep -q "dtoverlay=hifiberry-dac" /boot/config.txt; then
    echo "Adding I2S configuration to /boot/config.txt..."
    echo "" | sudo tee -a /boot/config.txt
    echo "# I2S Audio for PCM5102 DAC" | sudo tee -a /boot/config.txt
    echo "dtparam=i2s=on" | sudo tee -a /boot/config.txt
    echo "dtoverlay=hifiberry-dac" | sudo tee -a /boot/config.txt
else
    echo "I2S configuration already present"
fi

# Disable onboard audio
if ! grep -q "dtparam=audio=off" /boot/config.txt; then
    echo "Disabling onboard audio..."
    sudo sed -i 's/dtparam=audio=on/dtparam=audio=off/' /boot/config.txt
fi

# Configure ALSA for I2S DAC
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

echo ""
echo "========================================"
echo "  Dependencies Installed!"
echo "========================================"
echo ""
echo "Next Steps:"
echo "1. Copy test files to Pi (pi_audio_test.py, pi_test_gpio.py)"
echo "2. Reboot: sudo reboot"
echo "3. Verify I2S: aplay -l"
echo "4. Run test: python3 pi_audio_test.py --gpio"
echo ""
echo "GPIO Wiring:"
echo "  Encoder 1 (Volume): GPIO 17, 27 + GND"
echo "  Encoder 2 (Delay):  GPIO 22, 23 + GND"
echo "  Trigger Switch:     GPIO 4 + GND"
echo ""
echo "PCM5102 Wiring:"
echo "  VIN → 3.3V (Pin 1)"
echo "  GND → GND (Pin 6)"
echo "  LCK → GPIO 18 (Pin 12)"
echo "  BCK → GPIO 19 (Pin 35)"
echo "  DIN → GPIO 21 (Pin 40)"
echo "  SCK → GND, FLT → GND, FMT → GND"
echo ""
