# Dub Siren V2 - PCB HAT Schematic (Mermaid Diagrams)
## Hybrid Design: Panel-Mount Encoders + Edge Breakouts

## Board Architecture Overview

```mermaid
graph TB
    subgraph "Pi Zero 2 W (Bottom Side)"
        PI[Raspberry Pi Zero 2 W<br/>40-pin GPIO]
    end

    subgraph "PCB HAT - 150mm x 120mm"
        GPIO_HDR[40-pin Female Header<br/>Bottom Side]

        subgraph "Panel-Mounted Components (Rows 1-2)"
            E1[E1: Encoder 1<br/>GPIO 17, 2<br/>30, 45mm]
            E2[E2: Encoder 2<br/>GPIO 27, 22<br/>75, 45mm]
            E3[E3: Encoder 3<br/>GPIO 23, 24<br/>120, 45mm]
            E4[E4: Encoder 4<br/>GPIO 20, 26<br/>30, 90mm]
            E5[E5: Encoder 5<br/>GPIO 14, 13<br/>75, 90mm]
            PITCH[Pitch Switch<br/>GPIO 10, 9<br/>120, 90mm]
            LED[WS2812 LED<br/>GPIO 12, 5V<br/>75, 15mm]
        end

        subgraph "Bottom Edge Breakouts (Y=110mm)"
            PCM[PCM5102 DAC<br/>GPIO 18,19,21<br/>X: 10-20mm]
            WAVE[Waveform Switch<br/>GPIO 5,6,7,8<br/>X: 40-50mm]
            BANK[Bank Button<br/>GPIO 15<br/>X: 80mm]
            TRIG[Trigger Button<br/>GPIO 4<br/>X: 110mm]
        end
    end

    subgraph "External Components"
        PCM_DAC[PCM5102 Module<br/>I2S DAC]
        WAVE_SW[SP4T Rotary Switch<br/>Waveform Select]
        BANK_BTN[Momentary Button<br/>Bank Shift]
        TRIG_BTN[Momentary Button<br/>Trigger]
    end

    PI --> GPIO_HDR
    GPIO_HDR --> E1
    GPIO_HDR --> E2
    GPIO_HDR --> E3
    GPIO_HDR --> E4
    GPIO_HDR --> E5
    GPIO_HDR --> PITCH
    GPIO_HDR --> LED
    GPIO_HDR --> PCM
    GPIO_HDR --> WAVE
    GPIO_HDR --> BANK
    GPIO_HDR --> TRIG

    PCM -.Wire.-> PCM_DAC
    WAVE -.Wire.-> WAVE_SW
    BANK -.Wire.-> BANK_BTN
    TRIG -.Wire.-> TRIG_BTN

    style PI fill:#f9f,stroke:#333,stroke-width:2px
    style GPIO_HDR fill:#bbf,stroke:#333,stroke-width:2px
    style LED fill:#ff9,stroke:#333,stroke-width:2px
    style E1 fill:#bfb,stroke:#333,stroke-width:2px
    style E2 fill:#bfb,stroke:#333,stroke-width:2px
    style E3 fill:#bfb,stroke:#333,stroke-width:2px
    style E4 fill:#bfb,stroke:#333,stroke-width:2px
    style E5 fill:#bfb,stroke:#333,stroke-width:2px
    style PITCH fill:#bfb,stroke:#333,stroke-width:2px
```

## PCB Physical Layout (Top View - 150mm × 120mm)

