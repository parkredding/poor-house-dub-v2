# Hardware Configuration Guide

## Components Required

### Main Components
- **Raspberry Pi Zero 2 W** - Main controller
- **PCM5102 I2S DAC Module** - High-quality audio output
- **5x Rotary Encoders (360°)** - Continuous rotation encoders (KY-040 or similar)
- **4x Momentary Push Buttons** - Trigger, Pitch Envelope, Shift, and Shutdown switches
- **Power Supply** - 5V 2.5A recommended

### Optional Components
- Enclosure/case
- Knobs for rotary encoders
- PCB or perfboard for mounting
- Connecting wires (Dupont cables recommended)

## PCM5102 DAC Wiring

The PCM5102 connects to the Raspberry Pi via I2S (Inter-IC Sound).

### Connection Table

| PCM5102 Pin | Raspberry Pi Pin | GPIO/Function | Notes |
|-------------|------------------|---------------|-------|
| VIN         | Pin 1            | 3.3V          | Power |
| GND         | Pin 6            | Ground        | Ground |
| LCK         | Pin 12           | GPIO 18       | I2S LRCLK (Word Clock) |
| BCK         | Pin 35           | GPIO 19       | I2S BCLK (Bit Clock) |
| DIN         | Pin 40           | GPIO 21       | I2S DOUT (Data) |
| SCK         | -                | GND           | Tie to GND for 48kHz |
| FLT         | -                | GND           | Normal filter latency |
| FMT         | -                | GND           | I2S format |
| XMT         | -                | 3.3V or GND   | Soft mute (GND=normal) |

**Note:** Some PCM5102 boards have these configuration pins already set via solder jumpers.

### I2S Pin Diagram (Physical Pin Layout)

```
Raspberry Pi Zero 2 (Top View)
    3.3V  [1]  [2]  5V
   GPIO2  [3]  [4]  5V
   GPIO3  [5]  [6]  GND  <--- PCM5102 GND
   GPIO4  [7]  [8]  GPIO14
     GND  [9]  [10] GPIO15
  GPIO17  [11] [12] GPIO18 <--- PCM5102 LCK
  GPIO27  [13] [14] GND
  GPIO22  [15] [16] GPIO23
    3.3V  [17] [18] GPIO24
  GPIO10  [19] [20] GND
   GPIO9  [21] [22] GPIO25
  GPIO11  [23] [24] GPIO8
     GND  [25] [26] GPIO7
   GPIO0  [27] [28] GPIO1
   GPIO5  [29] [30] GND
   GPIO6  [31] [32] GPIO12
  GPIO13  [33] [34] GND
  GPIO19  [35] [36] GPIO16 <--- PCM5102 BCK
  GPIO26  [37] [38] GPIO20
     GND  [39] [40] GPIO21 <--- PCM5102 DIN
```

## Control Surface GPIO Wiring

### GPIO Pin Assignments (BCM Numbering)

The design uses **5 rotary encoders** with **bank switching** to access 10 parameters. A shift button switches between Bank A (normal mode) and Bank B (shift held).

**Total GPIO pins used: 14** (10 encoder pins + 4 button pins)

⚠️ **Critical:** This design avoids GPIO 18, 19, and 21 which are reserved for I2S audio (PCM5102 DAC).

#### Rotary Encoders (5 encoders × 2 pins each = 10 pins)

| Encoder | CLK Pin | DT Pin | Bank A Parameter | Bank B Parameter (Shift Held) |
|---------|---------|--------|------------------|-------------------------------|
| **Encoder 1** | GPIO 17 | GPIO 2  | Volume           | Release Time |
| **Encoder 2** | GPIO 27 | GPIO 22 | Filter Frequency | Delay Time |
| **Encoder 3** | GPIO 23 | GPIO 24 | Filter Resonance | Reverb Size |
| **Encoder 4** | GPIO 20 | GPIO 26 | Delay Feedback   | Oscillator Waveform |
| **Encoder 5** | GPIO 14 | GPIO 13 | Reverb Mix       | LFO Waveform |

#### Momentary Switches (4 buttons)

| Button | GPIO Pin | Function |
|--------|----------|----------|
| **Trigger** | GPIO 4 | Main siren trigger (press/release) |
| **Pitch Envelope** | GPIO 10 | Cycle pitch envelope mode (none/up/down) |
| **Shift** | GPIO 15 | Hold to access Bank B parameters |
| **Shutdown** | GPIO 3 | Safe system shutdown |

### Rotary Encoder Wiring

Each rotary encoder has 3 pins:
- **CLK** (Clock) - Connect to CLK GPIO pin
- **DT** (Data) - Connect to DT GPIO pin
- **GND** - Connect to ground

