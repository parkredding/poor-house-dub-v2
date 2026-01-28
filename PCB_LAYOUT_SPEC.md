# Dub Siren V2 - PCB Layout Specification (Pi HAT Version)
## For PCB Designer

**Document Version:** 3.0
**Date:** 2026-01-27
**Project:** Poor House Dub Siren V2 - Raspberry Pi Zero 2 W HAT with Hybrid Design

---

## Overview

This PCB is a **Raspberry Pi Zero 2 W HAT** with a hybrid component mounting approach:

- **Pi HAT format:** Mounts directly onto Raspberry Pi Zero 2 W via 40-pin female header
- **Top side - Control Surface:**
  - **Rows 1-2:** Panel-mount encoders and pitch switch (direct mounting, 45mm spacing)
  - **LED:** Status indicator at top center
- **Bottom edge - Breakouts:**
  - Through-hole breakout pads for waveform switch, bank button, trigger button
  - Connector for PCM5102 DAC
- **Bottom side:** Female GPIO header, Pi Zero 2 W mounts here

---

## Board Dimensions

**PCB Size:** 150mm (W) × 120mm (H) × 1.6mm thickness

**Rationale:**
- Width: 150mm provides 30mm margins + 90mm for 3-column layout (45mm spacing)
- Height: 120mm provides space for encoders, pitch switch, and bottom edge breakouts
- Standard 1.6mm FR4 thickness

**Layer Stack:** 2-layer PCB
- Top: Encoder footprints, LED, silkscreen labels
- Bottom: Female GPIO header, Pi mounting holes, ground plane

---

## Raspberry Pi Zero 2 W Integration

### GPIO Header (Bottom Side)
- **Type:** 2×20 pin (40-pin) female header, through-hole mount
- **PCB Footprint:** 40 plated through-holes (2×20 array at 2.54mm pitch)
- **Position:** Centered on board width, starting 10mm from bottom edge
- **Assembly:** Solder female header to bottom side through-holes
- **Orientation:** Female header accepts Pi's male GPIO pins from below

### Mounting Holes
- **4× mounting holes** matching Pi Zero 2 W footprint
- **Hole diameter:** 2.75mm (M2.5 screws)
- **Positions:** Standard Pi Zero layout relative to GPIO header

### Clearance Zone
- **Bottom side:** Keep-out zone for Pi Zero 2 W (avoid component placement)
- Ensure adequate clearance for HDMI, USB ports, and SD card access

---

## Control Surface Layout (Top Side - Rows 1-2)

### 3×2 Encoder Matrix + Pitch Switch

All components **panel-mount** through PCB to front panel, 45mm center-to-center spacing.

```
                    150mm Width
    ┌────────────────────────────────────┐
    │           [  LED  ]                │ 15mm from top
    │                                    │
    │   [E1]      [E2]      [E3]        │ Row 1 (Y=45mm)
    │                                    │
    │                                    │
    │   [E4]      [E5]    [PITCH]       │ Row 2 (Y=90mm)
    │                                    │
    │ ┌──────────────────────────────┐  │
    │ │   BOTTOM EDGE BREAKOUTS      │  │ Y=110mm
    │ │ [PCM] [WAVE] [BANK] [TRIG]   │  │
    │ └──────────────────────────────┘  │
    └────────────────────────────────────┘
       30mm     75mm     120mm
```

### Component Positions (Center Coordinates from TOP-LEFT)

| Component | Type | X (mm) | Y (mm) | Mounting |
|-----------|------|--------|--------|----------|
| **LED** | WS2812 5mm | 75 | 15 | Surface mount or through-hole |
| **Encoder 1** | Rotary Encoder | 30 | 45 | Panel mount (Volume/Release) |
| **Encoder 2** | Rotary Encoder | 75 | 45 | Panel mount (Filter/Delay) |
| **Encoder 3** | Rotary Encoder | 120 | 45 | Panel mount (Base Freq/Filter Res) |
| **Encoder 4** | Rotary Encoder | 30 | 90 | Panel mount (Delay Feedback) |
| **Encoder 5** | Rotary Encoder | 75 | 90 | Panel mount (Reverb Mix/Size) |
| **Pitch Switch** | 3-Pos Toggle | 120 | 90 | Panel mount (Pitch Envelope) |

