# Dub Siren V2 - PCB Layout Specification
## For PCB Designer

**Document Version:** 1.0
**Date:** 2026-01-27
**Project:** Poor House Dub Siren V2 Control Surface PCB

---

## Overview

This document specifies the physical layout for a front-panel mounted control surface PCB. All rotary encoders, switches, and buttons mount **through the PCB to the front panel** of the enclosure, with the PCB positioned behind the panel. The front panel will have pre-cut mounting holes aligned with this layout.

**Key Design Principles:**
- All user controls mount to front panel (panel-mount components)
- PCB sits behind front panel and provides electrical connections only
- 45mm center-to-center spacing for all controls (allows large knobs)
- 3×3 matrix layout for intuitive operation
- Compact design suitable for desktop/rack mounting

---

## Board Dimensions

**Recommended PCB Size:** 150mm (W) × 180mm (H)

This provides:
- 30mm left/right margins from outer controls
- 30mm top margin (LED at 15mm from top)
- 30mm bottom margin
- Adequate space for routing and mounting holes

---

## Component Layout Matrix

### Grid Overview (3×3 Matrix + LED)

```
                    ┌─────────────────────────────┐
                    │         [  LED  ]           │  ← 15mm from top
                    │                             │
     Row 1 (30mm) → │  [E1]    [E2]    [E3]      │
                    │                             │
                    │                             │
     Row 2 (75mm) → │  [E4]    [E5]  [PITCH]     │
                    │                             │
                    │                             │
    Row 3 (120mm) → │ [WAVE]  [BANK]  [TRIG]     │
                    │                             │
                    └─────────────────────────────┘

    Column X-Pos:      30mm    75mm    120mm
```

### Component Positions (Center Coordinates)

All measurements from **TOP-LEFT corner** of PCB (0,0).

| Component | Type | Row | Column | X (mm) | Y (mm) | Notes |
|-----------|------|-----|--------|--------|--------|-------|
| **LED** | WS2812 5mm | - | Center | 75 | 15 | Status indicator |
| **Encoder 1** | Rotary Encoder | 1 | 1 | 30 | 45 | Volume / Release |
| **Encoder 2** | Rotary Encoder | 1 | 2 | 75 | 45 | Filter Freq / Delay Time |
| **Encoder 3** | Rotary Encoder | 1 | 3 | 120 | 45 | Base Freq / Filter Res |
| **Encoder 4** | Rotary Encoder | 2 | 1 | 30 | 90 | Delay Feedback |
| **Encoder 5** | Rotary Encoder | 2 | 2 | 75 | 90 | Reverb Mix / Size |
| **Pitch Switch** | 3-Pos Toggle (ON/OFF/ON) | 2 | 3 | 120 | 90 | Pitch envelope control |
| **Waveform Switch** | SP4T Rotary Switch | 3 | 1 | 30 | 135 | Waveform selection |
| **Bank Button** | Momentary SPST | 3 | 2 | 75 | 135 | Shift button (Bank A/B) |
| **Trigger Button** | Momentary SPST | 3 | 3 | 120 | 135 | Main trigger |

---

## Spacing Verification

### Horizontal Spacing
- Column 1 to Column 2: **45mm** ✓
- Column 2 to Column 3: **45mm** ✓
- Total width of controls: **90mm**

### Vertical Spacing
- Row 1 to Row 2: **45mm** ✓
- Row 2 to Row 3: **45mm** ✓
- Total height of controls: **90mm**

### LED Position
- Horizontal: **75mm** from left (centered on Column 2)
- Vertical: **15mm** from top edge
- Clearance to Row 1: **30mm** (15mm above Row 1 at 45mm)

---

## Component Specifications

### Rotary Encoders (5 units)
- **Part Type:** EC11 series rotary encoder (or equivalent)
- **Mounting:** Panel mount, threaded bushing with nut
- **Footprint:** 5-pin through-hole
  - CLK, DT, GND pins required
  - Push-switch pins (SW, SW) not used
- **Shaft:** 6mm D-shaft (knurled/flatted for knob attachment)
- **Thread:** M7 × 0.75 (standard for EC11)
- **Panel Hole Size:** 7mm diameter
- **Bushing Length:** 10-15mm (adjust based on panel thickness)

**Pin Assignment (each encoder):**
```
     [CLK] [DT] [GND] [SW] [SW]
       |    |    |     |    |
       |    |    |     └────┴─── Not connected
       |    |    └───────────── Ground
       |    └────────────────── Data (DT)
       └─────────────────────── Clock (CLK)
```

### Momentary Push Buttons (2 units)
- **Part Type:** 16mm momentary push button (SPST NO)
- **Mounting:** Panel mount, threaded bushing with nut
- **Footprint:** 2-pin through-hole
- **Thread:** M16 × 0.75
- **Panel Hole Size:** 16mm diameter
- **LED Illumination:** Not required (optional)
- **Wiring:** Active-low (one pin to GPIO, one pin to GND)

**Pin Assignment:**
```
  [Pin 1] ──→ GPIO (signal)
  [Pin 2] ──→ GND (ground)
```

