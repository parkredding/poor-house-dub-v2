# Dub Siren V2 - PCB Layout Specification (Pi HAT Version)
## For PCB Designer

**Document Version:** 2.0
**Date:** 2026-01-27
**Project:** Poor House Dub Siren V2 - Raspberry Pi Zero 2 W HAT with Edge Breakouts

---

## Overview

This PCB is a **Raspberry Pi Zero 2 W HAT** that provides breakout connections for an external control surface. The design philosophy:

- **Pi HAT format:** Mounts directly onto Raspberry Pi Zero 2 W via 40-pin female header
- **Dual-sided design:**
  - **TOP side:** Breakout pads for external control wiring
  - **BOTTOM side:** Female GPIO header, Pi Zero 2 W mounts here
- **Edge breakouts:** Through-hole pads at board edges for flexible component choice
- **External mounting:** All switches, encoders, and buttons mount to front panel enclosure and wire to breakout pads
- **Maximum flexibility:** Builder can choose any compatible components

---

## Board Dimensions

**PCB Size:** 65mm (W) × 120mm (H) × 1.6mm thickness

**Rationale:**
- Width matches Raspberry Pi Zero 2 W (65mm)
- Height provides 110mm of vertical space for breakout pads
- Standard 1.6mm FR4 thickness

**Layer Stack:** 2-layer PCB
- Top: Breakout pads, silkscreen labels, LED
- Bottom: Female GPIO header, Pi mounting holes, ground plane

---

## Raspberry Pi Zero 2 W Integration