```mermaid
graph TD
    subgraph "PCB Top Side - 150mm x 120mm"
        CTR["LED (75, 15mm)<br/>WS2812<br/>5V/DIN/GND"]

        subgraph "Row 1 - Y=45mm (Panel Mount)"
            R1C1["E1 (30, 45)<br/>GPIO 17/2<br/>Volume/Release"]
            R1C2["E2 (75, 45)<br/>GPIO 27/22<br/>Filter/Delay"]
            R1C3["E3 (120, 45)<br/>GPIO 23/24<br/>Base/Filter Res"]
        end

        subgraph "Row 2 - Y=90mm (Panel Mount)"
            R2C1["E4 (30, 90)<br/>GPIO 20/26<br/>Delay FB"]
            R2C2["E5 (75, 90)<br/>GPIO 14/13<br/>Reverb Mix/Size"]
            R2C3["PITCH (120, 90)<br/>GPIO 10/9<br/>Pitch Env"]
        end

        subgraph "Bottom Edge - Y=110mm (Breakout Pads)"
            BP1["PCM5102<br/>10-20mm<br/>5 pads"]
            BP2["WAVE SW<br/>40-50mm<br/>5 pads"]
            BP3["BANK<br/>80mm<br/>2 pads"]
            BP4["TRIG<br/>110mm<br/>2 pads"]
        end

        BTM["GPIO Header Below<br/>40-pin Female<br/>(Pi mounts on bottom)"]
    end

    style CTR fill:#ff9,stroke:#333,stroke-width:2px
    style BTM fill:#bbf,stroke:#333,stroke-width:2px
    style R1C1 fill:#bfb,stroke:#333,stroke-width:2px
    style R1C2 fill:#bfb,stroke:#333,stroke-width:2px
    style R1C3 fill:#bfb,stroke:#333,stroke-width:2px
    style R2C1 fill:#bfb,stroke:#333,stroke-width:2px
    style R2C2 fill:#bfb,stroke:#333,stroke-width:2px
    style R2C3 fill:#bfb,stroke:#333,stroke-width:2px
    style BP1 fill:#fbb,stroke:#333,stroke-width:2px
    style BP2 fill:#fbb,stroke:#333,stroke-width:2px
    style BP3 fill:#fbb,stroke:#333,stroke-width:2px
    style BP4 fill:#fbb,stroke:#333,stroke-width:2px
```

## Component Spacing Diagram

```mermaid
graph LR
    subgraph "Horizontal Spacing (3 columns)"
        C1["Column 1<br/>X = 30mm"]
        C2["Column 2<br/>X = 75mm"]
        C3["Column 3<br/>X = 120mm"]
    end

    C1 -->|45mm| C2
    C2 -->|45mm| C3

    subgraph "Vertical Spacing"
        LED_Y["LED Y = 15mm"]
        R1_Y["Row 1 Y = 45mm"]
        R2_Y["Row 2 Y = 90mm"]
        BP_Y["Breakouts Y = 110mm"]
    end

    LED_Y -->|30mm| R1_Y
    R1_Y -->|45mm| R2_Y
    R2_Y -->|20mm| BP_Y

    style C1 fill:#bfb
    style C2 fill:#bfb
    style C3 fill:#bfb
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
        PIN12[Pin 12<br/>GPIO 18]
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
        PIN35[Pin 35<br/>GPIO 19]
        PIN37[Pin 37<br/>GPIO 26]
        PIN38[Pin 38<br/>GPIO 20]
        PIN40[Pin 40<br/>GPIO 21]
        GND[GND Pins]
        V5[5V Pin 2/4]
        V33[3.3V Pin 1/17]
    end

    subgraph "Panel-Mounted Components"
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
        PITCH_U[PITCH_UP]
        PITCH_D[PITCH_DN]
        LED_D[LED_DIN]
    end

    subgraph "Edge Breakout Pads"
        DAC_LCK[DAC_LCK]
        DAC_BCK[DAC_BCK]
        DAC_DIN[DAC_DIN]
        WAVE1[WAVE_1]
        WAVE2[WAVE_2]
        WAVE3[WAVE_3]
        WAVE4[WAVE_4]
        BANK_B[BANK_BTN]
        TRIG_B[TRIG_BTN]
        DAC_V[DAC_3V3]
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
    PIN19 --> PITCH_U
    PIN21 --> PITCH_D
    PIN32 --> LED_D

    PIN12 --> DAC_LCK
    PIN35 --> DAC_BCK
    PIN40 --> DAC_DIN
    PIN29 --> WAVE1
    PIN31 --> WAVE2
    PIN26 --> WAVE3
    PIN24 --> WAVE4
    PIN10 --> BANK_B
    PIN7 --> TRIG_B

    V5 --> LED_D
    V33 --> DAC_V

    style E1_CLK fill:#bfb
    style E2_CLK fill:#bfb
    style E3_CLK fill:#bfb
    style E4_CLK fill:#bfb
    style E5_CLK fill:#bfb
    style PITCH_U fill:#bfb
    style DAC_LCK fill:#fbb
    style DAC_BCK fill:#fbb
    style DAC_DIN fill:#fbb
    style WAVE1 fill:#fbb
    style BANK_B fill:#fbb
    style TRIG_B fill:#fbb
```

## Electrical Connections: Panel-Mounted Encoder

