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
# Encoder pins: (clk, dt) pairs
ENCODER_PINS = [17, 18, 27, 22, 23, 24, 25, 8, 7, 12, 16, 20, 21, 26, 19, 13, 6, 5, 11, 9]
# Switch pins
SWITCH_PINS = [10, 4, 3]

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
