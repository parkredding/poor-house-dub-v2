#!/bin/bash
# One-line GPIO/I2C test installer for Raspberry Pi
# Usage: curl -sSL <raw-url> | bash -s -- <GITHUB_PAT>

set -e

PAT=$1

if [ -z "$PAT" ]; then
    echo "Error: GitHub PAT required"
    echo "Usage: $0 <GITHUB_PAT>"
    echo "Or: curl -sSL <raw-url> | bash -s -- <GITHUB_PAT>"
    exit 1
fi

echo "Installing GPIO/I2C test with 2 encoders + 1 switch..."

# Clone repo with PAT
git clone https://${PAT}@github.com/parkredding/poor-house-dub-v2.git ~/poor-house-dub-v2

# Run setup
cd ~/poor-house-dub-v2
chmod +x setup.sh
sudo ./setup.sh

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Reboot: sudo reboot"
echo "2. Run GPIO test: python3 ~/poor-house-dub-v2/pi_audio_test.py --gpio"
echo ""
echo "GPIO Wiring:"
echo "  Encoder 1 (Volume): GPIO 17, 27"
echo "  Encoder 2 (Delay):  GPIO 22, 23"
echo "  Trigger Switch:     GPIO 4"
echo ""