```mermaid
graph TB
    subgraph "Panel-Mounted Encoder Example (E1)"
        PANEL[Front Panel<br/>7mm hole]

        ENC[Rotary Encoder<br/>Threaded bushing<br/>Secured with nut]

        PCB_E1_CLK[PCB: E1 CLK Pad<br/>GPIO 17]
        PCB_E1_DT[PCB: E1 DT Pad<br/>GPIO 2]
        PCB_E1_GND[PCB: E1 GND Pad]

        GPIO17[Pi GPIO 17]
        GPIO2[Pi GPIO 2]
        PI_GND[Pi GND]
    end

    PANEL -->|Encoder shaft through| ENC
    ENC -->|Pins solder to| PCB_E1_CLK
    ENC -->|Pins solder to| PCB_E1_DT
    ENC -->|Pins solder to| PCB_E1_GND

    PCB_E1_CLK -->|Trace on PCB| GPIO17
    PCB_E1_DT -->|Trace on PCB| GPIO2
    PCB_E1_GND -->|Trace on PCB| PI_GND

    style PANEL fill:#ddd
    style ENC fill:#bfb
    style PCB_E1_CLK fill:#bbf
    style PCB_E1_DT fill:#bbf
    style PCB_E1_GND fill:#ccc
```

## Electrical Connections: Edge Breakout Pads

```mermaid
graph TB
    subgraph "PCM5102 DAC Breakout"
        PAD_3V3[PCB Pad: DAC_3V3<br/>3.3V]
        PAD_GND1[PCB Pad: DAC_GND<br/>GND]
        PAD_LCK[PCB Pad: DAC_LCK<br/>GPIO 18]
        PAD_BCK[PCB Pad: DAC_BCK<br/>GPIO 19]
        PAD_DIN[PCB Pad: DAC_DIN<br/>GPIO 21]

        DAC_3V3[PCM5102: VCC]
        DAC_GND[PCM5102: GND]
        DAC_LCK[PCM5102: LCK]
        DAC_BCK[PCM5102: BCK]
        DAC_DIN_PIN[PCM5102: DIN]

        PAD_3V3 -.22-26 AWG Wire.-> DAC_3V3
        PAD_GND1 -.Wire.-> DAC_GND
        PAD_LCK -.Wire.-> DAC_LCK
        PAD_BCK -.Wire.-> DAC_BCK
        PAD_DIN -.Wire.-> DAC_DIN_PIN
    end

    subgraph "Waveform Switch Breakout"
        WPAD1[PCB: WAVE_1<br/>GPIO 5]
        WPAD2[PCB: WAVE_2<br/>GPIO 6]
        WPAD3[PCB: WAVE_3<br/>GPIO 7]
        WPAD4[PCB: WAVE_4<br/>GPIO 8]
        WPAD_GND[PCB: WAVE_GND<br/>GND]

        SW_POS1[SP4T Switch<br/>Position 1]
        SW_POS2[SP4T Switch<br/>Position 2]
        SW_POS3[SP4T Switch<br/>Position 3]
        SW_POS4[SP4T Switch<br/>Position 4]
        SW_COM[SP4T Switch<br/>Common]

        WPAD1 -.Wire.-> SW_POS1
        WPAD2 -.Wire.-> SW_POS2
        WPAD3 -.Wire.-> SW_POS3
        WPAD4 -.Wire.-> SW_POS4
        WPAD_GND -.Wire.-> SW_COM
    end

    subgraph "Button Breakouts"
        BPAD_BTN[PCB: BANK_BTN<br/>GPIO 15]
        BPAD_GND[PCB: BANK_GND<br/>GND]

        TPAD_BTN[PCB: TRIG_BTN<br/>GPIO 4]
        TPAD_GND[PCB: TRIG_GND<br/>GND]

        BANK_PIN1[Bank Button<br/>Pin 1]
        BANK_PIN2[Bank Button<br/>Pin 2]

        TRIG_PIN1[Trigger Button<br/>Pin 1]
        TRIG_PIN2[Trigger Button<br/>Pin 2]

        BPAD_BTN -.Wire.-> BANK_PIN1
        BPAD_GND -.Wire.-> BANK_PIN2

        TPAD_BTN -.Wire.-> TRIG_PIN1
        TPAD_GND -.Wire.-> TRIG_PIN2
    end

    style PAD_3V3 fill:#fcc
    style PAD_LCK fill:#fbb
    style PAD_BCK fill:#fbb
    style PAD_DIN fill:#fbb
    style WPAD1 fill:#fbb
    style WPAD2 fill:#fbb
    style WPAD3 fill:#fbb
    style WPAD4 fill:#fbb
    style BPAD_BTN fill:#fbb
    style TPAD_BTN fill:#fbb
```

