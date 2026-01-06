# Hardware Configuration Guide

## Components Required

### Main Components
- **Raspberry Pi Zero 2 W** - Main controller
- **PCM5102 I2S DAC Module** - High-quality audio output
- **10x Rotary Encoders (360°)** - Continuous rotation encoders
- **2x Momentary Push Buttons** - Trigger switches
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

All rotary encoders need 2 GPIO pins (CLK and DT). All switches need 1 GPIO pin.

#### Row 1 - Encoders
| Control              | CLK Pin | DT Pin  | BCM GPIO |
|----------------------|---------|---------|----------|
| Volume               | 17      | 18      | GPIO 17, 18 (Note: GPIO 18 shared with I2S) |
| Low Pass Filter Freq | 27      | 22      | GPIO 27, 22 |
| Delay Effect Time    | 23      | 24      | GPIO 23, 24 |
| Reverb Size          | 25      | 8       | GPIO 25, 8  |

#### Row 2 - Encoders
| Control              | CLK Pin | DT Pin  | BCM GPIO |
|----------------------|---------|---------|----------|
| Oscillator Release   | 7       | 12      | GPIO 7, 12 |
| Filter Resonance     | 16      | 20      | GPIO 16, 20 |
| Delay Feedback       | 21      | 26      | GPIO 21, 26 (Note: GPIO 21 shared with I2S) |
| Reverb Dry/Wet       | 19      | 13      | GPIO 19, 13 (Note: GPIO 19 shared with I2S) |

#### Row 3 - Encoders & Switches
| Control              | CLK Pin | DT Pin  | BCM GPIO | Type |
|----------------------|---------|---------|----------|------|
| Oscillator Waveform  | 6       | 5       | GPIO 6, 5 | Encoder |
| LFO Waveform         | 11      | 9       | GPIO 11, 9 | Encoder |
| Airhorn Trigger      | 10      | -       | GPIO 10   | Switch |
| Siren Trigger        | 4       | -       | GPIO 4    | Switch |

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

```
┌────────────────────────────────────────────────┐
│                 DUB SIREN V2                   │
├────────────────────────────────────────────────┤
│                                                │
│  ┌───┐  ┌───┐  ┌───┐  ┌───┐                  │
│  │ ↻ │  │ ↻ │  │ ↻ │  │ ↻ │     Row 1        │
│  └───┘  └───┘  └───┘  └───┘                  │
│  Vol   Filt   Delay   Rev                    │
│                                                │
│  ┌───┐  ┌───┐  ┌───┐  ┌───┐                  │
│  │ ↻ │  │ ↻ │  │ ↻ │  │ ↻ │     Row 2        │
│  └───┘  └───┘  └───┘  └───┘                  │
│  Rel    Res     FB     Mix                    │
│                                                │
│  ┌───┐  ┌───┐  ┌───┐  ┌───┐                  │
│  │ ↻ │  │ ↻ │  │ ⏺ │  │ ⏺ │     Row 3        │
│  └───┘  └───┘  └───┘  └───┘                  │
│  Osc    LFO   AIRHORN SIREN                  │
│                                                │
└────────────────────────────────────────────────┘
```

## Important Notes

### GPIO Conflicts
⚠️ **Warning:** Some GPIO pins are shared between I2S and controls:
- GPIO 18, 19, 21 are used by I2S
- These are also assigned to some controls in the code

**Solution:** You have two options:
1. **Modify the pin assignments** in `gpio_controller.py` to use different GPIO pins
2. **Use an I2C GPIO expander** (like MCP23017) for the controls

### Recommended GPIO Pin Modification

To avoid conflicts, modify `gpio_controller.py` and use these alternative pins:

```python
ENCODER_PINS = {
    'volume': (2, 3),              # Row 1
    'filter_freq': (14, 15),
    'delay_time': (23, 24),
    'reverb_size': (25, 8),
    'release_time': (7, 12),       # Row 2
    'filter_res': (16, 20),
    'delay_feedback': (26, 6),
    'reverb_mix': (13, 5),
    'osc_waveform': (11, 9),       # Row 3
    'lfo_waveform': (27, 22),
}

SWITCH_PINS = {
    'airhorn': 10,
    'siren': 4,
}
```

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
- Check for conflicts with I2S pins

### Crackling Audio
- Increase buffer size in code
- Check power supply quality
- Reduce CPU load
- Add ferrite beads on power lines

## Advanced: Using I2C GPIO Expander

For a cleaner design without GPIO conflicts, use an MCP23017 I2C GPIO expander:

```python
# Install library
pip3 install adafruit-circuitpython-mcp230xx

# Connect MCP23017 to I2C (GPIO 2 & 3)
# Use expander pins for all controls
# Leaves I2S pins free
```

This requires modifying `gpio_controller.py` to use the expander library.
