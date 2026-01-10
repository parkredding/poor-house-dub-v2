# GPIO Wiring Guide for Pi Zero 2W Audio Test

Complete wiring instructions for connecting 2 rotary encoders and 1 momentary switch to control the audio test.

## Components Needed

- **2x Rotary Encoders** (KY-040 or similar)
- **1x Momentary Switch** (normally open, push button)
- **Breadboard** (optional, for easy prototyping)
- **Jumper wires**
- **Pi Zero 2W** with GPIO header

## Pin Assignments

### Encoder 1 - Volume Control
| Encoder Pin | Pi Zero 2W GPIO | Physical Pin |
|-------------|-----------------|--------------|
| CLK (A)     | GPIO 17         | Pin 11       |
| DT (B)      | GPIO 27         | Pin 13       |
| SW (button) | Not used        | -            |
| + (VCC)     | 3.3V            | Pin 1 or 17  |
| GND         | Ground          | Pin 9 or 14  |

### Encoder 2 - Delay Wet/Dry Control
| Encoder Pin | Pi Zero 2W GPIO | Physical Pin |
|-------------|-----------------|--------------|
| CLK (A)     | GPIO 22         | Pin 15       |
| DT (B)      | GPIO 23         | Pin 16       |
| SW (button) | Not used        | -            |
| + (VCC)     | 3.3V            | Pin 1 or 17  |
| GND         | Ground          | Pin 9 or 14  |

### Momentary Switch - Trigger
| Switch Pin  | Pi Zero 2W GPIO | Physical Pin |
|-------------|-----------------|--------------|
| One side    | GPIO 4          | Pin 7        |
| Other side  | Ground          | Pin 9 or 14  |

## Complete Wiring Diagram

```
Pi Zero 2W GPIO Header
┌────────────────────────────┐
│ 1  [3.3V]      [5V]     2  │
│ 3  GPIO 2      [5V]     4  │
│ 5  GPIO 3      [GND]    6  │  ← PCM5102 GND
│ 7  [GPIO 4]    GPIO 14  8  │  ← Trigger Switch
│ 9  [GND]       GPIO 15  10 │  ← Common GND
│ 11 [GPIO 17]   GPIO 18  12 │  ← Enc1-A, PCM5102 LCK
│ 13 [GPIO 27]   [GND]    14 │  ← Enc1-B
│ 15 [GPIO 22]   GPIO 23  16 │  ← Enc2-A, Enc2-B
│ 17 3.3V        GPIO 24  18 │  ← Encoder power
│ 19 GPIO 10     [GND]    20 │
│ 21 GPIO 9      GPIO 25  22 │
│ 23 GPIO 11     GPIO 8   24 │
│ 25 [GND]       GPIO 7   26 │
│ 27 ID_SD       ID_SC    28 │
│ 29 GPIO 5      [GND]    30 │
│ 31 GPIO 6      GPIO 12  32 │
│ 33 GPIO 13     [GND]    34 │
│ 35 [GPIO 19]   GPIO 16  36 │  ← PCM5102 BCK
│ 37 GPIO 26     GPIO 20  38 │
│ 39 [GND]       GPIO 21  40 │  ← PCM5102 DIN
└────────────────────────────┘

[Bracketed] = Used by this test
```

## Rotary Encoder Wiring

### Standard KY-040 Rotary Encoder Pinout
```
  ┌─────────┐
  │  Enc 1  │
  │ Volume  │
  └─────────┘
     │││││
     │││││
     ││││└─ GND ──────────────→ Pin 9 (GND)
     │││└── + (VCC) ──────────→ Pin 1 (3.3V)
     ││└─── SW (not used)
     │└──── DT (B) ───────────→ Pin 13 (GPIO 27)
     └───── CLK (A) ──────────→ Pin 11 (GPIO 17)

  ┌─────────┐
  │  Enc 2  │
  │  Delay  │
  └─────────┘
     │││││
     │││││
     ││││└─ GND ──────────────→ Pin 9 (GND)
     │││└── + (VCC) ──────────→ Pin 1 (3.3V)
     ││└─── SW (not used)
     │└──── DT (B) ───────────→ Pin 16 (GPIO 23)
     └───── CLK (A) ──────────→ Pin 15 (GPIO 22)
```

**Note:** If your encoder has pull-up resistors built-in, you can use them. The software enables internal pull-ups by default, so external resistors are optional.

## Momentary Switch Wiring

### Simple Push Button
```
     ┌─────────┐
     │ Trigger │
     │  Button │
     └─────────┘
        │   │
        │   └──────────────────→ Pin 9 (GND)
        └──────────────────────→ Pin 7 (GPIO 4)
```

**Important:** The switch is configured as **active low** (pressed = LOW/GND). The software enables internal pull-up resistors, so no external resistor is needed.

## Breadboard Layout Example

```
                    Pi Zero 2W
                 ┌───────────────┐
                 │   [GPIO]      │
                 └───────┬───────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         │           Breadboard          │
         │  ┌─────────────────────────┐  │
         │  │                         │  │
         ├──┤ Enc1    Enc2    Switch  │──┤
         │  │ (Vol)   (Delay) (Trig)  │  │
         │  │                         │  │
         │  │  [O]     [O]      [O]   │  │
         │  │   │       │        │    │  │
         │  └───┼───────┼────────┼────┘  │
         │      │       │        │       │
         └──────┴───────┴────────┴───────┘
            3.3V/GND Power & Signal
```

