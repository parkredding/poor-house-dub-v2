# Dub Siren V2 - C++ Implementation

High-performance C++ implementation of the dub siren synthesizer, optimized for Raspberry Pi Zero 2 W.

## Why C++?

The Python implementation was hitting CPU limits (~80-100% on a single core), causing audio pulsing when adding features. This C++ version provides:

- **5-10x faster DSP processing**
- **True real-time performance**
- **Headroom for new features**
- **Foundation for future JUCE integration**

## Building

### Prerequisites

**On Raspberry Pi:**
```bash
sudo apt update
sudo apt install build-essential cmake libasound2-dev libpigpio-dev
```

**On macOS (for development):**
```bash
brew install cmake
```

### Build Commands

**Debug build (with symbols, no optimization):**
```bash
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug
make -j4
```

**Release build (optimized):**
```bash
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4
```

**Raspberry Pi optimized build:**
```bash
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_FOR_PI=ON
make -j4
```

## Usage

```bash
# Test in simulation mode (no hardware required)
./dubsiren --simulate --interactive

# Run on hardware
./dubsiren

# Specify audio device
./dubsiren --device hw:0,0

# Adjust buffer size for lower latency or fewer underruns
./dubsiren --buffer-size 512
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--sample-rate RATE` | Audio sample rate | 48000 |
| `--buffer-size SIZE` | Audio buffer size | 256 |
| `--device DEVICE` | ALSA audio device | "default" |
| `--simulate` | Run without hardware | false |
| `--interactive` | Keyboard control mode | false |
| `--help` | Show help message | - |

### Interactive Mode Commands

| Key | Action |
|-----|--------|
| `t` | Toggle trigger (start/stop siren) |
| `p` | Cycle pitch envelope mode |
| `s` | Show status |
| `h` | Show help |
| `q` | Quit |

## Architecture

```
┌─────────────────────────────────────────┐
│           main.cpp                       │
│      (Application Entry Point)           │
└─────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌────────┐  ┌──────────┐  ┌──────────┐
│  GPIO  │  │  Audio   │  │  Audio   │
│Control │─▶│  Engine  │─▶│  Output  │
└────────┘  └──────────┘  └──────────┘
                │
    ┌───────────┴───────────────┐
    │          DSP              │
    │  ┌──────┐ ┌──────┐       │
    │  │ Osc  │ │ Env  │       │
    │  └──────┘ └──────┘       │
    │  ┌──────┐ ┌──────┐       │
    │  │Filter│ │ LFO  │       │
    │  └──────┘ └──────┘       │
    │  ┌──────┐ ┌──────┐       │
    │  │Delay │ │Reverb│       │
    │  └──────┘ └──────┘       │
    └───────────────────────────┘
```

## File Structure

```
cpp/
├── CMakeLists.txt           # Build configuration
├── README.md                # This file
├── include/
│   ├── Common.h             # Shared types and utilities
│   ├── DSP/
│   │   ├── Oscillator.h     # PolyBLEP oscillator
│   │   ├── Envelope.h       # ADSR envelope
│   │   ├── LFO.h            # Low-frequency oscillator
│   │   ├── Filter.h         # Low-pass filter
│   │   ├── Delay.h          # Tape-style delay
│   │   └── Reverb.h         # Chamber reverb
│   ├── Audio/
│   │   ├── AudioEngine.h    # Main synth engine
│   │   └── AudioOutput.h    # ALSA audio output
│   └── Hardware/
│       └── GPIOController.h # Raspberry Pi GPIO
├── src/
│   ├── main.cpp             # Entry point
│   ├── DSP/
│   │   ├── Oscillator.cpp
│   │   ├── Envelope.cpp
│   │   ├── LFO.cpp
│   │   ├── Filter.cpp
│   │   ├── Delay.cpp
│   │   └── Reverb.cpp
│   ├── Audio/
│   │   ├── AudioEngine.cpp
│   │   └── AudioOutput.cpp
│   └── Hardware/
│       └── GPIOController.cpp
└── build/                   # Build output (git-ignored)
```

## Performance

Compared to Python implementation:

| Metric | Python | C++ | Improvement |
|--------|--------|-----|-------------|
| CPU Usage (single core) | 80-100% | 10-20% | **5-8x** |
| Latency (256 samples) | ~5ms | ~5ms | Same |
| Headroom for features | None | **60-80%** | Massive |

## Hardware Requirements

Same as Python version:
- Raspberry Pi Zero 2 W
- PCM5102 I2S DAC
- 5x Rotary encoders (KY-040)
- 4x Momentary switches
- 5V 2.5A power supply

See [HARDWARE.md](../HARDWARE.md) in the parent directory for wiring.

## Future Plans

- [ ] JUCE framework integration for VST3 plugin support
- [ ] Pitch envelope (now feasible with C++ performance)
- [ ] MIDI input support
- [ ] Preset save/load
- [ ] OLED display support

## License

MIT License - see [LICENSE](../LICENSE) file.