### GPIO Header (Bottom Side)
- **Type:** 2×20 pin (40-pin) female header
- **Pitch:** 2.54mm (0.1" standard)
- **Position:** Centered on board width, starting 5mm from bottom edge
- **Height:** Standard through-hole female header (8.5mm pin length)
- **Orientation:** Pins face DOWN (Pi Zero mounts underneath)

### Mounting Holes
- **4× mounting holes** matching Pi Zero 2 W footprint
- **Hole diameter:** 2.75mm (M2.5 screws)
- **Positions (from GPIO header pin 1):**
  - Hole 1: 3.5mm, 3.5mm (near Pin 1)
  - Hole 2: 61.5mm, 3.5mm (near Pin 2)
  - Hole 3: 3.5mm, 52.5mm (near Pin 39)
  - Hole 4: 61.5mm, 52.5mm (near Pin 40)

### Clearance Zone
- **Bottom side:** 65mm × 56mm keep-out zone for Pi Zero 2 W
- No components on bottom except GPIO header and mounting hardware
- Ensure adequate clearance for HDMI, USB ports, and SD card access

---

## Breakout Pad Layout

### Design Concept
Instead of mounting components directly to the PCB, **through-hole pads** are provided at strategic board edges. The builder wires from these pads to panel-mounted components of their choice.

### Pad Specifications
- **Pad type:** Through-hole, round or oval
- **Pad diameter:** 2.0mm hole, 3.0mm pad (for easy hand soldering)
- **Spacing:** 2.54mm (0.1" pitch) for compatibility with headers/connectors
- **Labeling:** Clear silkscreen labels on top side

---

## Edge Breakout Locations

### Left Edge (X = 5mm, Y varies)
**Encoder 1 Breakout** (5 pins)
```
Y Position | Pin | Label    | GPIO  | Function
-----------|-----|----------|-------|------------------
20mm       | 1   | E1_CLK   | 17    | Encoder 1 Clock
22.54mm    | 2   | E1_DT    | 2     | Encoder 1 Data
25.08mm    | 3   | E1_GND   | GND   | Ground
```

**Encoder 4 Breakout** (5 pins)
```
Y Position | Pin | Label    | GPIO  | Function
-----------|-----|----------|-------|------------------
35mm       | 1   | E4_CLK   | 20    | Encoder 4 Clock
37.54mm    | 2   | E4_DT    | 26    | Encoder 4 Data
40.08mm    | 3   | E4_GND   | GND   | Ground
```

**Waveform Switch Breakout** (5 pins)
```
Y Position | Pin | Label    | GPIO  | Function
-----------|-----|----------|-------|------------------
50mm       | 1   | WAVE_1   | 5     | Position 1 (Sine)
52.54mm    | 2   | WAVE_2   | 6     | Position 2 (Square)
55.08mm    | 3   | WAVE_3   | 7     | Position 3 (Sawtooth)
57.62mm    | 4   | WAVE_4   | 8     | Position 4 (Triangle)
60.16mm    | 5   | WAVE_GND | GND   | Common ground
```

### Top Edge (Y = 115mm, X varies)
**Encoder 2 Breakout** (5 pins)
```
X Position | Pin | Label    | GPIO  | Function
-----------|-----|----------|-------|------------------
15mm       | 1   | E2_CLK   | 27    | Encoder 2 Clock
17.54mm    | 2   | E2_DT    | 22    | Encoder 2 Data
20.08mm    | 3   | E2_GND   | GND   | Ground
```

**Encoder 3 Breakout** (5 pins)
```
X Position | Pin | Label    | GPIO  | Function
-----------|-----|----------|-------|------------------
32.5mm     | 1   | E3_CLK   | 23    | Encoder 3 Clock
35.04mm    | 2   | E3_DT    | 24    | Encoder 3 Data
37.58mm    | 3   | E3_GND   | GND   | Ground
```

**Encoder 5 Breakout** (5 pins)
```
X Position | Pin | Label    | GPIO  | Function
-----------|-----|----------|-------|------------------
47.5mm     | 1   | E5_CLK   | 14    | Encoder 5 Clock
50.04mm    | 2   | E5_DT    | 13    | Encoder 5 Data
52.58mm    | 3   | E5_GND   | GND   | Ground
```

### Right Edge (X = 60mm, Y varies)
**Pitch Switch Breakout** (3 pins)
```
Y Position | Pin | Label    | GPIO  | Function
-----------|-----|----------|-------|------------------
35mm       | 1   | PITCH_UP | 10    | Pitch envelope up
37.54mm    | 2   | PITCH_DN | 9     | Pitch envelope down
40.08mm    | 3   | PITCH_GND| GND   | Common ground
```

**Bank Button Breakout** (2 pins)
```
Y Position | Pin | Label    | GPIO  | Function
-----------|-----|----------|-------|------------------
50mm       | 1   | BANK_BTN | 15    | Bank shift button
52.54mm    | 2   | BANK_GND | GND   | Ground
```

**Trigger Button Breakout** (2 pins)
```
Y Position | Pin | Label    | GPIO  | Function
-----------|-----|----------|-------|------------------
60mm       | 1   | TRIG_BTN | 4     | Trigger button
62.54mm    | 2   | TRIG_GND | GND   | Ground
```

### LED Position (Top Side, Surface Mount Area)
```
Position   | Component | GPIO  | Notes
-----------|-----------|-------|---------------------------
X=32.5mm   | WS2812    | 12    | Status LED, center of board
Y=105mm    | 5mm LED   |       | 10mm from top edge
           |           | +5V   | Power from Pi 5V rail
           |           | GND   | Ground
```

**LED Mounting Options:**
1. Direct solder WS2812 to pads on PCB top
2. Through-hole pads for external LED wiring (if LED mounts in enclosure)

---

## Breakout Summary Table

| Breakout Group | Edge | # Pins | GPIO Pins Used | Function |
|----------------|------|--------|----------------|----------|
| Encoder 1 | Left | 3 | 17, 2 | Volume / Release |
| Encoder 2 | Top | 3 | 27, 22 | Filter / Delay |
| Encoder 3 | Top | 3 | 23, 24 | Base Freq / Filter Res |
| Encoder 4 | Left | 3 | 20, 26 | Delay Feedback |
| Encoder 5 | Top | 3 | 14, 13 | Reverb Mix / Size |
| Waveform Switch | Left | 5 | 5, 6, 7, 8 | Waveform selector |
| Pitch Switch | Right | 3 | 10, 9 | Pitch envelope |
| Bank Button | Right | 2 | 15 | Shift button |
| Trigger Button | Right | 2 | 4 | Main trigger |
| LED | Top Center | 3 | 12 | Status indicator |

**Total Pads:** 27 through-hole pads + LED footprint

---

## GPIO Pin Mapping (Complete)

| Function | GPIO # | Pi Physical Pin | Breakout Label |
|----------|--------|-----------------|----------------|
| Encoder 1 CLK | 17 | 11 | E1_CLK |
| Encoder 1 DT | 2 | 3 | E1_DT |
| Encoder 2 CLK | 27 | 13 | E2_CLK |
| Encoder 2 DT | 22 | 15 | E2_DT |
| Encoder 3 CLK | 23 | 16 | E3_CLK |
| Encoder 3 DT | 24 | 18 | E3_DT |
| Encoder 4 CLK | 20 | 38 | E4_CLK |
| Encoder 4 DT | 26 | 37 | E4_DT |
| Encoder 5 CLK | 14 | 8 | E5_CLK |
| Encoder 5 DT | 13 | 33 | E5_DT |
| Bank Button | 15 | 10 | BANK_BTN |
| Trigger Button | 4 | 7 | TRIG_BTN |
| Pitch Switch UP | 10 | 19 | PITCH_UP |
| Pitch Switch DOWN | 9 | 21 | PITCH_DN |
| Waveform Pos 1 | 5 | 29 | WAVE_1 |
| Waveform Pos 2 | 6 | 31 | WAVE_2 |
| Waveform Pos 3 | 7 | 26 | WAVE_3 |
| Waveform Pos 4 | 8 | 24 | WAVE_4 |
| LED Data | 12 | 32 | LED_DIN |

### Reserved Pins (Do Not Use)
- **GPIO 18** (Pin 12) - I2S LRCLK (PCM5102 DAC)
- **GPIO 19** (Pin 35) - I2S BCLK (PCM5102 DAC)
- **GPIO 21** (Pin 40) - I2S DOUT (PCM5102 DAC)

---

## Electrical Design

### Power Distribution
- **5V:** Available from Pi header Pin 2/4 for LED (max 60mA)
- **3.3V:** Not required (all inputs use internal pull-ups)
- **GND:** Multiple ground pads distributed around edges

### Signal Routing
- All GPIO traces route from female header to edge breakout pads
- **Trace width:** 0.3mm minimum for signals
- **Ground pour:** Bottom layer, connected to all GND pads
- **Via stitching:** Connect top/bottom ground at multiple points

### Protection (Optional)
- Consider adding:
  - **Series resistors:** 100Ω-330Ω on GPIO lines for ESD protection
  - **TVS diodes:** On critical GPIO pins
  - **Ferrite bead:** On 5V LED power line

### LED Circuit
```
Pi 5V (Pin 2) → [Optional: 100µF cap] → WS2812 VCC
Pi GPIO 12    → [Optional: 330Ω]     → WS2812 DIN
Pi GND        →                      → WS2812 GND
```

---

## PCB Design Guidelines

### Top Side (Component/Breakout Side)
- All breakout pads clearly labeled with silkscreen
- LED footprint or breakout pads at top center
- Ground test points at convenient locations
- Board identification: "DUB SIREN V2 HAT" silkscreen
- Version number and date code

### Bottom Side (Pi Mounting Side)
- 40-pin female GPIO header
- 4× Pi Zero 2 W mounting holes (M2.5)
- Ground plane with proper clearances
- GPIO pin numbers in silkscreen (for debugging)
- "TOP" arrow indicator (since Pi mounts upside-down)

### Routing Guidelines
- Keep all traces as short as possible
- Route high-speed signals (I2S) on bottom layer away from GPIO
- Use ground vias liberally
- Avoid routing under Pi Zero 2 W if possible
- Star ground topology for analog/digital grounds

### Silkscreen Requirements
```
Top side labels (example):
┌─────────────────────────────────┐
│  [E2]  [E3]     [E5]  LED      │
│  CLK   CLK      CLK    ●       │
│  DT    DT       DT     [5V]    │
│  GND   GND      GND    [DIN]   │
│                        [GND]    │
│                                 │
│ [E1]                    [PITCH] │
│ CLK                     UP      │
│ DT                      DN      │
│ GND                     GND     │
│                                 │
│ [E4]                    [BANK]  │
│ CLK                     BTN     │
│ DT                      GND     │
│ GND                             │
│                         [TRIG]  │
│ [WAVE]                  BTN     │
│ POS1                    GND     │
│ POS2                            │
│ POS3                            │
│ POS4                            │
│ GND                             │
│                                 │
│  ╔════════════════════════╗    │
│  ║   DUB SIREN V2 HAT    ║    │
│  ║   github.com/         ║    │
│  ║   parkredding         ║    │
│  ╚════════════════════════╝    │
│                                 │
│  [GPIO HEADER BELOW]            │
└─────────────────────────────────┘
```

---

## Bill of Materials (BOM)

| Qty | Part Description | Designator | Package | Notes |
|-----|------------------|------------|---------|-------|
| 1 | Female GPIO Header | J1 | 2×20 pin, 2.54mm | Through-hole, 8.5mm pin |
| 4 | Nylon Standoffs | - | M2.5 × 11mm | For Pi Zero mounting |
| 4 | Screws | - | M2.5 × 6mm | For Pi Zero mounting |
| 27 | Breakout Pads | - | 2.0mm hole, 3.0mm pad | Through-hole solder points |
| 1 | RGB LED (optional) | LED1 | WS2812-5mm | Can be external via breakout |
| 1 | Capacitor (optional) | C1 | 100µF, electrolytic | For LED power filtering |
| 1 | Resistor (optional) | R1 | 330Ω, 1/4W | For LED data protection |
| - | Hookup Wire | - | 22-26 AWG | For wiring to external components |

---

## Assembly Instructions

### Step 1: Solder GPIO Header
1. Place female header on **bottom side** of PCB
2. Ensure pins point downward (away from PCB)
3. Solder all 40 pins from top side
4. Trim any excess if needed

### Step 2: Optional LED (if PCB-mounted)
1. Solder WS2812 LED to top side pads
2. Add optional capacitor (C1) near LED
3. Add optional series resistor (R1) on data line

### Step 3: Mount Pi Zero 2 W
1. Install M2.5 standoffs in mounting holes
2. Carefully align Pi Zero GPIO with female header
3. Press Pi Zero onto header (all 40 pins must engage)
4. Secure with M2.5 screws

### Step 4: Wire External Components
1. Mount encoders, switches, buttons to front panel enclosure
2. Run wires from components to corresponding breakout pads
3. Strip wire ends and solder to pads
4. Use heat shrink or wire management for clean install
5. Test continuity with multimeter before powering on

---

## External Wiring Guide

### Example: Encoder Wiring
```
Encoder pins → PCB Breakout Pads
─────────────────────────────────
CLK pin     →  E1_CLK (Left edge, 20mm)
DT pin      →  E1_DT  (Left edge, 22.54mm)
GND pin     →  E1_GND (Left edge, 25.08mm)
```

### Example: Button Wiring
```
Button pins → PCB Breakout Pads
─────────────────────────────────
Pin 1       →  TRIG_BTN (Right edge, 60mm)
Pin 2       →  TRIG_GND (Right edge, 62.54mm)
```

### Wire Recommendations
- **Wire gauge:** 22-26 AWG stranded
- **Length:** Keep as short as practical (< 150mm ideal)
- **Color coding:**
  - Red: 5V (LED only)
  - Black: GND
  - Other colors: Signal wires
- **Strain relief:** Use zip ties or adhesive mounts near PCB

---

## Testing & Verification

### Continuity Tests (Before Power-On)
1. GPIO header pins to breakout pads (use multimeter)
2. All GND pads connected together
3. No shorts between adjacent signal pads
4. Pi Zero mounts correctly (all pins aligned)

### Power-On Tests
1. Connect Pi Zero to 5V power supply
2. Boot Raspberry Pi OS
3. Run GPIO test script (see software documentation)
4. Verify each encoder/button responds correctly
5. Test LED illumination (if installed)

---

## Design Files Checklist

- [ ] Schematic shows all GPIO connections
- [ ] PCB layout matches breakout pad positions
- [ ] Female header footprint correct (2×20, 2.54mm pitch)
- [ ] Pi Zero mounting holes positioned correctly
- [ ] All breakout pads labeled on silkscreen
- [ ] Ground plane on bottom layer
- [ ] Board dimensions: 65mm × 120mm
- [ ] I2S pins (18, 19, 21) reserved and not used
- [ ] Mounting holes: 2.75mm diameter, at Pi Zero positions
- [ ] Version number and project name on silkscreen

---

## Additional Notes

### Why This Design?
1. **Flexibility:** Builder can use any encoder/switch brand or size
2. **Easy assembly:** No SMD soldering except optional LED
3. **Repairability:** Individual wires can be replaced if damaged
4. **Custom enclosures:** Components mount to front panel, not PCB
5. **HAT compatibility:** Standard Pi Zero footprint

### Enclosure Recommendations
- Front panel thickness: 2-3mm (acrylic or aluminum)
- Pre-drill holes for encoders (7mm) and buttons (16mm)
- Use spacers between PCB and front panel if needed
- Leave access for SD card, HDMI, and power

### Alternative LED Mounting
Instead of soldering LED to PCB, you can:
1. Add through-hole pads for LED at top center
2. Wire external LED mounted in enclosure
3. Provides more flexibility for LED placement/visibility

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-27 | Claude | Initial panel-mount PCB specification |
| 2.0 | 2026-01-27 | Claude | Redesigned as Pi Zero HAT with edge breakouts |

---

**END OF DOCUMENT**