**Spacing Verification:**
- Horizontal: 45mm between all columns ✓
- Vertical: 45mm between rows ✓
- LED to Row 1: 30mm clearance ✓

---

## Bottom Edge Breakouts (Y = 110mm)

### Breakout Pad Groups (2.54mm / 0.1" pitch)

Through-hole pads along bottom edge for external wiring.

#### PCM5102 DAC Connector (Left Side)

| X Position | Pin | Label | Signal | Function |
|------------|-----|-------|--------|----------|
| 10mm | 1 | DAC_3V3 | 3.3V | Power for DAC |
| 12.54mm | 2 | DAC_GND | GND | Ground |
| 15.08mm | 3 | DAC_LCK | GPIO 18 | I2S LRCLK (Word Clock) |
| 17.62mm | 4 | DAC_BCK | GPIO 19 | I2S BCLK (Bit Clock) |
| 20.16mm | 5 | DAC_DIN | GPIO 21 | I2S DOUT (Data) |

**Note:** Use 5-pin header or direct wire connection to PCM5102 module.

#### Waveform Switch Breakout (Left-Center)

| X Position | Pin | Label | GPIO | Function |
|------------|-----|-------|------|----------|
| 40mm | 1 | WAVE_1 | 5 | Position 1 (Sine) |
| 42.54mm | 2 | WAVE_2 | 6 | Position 2 (Square) |
| 45.08mm | 3 | WAVE_3 | 7 | Position 3 (Sawtooth) |
| 47.62mm | 4 | WAVE_4 | 8 | Position 4 (Triangle) |
| 50.16mm | 5 | WAVE_GND | GND | Common ground |

#### Bank Button Breakout (Right-Center)

| X Position | Pin | Label | GPIO | Function |
|------------|-----|-------|------|----------|
| 80mm | 1 | BANK_BTN | 15 | Bank shift button signal |
| 82.54mm | 2 | BANK_GND | GND | Ground |

#### Trigger Button Breakout (Right Side)

| X Position | Pin | Label | GPIO | Function |
|------------|-----|-------|------|----------|
| 110mm | 1 | TRIG_BTN | 4 | Trigger button signal |
| 112.54mm | 2 | TRIG_GND | GND | Ground |

---

## Component Specifications

### Rotary Encoders (5 units) - PANEL MOUNT
- **Part Type:** EC11 series rotary encoder
- **Mounting:** Panel mount, threaded bushing with nut
- **Footprint:** 5-pin through-hole (CLK, DT, GND required; SW pins unused)
- **Shaft:** 6mm D-shaft for knobs
- **Thread:** M7 × 0.75
- **Panel Hole Size:** 7mm diameter
- **Bushing Length:** 10-15mm (adjust for panel + PCB thickness)

**PCB Footprint:**
- 3 plated through-holes for CLK, DT, GND pins
- 2.54mm or 5mm pitch (depending on encoder model)
- Component mounts from **front panel through PCB**

### 3-Position Toggle Switch (1 unit) - PANEL MOUNT
- **Part Type:** ON/OFF/ON toggle switch (SPDT center-off)
- **Mounting:** Panel mount, threaded bushing with nut
- **Footprint:** 3-pin through-hole
- **Thread:** M6 × 0.75
- **Panel Hole Size:** 6mm diameter

**Pin Assignment:**
```
[UP]  [COMMON]  [DOWN]
  |       |       |
  GPIO10  GND    GPIO9
```

