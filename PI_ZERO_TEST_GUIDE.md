# Pi Zero 2W Audio Test Guide

Quick setup guide for testing audio output to PCM5102 DAC on Raspberry Pi Zero 2W.

## Prerequisites

1. **Pi Zero 2W** flashed with Raspberry Pi OS
2. **PCM5102 DAC** connected via I2S
3. **SSH or direct access** to the Pi

## Quick Start

### 1. Clone the Repository

```bash
cd ~
git clone https://github.com/parkredding/poor-house-dub-v2.git
cd poor-house-dub-v2
```

### 2. Checkout Test Branch

```bash
git checkout claude/test-pi-zero-audio-KdzFG
```

### 3. Run Setup Script

```bash
chmod +x setup.sh
sudo ./setup.sh
```

This will:
- Install system dependencies
- Install Python packages
- Configure I2S in `/boot/config.txt`
- Set up ALSA configuration
- Create systemd service (optional)

**Important:** Reboot after setup to enable I2S:
```bash
sudo reboot
```

### 4. Verify I2S Configuration

After reboot, check that I2S device is detected:

```bash
aplay -l
```

You should see something like:
```
card 0: sndrpihifiberry [snd_rpi_hifiberry_dac]
```

### 5. Run Audio Test

```bash
cd ~/poor-house-dub-v2
python3 pi_audio_test.py
```

Or for a quick test:
```bash
python3 pi_audio_test.py --quick
```

## Test Description

The test runs three verification steps:

### Test 1: Volume Sweep (0% → 100%)
- Tests volume control from silent to full
- Verifies audio is reaching the PCM5102
- **Expected:** Tone should get progressively louder

### Test 2: Delay Wet/Dry Mix (0% → 100%)
- Tests delay effect from dry to fully wet
- Verifies signal path through delay
- **Expected:** Echo/delay effect should increase

### Test 3: Continuous Tone with Delay
- Plays a 5-second tone with delay and slight reverb
- Final verification of full audio path
- **Expected:** Clean tone with echo effect

## Troubleshooting

### No Audio Output

1. **Check I2S configuration:**
   ```bash
   cat /boot/config.txt | grep i2s
   ```
   Should show: `dtparam=i2s=on` and `dtoverlay=hifiberry-dac`

2. **Check wiring connections:**
   - VIN → 3.3V (Pin 1)
   - GND → Ground (Pin 6)
   - LCK → GPIO 18 (Pin 12)
   - BCK → GPIO 19 (Pin 35)
   - DIN → GPIO 21 (Pin 40)
   - SCK → GND
   - FLT → GND
   - FMT → GND

3. **List audio devices:**
   ```bash
   python3 pi_audio_test.py --list-devices
   ```

4. **Test with aplay:**
   ```bash
   speaker-test -t wav -c 2
   ```

### Distorted Audio

- Check power supply (Pi Zero 2W needs adequate 5V power)
- Verify PCM5102 VIN is connected to 3.3V (NOT 5V)
- Check for loose I2S connections

### Device Not Found

If auto-detection fails, manually specify device:
```bash
python3 pi_audio_test.py --device 0
```

## PCM5102 Wiring Reference

| PCM5102 Pin | Pi Zero 2W Pin | Description |
|-------------|----------------|-------------|
| VIN | Pin 1 (3.3V) | Power |
| GND | Pin 6 (GND) | Ground |
| LCK | Pin 12 (GPIO 18) | I2S Word Clock |
| BCK | Pin 35 (GPIO 19) | I2S Bit Clock |
| DIN | Pin 40 (GPIO 21) | I2S Data |
| SCK | GND | System Clock (48kHz) |
| FLT | GND | Filter Select |
| FMT | GND | Format (I2S) |

## Next Steps

After successful test:

1. **Run the full synthesizer:**
   ```bash
   python3 main.py
   ```

2. **Enable auto-start on boot:**
   ```bash
   sudo systemctl enable dubsiren.service
   sudo systemctl start dubsiren.service
   ```

3. **View logs:**
   ```bash
   sudo journalctl -u dubsiren.service -f
   ```

## Additional Commands

**Stop the service:**
```bash
sudo systemctl stop dubsiren.service
```

**Disable auto-start:**
```bash
sudo systemctl disable dubsiren.service
```

**Check service status:**
```bash
sudo systemctl status dubsiren.service
```

## Performance Notes

The Pi Zero 2W has limited CPU compared to Pi 4/5:
- Single audio buffer processing should work fine
- Multiple simultaneous effects may cause glitches
- Monitor CPU usage: `htop`
- Consider increasing buffer size if audio stutters

## Support

If you encounter issues:
1. Check wiring and power supply
2. Verify I2S configuration
3. Review logs: `sudo journalctl -u dubsiren.service`
4. Test with basic audio: `speaker-test -t wav -c 2`
