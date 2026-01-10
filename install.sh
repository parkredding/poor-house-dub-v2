#!/bin/bash
# One-line installer for Poor House Dub GPIO/I2C Test
# Usage: curl -H "Authorization: token YOUR_PAT" -L https://raw.githubusercontent.com/parkredding/poor-house-dub-v2/claude/gpio-i2c-installer-SAiHA/install.sh | bash

set -e

echo "=================================="
echo "Poor House Dub GPIO/I2C Test Setup"
echo "=================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/cpuinfo ] || ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   GPIO and I2S tests may not work correctly"
    echo ""
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "📦 Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-numpy \
    libasound2-dev \
    libportaudio2 \
    git \
    >/dev/null 2>&1

echo "✓ System dependencies installed"

echo ""
echo "🐍 Installing Python packages..."
pip3 install --quiet numpy>=1.21.0 sounddevice>=0.4.5 RPi.GPIO>=0.7.1

echo "✓ Python packages installed"

echo ""
echo "📥 Downloading test script..."

# Download the test script
if [ -n "$GITHUB_TOKEN" ] || [ -n "$GITHUB_PAT" ]; then
    TOKEN="${GITHUB_TOKEN:-$GITHUB_PAT}"
    curl -H "Authorization: token $TOKEN" \
         -H 'Accept: application/vnd.github.v3.raw' \
         -sL "https://api.github.com/repos/parkredding/poor-house-dub-v2/contents/pi_audio_test.py?ref=claude/gpio-i2c-installer-SAiHA" \
         -o pi_audio_test.py

    curl -H "Authorization: token $TOKEN" \
         -H 'Accept: application/vnd.github.v3.raw' \
         -sL "https://api.github.com/repos/parkredding/poor-house-dub-v2/contents/pi_test_gpio.py?ref=claude/gpio-i2c-installer-SAiHA" \
         -o pi_test_gpio.py 2>/dev/null || echo "  (GPIO controller optional)"
else
    echo "❌ Error: No GitHub token found"
    echo "   Please set GITHUB_TOKEN or GITHUB_PAT environment variable"
    echo ""
    echo "   Example:"
    echo "   export GITHUB_PAT=your_token_here"
    echo "   curl ... | bash"
    exit 1
fi

# Download required modules
echo "📥 Downloading dependencies..."
for module in audio_output.py synthesizer.py effects.py; do
    if [ -n "$TOKEN" ]; then
        curl -H "Authorization: token $TOKEN" \
             -H 'Accept: application/vnd.github.v3.raw' \
             -sL "https://api.github.com/repos/parkredding/poor-house-dub-v2/contents/$module?ref=claude/gpio-i2c-installer-SAiHA" \
             -o "$module" 2>/dev/null || echo "  ($module optional)"
    fi
done

echo "✓ Files downloaded to $TEMP_DIR"

echo ""
echo "=================================="
echo "✅ Installation Complete!"
echo "=================================="
echo ""
echo "Test script location: $TEMP_DIR/pi_audio_test.py"
echo ""
echo "Run tests with:"
echo "  cd $TEMP_DIR"
echo "  python3 pi_audio_test.py          # Full test suite"
echo "  python3 pi_audio_test.py --quick  # Quick test"
echo "  python3 pi_audio_test.py --gpio   # GPIO control mode"
echo "  python3 pi_audio_test.py --list-devices  # List audio devices"
echo ""
echo "To run tests now, type: cd $TEMP_DIR && python3 pi_audio_test.py"
echo ""
