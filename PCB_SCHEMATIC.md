# Dub Siren V2 - PCB HAT Schematic (Mermaid Diagrams)

## Board Architecture Overview

```mermaid
graph TB
    subgraph "Pi Zero 2 W (Bottom Side)"
        PI[Raspberry Pi Zero 2 W<br/>40-pin GPIO]
    end

    subgraph "PCB HAT - 65mm x 120mm"
        GPIO_HDR[40-pin Female Header<br/>Bottom Side]

        subgraph "Top Edge Breakouts (Y=115mm)"
            E2[E2 Breakout<br/>GPIO 27, 22]
            E3[E3 Breakout<br/>GPIO 23, 24]
            E5[E5 Breakout<br/>GPIO 14, 13]
        end

        subgraph "Left Edge Breakouts (X=5mm)"
            E1[E1 Breakout<br/>GPIO 17, 2]
            E4[E4 Breakout<br/>GPIO 20, 26]
            WAVE[Waveform Switch<br/>GPIO 5,6,7,8]
        end

        subgraph "Right Edge Breakouts (X=60mm)"
            PITCH[Pitch Switch<br/>GPIO 10, 9]
            BANK[Bank Button<br/>GPIO 15]
            TRIG[Trigger Button<br/>GPIO 4]
        end

        LED[WS2812 LED<br/>GPIO 12, 5V<br/>Center Top]
    end

    subgraph "External Components (Panel Mounted)"
        ENC1[Rotary Encoder 1<br/>Volume/Release]
        ENC2[Rotary Encoder 2<br/>Filter/Delay]
        ENC3[Rotary Encoder 3<br/>Base Freq/Filter Res]
        ENC4[Rotary Encoder 4<br/>Delay Feedback]
        ENC5[Rotary Encoder 5<br/>Reverb Mix/Size]
        WAVE_SW[SP4T Rotary Switch<br/>Waveform Select]
        PITCH_SW[3-Pos Toggle<br/>Pitch Envelope]
        BANK_BTN[Momentary Button<br/>Bank Shift]
        TRIG_BTN[Momentary Button<br/>Trigger]
        LED_EXT[RGB Status LED]
    end

    PI --> GPIO_HDR
    GPIO_HDR --> E1
    GPIO_HDR --> E2
    GPIO_HDR --> E3
    GPIO_HDR --> E4
    GPIO_HDR --> E5
    GPIO_HDR --> WAVE
    GPIO_HDR --> PITCH
    GPIO_HDR --> BANK
    GPIO_HDR --> TRIG
    GPIO_HDR --> LED

    E1 -.Wire.-> ENC1
    E2 -.Wire.-> ENC2
    E3 -.Wire.-> ENC3
    E4 -.Wire.-> ENC4
    E5 -.Wire.-> ENC5
    WAVE -.Wire.-> WAVE_SW
    PITCH -.Wire.-> PITCH_SW
    BANK -.Wire.-> BANK_BTN
    TRIG -.Wire.-> TRIG_BTN
    LED -.Wire.-> LED_EXT

    style PI fill:#f9f,stroke:#333,stroke-width:2px
    style GPIO_HDR fill:#bbf,stroke:#333,stroke-width:2px
    style LED fill:#ff9,stroke:#333,stroke-width:2px
```

## PCB Physical Layout (Top View)

```mermaid
graph TD
    subgraph "PCB Top Side - 65mm x 120mm"
        subgraph "Top Edge - Y=115mm"
            T1["E2_CLK (15mm)<br/>E2_DT<br/>E2_GND"]
            T2["E3_CLK (32.5mm)<br/>E3_DT<br/>E3_GND"]
            T3["E5_CLK (47.5mm)<br/>E5_DT<br/>E5_GND"]
        end

        CTR["LED (32.5mm, 105mm)<br/>WS2812<br/>5V/DIN/GND"]

        subgraph "Left Edge - X=5mm"
            L1["E1_CLK (Y=20mm)<br/>E1_DT<br/>E1_GND"]
            L2["E4_CLK (Y=35mm)<br/>E4_DT<br/>E4_GND"]
            L3["WAVE_1 (Y=50mm)<br/>WAVE_2<br/>WAVE_3<br/>WAVE_4<br/>WAVE_GND"]
        end

        subgraph "Right Edge - X=60mm"
            R1["PITCH_UP (Y=35mm)<br/>PITCH_DN<br/>PITCH_GND"]
            R2["BANK_BTN (Y=50mm)<br/>BANK_GND"]
            R3["TRIG_BTN (Y=60mm)<br/>TRIG_GND"]
        end

        BTM["GPIO Header Below<br/>40-pin Female<br/>(Pi mounts on bottom)"]
    end

    style CTR fill:#ff9,stroke:#333,stroke-width:2px
    style BTM fill:#bbf,stroke:#333,stroke-width:2px
```

