# GPIO Wiring Guide for Dub Siren V2

Complete wiring instructions for the Poor House Dub V2 control surface with shift button bank switching.

## Overview

The Dub Siren V2 uses **5 rotary encoders** with a **shift button** to control 10 parameters across 2 banks, plus 3 additional function buttons.

**Total GPIO pins: 14** (10 for encoders + 4 for buttons)

### Bank System
- **Bank A (Normal):** Primary dub controls (volume, filter, delay, reverb)
- **Bank B (Shift held):** Secondary controls (envelopes, waveforms, timing)

## Components Needed

- **5x Rotary Encoders** (KY-040 or EC11 compatible)
- **4x Momentary Switches** (Trigger, Pitch Env, Shift, Shutdown)
- **Breadboard** or **PCB** for prototyping
- **Jumper wires** (male-to-female, 10-15cm)
- **Pi Zero 2W** with 40-pin GPIO header
- **Optional:** Panel-mount encoders with knobs for enclosure

## Critical: I2S Pin Avoidance

⚠️ **DO NOT USE** these GPIO pins - they are reserved for PCM5102 DAC audio:
- **GPIO 18** (Pin 12) - I2S LRCLK
- **GPIO 19** (Pin 35) - I2S BCLK
- **GPIO 21** (Pin 40) - I2S DOUT

The pin assignments below carefully avoid these pins.

## Complete Pin Assignments

### 5 Rotary Encoders (10 GPIO pins)

| Encoder | Function (Bank A / Bank B) | CLK Pin | DT Pin | Physical Pins |
|---------|---------------------------|---------|--------|---------------|
| **Encoder 1** | Volume / Release Time | GPIO 17 | GPIO 2 | Pin 11, Pin 3 |
| **Encoder 2** | Filter Freq / Delay Time | GPIO 27 | GPIO 22 | Pin 13, Pin 15 |
| **Encoder 3** | Base Freq / Filter Res | GPIO 23 | GPIO 24 | Pin 16, Pin 18 |
| **Encoder 4** | Delay Feedback / Osc Wave | GPIO 20 | GPIO 26 | Pin 38, Pin 37 |
| **Encoder 5** | Reverb Mix / Reverb Size | GPIO 14 | GPIO 13 | Pin 8, Pin 33 |

### 4 Buttons (4 GPIO pins)

| Button | Function | GPIO Pin | Physical Pin |
|--------|----------|----------|--------------|
| **Trigger** | Main sound trigger (hold to play) | GPIO 4 | Pin 7 |
| **Pitch Env** | Cycle pitch envelope (none/up/down) | GPIO 10 | Pin 19 |
| **Shift** | Access Bank B parameters | GPIO 15 | Pin 10 |
| **Shutdown** | Safe system shutdown | GPIO 3 | Pin 5 |

### Power Connections

| Connection | Pin(s) |
|------------|--------|
| **3.3V** (encoder power) | Pin 1, Pin 17 |
| **GND** (common ground) | Pins 6, 9, 14, 20, 25, 30, 34, 39 |

## Parameter Bank Mapping

### Bank A (Normal - no shift)
1. **Volume** - Master output level (0-100%)
2. **Filter Frequency** - Low-pass filter cutoff (20-20000 Hz)
3. **Base Frequency** - Oscillator pitch (50-2000 Hz)
4. **Delay Feedback** - Echo repeats (0-95%)
5. **Reverb Mix** - Reverb dry/wet (0-100%)

### Bank B (Hold Shift)
1. **Release Time** - Envelope decay (0.001-5.0s)
2. **Delay Time** - Echo timing (0.001-2.0s)
3. **Filter Resonance** - Filter emphasis (0-95%)
4. **Osc Waveform** - Oscillator shape (Sine/Square/Saw/Triangle)
5. **Reverb Size** - Room size (0-100%)

## Detailed Wiring Diagrams

### GPIO Header Overview (Pi Zero 2W)