## Power Distribution

```mermaid
graph TD
    subgraph "Raspberry Pi Zero 2 W"
        PI_5V_IN[5V Power Input<br/>USB-C]
        PI_5V_OUT[5V Output<br/>Pin 2, Pin 4]
        PI_3V3_OUT[3.3V Output<br/>Pin 1, Pin 17]
        PI_GND[GND Pins<br/>Multiple pins]
    end

    subgraph "PCB HAT Power Rails"
        HAT_5V[5V Rail]
        HAT_3V3[3.3V Rail]
        HAT_GND[Ground Plane<br/>Bottom Layer]
    end

    subgraph "Loads"
        LED_LOAD[WS2812 LED<br/>~60mA @ 5V]
        DAC_LOAD[PCM5102 DAC<br/>~10mA @ 3.3V]
        ENC_PASSIVE[5× Encoders<br/>Passive - No power]
        SW_PASSIVE[Pitch Switch<br/>Passive - No power]
        BTN_PASSIVE[2× Buttons<br/>Passive - No power]
        WAVE_PASSIVE[Waveform Switch<br/>Passive - No power]
    end

    PI_5V_IN --> PI_5V_OUT
    PI_5V_OUT --> HAT_5V
    HAT_5V --> LED_LOAD

    PI_3V3_OUT --> HAT_3V3
    HAT_3V3 --> DAC_LOAD

    PI_GND --> HAT_GND
    HAT_GND --> LED_LOAD
    HAT_GND --> DAC_LOAD
    HAT_GND --> ENC_PASSIVE
    HAT_GND --> SW_PASSIVE
    HAT_GND --> BTN_PASSIVE
    HAT_GND --> WAVE_PASSIVE

    style PI_5V_IN fill:#fcc
    style PI_5V_OUT fill:#fcc
    style PI_3V3_OUT fill:#fcf
    style HAT_5V fill:#fcc
    style HAT_3V3 fill:#fcf
    style PI_GND fill:#ccc
    style HAT_GND fill:#ccc
```

## PCB Assembly Cross-Section

```mermaid
graph TB
    subgraph "Assembly Stack (Side View)"
        PANEL[Front Panel<br/>2-3mm acrylic/aluminum]
        NUT[Encoder Nut<br/>M7 thread]
        ENCODER[Rotary Encoder<br/>Threaded bushing]
        PCB[PCB HAT<br/>1.6mm FR4]
        STANDOFF[Standoff<br/>M2.5 × 11mm]
        PI[Pi Zero 2 W<br/>GPIO pins engage header]
    end

    PANEL -->|7mm hole| ENCODER
    NUT -->|Secures to panel| ENCODER
    ENCODER -->|Pins solder through| PCB
    PCB -->|Female header| PI
    STANDOFF -->|Mechanical support| PI

    style PANEL fill:#ddd
    style ENCODER fill:#bfb
    style PCB fill:#bbf
    style PI fill:#f9f
```

## I2S Reserved Pins Warning

```mermaid
graph LR
    subgraph "⚠️ RESERVED FOR PCM5102 DAC ⚠️"
        I2S_LRCLK[GPIO 18<br/>Pin 12<br/>I2S LRCLK<br/>⛔ DO NOT USE]
        I2S_BCLK[GPIO 19<br/>Pin 35<br/>I2S BCLK<br/>⛔ DO NOT USE]
        I2S_DOUT[GPIO 21<br/>Pin 40<br/>I2S DOUT<br/>⛔ DO NOT USE]
    end

    subgraph "PCM5102 DAC Module (Edge Breakout)"
        DAC_LCK[PCM5102: LCK]
        DAC_BCK[PCM5102: BCK]
        DAC_DIN[PCM5102: DIN]
    end

    I2S_LRCLK -->|Via edge pad| DAC_LCK
    I2S_BCLK -->|Via edge pad| DAC_BCK
    I2S_DOUT -->|Via edge pad| DAC_DIN

    style I2S_LRCLK fill:#fcc,stroke:#f00,stroke-width:3px
    style I2S_BCLK fill:#fcc,stroke:#f00,stroke-width:3px
    style I2S_DOUT fill:#fcc,stroke:#f00,stroke-width:3px
```