### 3-Position Toggle Switch (1 unit)
- **Part Type:** ON/OFF/ON toggle switch (SPDT with center-off)
- **Mounting:** Panel mount, threaded bushing with nut
- **Footprint:** 3-pin through-hole
- **Thread:** M6 × 0.75 (or M12, depending on switch body size)
- **Panel Hole Size:** 6mm or 12mm diameter (specify based on part)
- **Toggle Travel:** ±30° from center

**Pin Assignment:**
```
  [UP]  [COMMON]  [DOWN]
    |       |       |
    |       └───────┴──→ Ground (common)
    └──────────────────→ GPIO 10 (UP position)
    └──────────────────→ GPIO 9 (DOWN position)
```

### 4-Position Rotary Switch (1 unit)
- **Part Type:** Single Pole 4 Throw (SP4T) rotary selector switch
- **Mounting:** Panel mount, threaded bushing with nut
- **Footprint:** 5-pin through-hole (4 positions + common)
- **Rotation:** 90° per position (4 × 90° = 360° total, or 4 × 30° detents)
- **Thread:** M12 × 0.75
- **Panel Hole Size:** 12mm diameter
- **Detents:** 4 positions with positive click detents

**Pin Assignment:**
```
  [POS1] [POS2] [COMMON] [POS3] [POS4]
     |      |       |       |      |
     |      |       └───────┴──────┴──→ Ground (common)
     └──────┴───────────────────────→ GPIO 5, 6, 7, 8
```

### WS2812 LED (1 unit)
- **Part Type:** WS2812D-F5 (5mm through-hole addressable RGB LED)
- **Mounting:** Press-fit into 5mm hole or LED holder clip
- **Footprint:** 4-pin through-hole
- **Panel Hole Size:** 5mm diameter
- **Polarity:** Check datasheet - VCC, GND, DIN, DOUT

**Pin Assignment:**
```
  [VCC] [GND] [DIN] [DOUT]
    |     |     |      |
    |     |     |      └───→ Not connected
    |     |     └──────────→ GPIO 12 (data in)
    |     └────────────────→ Ground
    └──────────────────────→ +5V (NOT 3.3V!)
```

**Important:** WS2812 requires **5V power**, but accepts 3.3V data signals.

---

## Connector Specifications