## GPIO Pin Routing Schematic

```mermaid
graph LR
    subgraph "Pi Zero GPIO Header"
        PIN3[Pin 3<br/>GPIO 2]
        PIN7[Pin 7<br/>GPIO 4]
        PIN8[Pin 8<br/>GPIO 14]
        PIN10[Pin 10<br/>GPIO 15]
        PIN11[Pin 11<br/>GPIO 17]
        PIN13[Pin 13<br/>GPIO 27]
        PIN15[Pin 15<br/>GPIO 22]
        PIN16[Pin 16<br/>GPIO 23]
        PIN18[Pin 18<br/>GPIO 24]
        PIN19[Pin 19<br/>GPIO 10]
        PIN21[Pin 21<br/>GPIO 9]
        PIN24[Pin 24<br/>GPIO 8]
        PIN26[Pin 26<br/>GPIO 7]
        PIN29[Pin 29<br/>GPIO 5]
        PIN31[Pin 31<br/>GPIO 6]
        PIN32[Pin 32<br/>GPIO 12]
        PIN33[Pin 33<br/>GPIO 13]
        PIN37[Pin 37<br/>GPIO 26]
        PIN38[Pin 38<br/>GPIO 20]
        GND[GND Pins<br/>Multiple]
        V5[5V Pins<br/>2, 4]
    end

    subgraph "Edge Breakouts"
        E1_CLK[E1_CLK]
        E1_DT[E1_DT]
        E2_CLK[E2_CLK]
        E2_DT[E2_DT]
        E3_CLK[E3_CLK]
        E3_DT[E3_DT]
        E4_CLK[E4_CLK]
        E4_DT[E4_DT]
        E5_CLK[E5_CLK]
        E5_DT[E5_DT]
        WAVE1[WAVE_1]
        WAVE2[WAVE_2]
        WAVE3[WAVE_3]
        WAVE4[WAVE_4]
        PITCH_U[PITCH_UP]
        PITCH_D[PITCH_DN]
        BANK_B[BANK_BTN]
        TRIG_B[TRIG_BTN]
        LED_D[LED_DIN]
        LED_V[LED_5V]
        PAD_GND[GND Pads x15]
    end

    PIN11 --> E1_CLK
    PIN3 --> E1_DT
    PIN13 --> E2_CLK
    PIN15 --> E2_DT
    PIN16 --> E3_CLK
    PIN18 --> E3_DT
    PIN38 --> E4_CLK
    PIN37 --> E4_DT
    PIN8 --> E5_CLK
    PIN33 --> E5_DT
    PIN29 --> WAVE1
    PIN31 --> WAVE2
    PIN26 --> WAVE3
    PIN24 --> WAVE4
    PIN19 --> PITCH_U
    PIN21 --> PITCH_D
    PIN10 --> BANK_B
    PIN7 --> TRIG_B
    PIN32 --> LED_D
    V5 --> LED_V
    GND --> PAD_GND

    style GND fill:#ccc
    style V5 fill:#fcc
    style PAD_GND fill:#ccc
    style LED_V fill:#fcc
```

## Electrical Connections Detail