### WS2812 LED (1 unit)
- **Part Type:** WS2812D-F5 (5mm through-hole RGB LED)
- **Mounting:** Press-fit into 5mm hole or LED holder clip
- **Footprint:** 4-pin through-hole
- **Panel Hole Size:** 5mm diameter (if panel-mounted)

**Pin Assignment:**
```
[VCC] [GND] [DIN] [DOUT]
  5V   GND  GPIO12  NC
```

---

## GPIO Pin Mapping

### Panel-Mounted Components (Rows 1-2)

| Component | Signal | GPIO # | Pi Physical Pin | PCB Footprint |
|-----------|--------|--------|-----------------|---------------|
| **Encoder 1** | CLK | 17 | 11 | Through-hole |
| **Encoder 1** | DT | 2 | 3 | Through-hole |
| **Encoder 2** | CLK | 27 | 13 | Through-hole |
| **Encoder 2** | DT | 22 | 15 | Through-hole |
| **Encoder 3** | CLK | 23 | 16 | Through-hole |
| **Encoder 3** | DT | 24 | 18 | Through-hole |
| **Encoder 4** | CLK | 20 | 38 | Through-hole |
| **Encoder 4** | DT | 26 | 37 | Through-hole |
| **Encoder 5** | CLK | 14 | 8 | Through-hole |
| **Encoder 5** | DT | 13 | 33 | Through-hole |
| **Pitch Switch** | UP | 10 | 19 | Through-hole |
| **Pitch Switch** | DOWN | 9 | 21 | Through-hole |
| **LED** | Data | 12 | 32 | Through-hole or SMD |

### Edge Breakouts (Bottom)

| Component | Signal | GPIO # | Pi Physical Pin | Breakout Pad |
|-----------|--------|--------|-----------------|--------------|
| **PCM5102** | LCK | 18 | 12 | Edge pad |
| **PCM5102** | BCK | 19 | 35 | Edge pad |
| **PCM5102** | DIN | 21 | 40 | Edge pad |
| **Waveform Sw** | Pos 1 | 5 | 29 | Edge pad |
| **Waveform Sw** | Pos 2 | 6 | 31 | Edge pad |
| **Waveform Sw** | Pos 3 | 7 | 26 | Edge pad |
| **Waveform Sw** | Pos 4 | 8 | 24 | Edge pad |
| **Bank Button** | Signal | 15 | 10 | Edge pad |
| **Trigger Button** | Signal | 4 | 7 | Edge pad |

**Total GPIO Used:** 18 pins (12 for encoders/pitch switch, 3 for I2S DAC, 1 for LED, 2 for buttons)
**Optional GPIO:** 4 pins for waveform switch (GPIO 5, 6, 7, 8 if installed)

---

## Electrical Design

### Power Distribution
- **5V:** From Pi header Pin 2/4
  - LED: ~60mA max
  - Encoders: Passive (no power required)
- **3.3V:** From Pi header Pin 1/17
  - PCM5102 DAC: ~10mA
- **GND:** Multiple ground pins, distributed across PCB

### Signal Routing
- All GPIO traces route from female header to component footprints or edge pads
- **Trace width:** 0.3mm minimum for signals, 0.5mm for power
- **Ground pour:** Bottom layer, connected to all GND pads/pins
- **Via stitching:** Connect top/bottom ground at multiple points

### Pull-up Resistors
- **All encoder and switch inputs use internal pull-ups** (configured in software)
- **No external pull-up resistors required**
- **Active-low logic:** Pressed/selected = LOW (0V)

### LED Circuit
```
Pi 5V (Pin 2) → [Optional: 100µF cap] → WS2812 VCC
Pi GPIO 12    → [Optional: 330Ω]     → WS2812 DIN
Pi GND        →                      → WS2812 GND
```

### PCM5102 Connection
```
Pi 3.3V       → PCM5102 VCC
Pi GND        → PCM5102 GND
Pi GPIO 18    → PCM5102 LCK (LRCLK)
Pi GPIO 19    → PCM5102 BCK (BCLK)
Pi GPIO 21    → PCM5102 DIN (DOUT)
```