## Complete GPIO Allocation Map

```mermaid
graph TB
    subgraph "GPIO Allocation (150mm × 120mm HAT)"
        subgraph "Panel-Mounted (13 pins)"
            PM1[GPIO 2 - E1_DT]
            PM2[GPIO 9 - PITCH_DN]
            PM3[GPIO 10 - PITCH_UP]
            PM4[GPIO 12 - LED_DIN]
            PM5[GPIO 13 - E5_DT]
            PM6[GPIO 14 - E5_CLK]
            PM7[GPIO 17 - E1_CLK]
            PM8[GPIO 20 - E4_CLK]
            PM9[GPIO 22 - E2_DT]
            PM10[GPIO 23 - E3_CLK]
            PM11[GPIO 24 - E3_DT]
            PM12[GPIO 26 - E4_DT]
            PM13[GPIO 27 - E2_CLK]
        end

        subgraph "Edge Breakouts (6 pins)"
            EB1[GPIO 4 - TRIG_BTN]
            EB2[GPIO 5 - WAVE_1 opt]
            EB3[GPIO 6 - WAVE_2 opt]
            EB4[GPIO 7 - WAVE_3 opt]
            EB5[GPIO 8 - WAVE_4 opt]
            EB6[GPIO 15 - BANK_BTN]
        end

        subgraph "I2S DAC Reserved (3 pins)"
            I2S1[GPIO 18 - I2S LRCLK]
            I2S2[GPIO 19 - I2S BCLK]
            I2S3[GPIO 21 - I2S DOUT]
        end

        subgraph "Available (6 pins)"
            AV[GPIO 0, 1, 11, 16, 25]
            AV2[GPIO 3 - Shutdown removed]
        end
    end

    style PM1 fill:#bfb
    style PM2 fill:#bfb
    style PM3 fill:#bfb
    style PM4 fill:#ff9
    style PM5 fill:#bfb
    style PM6 fill:#bfb
    style PM7 fill:#bfb
    style PM8 fill:#bfb
    style PM9 fill:#bfb
    style PM10 fill:#bfb
    style PM11 fill:#bfb
    style PM12 fill:#bfb
    style PM13 fill:#bfb
    style EB1 fill:#fbb
    style EB2 fill:#fbb
    style EB3 fill:#fbb
    style EB4 fill:#fbb
    style EB5 fill:#fbb
    style EB6 fill:#fbb
    style I2S1 fill:#fcc
    style I2S2 fill:#fcc
    style I2S3 fill:#fcc
    style AV fill:#eee
    style AV2 fill:#eee
```

## Board Dimensions Summary

```mermaid
graph TD
    DIMS["PCB Dimensions<br/>150mm × 120mm<br/>1.6mm FR4"]

    DIMS --> HORIZ["Horizontal Layout<br/>3 columns @ 45mm spacing<br/>30mm + 75mm + 120mm"]
    DIMS --> VERT["Vertical Layout<br/>LED: 15mm<br/>Row 1: 45mm<br/>Row 2: 90mm<br/>Breakouts: 110mm"]
    DIMS --> MARGINS["Margins<br/>Left/Right: 30mm<br/>Top: 15mm<br/>Bottom: 10mm"]

    style DIMS fill:#bbf,stroke:#333,stroke-width:3px
```

---

## Key Design Features

### Panel-Mounted Components (Green)
- **5 Rotary Encoders** at 45mm spacing
- **Pitch Toggle Switch** at 45mm spacing
- **LED** at top center
- All mount through PCB to front panel with threaded bushings

### Edge Breakouts (Red)
- **PCM5102 DAC** (5 pads) - I2S audio interface
- **Waveform Switch** (5 pads) - Optional SP4T rotary
- **Bank Button** (2 pads) - External momentary switch
- **Trigger Button** (2 pads) - External momentary switch

### Electrical Design
- All encoders/switches use **internal pull-up resistors** (active-low logic)
- No external resistors required on GPIO inputs
- WS2812 LED requires **5V power**, accepts 3.3V data
- PCM5102 DAC uses **3.3V power**
- I2S pins (18, 19, 21) dedicated to audio DAC

---

**Document Version:** 2.0
**Date:** 2026-01-27
**Project:** Dub Siren V2 - Raspberry Pi Zero HAT (Hybrid Design)