```
Encoder Wiring:
  +-------+
  |  CLK  |------> GPIO CLK pin
  |  DT   |------> GPIO DT pin
  |  GND  |------> Ground
  +-------+
```

**Note:** The code uses internal pull-up resistors, so no external resistors needed.

### Momentary Switch Wiring

Each switch has 2 pins:
- One pin to GPIO
- One pin to Ground

```
Switch Wiring:
  +-------+
  |  Pin1 |------> GPIO pin
  |  Pin2 |------> Ground
  +-------+
```

**Note:** Switches are active-low (pressed = LOW signal).

## Control Surface Layout (Physical)

### Suggested Layout

```
┌──────────────────────────────────────────────────┐
│              DUB SIREN V2                        │
│         (Bank Switching Design)                  │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐       │
│  │ ↻1 │  │ ↻2 │  │ ↻3 │  │ ↻4 │  │ ↻5 │       │
│  └────┘  └────┘  └────┘  └────┘  └────┘       │
│                                                  │
│  Bank A:  Vol   Freq    Res     D.FB   R.Mix   │
│  Bank B:  Rel   Delay  R.Size  Osc.W  LFO.W    │
│                                                  │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐              │
│  │  ⏺  │ │  ⏺  │ │  ⏺  │ │  ⏺  │              │
│  └─────┘ └─────┘ └─────┘ └─────┘              │
│  TRIGGER PITCH  SHIFT  SHUTDOWN                │
│           ENV                                    │
│                                                  │
└──────────────────────────────────────────────────┘
```

**How it works:**
- **Normal operation (Bank A):** Encoders control Volume, Filter Freq, Filter Res, Delay FB, Reverb Mix
- **Hold SHIFT (Bank B):** Same encoders now control Release, Delay Time, Reverb Size, Osc Waveform, LFO Waveform
- **TRIGGER:** Press to start siren, release to stop
- **PITCH ENV:** Cycles through pitch envelope modes (none → up → down)
- **SHUTDOWN:** Safely powers down the Raspberry Pi

## Important Notes

### I2S Audio Pin Protection

✅ **No GPIO conflicts:** This design carefully avoids GPIO 18, 19, and 21 which are used by the PCM5102 DAC for I2S audio:
- **GPIO 18** - I2S LRCLK (Word Clock)
- **GPIO 19** - I2S BCLK (Bit Clock)
- **GPIO 21** - I2S DOUT (Data)

The 14 GPIO pins used by the control surface (GPIO 2, 3, 4, 10, 13, 14, 15, 17, 20, 22, 23, 24, 26, 27) are all safe to use alongside I2S.

### Bank Switching Operation

The shift button enables access to 10 parameters with only 5 encoders:

**Bank A (default):**
- Immediate sound shaping: Volume, Filter Freq, Filter Res, Delay FB, Reverb Mix

**Bank B (shift held):**
- Advanced parameters: Release Time, Delay Time, Reverb Size, Oscillator Waveform, LFO Waveform

When you hold the shift button, all 5 encoders immediately control their Bank B parameters. Release shift to return to Bank A.

## Power Considerations

- **Raspberry Pi Zero 2:** ~400mA typical, 1A peak
- **PCM5102 DAC:** ~10mA
- **Rotary Encoders:** Negligible (passive)
- **LED indicators (optional):** ~20mA each

**Recommended:** 5V 2.5A power supply with good quality USB cable.

## Testing Procedure

1. **Test I2S audio first** (without controls)
   ```bash
   python3 audio_output.py
   ```

2. **Test individual encoders**
   ```bash
   python3 gpio_controller.py
   ```

3. **Test complete system**
   ```bash
   python3 main.py --simulate
   python3 main.py
   ```

## Troubleshooting

### No Audio Output
- Check I2S wiring (especially LCK, BCK, DIN)
- Verify I2S is enabled: `dtparam=i2s=on` in `/boot/config.txt`
- Check ALSA device: `aplay -l`
- Test with: `speaker-test -t wav -c 2`

### Encoders Not Working
- Check pull-up resistors are enabled (done in code)
- Verify GPIO pin numbers (BCM vs physical numbering)
- Test with multimeter or oscilloscope
- Run GPIO cleanup before starting: `python3 gpio_cleanup.py`
- Check encoder wiring (CLK and DT might be swapped)

### Crackling Audio
- Increase buffer size in code
- Check power supply quality
- Reduce CPU load
- Add ferrite beads on power lines

## Additional Resources

For complete wiring diagrams and pin-by-pin instructions, see:
- **[GPIO_WIRING_GUIDE.md](GPIO_WIRING_GUIDE.md)** - Detailed step-by-step wiring guide with diagrams
- **[README.md](README.md)** - Complete project documentation and feature overview
- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup and installation guide
