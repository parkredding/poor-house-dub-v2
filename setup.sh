#!/bin/bash
# Setup script for Dub Siren V2
# Run this on your Raspberry Pi Zero 2

set -e

echo "========================================"
echo "  Dub Siren V2 Setup"
echo "  Raspberry Pi Zero 2 + PCM5102 DAC"
echo "========================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "WARNING: Not running on Raspberry Pi?"
fi

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
pip3 install -r requirements.txt

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

# Make Python scripts executable
echo "Making scripts executable..."
chmod +x main.py
chmod +x synthesizer.py
chmod +x gpio_controller.py
chmod +x audio_output.py

# Create systemd service
echo "Creating systemd service..."
cat > /tmp/dubsiren.service << 'EOF'
[Unit]
Description=Dub Siren V2 Synthesizer
After=sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/poor-house-dub-v2
ExecStart=/usr/bin/python3 /home/pi/poor-house-dub-v2/main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/dubsiren.service /etc/systemd/system/dubsiren.service
sudo systemctl daemon-reload

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "PCM5102 Wiring Guide:"
echo "--------------------"
echo "  PCM5102    ->  Raspberry Pi Zero 2"
echo "  VIN        ->  3.3V (Pin 1)"
echo "  GND        ->  GND (Pin 6)"
echo "  LCK        ->  GPIO 18 (Pin 12) - I2S LRCLK"
echo "  BCK        ->  GPIO 19 (Pin 35) - I2S BCLK"
echo "  DIN        ->  GPIO 21 (Pin 40) - I2S DOUT"
echo "  SCK        ->  GND (for 48kHz)"
echo "  FLT        ->  GND (normal filter)"
echo "  FMT        ->  GND (I2S format)"
echo ""
echo "GPIO Pin Assignments:"
echo "--------------------"
echo "See gpio_controller.py for detailed pin assignments"
echo ""
echo "Next Steps:"
echo "1. Wire up the PCM5102 DAC according to the guide above"
echo "2. Wire up the 10 rotary encoders and 2 switches"
echo "3. Reboot: sudo reboot"
echo "4. Test audio: python3 audio_output.py"
echo "5. Test controls: python3 gpio_controller.py"
echo "6. Run the siren: python3 main.py --simulate  (for testing)"
echo "7. Run the siren: python3 main.py  (on hardware)"
echo "8. Enable service: sudo systemctl enable dubsiren.service"
echo "9. Start service: sudo systemctl start dubsiren.service"
echo ""
