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
    python3-venv \
    python3-numpy \
    libasound2-dev \
    libportaudio2 \
    git

# Create virtual environment
echo "Creating Python virtual environment..."
VENV_DIR="$HOME/poor-house-dub-v2-venv"
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists, removing..."
    rm -rf "$VENV_DIR"
fi
python3 -m venv "$VENV_DIR"

# Install Python packages in virtual environment
echo "Installing Python packages..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r requirements.txt

# Configure I2S for PCM5102
echo "Configuring I2S audio interface for PCM5102..."

# Detect correct config.txt location (newer OS uses /boot/firmware/config.txt)
if [ -f /boot/firmware/config.txt ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
else
    CONFIG_FILE="/boot/config.txt"
fi

echo "Using config file: $CONFIG_FILE"

# Backup config if it exists
if [ -f "$CONFIG_FILE" ]; then
    sudo cp "$CONFIG_FILE" "$CONFIG_FILE.backup"
fi

# Add dtoverlay for I2S if not already present
if ! grep -q "dtoverlay=hifiberry-dac" "$CONFIG_FILE"; then
    echo "Adding I2S configuration to $CONFIG_FILE..."
    echo "" | sudo tee -a "$CONFIG_FILE"
    echo "# I2S Audio for PCM5102 DAC" | sudo tee -a "$CONFIG_FILE"
    echo "dtparam=i2s=on" | sudo tee -a "$CONFIG_FILE"
    echo "dtoverlay=hifiberry-dac" | sudo tee -a "$CONFIG_FILE"
else
    echo "I2S configuration already present"
fi

# Disable onboard audio
if ! grep -q "dtparam=audio=off" "$CONFIG_FILE"; then
    echo "Disabling onboard audio..."
    sudo sed -i 's/dtparam=audio=on/dtparam=audio=off/' "$CONFIG_FILE"
fi

# Configure ALSA for I2S DAC
echo ""
echo "========================================"
echo "  Audio Device Selection"
echo "========================================"
echo ""
echo "Available audio devices:"
echo ""

# List audio devices and create an array
CARD_NUM=0
declare -a DEVICES
declare -a CARD_NUMBERS
INDEX=1

# Parse aplay -l output to get device info
while IFS= read -r line; do
    if [[ $line =~ ^card\ ([0-9]+):\ (.+)\[(.+)\] ]]; then
        CARD_NUM="${BASH_REMATCH[1]}"
        CARD_NAME="${BASH_REMATCH[2]}"
        DEVICE_NAME="${BASH_REMATCH[3]}"
        DEVICES[$INDEX]="$CARD_NAME[$DEVICE_NAME]"
        CARD_NUMBERS[$INDEX]=$CARD_NUM
        echo "  $INDEX) Card $CARD_NUM: $CARD_NAME[$DEVICE_NAME]"
        ((INDEX++))
    fi
done < <(aplay -l 2>/dev/null)

if [ ${#DEVICES[@]} -eq 0 ]; then
    echo "⚠️  No audio devices detected!"
    echo "   Using default card 0 (this may not work)"
    SELECTED_CARD=0
else
    echo ""
    echo "Which audio device would you like to use?"
    echo "(For PCM5102 DAC, select the hifiberry-dac or snd_rpi_hifiberry_dac device)"
    read -p "Enter number [1]: " DEVICE_CHOICE </dev/tty

    # Default to 1 if empty
    DEVICE_CHOICE=${DEVICE_CHOICE:-1}

    if [ $DEVICE_CHOICE -ge 1 ] && [ $DEVICE_CHOICE -lt $INDEX ]; then
        SELECTED_CARD=${CARD_NUMBERS[$DEVICE_CHOICE]}
        echo "✓ Selected: ${DEVICES[$DEVICE_CHOICE]}"
    else
        echo "⚠️  Invalid selection, using default card 0"
        SELECTED_CARD=0
    fi
fi

echo ""
echo "Configuring ALSA for card $SELECTED_CARD..."
cat > /tmp/asound.conf << EOF
pcm.!default {
    type hw
    card $SELECTED_CARD
}

ctl.!default {
    type hw
    card $SELECTED_CARD
}
EOF

sudo mv /tmp/asound.conf /etc/asound.conf
echo "✓ ALSA configured"

# Make Python scripts executable
echo "Making scripts executable..."
chmod +x main.py
chmod +x synthesizer.py
chmod +x gpio_controller.py
chmod +x audio_output.py

# Create systemd service
echo "Creating systemd service..."
INSTALL_USER=$(whoami)
cat > /tmp/dubsiren.service << EOF
[Unit]
Description=Dub Siren V2 Synthesizer
After=sound.target

[Service]
Type=simple
User=$INSTALL_USER
WorkingDirectory=$HOME/poor-house-dub-v2
ExecStart=$HOME/poor-house-dub-v2-venv/bin/python3 $HOME/poor-house-dub-v2/main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/dubsiren.service /etc/systemd/system/dubsiren.service
sudo systemctl daemon-reload

# Ask user if they want to enable auto-start on boot
echo ""
echo "========================================"
echo "  Auto-Start Configuration"
echo "========================================"
echo ""
echo "Would you like the Dub Siren to start automatically on boot?"
read -p "Enable auto-start? (y/N): " -n 1 -r </dev/tty
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Enabling auto-start service..."
    sudo systemctl enable dubsiren.service
    echo "✓ Auto-start enabled - Dub Siren will start on boot"
    echo ""
    echo "Note: You can disable auto-start later with:"
    echo "      sudo systemctl disable dubsiren.service"
else
    echo "Auto-start not enabled."
    echo ""
    echo "You can enable it later with:"
    echo "      sudo systemctl enable dubsiren.service"
fi

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
echo "4. Test in simulation mode: ~/poor-house-dub-v2-venv/bin/python3 main.py --simulate --interactive"
echo "5. Run on hardware: ~/poor-house-dub-v2-venv/bin/python3 main.py"
echo ""
echo "To manage the service:"
echo "  Start:   sudo systemctl start dubsiren.service"
echo "  Stop:    sudo systemctl stop dubsiren.service"
echo "  Status:  sudo systemctl status dubsiren.service"
echo ""
echo "Note: Python packages are installed in a virtual environment at:"
echo "      $HOME/poor-house-dub-v2-venv"
echo ""
