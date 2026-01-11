# Dub Siren V2

A professional dub siren synthesizer built on Raspberry Pi Zero 2 with PCM5102 I2S DAC.

![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%20Zero%202-red)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![Test Suite](https://github.com/parkredding/poor-house-dub-v2/actions/workflows/test.yml/badge.svg)](https://github.com/parkredding/poor-house-dub-v2/actions/workflows/test.yml)

## Features

- **Real-time Audio Synthesis**
  - Multiple oscillator waveforms (Sine, Square, Saw, Triangle)
  - Envelope generator with adjustable release
  - Low-frequency oscillator (LFO) for modulation

- **Professional DSP Effects**
  - Low-pass filter with resonance control
  - Analog-style delay/echo with pitch-shifting time modulation
  - Hybrid chamber reverb (Ableton-inspired) with early reflections, diffusion, and warm damping

- **Hardware Control Surface**
  - 5 rotary encoders with bank switching (10 parameters total)
  - 4 momentary switches (trigger, pitch envelope, shift, shutdown)
  - Shift button for accessing Bank A/B parameters
  - Uses only 14 GPIO pins (avoids I2S conflict)

- **High-Quality Audio**
  - PCM5102 I2S DAC for pristine audio output
  - 48kHz sample rate
  - Low latency real-time processing

## Quick Start

### Prerequisites

- Raspberry Pi Zero 2 W
- PCM5102 DAC module
- 5x rotary encoders (KY-040 or similar)
- 4x momentary switches
- MicroSD card (8GB+)
- 5V 2.5A power supply

### Installation

#### One-Line Installer (Recommended)

The easiest way to install on your Raspberry Pi Zero 2W:

```bash
curl -sSL https://raw.githubusercontent.com/parkredding/poor-house-dub-v2/main/install.sh | bash
```

This will:
- Install all system dependencies
- Clone the repository to `~/poor-house-dub-v2`
- Configure I2S audio for PCM5102 DAC
- Set up the systemd service
- Display wiring instructions

After installation completes, reboot your Pi and follow the on-screen instructions.

#### Manual Installation

If you prefer to install manually:

1. **Flash Raspberry Pi OS**
   ```bash
   # Use Raspberry Pi Imager to flash Raspberry Pi OS Lite (64-bit)
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/parkredding/poor-house-dub-v2.git
   cd poor-house-dub-v2
   ```

3. **Run setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Reboot**
   ```bash
   sudo reboot
   ```

### Hardware Setup

See [HARDWARE.md](HARDWARE.md) for detailed wiring instructions.

**Quick PCM5102 Wiring:**
```
PCM5102    ->  Raspberry Pi Zero 2
VIN        ->  3.3V (Pin 1)
GND        ->  GND (Pin 6)
LCK        ->  GPIO 18 (Pin 12)
BCK        ->  GPIO 19 (Pin 35)
DIN        ->  GPIO 21 (Pin 40)
```

### Running the Siren

**Test in simulation mode (no hardware required):**
```bash
python3 main.py --simulate --interactive
```

**Run on hardware:**
```bash
python3 main.py
```

**Run as system service:**
```bash
sudo systemctl enable dubsiren.service
sudo systemctl start dubsiren.service
```

## Control Layout

The control surface uses 5 rotary encoders with a **shift button** for bank switching, providing access to 10 parameters across two banks:

```
Encoders:  [Encoder 1]  [Encoder 2]  [Encoder 3]  [Encoder 4]  [Encoder 5]
Buttons:   [TRIGGER]    [PITCH ENV]  [SHIFT]      [SHUTDOWN]
```

### Bank A (Normal Mode)

| Encoder | Parameter | Function | Range |
|---------|-----------|----------|-------|
| **Encoder 1** | Volume | Master output volume | 0.0 to 1.0 |
| **Encoder 2** | Filter Freq | Low-pass filter cutoff frequency | 20Hz to 20kHz |
| **Encoder 3** | Filter Res | Filter resonance/emphasis | 0.0 to 0.95 |
| **Encoder 4** | Delay FB | Delay feedback amount | 0.0 to 0.95 |
| **Encoder 5** | Reverb Mix | Reverb dry/wet mix | 0.0 (dry) to 1.0 (wet) |

### Bank B (Shift Held)

| Encoder | Parameter | Function | Range |
|---------|-----------|----------|-------|
| **Encoder 1** | Release Time | Oscillator envelope release time | 0.001s to 5.0s |
| **Encoder 2** | Delay Time | Delay effect time | 0.001s to 2.0s |
| **Encoder 3** | Reverb Size | Reverb room size | 0.0 to 1.0 |
| **Encoder 4** | Osc Wave | Oscillator waveform | Sine/Square/Saw/Triangle |
| **Encoder 5** | LFO Wave | LFO waveform | Sine/Square/Saw/Triangle |

### Button Functions

| Button | Function | Behavior |
|--------|----------|----------|
| **TRIGGER** | Trigger the siren | Press to start, release to stop |
| **PITCH ENV** | Cycle pitch envelope mode | Cycles through: none → up → down |
| **SHIFT** | Switch to Bank B | Hold to access Bank B parameters |
| **SHUTDOWN** | Safe system shutdown | Press to safely power down the Pi |

## Architecture

### Software Components

```
┌─────────────────────────────────────────┐
│           main.py                       │
│      (Application Entry Point)          │
└─────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌────────┐  ┌──────────┐  ┌──────────┐
│  GPIO  │  │  Synth   │  │  Audio   │
│Control │─▶│  Engine  │─▶│  Output  │
└────────┘  └──────────┘  └──────────┘
    │             │             │
    │         ┌───┴───┐         │
    │         │  DSP  │         │
    │         │Effects│         │
    │         └───────┘         │
    ▼                           ▼
[Encoders]                  [PCM5102]
[Switches]                   [I2S DAC]
```

### File Structure

```
poor-house-dub-v2/
├── main.py                  # Main application
├── synthesizer.py           # Audio synthesis engine
├── gpio_controller.py       # GPIO control surface handler
├── audio_output.py          # Audio output (PCM5102/I2S)
├── requirements.txt         # Python dependencies
├── setup.sh                 # Setup script
├── README.md               # This file
└── HARDWARE.md             # Hardware wiring guide
```

## Development

### Testing Components Individually

**Test audio synthesis:**
```bash
python3 synthesizer.py
```

**Test audio output:**
```bash
python3 audio_output.py
```

**Test GPIO controls:**
```bash
python3 gpio_controller.py
```

### Command Line Options

```bash
python3 main.py --help

Options:
  --sample-rate RATE        Audio sample rate (default: 48000)
  --buffer-size SIZE        Audio buffer size (default: 256)
  --audio-device INDEX      Audio device index
  --list-devices            List available audio devices
  --simulate               Run in simulation mode
  --interactive            Run in interactive mode
```

### Simulation Mode

Test without hardware using simulation mode:

```bash
python3 main.py --simulate --interactive

Commands:
  t - Trigger siren (press/release)
  p - Cycle pitch envelope mode
  s - Show status
  q - Quit
```

## Performance

- **CPU Usage:** ~15-25% on Raspberry Pi Zero 2 (single core)
- **Latency:** ~5ms (256 sample buffer @ 48kHz)
- **Sample Rate:** 48kHz (configurable)
- **Bit Depth:** 32-bit float internal, 24-bit I2S output

### Optimization Tips

1. **Reduce buffer underruns:**
   - Increase buffer size: `--buffer-size 512`
   - Disable unnecessary services
   - Use performance CPU governor

2. **Lower latency:**
   - Decrease buffer size: `--buffer-size 128`
   - Overclock Pi (not recommended for Pi Zero 2)

3. **CPU governor:**
   ```bash
   sudo apt-get install cpufrequtils
   sudo cpufreq-set -g performance
   ```

## Troubleshooting

### No audio output
```bash
# Check I2S configuration
grep "dtparam=i2s=on" /boot/config.txt
grep "dtoverlay=hifiberry-dac" /boot/config.txt

# List audio devices
python3 main.py --list-devices

# Test with ALSA
speaker-test -t wav -c 2 -D hw:0,0
```

### GPIO errors
```bash
# Check GPIO permissions
sudo usermod -a -G gpio pi

# Verify pin assignments
python3 gpio_controller.py
```

### Buffer underruns
```bash
# Increase buffer size
python3 main.py --buffer-size 512

# Check system load
top
```

See [HARDWARE.md](HARDWARE.md) for more troubleshooting tips.

## Technical Details

### Audio Processing Chain

```
Oscillator → Envelope → Filter → Delay → Reverb → Output
     ↑
    LFO (modulation)
```

### DSP Algorithms

- **Filter:** One-pole low-pass with resonance feedback
- **Delay:** Circular buffer with feedback and analog-style pitch-shifting modulation
- **Reverb:** Hybrid chamber reverb (early reflections + allpass diffusion + 6 damped comb filters)
  - Early reflections simulate first bounces off chamber walls
  - Allpass filters create density and smoothness
  - Damped comb filters with frequency-dependent feedback for warmth
  - Subtle modulation prevents metallic ringing
- **Envelope:** ADSR with configurable release

### GPIO Interrupt Handling

- Rotary encoders use quadrature decoding
- Hardware debouncing via software (50ms)
- Interrupt-driven for low latency
- Internal pull-up resistors enabled

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on actual hardware
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- PCM5102 DAC implementation based on HiFiBerry DAC
- DSP algorithms inspired by classic analog synthesizers
- Dub siren concept from Jamaican sound system culture

## Support

- **Issues:** https://github.com/yourusername/poor-house-dub-v2/issues
- **Documentation:** See [HARDWARE.md](HARDWARE.md)
- **Community:** [Add Discord/Forum link]

## Roadmap

- [ ] MIDI input support
- [ ] Preset save/load system
- [ ] OLED display for parameter feedback
- [ ] Additional effects (chorus, phaser)
- [ ] CV/Gate inputs for modular integration
- [ ] Web interface for remote control

---

**Built with ❤️ for the dub community**