```mermaid
graph TB
    subgraph "Encoder Connection (Example: E1)"
        E1_PAD_CLK[PCB: E1_CLK<br/>GPIO 17]
        E1_PAD_DT[PCB: E1_DT<br/>GPIO 2]
        E1_PAD_GND[PCB: E1_GND<br/>Ground]

        E1_ENC_CLK[Encoder 1: CLK Pin]
        E1_ENC_DT[Encoder 1: DT Pin]
        E1_ENC_GND[Encoder 1: GND Pin]

        E1_PAD_CLK -.22-26 AWG Wire.-> E1_ENC_CLK
        E1_PAD_DT -.22-26 AWG Wire.-> E1_ENC_DT
        E1_PAD_GND -.22-26 AWG Wire.-> E1_ENC_GND
    end

    subgraph "Button Connection (Example: Trigger)"
        BTN_PAD_SIG[PCB: TRIG_BTN<br/>GPIO 4]
        BTN_PAD_GND[PCB: TRIG_GND<br/>Ground]

        BTN_PIN1[Button: Pin 1]
        BTN_PIN2[Button: Pin 2]

        BTN_PAD_SIG -.Wire.-> BTN_PIN1
        BTN_PAD_GND -.Wire.-> BTN_PIN2
    end

    subgraph "Waveform Switch Connection"
        WAVE_PAD1[PCB: WAVE_1<br/>GPIO 5]
        WAVE_PAD2[PCB: WAVE_2<br/>GPIO 6]
        WAVE_PAD3[PCB: WAVE_3<br/>GPIO 7]
        WAVE_PAD4[PCB: WAVE_4<br/>GPIO 8]
        WAVE_PAD_GND[PCB: WAVE_GND<br/>Ground]

        SW_POS1[Switch: Position 1]
        SW_POS2[Switch: Position 2]
        SW_POS3[Switch: Position 3]
        SW_POS4[Switch: Position 4]
        SW_COM[Switch: Common]

        WAVE_PAD1 -.Wire.-> SW_POS1
        WAVE_PAD2 -.Wire.-> SW_POS2
        WAVE_PAD3 -.Wire.-> SW_POS3
        WAVE_PAD4 -.Wire.-> SW_POS4
        WAVE_PAD_GND -.Wire.-> SW_COM
    end

    subgraph "LED Connection"
        LED_PAD_5V[PCB: LED_5V<br/>+5V]
        LED_PAD_DIN[PCB: LED_DIN<br/>GPIO 12]
        LED_PAD_GND[PCB: LED_GND<br/>Ground]

        LED_VCC[WS2812: VCC]
        LED_DIN[WS2812: DIN]
        LED_GND_PIN[WS2812: GND]

        LED_PAD_5V -->|Optional 100µF cap| LED_VCC
        LED_PAD_DIN -->|Optional 330Ω| LED_DIN
        LED_PAD_GND --> LED_GND_PIN
    end

    style E1_PAD_CLK fill:#bbf
    style E1_PAD_DT fill:#bbf
    style BTN_PAD_SIG fill:#bbf
    style WAVE_PAD1 fill:#bbf
    style WAVE_PAD2 fill:#bbf
    style WAVE_PAD3 fill:#bbf
    style WAVE_PAD4 fill:#bbf
    style LED_PAD_DIN fill:#bbf
    style LED_PAD_5V fill:#fcc
```

## Power Distribution

```mermaid
graph TD
    subgraph "Raspberry Pi Zero 2 W"
        PI_5V_IN[5V Power Input<br/>USB-C or GPIO Pin]
        PI_5V_OUT[5V Output<br/>Pin 2, Pin 4]
        PI_GND[GND Pins<br/>Multiple pins]
    end

    subgraph "PCB HAT"
        HAT_5V[5V Rail]
        HAT_GND[Ground Plane<br/>Bottom Layer]
    end

    subgraph "Loads"
        LED_LOAD[WS2812 LED<br/>~60mA max]
        ENC_PASSIVE[Encoders<br/>Passive - No power]
        BTN_PASSIVE[Buttons/Switches<br/>Passive - No power]
    end

    PI_5V_IN --> PI_5V_OUT
    PI_5V_OUT --> HAT_5V
    HAT_5V --> LED_LOAD

    PI_GND --> HAT_GND
    HAT_GND --> LED_LOAD
    HAT_GND --> ENC_PASSIVE
    HAT_GND --> BTN_PASSIVE

    style PI_5V_IN fill:#fcc
    style PI_5V_OUT fill:#fcc
    style HAT_5V fill:#fcc
    style PI_GND fill:#ccc
    style HAT_GND fill:#ccc
```

## Signal Flow: Encoder Example

```mermaid
sequenceDiagram
    participant User
    participant Encoder as Rotary Encoder
    participant Wire as Wire Connection
    participant PCB as PCB Breakout Pad
    participant GPIO as Pi GPIO Pin
    participant SW as Software (libgpiod)
    participant App as Dub Siren App

    User->>Encoder: Rotates knob
    Encoder->>Wire: CLK/DT pulse sequence
    Wire->>PCB: Signal at breakout pad
    PCB->>GPIO: Routed via PCB trace
    GPIO->>SW: libgpiod polls GPIO
    SW->>App: Rotation detected
    App->>App: Update parameter
    Note over App: Audio engine applies<br/>new parameter value
```

## PCB Layer Stack

```mermaid
graph TB
    subgraph "2-Layer PCB Construction"
        subgraph "Top Layer (Component Side)"
            TOP_PADS[Through-hole Breakout Pads<br/>27 pads @ 2.54mm pitch]
            TOP_SILK[Silkscreen Labels<br/>Component names, GPIO #s]
            TOP_LED[Optional LED Footprint<br/>WS2812]
            TOP_TRACES[Signal Traces<br/>0.3mm width min]
        end

        subgraph "Core"
            FR4[FR4 Substrate<br/>1.6mm thickness]
        end

        subgraph "Bottom Layer (Pi Side)"
            BOT_HEADER[40-pin Female Header<br/>Through-hole]
            BOT_GND[Ground Plane<br/>Copper pour]
            BOT_TRACES[Signal Traces<br/>0.3mm width min]
            BOT_HOLES[Mounting Holes<br/>4× M2.5]
            BOT_SILK[Silkscreen<br/>GPIO pin numbers]
        end
    end

    TOP_PADS --> FR4
    FR4 --> BOT_HEADER

    style TOP_PADS fill:#bbf
    style BOT_HEADER fill:#bbf
    style BOT_GND fill:#ccc
    style FR4 fill:#efe
```