## Step-by-Step Assembly

### 1. Prepare the Breadboard (Optional)
- Use breadboard rails for 3.3V and GND distribution
- Keep wires short to minimize noise

### 2. Connect Power Rails
```bash
Pin 1 (3.3V)  → Breadboard + rail
Pin 9 (GND)   → Breadboard - rail
```

### 3. Connect Encoder 1 (Volume)
```bash
Enc1 CLK → GPIO 17 (Pin 11)
Enc1 DT  → GPIO 27 (Pin 13)
Enc1 +   → 3.3V rail
Enc1 GND → GND rail
```

### 4. Connect Encoder 2 (Delay)
```bash
Enc2 CLK → GPIO 22 (Pin 15)
Enc2 DT  → GPIO 23 (Pin 16)
Enc2 +   → 3.3V rail
Enc2 GND → GND rail
```

### 5. Connect Trigger Switch
```bash
Switch pin 1 → GPIO 4 (Pin 7)
Switch pin 2 → GND rail
```

## Testing the Connections

### 1. Check Continuity (Power Off!)
Before powering on, verify:
- No shorts between 3.3V and GND
- All encoder pins properly connected
- Switch properly connected

### 2. Power On and Test
```bash
cd ~/poor-house-dub-v2
python3 pi_audio_test.py --gpio
```

### 3. Verify Each Control

**Encoder 1 (Volume):**
- Turn clockwise → Volume should increase
- Turn counter-clockwise → Volume should decrease
- Display should show: `Volume: XXX%`

**Encoder 2 (Delay):**
- Turn clockwise → Delay mix should increase
- Turn counter-clockwise → Delay mix should decrease
- Display should show: `Delay: XXX%`

**Trigger Switch:**
- Press → Should see `[TRIGGER PRESSED]` and hear tone
- Release → Should see `[TRIGGER RELEASED]` and tone stops

## Troubleshooting

### Encoder Not Responding
1. **Check wiring:**
   ```bash
   # Test GPIO read (encoder should be LOW when idle)
   python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP); print(GPIO.input(17))"
   ```
   Should print: `1` (HIGH)

2. **Swap CLK and DT** if encoder direction is reversed

3. **Check for loose connections**

### Switch Not Responding
1. **Test switch continuity** with multimeter
2. **Verify GPIO 4 is not used elsewhere**
3. **Try different switch** (some switches are normally closed)

### Encoder Direction Reversed
- Swap CLK and DT wires
- Or modify code: swap `pin_a` and `pin_b` in `pi_test_gpio.py`

### Noisy/Jittery Encoders
- Add 0.1µF capacitors between each signal pin and GND
- Use shorter wires
- Keep wires away from PCM5102 I2S signals

## Advanced: Custom Pin Assignments

To use different GPIO pins, edit `pi_test_gpio.py`:

```python
gpio = TestGPIOController(
    synth,
    volume_pins=(17, 27),   # Change these
    delay_pins=(22, 23),    # Change these
    trigger_pin=4           # Change this
)
```

## Compatible with PCM5102 DAC

This GPIO setup is fully compatible with the PCM5102 DAC wiring. Pins used:

**PCM5102 I2S Pins:**
- GPIO 18 (Pin 12) - LCK
- GPIO 19 (Pin 35) - BCK
- GPIO 21 (Pin 40) - DIN

**GPIO Test Control Pins (non-conflicting):**
- GPIO 17, 27 - Encoder 1
- GPIO 22, 23 - Encoder 2
- GPIO 4 - Trigger

**Shared:**
- 3.3V (Pin 1) - Both PCM5102 and encoders
- GND (Pins 6, 9, 14, 20, etc.) - Common ground

## Safety Notes

⚠️ **Important:**
- Never connect encoders to 5V (use 3.3V only!)
- Double-check wiring before powering on
- Disconnect GPIO during flashing/programming
- Use GPIO-safe components (3.3V logic level)

## Enclosure Mounting Tips

When mounting in an enclosure:
- Mount encoders on front panel
- Use panel-mount encoders with nuts
- Mount switch within easy reach
- Keep wires away from audio path to minimize noise
- Use shielded cable for long runs (>6 inches)

## Shopping List

Recommended components:

- **Rotary Encoders:** KY-040 or EC11 compatible (2x)
- **Momentary Switch:** 6mm tactile switch or arcade button (1x)
- **Breadboard:** 400-point solderless breadboard
- **Jumper Wires:** Male-to-female, 10cm length
- **Optional:** 0.1µF ceramic capacitors for debouncing

## Next Steps

Once wired and tested:

1. **Run the GPIO test:**
   ```bash
   python3 pi_audio_test.py --gpio
   ```

2. **Verify each control works**

3. **Proceed to full synthesizer** with full GPIO control surface

4. **Build enclosure** for permanent installation

Happy building! 🎛️
