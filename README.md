# Dub Siren V2

A professional dub siren synthesizer built on Raspberry Pi Zero 2 with PCM5102 I2S DAC.

![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%20Zero%202-red)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Real-time Audio Synthesis**
  - Multiple oscillator waveforms (Sine, Square, Saw, Triangle)
  - Envelope generator with adjustable release
  - Low-frequency oscillator (LFO) for modulation

- **Professional DSP Effects**
  - Low-pass filter with resonance control
  - Delay/echo effect with feedback
  - Reverb effect with size and dry/wet controls

- **Hardware Control Surface**
  - 10 rotary encoders (360° continuous)
  - 2 momentary trigger switches
  - Airhorn and siren presets

- **High-Quality Audio**
  - PCM5102 I2S DAC for pristine audio output
  - 48kHz sample rate
  - Low latency real-time processing

## Quick Start

### Prerequisites

- Raspberry Pi Zero 2 W
- PCM5102 DAC module
- 10x rotary encoders
- 2x momentary switches
- MicroSD card (8GB+)
- 5V 2.5A power supply

### Installation

1. **Flash Raspberry Pi OS**
   ```bash
   # Use Raspberry Pi Imager to flash Raspberry Pi OS Lite (64-bit)
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/poor-house-dub-v2.git
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

```
Row 1:  [Volume]     [Filter Freq]   [Delay Time]    [Reverb Size]
Row 2:  [Release]    [Filter Res]    [Delay FB]      [Reverb Mix]
Row 3:  [Osc Wave]   [LFO Wave]      [AIRHORN]       [SIREN]
```

### Control Descriptions

| Control | Function | Range |
|---------|----------|-------|
| **Volume** | Master output volume | 0.0 to 1.0 |
| **Filter Freq** | Low-pass filter cutoff frequency | 20Hz to 20kHz |
| **Delay Time** | Delay effect time | 0.001s to 2.0s |
| **Reverb Size** | Reverb room size | 0.0 to 1.0 |
| **Release** | Oscillator envelope release time | 0.001s to 5.0s |
| **Filter Res** | Filter resonance/emphasis | 0.0 to 0.95 |
| **Delay FB** | Delay feedback amount | 0.0 to 0.95 |
| **Reverb Mix** | Reverb dry/wet mix | 0.0 (dry) to 1.0 (wet) |
| **Osc Wave** | Oscillator waveform | Sine/Square/Saw/Triangle |
| **LFO Wave** | LFO waveform | Sine/Square/Saw/Triangle |
| **AIRHORN** | Trigger airhorn sound | Momentary switch |
| **SIREN** | Trigger siren sound | Momentary switch |

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
  1 - Trigger airhorn
  2 - Trigger siren
  r - Release
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
- **Delay:** Circular buffer with feedback
- **Reverb:** Schroeder reverb (4 parallel comb filters)
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