## I2S Audio Reserved Pins (Do Not Use)

```mermaid
graph LR
    subgraph "Reserved for PCM5102 DAC"
        I2S_LRCLK[GPIO 18<br/>Pin 12<br/>I2S LRCLK<br/>⚠️ RESERVED]
        I2S_BCLK[GPIO 19<br/>Pin 35<br/>I2S BCLK<br/>⚠️ RESERVED]
        I2S_DOUT[GPIO 21<br/>Pin 40<br/>I2S DOUT<br/>⚠️ RESERVED]
    end

    subgraph "PCM5102 DAC Module"
        DAC_LCK[PCM5102: LCK]
        DAC_BCK[PCM5102: BCK]
        DAC_DIN[PCM5102: DIN]
    end

    I2S_LRCLK -->|Direct connection| DAC_LCK
    I2S_BCLK -->|Direct connection| DAC_BCK
    I2S_DOUT -->|Direct connection| DAC_DIN

    style I2S_LRCLK fill:#fcc,stroke:#f00,stroke-width:3px
    style I2S_BCLK fill:#fcc,stroke:#f00,stroke-width:3px
    style I2S_DOUT fill:#fcc,stroke:#f00,stroke-width:3px
```

## Complete GPIO Allocation Map

```mermaid
graph TB
    subgraph "GPIO Allocation Summary"
        subgraph "Used by Control Surface (16 pins)"
            C1[GPIO 2 - E1_DT]
            C2[GPIO 4 - TRIG_BTN]
            C3[GPIO 9 - PITCH_DN]
            C4[GPIO 10 - PITCH_UP]
            C5[GPIO 13 - E5_DT]
            C6[GPIO 14 - E5_CLK]
            C7[GPIO 15 - BANK_BTN]
            C8[GPIO 17 - E1_CLK]
            C9[GPIO 20 - E4_CLK]
            C10[GPIO 22 - E2_DT]
            C11[GPIO 23 - E3_CLK]
            C12[GPIO 24 - E3_DT]
            C13[GPIO 26 - E4_DT]
            C14[GPIO 27 - E2_CLK]
            C15[GPIO 12 - LED_DIN]
        end

        subgraph "Optional (4 pins)"
            O1[GPIO 5 - WAVE_1]
            O2[GPIO 6 - WAVE_2]
            O3[GPIO 7 - WAVE_3]
            O4[GPIO 8 - WAVE_4]
        end

        subgraph "Reserved for I2S (3 pins)"
            R1[GPIO 18 - I2S LRCLK]
            R2[GPIO 19 - I2S BCLK]
            R3[GPIO 21 - I2S DOUT]
        end

        subgraph "Available (7 pins)"
            A1[GPIO 0, 1, 11, 16, 25]
            A2[GPIO 3 - Shutdown removed]
        end
    end

    style C1 fill:#bfb
    style C2 fill:#bfb
    style C3 fill:#bfb
    style C4 fill:#bfb
    style C5 fill:#bfb
    style C6 fill:#bfb
    style C7 fill:#bfb
    style C8 fill:#bfb
    style C9 fill:#bfb
    style C10 fill:#bfb
    style C11 fill:#bfb
    style C12 fill:#bfb
    style C13 fill:#bfb
    style C14 fill:#bfb
    style C15 fill:#bfb
    style O1 fill:#ffb
    style O2 fill:#ffb
    style O3 fill:#ffb
    style O4 fill:#ffb
    style R1 fill:#fcc
    style R2 fill:#fcc
    style R3 fill:#fcc
    style A1 fill:#eee
    style A2 fill:#eee
```

---

## Notes

- All encoders and buttons use **internal pull-up resistors** (configured in software)
- **Active-low logic:** Pressed/selected = LOW (0V), Released = HIGH (3.3V)
- No external resistors required on GPIO inputs
- WS2812 LED requires **5V power** but accepts 3.3V data signals
- PCB acts as simple breakout/routing board - all intelligence in Pi software
- External components mount to front panel, wire to PCB edge pads

---

**Document Version:** 1.0
**Date:** 2026-01-27
**Project:** Dub Siren V2 - Raspberry Pi Zero HAT