**PCM5102 Configuration Pins:**
- SCK → GND (48kHz sample rate)
- FLT → GND (normal filter)
- FMT → GND (I2S format)
- XMT → GND (unmute)

---

## PCB Design Guidelines

### Top Side (Component Side)
- Encoder footprints at specified positions (45mm spacing)
- Pitch switch footprint at (120, 90)
- LED footprint at (75, 15)
- Silkscreen labels for all components
- Board identification: "DUB SIREN V2 HAT"
- Version number and date code
- Bottom edge breakout pads with clear labels

### Bottom Side (Pi Mounting Side)
- 40-pin female GPIO header (centered, 10mm from bottom)
- 4× Pi Zero 2 W mounting holes (M2.5)
- Ground plane with proper clearances
- GPIO pin numbers in silkscreen (debugging)
- "TOP" arrow indicator

### Routing Guidelines
- Keep all traces as short as possible
- Route I2S signals (GPIO 18, 19, 21) with care:
  - Use bottom layer
  - Keep away from encoders if possible
  - Minimize crosstalk
- Use ground vias liberally
- Star ground topology for analog/digital grounds

### Silkscreen Requirements

**Top side:**
```
┌─────────────────────────────────────────────┐
│              [  LED  ]                      │
│              GPIO 12                        │
│                                             │
│   [E1]         [E2]         [E3]           │
│  17/2         27/22        23/24            │
│                                             │
│                                             │
│   [E4]         [E5]       [PITCH]          │
│  20/26        14/13        10/9             │
│                                             │
│┌───────────────────────────────────────┐   │
││ DAC   WAVE  WAVE  WAVE  WAVE  BANK TRIG│   │
││ 3V3   POS1  POS2  POS3  POS4  BTN  BTN │   │
││ GND   (5)   (6)   (7)   (8)   (15) (4) │   │
││ LCK   GND   GND   GND   GND   GND  GND │   │
││ BCK                                     │   │
││ DIN                                     │   │
│└───────────────────────────────────────┘   │
│                                             │
│  ╔══════════════════════════════════╗      │
│  ║    DUB SIREN V2 HAT v3.0        ║      │
│  ║    github.com/parkredding        ║      │
│  ╚══════════════════════════════════╝      │
│                                             │
│  [GPIO HEADER & Pi ZERO 2 W BELOW]         │
└─────────────────────────────────────────────┘
```

---

## Bill of Materials (BOM)

| Qty | Part Description | Designator | Package | Mounts To |
|-----|------------------|------------|---------|-----------|
| 1 | Female GPIO Header | J1 | 2×20 pin, 2.54mm, through-hole | Bottom side (solder to PCB) |
| 5 | Rotary Encoders | E1-E5 | EC11, panel mount | Front panel |
| 1 | 3-Pos Toggle Switch | SW1 | ON/OFF/ON, panel mount | Front panel |
| 1 | RGB LED | LED1 | WS2812-5mm | Top side or panel |
| 1 | Resistor (optional) | R1 | 330Ω, 1/4W | Top side |
| 1 | Capacitor (optional) | C1 | 100µF electrolytic | Top side |
| 4 | Nylon Standoffs | - | M2.5 × 11mm | Pi mounting |
| 4 | Screws | - | M2.5 × 6mm | Pi mounting |
| - | Hookup Wire | - | 22-26 AWG | Waveform/buttons |
| 1 | PCM5102 DAC Module | - | Breakout board | External wire |

---

## Assembly Instructions

