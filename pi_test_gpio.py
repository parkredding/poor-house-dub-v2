#!/usr/bin/env python3
"""
Simplified GPIO Controller for Pi Zero 2W Audio Test
Controls: 2 rotary encoders + 1 momentary switch
"""

import RPi.GPIO as GPIO
import time
from typing import Callable, Optional

class RotaryEncoder:
    """Simple rotary encoder handler with acceleration"""

    def __init__(self, pin_a: int, pin_b: int, callback: Callable[[int], None],
                 min_val: float = 0.0, max_val: float = 1.0, initial: float = 0.5,
                 step: float = 0.02):
        """
        Initialize rotary encoder

        Args:
            pin_a: GPIO pin for encoder A
            pin_b: GPIO pin for encoder B
            callback: Function to call with new value
            min_val: Minimum value
            max_val: Maximum value
            initial: Initial value
            step: Step size per detent
        """
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.callback = callback
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial
        self.step = step

        self.last_a = False
        self.last_b = False

        # Setup GPIO
        GPIO.setup(self.pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Add event detection
        GPIO.add_event_detect(self.pin_a, GPIO.BOTH, callback=self._on_change)
        GPIO.add_event_detect(self.pin_b, GPIO.BOTH, callback=self._on_change)

    def _on_change(self, channel):
        """Handle encoder state change"""
        a = GPIO.input(self.pin_a)
        b = GPIO.input(self.pin_b)

        # Only process on A channel falling edge
        if channel == self.pin_a and a == False and self.last_a == True:
            if b:
                # Clockwise
                self.value = min(self.max_val, self.value + self.step)
            else:
                # Counter-clockwise
                self.value = max(self.min_val, self.value - self.step)

            # Call callback with new value
            self.callback(self.value)

        self.last_a = a
        self.last_b = b

class MomentarySwitch:
    """Simple momentary switch handler with debouncing"""

    def __init__(self, pin: int, on_press: Optional[Callable] = None,
                 on_release: Optional[Callable] = None, debounce_ms: int = 50):
        """
        Initialize momentary switch

        Args:
            pin: GPIO pin
            on_press: Callback when pressed
            on_release: Callback when released
            debounce_ms: Debounce time in milliseconds
        """
        self.pin = pin
        self.on_press = on_press
        self.on_release = on_release
        self.debounce_ms = debounce_ms
        self.pressed = False

        # Setup GPIO
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Add event detection
        GPIO.add_event_detect(self.pin, GPIO.BOTH,
                            callback=self._on_change,
                            bouncetime=debounce_ms)

    def _on_change(self, channel):
        """Handle switch state change"""
        state = GPIO.input(self.pin)

        # Active low (pressed = False/GND)
        if state == False and not self.pressed:
            self.pressed = True
            if self.on_press:
                self.on_press()
        elif state == True and self.pressed:
            self.pressed = False
            if self.on_release:
                self.on_release()

class TestGPIOController:
    """GPIO controller for audio test"""

    def __init__(self, synth,
                 volume_pins=(17, 27),      # Encoder 1: Volume
                 delay_pins=(22, 23),        # Encoder 2: Delay Wet/Dry
                 trigger_pin=4):             # Momentary switch
        """
        Initialize GPIO controller

        Args:
            synth: DubSiren instance to control
            volume_pins: (pin_a, pin_b) for volume encoder
            delay_pins: (pin_a, pin_b) for delay wet/dry encoder
            trigger_pin: GPIO pin for trigger switch
        """
        self.synth = synth

        # Setup GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        print("\nInitializing GPIO controls...")

        # Volume encoder
        self.volume_encoder = RotaryEncoder(
            pin_a=volume_pins[0],
            pin_b=volume_pins[1],
            callback=self._on_volume_change,
            min_val=0.0,
            max_val=1.0,
            initial=0.5,
            step=0.02
        )
        print(f"  Volume Encoder: GPIO {volume_pins[0]}, {volume_pins[1]}")

        # Delay wet/dry encoder
        self.delay_encoder = RotaryEncoder(
            pin_a=delay_pins[0],
            pin_b=delay_pins[1],
            callback=self._on_delay_change,
            min_val=0.0,
            max_val=1.0,
            initial=0.3,
            step=0.02
        )
        print(f"  Delay Encoder:  GPIO {delay_pins[0]}, {delay_pins[1]}")

        # Trigger switch
        self.trigger_switch = MomentarySwitch(
            pin=trigger_pin,
            on_press=self._on_trigger_press,
            on_release=self._on_trigger_release
        )
        print(f"  Trigger Switch: GPIO {trigger_pin}")

        # Set initial values
        self.synth.set_volume(self.volume_encoder.value)
        self.synth.set_delay_wet_dry(self.delay_encoder.value)

        print("✓ GPIO controls initialized\n")

    def _on_volume_change(self, value: float):
        """Volume encoder changed"""
        self.synth.set_volume(value)
        print(f"\r  Volume: {int(value * 100):3d}%  |  Delay: {int(self.delay_encoder.value * 100):3d}%  ", end='', flush=True)

    def _on_delay_change(self, value: float):
        """Delay wet/dry encoder changed"""
        self.synth.set_delay_wet_dry(value)
        print(f"\r  Volume: {int(self.volume_encoder.value * 100):3d}%  |  Delay: {int(value * 100):3d}%  ", end='', flush=True)

    def _on_trigger_press(self):
        """Trigger switch pressed"""
        self.synth.trigger()
        print("\n  [TRIGGER PRESSED]", flush=True)

    def _on_trigger_release(self):
        """Trigger switch released"""
        self.synth.release()
        print("  [TRIGGER RELEASED]", flush=True)

    def cleanup(self):
        """Clean up GPIO"""
        GPIO.cleanup()
        print("\n✓ GPIO cleaned up")

if __name__ == "__main__":
    print("\nGPIO Test Controller")
    print("This module should be imported, not run directly")
    print("\nDefault pin assignments:")
    print("  Volume Encoder:  GPIO 17, 27")
    print("  Delay Encoder:   GPIO 22, 23")
    print("  Trigger Switch:  GPIO 4")
    print()
