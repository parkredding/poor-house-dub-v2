#!/usr/bin/env python3
"""
GPIO Controller for Dub Siren Control Surface
Handles 10 rotary encoders and 2 momentary switches
"""

import threading
import time
from typing import Callable, Optional

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    print("WARNING: RPi.GPIO not available. Running in simulation mode.")
    GPIO_AVAILABLE = False


class RotaryEncoder:
    """Rotary encoder handler with quadrature decoding"""

    def __init__(self, clk_pin: int, dt_pin: int, callback: Optional[Callable[[int], None]] = None):
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.callback = callback
        self.position = 0
        self.last_clk = 1
        self.last_dt = 1

        if GPIO_AVAILABLE:
            GPIO.setup(clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(clk_pin, GPIO.BOTH, callback=self._update)
            GPIO.add_event_detect(dt_pin, GPIO.BOTH, callback=self._update)

    def _update(self, channel):
        """Update encoder position based on quadrature signals"""
        clk_state = GPIO.input(self.clk_pin)
        dt_state = GPIO.input(self.dt_pin)

        # Quadrature decoding
        if clk_state != self.last_clk:
            if dt_state != clk_state:
                self.position += 1
                direction = 1
            else:
                self.position -= 1
                direction = -1

            if self.callback:
                self.callback(direction)

        self.last_clk = clk_state
        self.last_dt = dt_state

    def get_position(self) -> int:
        """Get current encoder position"""
        return self.position

    def reset_position(self):
        """Reset encoder position to zero"""
        self.position = 0


class MomentarySwitch:
    """Momentary switch handler with debouncing"""

    def __init__(
        self,
        pin: int,
        press_callback: Optional[Callable[[], None]] = None,
        release_callback: Optional[Callable[[], None]] = None,
        debounce_ms: int = 50
    ):
        self.pin = pin
        self.press_callback = press_callback
        self.release_callback = release_callback
        self.debounce_ms = debounce_ms
        self.is_pressed = False

        if GPIO_AVAILABLE:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # Use both edges to detect press and release
            GPIO.add_event_detect(
                pin,
                GPIO.BOTH,
                callback=self._handle_event,
                bouncetime=debounce_ms
            )

    def _handle_event(self, channel):
        """Handle button press/release events"""
        state = GPIO.input(self.pin)

        # Button is active low (pressed when pin reads 0)
        if state == GPIO.LOW and not self.is_pressed:
            # Button pressed
            self.is_pressed = True
            if self.press_callback:
                self.press_callback()
        elif state == GPIO.HIGH and self.is_pressed:
            # Button released
            self.is_pressed = False
            if self.release_callback:
                self.release_callback()


class ControlSurface:
    """
    Main control surface handler for the Dub Siren
    Layout (4x3 matrix):
    Row 1: Volume, Filter Freq, Delay Time, Reverb Size
    Row 2: Release Time, Filter Res, Delay FB, Reverb Mix
    Row 3: Osc Wave, LFO Wave, Pitch Env (cycle), Trigger
    """

    # GPIO pin assignments (BCM numbering)
    ENCODER_PINS = {
        'volume': (17, 18),           # Row 1
        'filter_freq': (27, 22),
        'delay_time': (23, 24),
        'reverb_size': (25, 8),
        'release_time': (7, 12),      # Row 2
        'filter_res': (16, 20),
        'delay_feedback': (21, 26),
        'reverb_mix': (19, 13),
        'osc_waveform': (6, 5),       # Row 3
        'lfo_waveform': (11, 9),
    }

    SWITCH_PINS = {
        'pitch_env': 10,              # Pitch envelope cycle (was airhorn)
        'trigger': 4,                 # Main trigger (was siren)
    }

    def __init__(self, synth):
        self.synth = synth
        self.encoders = {}
        self.switches = {}
        self.running = False

        # Parameter ranges for encoders
        self.param_values = {
            'volume': 0.5,              # 0.0 to 1.0
            'filter_freq': 2000.0,      # 20 to 20000 Hz
            'delay_time': 0.5,          # 0.001 to 2.0 seconds
            'reverb_size': 0.5,         # 0.0 to 1.0
            'release_time': 0.5,        # 0.001 to 5.0 seconds
            'filter_res': 0.1,          # 0.0 to 0.95
            'delay_feedback': 0.3,      # 0.0 to 0.95
            'reverb_mix': 0.3,          # 0.0 to 1.0
            'osc_waveform': 0,          # 0 to 3 (discrete)
            'lfo_waveform': 0,          # 0 to 3 (discrete)
        }

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            self._setup_controls()

    def _setup_controls(self):
        """Initialize all encoders and switches"""
        # Setup encoders
        for name, (clk, dt) in self.ENCODER_PINS.items():
            callback = lambda direction, n=name: self._handle_encoder(n, direction)
            self.encoders[name] = RotaryEncoder(clk, dt, callback)

        # Setup switches
        # Pitch envelope button: cycles through none -> up -> down on press
        self.switches['pitch_env'] = MomentarySwitch(
            self.SWITCH_PINS['pitch_env'],
            press_callback=self._cycle_pitch_envelope,
            release_callback=None  # No action on release
        )

        # Main trigger button
        self.switches['trigger'] = MomentarySwitch(
            self.SWITCH_PINS['trigger'],
            press_callback=self.synth.trigger,
            release_callback=self.synth.release
        )

    def _cycle_pitch_envelope(self):
        """Cycle through pitch envelope modes and log the change"""
        new_mode = self.synth.cycle_pitch_envelope()
        print(f"Pitch envelope: {new_mode}")

    def _handle_encoder(self, name: str, direction: int):
        """Handle encoder rotation"""
        current_value = self.param_values[name]

        # Update value based on parameter type
        if name == 'volume':
            step = 0.02 * direction
            new_value = max(0.0, min(1.0, current_value + step))
            self.param_values[name] = new_value
            self.synth.set_volume(new_value)

        elif name == 'filter_freq':
            # Logarithmic scale for frequency
            step = 50 * direction
            new_value = max(20.0, min(20000.0, current_value + step))
            self.param_values[name] = new_value
            self.synth.set_filter_frequency(new_value)

        elif name == 'delay_time':
            step = 0.05 * direction
            new_value = max(0.001, min(2.0, current_value + step))
            self.param_values[name] = new_value
            self.synth.set_delay_time(new_value)

        elif name == 'reverb_size':
            step = 0.02 * direction
            new_value = max(0.0, min(1.0, current_value + step))
            self.param_values[name] = new_value
            self.synth.set_reverb_size(new_value)

        elif name == 'release_time':
            step = 0.1 * direction
            new_value = max(0.001, min(5.0, current_value + step))
            self.param_values[name] = new_value
            self.synth.set_release_time(new_value)

        elif name == 'filter_res':
            step = 0.02 * direction
            new_value = max(0.0, min(0.95, current_value + step))
            self.param_values[name] = new_value
            self.synth.set_filter_resonance(new_value)

        elif name == 'delay_feedback':
            step = 0.02 * direction
            new_value = max(0.0, min(0.95, current_value + step))
            self.param_values[name] = new_value
            self.synth.set_delay_feedback(new_value)

        elif name == 'reverb_mix':
            step = 0.02 * direction
            new_value = max(0.0, min(1.0, current_value + step))
            self.param_values[name] = new_value
            self.synth.set_reverb_dry_wet(new_value)

        elif name == 'osc_waveform':
            # Discrete values 0-3
            new_value = int((current_value + direction) % 4)
            if new_value < 0:
                new_value = 3
            self.param_values[name] = new_value
            self.synth.set_oscillator_waveform(new_value)

        elif name == 'lfo_waveform':
            # Discrete values 0-3
            new_value = int((current_value + direction) % 4)
            if new_value < 0:
                new_value = 3
            self.param_values[name] = new_value
            self.synth.set_lfo_waveform(new_value)

        # Print status for debugging
        waveform_names = ['Sine', 'Square', 'Saw', 'Triangle']
        if name in ['osc_waveform', 'lfo_waveform']:
            value_str = waveform_names[int(self.param_values[name])]
        else:
            value_str = f"{self.param_values[name]:.3f}"

        print(f"{name}: {value_str}")

    def start(self):
        """Start the control surface"""
        self.running = True
        print("Control surface started")

    def stop(self):
        """Stop the control surface"""
        self.running = False
        if GPIO_AVAILABLE:
            GPIO.cleanup()
        print("Control surface stopped")

    def get_status(self) -> dict:
        """Get current status of all controls"""
        return self.param_values.copy()


class SimulatedControlSurface:
    """Simulated control surface for testing without GPIO hardware"""

    def __init__(self, synth):
        self.synth = synth
        self.running = False
        print("Running in SIMULATION mode (no GPIO hardware)")

    def start(self):
        self.running = True
        print("Simulated control surface started")
        print("Available commands:")
        print("  1 = trigger airhorn")
        print("  2 = trigger siren")
        print("  q = quit")

    def stop(self):
        self.running = False
        print("Simulated control surface stopped")

    def get_status(self) -> dict:
        return {}


if __name__ == "__main__":
    # Test the control surface
    from synthesizer import DubSiren

    print("GPIO Controller Test")
    synth = DubSiren()

    if GPIO_AVAILABLE:
        controller = ControlSurface(synth)
    else:
        controller = SimulatedControlSurface(synth)

    controller.start()

    try:
        print("Control surface running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        controller.stop()
