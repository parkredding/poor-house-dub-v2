# Quick Start Guide

This guide will get your Dub Siren up and running in 15 minutes.

## Step 1: Hardware Assembly (5 minutes)

### Minimal Setup (PCM5102 only)

Connect just the DAC first to test audio:

```
PCM5102 Pin    →    Raspberry Pi Pin
VIN            →    Pin 1 (3.3V)
GND            →    Pin 6 (GND)
LCK            →    Pin 12 (GPIO 18)
BCK            →    Pin 35 (GPIO 19)
DIN            →    Pin 40 (GPIO 21)
```

Additional PCM5102 configuration pins (if available):
- SCK → GND
- FLT → GND
- FMT → GND

## Step 2: Software Installation (5 minutes)

### On your Raspberry Pi:

```bash
# Clone repository
cd ~
git clone https://github.com/yourusername/poor-house-dub-v2.git
cd poor-house-dub-v2

# Run setup
chmod +x setup.sh
./setup.sh

# This will:
# - Install dependencies
# - Configure I2S audio
# - Setup systemd service
# - Create ALSA configuration
```

### Reboot Required

```bash
sudo reboot
```

## Step 3: Test Audio (2 minutes)

### After reboot, test the audio output:

```bash
cd ~/poor-house-dub-v2

# List audio devices
python3 main.py --list-devices

# Test audio output
python3 audio_output.py
```

You should hear a test tone for 5 seconds.

### If no audio:

```bash
# Check ALSA devices
aplay -l

# You should see something like:
# card 0: sndrpihifiberry [snd_rpi_hifiberry_dac]

# Test with ALSA
speaker-test -t wav -c 2 -D hw:0,0
```

## Step 4: Test Without Controls (1 minute)

Run in simulation mode to test the synthesizer:

```bash
python3 main.py --simulate --interactive
```

Commands in interactive mode:
- `1` - Trigger airhorn
- `2` - Trigger siren
- `r` - Release
- `s` - Show status
- `q` - Quit

## Step 5: Add Controls (Optional)

If you have the rotary encoders and switches wired up:

### Test GPIO:

```bash
python3 gpio_controller.py
```

Rotate encoders and press buttons to see output.

### Run full system:

```bash
python3 main.py
```

## Step 6: Run at Startup (Optional)

Enable the systemd service to start on boot:

```bash
sudo systemctl enable dubsiren.service
sudo systemctl start dubsiren.service

# Check status
sudo systemctl status dubsiren.service

# View logs
journalctl -u dubsiren.service -f
```

## Troubleshooting Quick Fixes

### No audio output?

```bash
# Check I2S enabled
grep "dtparam=i2s=on" /boot/config.txt

# Should return: dtparam=i2s=on

# Check DAC overlay
grep "dtoverlay=hifiberry-dac" /boot/config.txt

# Should return: dtoverlay=hifiberry-dac

# If missing, add them and reboot
```

### Permission errors?

```bash
# Add user to gpio and audio groups
sudo usermod -a -G gpio,audio $USER

# Log out and back in
```

### Import errors?

```bash
# Reinstall dependencies
pip3 install -r requirements.txt
```

## Basic Usage

### Command Line Options

```bash
# Default mode (hardware)
python3 main.py

# Simulation mode (no hardware)
python3 main.py --simulate --interactive

# Custom sample rate
python3 main.py --sample-rate 44100

# Larger buffer for stability
python3 main.py --buffer-size 512

# List available audio devices
python3 main.py --list-devices
```

## What's Next?

1. **Wire up controls** - See [HARDWARE.md](HARDWARE.md) for GPIO pin assignments
2. **Customize sounds** - Edit preset frequencies in `synthesizer.py`
3. **Add effects** - Modify DSP parameters in the synth engine
4. **Create enclosure** - Design a case for your dub siren
5. **Go dub!** - Connect to speakers and make some noise!

## Default Control Values

When you start the siren, these are the default values:

| Parameter | Default Value |
|-----------|---------------|
| Volume | 0.5 (50%) |
| Filter Frequency | 2000 Hz |
| Filter Resonance | 0.1 |
| Delay Time | 0.5 seconds |
| Delay Feedback | 0.3 |
| Reverb Size | 0.5 |
| Reverb Mix | 0.3 (30% wet) |
| Release Time | 0.5 seconds |
| Osc Waveform | Sine |
| LFO Waveform | Sine |
| Airhorn Freq | 150 Hz |
| Siren Freq | 800 Hz |

## Performance Tweaks

### For better performance on Pi Zero 2:

```bash
# Use performance governor
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable wifi

# Reduce GPU memory (in /boot/config.txt)
gpu_mem=16
```

## Next Steps

- Read the full [README.md](README.md) for detailed information
- Check [HARDWARE.md](HARDWARE.md) for complete wiring guide
- Join the community (add link)
- Share your build!

---

**You're ready to dub! 🔊**