```
Raspberry Pi Zero 2W GPIO Header (40-pin)
┌────────────────────────────────────────┐
│ 1  [3.3V]      [5V]     2  │  ← Encoder power
│ 3  [GPIO 2]    [5V]     4  │  ← Enc1-DT
│ 5  [GPIO 3]    [GND]    6  │  ← Shutdown, PCM5102 GND
│ 7  [GPIO 4]    GPIO 14  8  │  ← Trigger
│ 9  [GND]       GPIO 15  10 │  ← Common GND, Shift
│ 11 [GPIO 17]   GPIO 18  12 │  ← Enc1-CLK, I2S-LCK (DO NOT USE 18!)
│ 13 [GPIO 27]   [GND]    14 │  ← Enc2-CLK
│ 15 [GPIO 22]   GPIO 23  16 │  ← Enc2-DT, Enc3-CLK
│ 17 3.3V        GPIO 24  18 │  ← Enc3-DT
│ 19 GPIO 10     [GND]    20 │  ← Pitch Env
│ 21 GPIO 9      GPIO 25  22 │
│ 23 GPIO 11     GPIO 8   24 │
│ 25 [GND]       GPIO 7   26 │
│ 27 ID_SD       ID_SC    28 │
│ 29 GPIO 5      [GND]    30 │
│ 31 GPIO 6      GPIO 12  32 │
│ 33 [GPIO 13]   [GND]    34 │  ← Enc5-DT
│ 35 GPIO 19     GPIO 16  36 │  ← I2S-BCK (DO NOT USE 19!)
│ 37 [GPIO 26]   GPIO 20  38 │  ← Enc4-DT, Enc4-CLK
│ 39 [GND]       GPIO 21  40 │  ← I2S-DOUT (DO NOT USE 21!)
└────────────────────────────────────────┘

[Bracketed] = Used by Dub Siren V2
```

### Rotary Encoder Wiring (All 5 Encoders)

Standard KY-040/EC11 rotary encoder pinout:
```
┌─────────┐
│ Encoder │
└─────────┘
   │││││
   │││││
   ││││└─ GND      → Common GND
   │││└── + (VCC)  → 3.3V
   ││└─── SW (not used)
   │└──── DT (B)   → See table above
   └───── CLK (A)  → See table above
```

**Encoder 1 (Volume / Release Time):**
```
CLK (A) → Pin 11 (GPIO 17)
DT (B)  → Pin 3  (GPIO 2)
+ (VCC) → Pin 1  (3.3V)
GND     → Pin 9  (GND)
```

**Encoder 2 (Filter Freq / Delay Time):**
```
CLK (A) → Pin 13 (GPIO 27)
DT (B)  → Pin 15 (GPIO 22)
+ (VCC) → Pin 1  (3.3V)
GND     → Pin 9  (GND)
```

**Encoder 3 (Base Freq / Filter Res):**
```
CLK (A) → Pin 16 (GPIO 23)
DT (B)  → Pin 18 (GPIO 24)
+ (VCC) → Pin 1  (3.3V)
GND     → Pin 9  (GND)
```

**Encoder 4 (Delay FB / Osc Wave):**
```
CLK (A) → Pin 38 (GPIO 20)
DT (B)  → Pin 37 (GPIO 26)
+ (VCC) → Pin 17 (3.3V)
GND     → Pin 39 (GND)
```

**Encoder 5 (Reverb Mix / Reverb Size):**
```
CLK (A) → Pin 8  (GPIO 14)
DT (B)  → Pin 33 (GPIO 13)
+ (VCC) → Pin 1  (3.3V)
GND     → Pin 9  (GND)
```

### Button Wiring (All 4 Buttons)

All buttons are wired as **active low** (pressed = connects to GND). Internal pull-ups are enabled in software.

**Trigger Button (Main Sound):**
```
Pin 1 → Pin 7  (GPIO 4)
Pin 2 → Pin 9  (GND)
```

**Pitch Envelope Button (Cycle Modes):**
```
Pin 1 → Pin 19 (GPIO 10)
Pin 2 → Pin 20 (GND)
```

**Shift Button (Access Bank B):**
```
Pin 1 → Pin 10 (GPIO 15)
Pin 2 → Pin 9  (GND)
```

**Shutdown Button (Power Off):**
```
Pin 1 → Pin 5  (GPIO 3)
Pin 2 → Pin 6  (GND)
```

## Breadboard Layout Example

