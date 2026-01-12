#!/usr/bin/env python3
"""
GPIO Cleanup Script (Python version)
Clears GPIO state using RPi.GPIO library before starting the dubsiren service
This is necessary when the service crashes without proper GPIO cleanup
"""

import sys

try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError) as e:
    print(f"Warning: RPi.GPIO not available: {e}")
    sys.exit(0)

# All GPIO pins used by the Dub Siren (from gpio_controller.py)
# 5 Encoders (clk, dt pairs) + 4 Switches = 14 GPIO pins total
# NOTE: Avoids I2S pins (18, 19, 21) used by PCM5102 DAC

# Encoder pins: 5 encoders x 2 pins = 10 pins
ENCODER_PINS = [
    17, 2,    # Encoder 1
    27, 22,   # Encoder 2
    23, 24,   # Encoder 3
    20, 26,   # Encoder 4
    14, 13,   # Encoder 5
]

# Switch pins: 4 switches
SWITCH_PINS = [
    4,   # Trigger
    10,  # Pitch envelope
    15,  # Shift
    3,   # Shutdown
]

# Combine all pins
ALL_PINS = ENCODER_PINS + SWITCH_PINS

def cleanup_gpio():
    """Clean up all GPIO pins used by the Dub Siren"""
    try:
        # Try to cleanup any existing GPIO state
        # This will fail if no channels are set up, which is fine
        GPIO.cleanup()
    except:
        pass

    # Set mode to BCM to match the main application
    try:
        GPIO.setmode(GPIO.BCM)
    except:
        pass

    # Turn off warnings
    GPIO.setwarnings(False)

    # For each pin, try to clean it up individually
    for pin in ALL_PINS:
        try:
            # Setup as input (this will reset the pin)
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # Try to remove any event detection
            GPIO.remove_event_detect(pin)
        except:
            # Ignore any errors - pin might not have event detection
            pass

    # Final cleanup
    try:
        GPIO.cleanup()
    except:
        pass

    print("GPIO cleanup completed")

if __name__ == "__main__":
    cleanup_gpio()
    sys.exit(0)