### Raspberry Pi Connection
- **Connector Type:** 2×20 pin (40-pin) female header
- **Pitch:** 2.54mm (0.1")
- **Placement:** Right side or bottom edge of PCB (designer's choice)
- **Orientation:** Position for easy cable access to Pi Zero 2

**Alternative:** Use a 40-pin ribbon cable with IDC connectors (2×20 female)

### PCM5102 DAC Connection (Optional)
- **Connector Type:** 5-pin header (or direct solder pads)
- **Signals:** 3.3V, GND, BCK, LRCK, DIN
- **Placement:** Bottom or right edge of PCB

---

## GPIO Pin Mapping

### Pin Assignments Table

| Component | Signal | GPIO # | Pi Physical Pin | Notes |
|-----------|--------|--------|-----------------|-------|
| **Encoder 1** | CLK | 17 | 11 | Volume / Release |
| **Encoder 1** | DT | 2 | 3 | |
| **Encoder 2** | CLK | 27 | 13 | Filter / Delay |
| **Encoder 2** | DT | 22 | 15 | |
| **Encoder 3** | CLK | 23 | 16 | Base Freq / Filter Res |
| **Encoder 3** | DT | 24 | 18 | |
| **Encoder 4** | CLK | 20 | 38 | Delay Feedback |
| **Encoder 4** | DT | 26 | 37 | |
| **Encoder 5** | CLK | 14 | 8 | Reverb |
| **Encoder 5** | DT | 13 | 33 | |
| **Bank Button** | Signal | 15 | 10 | Active-low |
| **Trigger Button** | Signal | 4 | 7 | Active-low |
| **Pitch Switch** | UP | 10 | 19 | Active-low |
| **Pitch Switch** | DOWN | 9 | 21 | Active-low |
| **Waveform Sw** | Pos1 (Sine) | 5 | 29 | Active-low |
| **Waveform Sw** | Pos2 (Square) | 6 | 31 | Active-low |
| **Waveform Sw** | Pos3 (Saw) | 7 | 26 | Active-low |
| **Waveform Sw** | Pos4 (Triangle) | 8 | 24 | Active-low |
| **LED** | Data | 12 | 32 | PWM0 |

### Reserved Pins (Do Not Use)
- **GPIO 18** (Pin 12) - I2S LRCLK (PCM5102 DAC)
- **GPIO 19** (Pin 35) - I2S BCLK (PCM5102 DAC)
- **GPIO 21** (Pin 40) - I2S DOUT (PCM5102 DAC)

---

## Electrical Design Notes

### Pull-up Resistors
- **All encoder and switch inputs use internal pull-ups** (configured in software)
- **No external pull-up resistors required** on GPIO inputs
- **Active-low logic:** Pressed/selected = LOW (0V), Released/unselected = HIGH (3.3V)

### Button/Switch Wiring
- All encoders, buttons, and switches connect:
  - One side to GPIO pin
  - Other side to GND
- When closed, GPIO pin is pulled to ground (reads LOW)

### LED Circuit
- **WS2812 LED requires 5V power supply**
- Data signal is 3.3V from GPIO 12 (acceptable by WS2812)
- Optional: Add 330Ω resistor in series with data line for protection
- Optional: Add 100µF capacitor across VCC/GND near LED

### Power Distribution
- **5V rail:** LED only (max 60mA for WS2812)
- **3.3V rail:** Not required (all GPIO inputs use internal pull-ups)
- **GND:** Common ground for all components

### Recommended Schematic
```
Raspberry Pi GPIO → [No resistors] → Switch/Encoder/Button → GND
                                                 (active-low)

Raspberry Pi 5V → [Optional 330Ω] → WS2812 DIN (GPIO 12)
                → [100µF cap]     → WS2812 VCC/GND
```

---

## PCB Design Guidelines

### Layer Stack
- **2-layer PCB recommended** (cost-effective)
- Top layer: Component pads, traces
- Bottom layer: Ground plane, traces

### Traces
- **Signal traces:** 0.3mm minimum width
- **Power traces (5V, 3.3V):** 0.5mm minimum width
- **Ground traces:** 0.5mm or pour ground plane

### Mounting Holes
- **4× mounting holes** at corners
- **Hole diameter:** 3.2mm (M3 screws)
- **Positions:** 5mm from corners
- **Grounded:** Connect to GND plane

### Silkscreen
- Label each component with name (E1, E2, TRIG, BANK, etc.)
- Include GPIO numbers for debugging
- Add polarity markings for LED (+5V, GND, DIN)
- Add "TOP" or "FRONT" indicator

### Clearances
- **Component to board edge:** 5mm minimum
- **Component to component:** 10mm minimum (provided by 45mm spacing)
- **Trace to trace:** 0.3mm minimum
- **Trace to pad:** 0.2mm minimum

---

## Mechanical Notes

### Front Panel Mounting
- Components mount **from front panel through PCB**
- PCB sits **behind** front panel (inside enclosure)
- Typical standoff distance: 10-15mm from panel to PCB
- Use threaded bushings on components to secure to panel
- PCB floats on component leads or uses standoffs for support

### Panel Cutout Dimensions
- **Encoders:** 7mm diameter holes
- **Buttons:** 16mm diameter holes
- **Pitch toggle:** 6mm or 12mm hole (depends on switch body)
- **Waveform rotary:** 12mm diameter hole
- **LED:** 5mm diameter hole

### Component Orientation
- All components face **forward** (toward front panel)
- Encoder shafts protrude through panel (~10mm)
- Button actuators protrude through panel (~5-8mm)
- LED lens flush with or slightly recessed behind panel

### Assembly Order
1. Insert components through front panel cutouts
2. Position PCB behind panel onto component pins/legs
3. Secure components to panel with nuts (hand-tight)
4. Solder component pins to PCB pads
5. Connect ribbon cable to Raspberry Pi

---

## Bill of Materials (BOM)

| Qty | Part Description | Designator | Specifications |
|-----|------------------|------------|----------------|
| 5 | Rotary Encoder | E1-E5 | EC11 compatible, 5-pin, panel mount |
| 2 | Momentary Button | BANK, TRIG | 16mm SPST NO, panel mount |
| 1 | Toggle Switch | PITCH | 3-pos ON/OFF/ON, SPDT, panel mount |
| 1 | Rotary Switch | WAVE | SP4T 4-position, panel mount |
| 1 | RGB LED | LED1 | WS2812D-F5, 5mm through-hole |
| 1 | Resistor (optional) | R1 | 330Ω, 1/4W (for LED data line) |
| 1 | Capacitor (optional) | C1 | 100µF electrolytic, 16V (for LED power) |
| 1 | Pin Header | J1 | 2×20 female header, 2.54mm pitch |
| 4 | Mounting Holes | - | M3 size, 3.2mm diameter |

---

## Design Checklist

- [ ] All component positions match coordinate table
- [ ] 45mm center-to-center spacing verified for all components
- [ ] LED positioned 15mm from top edge, 75mm from left (centered)
- [ ] All GPIO pins correctly routed (no conflicts with I2S pins)
- [ ] Ground plane on bottom layer
- [ ] All pads match component footprints (verify datasheets)
- [ ] Mounting holes positioned and grounded
- [ ] Silkscreen labels added for all components
- [ ] 5V and GND traces sized appropriately for LED current
- [ ] Optional protection components (R1, C1) included
- [ ] Connector (J1) positioned for easy cable access
- [ ] Board dimensions allow 5mm edge clearance

---

## Reference Documents

- **Main Documentation:** `/home/user/poor-house-dub-v2/README.md`
- **GPIO Wiring Guide:** `/home/user/poor-house-dub-v2/GPIO_WIRING_GUIDE.md`
- **Hardware Guide:** `/home/user/poor-house-dub-v2/HARDWARE.md`
- **Source Code:** `/home/user/poor-house-dub-v2/cpp/`

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-27 | Claude | Initial PCB layout specification |

---

**END OF DOCUMENT**