```
                Raspberry Pi Zero 2W
             ┌─────────────────────────┐
             │      [40-pin GPIO]      │
             │   PCM5102 DAC attached  │
             └───────────┬─────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                                         │
    │           Breadboard / Perfboard        │
    │  ┌────────────────────────────────────┐ │
    │  │                                    │ │
    │  │  [Enc1] [Enc2] [Enc3] [Enc4] [Enc5]│ │
    │  │   Vol  Filter  Pitch Delay  Reverb │ │
    │  │                                    │ │
    │  │  [Trig] [Pitch] [Shift] [Shutdown]│ │
    │  │                                    │ │
    │  └────────────────────────────────────┘ │
    │                                         │
    └─────────────────────────────────────────┘
         3.3V, GND, and Signal connections
```

## Step-by-Step Assembly

### 1. Prepare Your Workspace
- **Power off** the Raspberry Pi
- Gather all components
- Use ESD protection (wrist strap recommended)

### 2. Connect Power Rails
```
Pin 1  (3.3V) → Breadboard + rail
Pin 9  (GND)  → Breadboard - rail
Pin 17 (3.3V) → Breadboard + rail (additional power)
Pin 39 (GND)  → Breadboard - rail (additional ground)
```

### 3. Wire Encoders (in order)
Wire one encoder at a time and test:

```bash
# Encoder 1
CLK: GPIO 17 (Pin 11), DT: GPIO 2 (Pin 3)

# Encoder 2
CLK: GPIO 27 (Pin 13), DT: GPIO 22 (Pin 15)

# Encoder 3
CLK: GPIO 23 (Pin 16), DT: GPIO 24 (Pin 18)

# Encoder 4
CLK: GPIO 20 (Pin 38), DT: GPIO 26 (Pin 37)

# Encoder 5
CLK: GPIO 14 (Pin 8), DT: GPIO 13 (Pin 33)
```

### 4. Wire Buttons
```bash
Trigger:   GPIO 4  (Pin 7)  to GND
Pitch Env: GPIO 10 (Pin 19) to GND
Shift:     GPIO 15 (Pin 10) to GND
Shutdown:  GPIO 3  (Pin 5)  to GND
```

### 5. Double-Check Connections
⚠️ **Critical checks before powering on:**
- [ ] No shorts between 3.3V and GND
- [ ] No connections to GPIO 18, 19, or 21 (I2S pins)
- [ ] All encoder power pins to 3.3V (NOT 5V!)
- [ ] All grounds connected to common GND

## Testing the Control Surface

### 1. Power On and Start Service
```bash
cd ~/poor-house-dub-v2
sudo systemctl start dubsiren.service
sudo journalctl -u dubsiren.service -f
```

### 2. Test Each Encoder (Bank A)

**Encoder 1 (Volume):**
- Turn clockwise → Should see `[Bank A] volume: 0.520`
- Turn counter-clockwise → Should see `[Bank A] volume: 0.480`

**Encoder 2 (Filter Frequency):**
- Turn → Should see `[Bank A] filter_freq: XXXX.000`

**Encoder 3 (Base Frequency):**
- Turn → Should see `[Bank A] base_freq: XXX.XXX`

**Encoder 4 (Delay Feedback):**
- Turn → Should see `[Bank A] delay_feedback: 0.XXX`

**Encoder 5 (Reverb Mix):**
- Turn → Should see `[Bank A] reverb_mix: 0.XXX`

### 3. Test Shift Button (Bank B)

**Hold Shift and turn encoders:**
- Should see `Bank B active`
- Encoder 1 → `[Bank B] release: X.XXX`
- Encoder 2 → `[Bank B] delay_time: X.XXX`
- Encoder 3 → `[Bank B] filter_res: 0.XXX`
- Encoder 4 → `[Bank B] osc_waveform: Sine/Square/Saw/Triangle`
- Encoder 5 → `[Bank B] reverb_size: 0.XXX`

**Release Shift:**
- Should see `Bank A active`
- Encoders return to Bank A parameters

### 4. Test Function Buttons

**Trigger Button:**
- Press and hold → Should hear dub siren sound
- Release → Sound stops

**Pitch Envelope Button:**
- Press repeatedly → Cycles: `none` → `up` → `down` → `none`

**Shutdown Button:**
- Press → System shuts down safely after 1 second

## Troubleshooting

### Encoder Not Responding
1. **Check wiring** - verify CLK and DT pins
2. **Test GPIO:**
   ```bash
   python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); \
   GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP); \
   print('GPIO 17:', GPIO.input(17))"
   ```
   Should print `GPIO 17: 1`