### Step 1: Solder Female GPIO Header (Bottom Side)
1. PCB has 40 through-holes (2×20) for the GPIO header on bottom side
2. Insert 2×20 female header into through-holes from **bottom side**
3. Female header socket should face downward (to accept Pi's male pins)
4. Solder all 40 pins from **top side** of PCB
5. Ensure header is flush and perpendicular to PCB before soldering

### Step 2: Optional LED and Protection Components (Top Side)
1. Solder WS2812 LED to top side pads (or prep for panel mounting)
2. Add optional capacitor (C1) near LED for power filtering
3. Add optional series resistor (R1) on data line

### Step 3: Mount Pi Zero 2 W (Bottom Side)
1. Install M2.5 standoffs in PCB mounting holes (11mm height recommended)
2. Carefully align Pi Zero 2 W's **male GPIO pins** with PCB's female header socket
3. Gently press Pi Zero down - all 40 male pins must fully insert into female header
4. Secure Pi Zero to standoffs with M2.5 screws
5. Verify all GPIO pins are properly seated (no gaps between Pi and header)

### Step 4: Mount Encoders and Switches (Front Panel)
1. Pre-drill front panel: 7mm holes for encoders, 6mm for pitch switch
2. Insert encoders through front panel holes
3. Position PCB behind panel, align with encoder pins
4. Solder encoder pins to PCB pads from top side
5. Secure encoders to front panel with nuts (hand-tight)
6. Repeat for pitch toggle switch

### Step 5: Wire External Components (Bottom Edge Breakouts)
1. **PCM5102 DAC:**
   - Run wires from PCB breakout pads to DAC module
   - Keep wires short and twisted (< 100mm ideal)
   - Solder to pads: 3.3V, GND, LCK, BCK, DIN

2. **Waveform Switch (optional):**
   - Mount SP4T switch to panel or enclosure
   - Wire each position to corresponding WAVE pad
   - Wire common to WAVE_GND pad

3. **Bank and Trigger Buttons:**
   - Mount buttons to panel or enclosure
   - Wire button pin 1 to BTN signal pad
   - Wire button pin 2 to corresponding GND pad

### Step 6: Test and Verify
1. Check continuity with multimeter
2. Verify no shorts between adjacent pads
3. Power on and test with software

---

## External Wiring Guide

### PCM5102 DAC Wiring
```
PCB Breakout → PCM5102 Module
─────────────────────────────
DAC_3V3     → VCC
DAC_GND     → GND
DAC_LCK     → LCK (LRCLK)
DAC_BCK     → BCK (BCLK)
DAC_DIN     → DIN (Data In)
```

### Waveform Switch Wiring (SP4T)
```
PCB Breakout → Switch Terminal
──────────────────────────────
WAVE_1      → Position 1
WAVE_2      → Position 2
WAVE_3      → Position 3
WAVE_4      → Position 4
WAVE_GND    → Common
```

### Button Wiring (Momentary SPST)
```
PCB Breakout → Button
──────────────────────
BANK_BTN    → Pin 1
BANK_GND    → Pin 2

TRIG_BTN    → Pin 1
TRIG_GND    → Pin 2
```

---

## Design Files Checklist

- [ ] Schematic shows all GPIO connections
- [ ] PCB layout matches component positions (45mm spacing)
- [ ] GPIO header footprint: 40 through-holes (2×20, 2.54mm pitch) for female header
- [ ] Pi Zero mounting holes positioned correctly (M2.5, standard Pi Zero footprint)
- [ ] All encoder footprints positioned at (X, Y) coordinates
- [ ] Pitch switch footprint at (120, 90)
- [ ] LED footprint at (75, 15)
- [ ] Bottom edge breakout pads labeled clearly
- [ ] Ground plane on bottom layer
- [ ] Board dimensions: 150mm × 120mm
- [ ] I2S traces routed carefully (GPIO 18, 19, 21)
- [ ] Version number and project name on silkscreen

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-27 | Claude | Initial panel-mount PCB specification |
| 2.0 | 2026-01-27 | Claude | Redesigned as Pi Zero HAT with edge breakouts |
| 3.0 | 2026-01-27 | Claude | Hybrid design: encoders panel-mount, bottom edge breakouts |

---

**END OF DOCUMENT**