3. **Swap CLK and DT** if direction is reversed

### Button Not Responding
1. **Check switch type** - must be normally open (NO)
2. **Test continuity** with multimeter
3. **Verify GPIO not shorted to ground**

### Shift Button Stuck
- Check for debris in switch
- Verify wiring (GPIO 15 to GND)
- Test switch with multimeter

### I2S Audio Conflict Error
```
RuntimeError: Failed to add edge detection
```
**Cause:** Using GPIO 18, 19, or 21 (reserved for I2S audio)
**Solution:** Verify pin assignments match this guide exactly

### Encoder Direction Reversed
- **Quick fix:** Swap CLK and DT wires
- **Code fix:** Edit `gpio_controller.py` encoder pin order

### Noisy/Jittery Encoders
- Add **0.1µF capacitors** between each signal pin and GND
- Use **shorter wires** (<15cm recommended)
- **Twist CLK/DT pairs** together to reduce noise
- Keep wires away from I2S audio signals

## Panel Mount Installation

For a permanent enclosure build:

### Recommended Layout
```
┌──────────────────────────────────┐
│                                  │
│  [1]    [2]    [3]    [4]   [5]  │  ← Encoders
│  Vol  Filter Pitch  Delay  Rev   │
│                                  │
│  (Trigger)  (Pitch)  (Shift)     │  ← Buttons
│                                  │
│  [Power LED]        (Shutdown)   │
│                                  │
└──────────────────────────────────┘
```

### Tips
- Use **panel-mount encoders** with mounting nuts
- **Label each knob** with bank functions:
  - `VOL / REL` (Volume / Release Time)
  - `FILT / DLY` (Filter Freq / Delay Time)
  - `PITCH / RES` (Base Freq / Filter Res)
  - `FB / WAVE` (Delay Feedback / Osc Wave)
  - `MIX / SIZE` (Reverb Mix / Reverb Size)
- Mount **Shift button** in easy reach
- Add **LED indicator** for shift/bank status (optional)
- Use **arcade buttons** for trigger (satisfying tactile feel)

## Shopping List

### Encoders (5x)
- **KY-040** rotary encoder modules, OR
- **EC11** encoders with breakout boards
- Encoder knobs (recommend 20mm diameter)

### Buttons (4x)
- **Trigger:** Arcade button (30mm) or large tactile switch
- **Pitch/Shift:** 6mm tactile switches or small arcade buttons
- **Shutdown:** Latching switch or recessed button (prevent accidents)

### Wiring
- **Male-to-female jumper wires** (20-pack, 15cm length)
- **Breadboard** (400-point) for prototyping, OR
- **Perfboard** (70x90mm) for permanent build

### Optional
- **0.1µF ceramic capacitors** (10-pack) for noise reduction
- **Panel-mount encoder brackets**
- **Enclosure** (Hammond 1590DD or similar)
- **Status LEDs** (3mm, various colors)

## Advanced: Custom Pin Configuration

To use different GPIO pins, edit `gpio_controller.py`:

```python
ENCODER_PINS = {
    'encoder_1': (17, 2),    # Change these
    'encoder_2': (27, 22),   # Change these
    'encoder_3': (23, 24),   # Change these
    'encoder_4': (20, 26),   # Change these
    'encoder_5': (14, 13),   # Change these
}

SWITCH_PINS = {
    'trigger': 4,      # Change these
    'pitch_env': 10,   # Change these
    'shift': 15,       # Change these
    'shutdown': 3,     # Change these
}
```

**Remember:** Avoid GPIOs 18, 19, 21 (I2S audio)!

## Safety Notes

⚠️ **Critical Safety:**
- **NEVER** connect encoders to 5V (3.3V ONLY!)
- **Double-check** all wiring before powering on
- **Avoid** GPIO 18, 19, 21 (will conflict with audio)
- **Use ESD protection** when handling components
- **Disconnect GPIO** during SD card flashing

## Next Steps

1. ✅ Wire according to this guide
2. ✅ Test with `sudo journalctl -u dubsiren.service -f`
3. ✅ Verify all encoders and buttons respond
4. ✅ Test shift button bank switching
5. ✅ Build enclosure for permanent installation
6. 🎵 Make dub music!

Happy building! 🎛️🔊
