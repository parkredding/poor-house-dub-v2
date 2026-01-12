#!/usr/bin/env python3
"""
GPIO Controller for Dub Siren Control Surface
Handles 10 rotary encoders and 2 momentary switches
"""

import threading
import time
import os
import subprocess
from typing import Callable, Optional

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    print("WARNING: RPi.GPIO not available. Running in simulation mode.")
    GPIO_AVAILABLE = False


class RotaryEncoder:
    """Rotary encoder handler with quadrature decoding (supports polling fallback)"""

    def __init__(self, clk_pin: int, dt_pin: int, callback: Optional[Callable[[int], None]] = None):
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.callback = callback
        self.position = 0
        self.last_clk = 1
        self.last_dt = 1
        self.use_polling = False
        self.poll_thread = None
        self.running = True

        if GPIO_AVAILABLE:
            GPIO.setup(clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            # Try edge detection first, fall back to polling if it fails
            try:
                # Remove any existing edge detection
                try:
                    GPIO.remove_event_detect(clk_pin)
                    GPIO.remove_event_detect(dt_pin)
                except:
                    pass

                GPIO.add_event_detect(clk_pin, GPIO.BOTH, callback=self._update)
                GPIO.add_event_detect(dt_pin, GPIO.BOTH, callback=self._update)
            except RuntimeError as e:
                # Edge detection not supported, use polling instead
                print(f"      Edge detection not available, using polling mode")
                self.use_polling = True
                self._start_polling()

            # Initialize last states
            self.last_clk = GPIO.input(clk_pin)
            self.last_dt = GPIO.input(dt_pin)

    def _start_polling(self):
        """Start polling thread for reading encoder state"""
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()

    def _poll_loop(self):
        """Polling loop for encoder state (runs in separate thread)"""
        while self.running:
            self._update(None)
            time.sleep(0.001)  # Poll every 1ms

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

    def stop(self):
        """Stop the polling thread if running"""
        self.running = False
        if self.poll_thread and self.poll_thread.is_alive():
            self.poll_thread.join(timeout=0.1)


class MomentarySwitch:
    """Momentary switch handler with debouncing (supports polling fallback)"""

    def __init__(
        self,
        pin: int,
        press_callback: Optional[Callable[[], None]] = None,
        release_callback: Optional[Callable[[], None]] = None,
        debounce_ms: int = 10
    ):
        self.pin = pin
        self.press_callback = press_callback
        self.release_callback = release_callback
        self.debounce_ms = debounce_ms
        self.is_pressed = False
        self.use_polling = False
        self.poll_thread = None
        self.running = True
        self.last_event_time = 0

        if GPIO_AVAILABLE:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            # Try edge detection first, fall back to polling if it fails
            try:
                # Remove any existing edge detection
                try:
                    GPIO.remove_event_detect(pin)
                except:
                    pass

                # Use both edges to detect press and release
                GPIO.add_event_detect(
                    pin,
                    GPIO.BOTH,
                    callback=self._handle_event,
                    bouncetime=debounce_ms
                )
            except RuntimeError as e:
                # Edge detection not supported, use polling instead
                print(f"      Edge detection not available, using polling mode")
                self.use_polling = True
                self._start_polling()

            # Initialize state
            self.is_pressed = (GPIO.input(pin) == GPIO.LOW)

    def _start_polling(self):
        """Start polling thread for reading button state"""
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()

    def _poll_loop(self):
        """Polling loop for button state (runs in separate thread)"""
        while self.running:
            self._handle_event(None)
            time.sleep(0.003)  # Faster poll for better responsiveness

    def _handle_event(self, channel):
        """Handle button press/release events with software debouncing"""
        # Software debouncing for polling mode
        if self.use_polling:
            current_time = time.time()
            if current_time - self.last_event_time < (self.debounce_ms / 1000.0):
                return

        state = GPIO.input(self.pin)

        # Button is active low (pressed when pin reads 0)
        if state == GPIO.LOW and not self.is_pressed:
            # Button pressed
            self.is_pressed = True
            if self.use_polling:
                self.last_event_time = time.time()
            if self.press_callback:
                self.press_callback()
        elif state == GPIO.HIGH and self.is_pressed:
            # Button released
            self.is_pressed = False
            if self.use_polling:
                self.last_event_time = time.time()
            if self.release_callback:
                self.release_callback()

    def stop(self):
        """Stop the polling thread if running"""
        self.running = False
        if self.poll_thread and self.poll_thread.is_alive():
            self.poll_thread.join(timeout=0.1)


class ControlSurface:
    """
    Main control surface handler for the Dub Siren

    5 Encoders + Shift Button = 10 Parameters

    Bank A (Normal):
      Encoder 1: Volume
      Encoder 2: Filter Frequency
      Encoder 3: Filter Resonance
      Encoder 4: Delay Feedback
      Encoder 5: Reverb Mix

    Bank B (Shift held):
      Encoder 1: Release Time
      Encoder 2: Delay Time
      Encoder 3: Reverb Size
      Encoder 4: Osc Waveform
      Encoder 5: LFO Waveform

    Buttons: Trigger, Pitch Env, Shift, Shutdown

    NOTE: Avoids I2S pins (18, 19, 21) used by PCM5102 DAC
    """

    # GPIO pin assignments (BCM numbering) - 5 encoders
    # Avoiding I2S pins: GPIO 18 (LRCLK), 19 (BCLK), 21 (DOUT)
    ENCODER_PINS = {
        'encoder_1': (17, 2),         # Bank A: Volume    | Bank B: Release Time
        'encoder_2': (27, 22),        # Bank A: Filter Freq | Bank B: Delay Time
        'encoder_3': (23, 24),        # Bank A: Filter Res | Bank B: Reverb Size
        'encoder_4': (20, 26),        # Bank A: Delay FB   | Bank B: Osc Wave
        'encoder_5': (14, 13),        # Bank A: Reverb Mix | Bank B: LFO Wave
    }

    SWITCH_PINS = {
        'trigger': 4,                 # Main trigger button
        'pitch_env': 10,              # Pitch envelope cycle (none/up/down)
        'shift': 15,                  # Shift button (access Bank B)
        'shutdown': 3,                # Shutdown/power button
    }

    # Bank mapping - which parameter each encoder controls in each bank
    BANK_A_PARAMS = {
        'encoder_1': 'volume',
        'encoder_2': 'filter_freq',
        'encoder_3': 'filter_res',
        'encoder_4': 'delay_feedback',
        'encoder_5': 'reverb_mix',
    }

    BANK_B_PARAMS = {
        'encoder_1': 'release_time',
        'encoder_2': 'delay_time',
        'encoder_3': 'reverb_size',
        'encoder_4': 'osc_waveform',
        'encoder_5': 'lfo_waveform',
    }

    def __init__(self, synth, shutdown_callback=None):
        self.synth = synth
        self.shutdown_callback = shutdown_callback
        self.encoders = {}
        self.switches = {}
        self.running = False
        self.shift_pressed = False    # Track shift button state
        self.current_bank = 'A'       # Current bank (A or B)
        self._trigger_min_gate = 0.08  # seconds minimum gate time
        self._last_trigger_press = 0.0
        self._pending_trigger_release = None

        # Parameter ranges for all parameters (both banks)
        self.param_values = {
            # Bank A parameters
            'volume': 0.9,              # Start loud
            'filter_freq': 12000.0,     # Start bright
            'filter_res': 0.1,          # Lower Q by default
            'delay_feedback': 0.0,      # Start dry
            'reverb_mix': 0.0,          # Start dry
            # Bank B parameters
            'release_time': 0.8,        # 0.001 to 5.0 seconds (longer sustain)
            'delay_time': 0.5,          # 0.001 to 2.0 seconds
            'reverb_size': 0.5,         # 0.0 to 1.0
            'osc_waveform': 0,          # 0 to 3 (discrete)
            'lfo_waveform': 0,          # 0 to 3 (discrete)
        }

        if GPIO_AVAILABLE:
            # Clean up any existing GPIO state from previous runs
            # This is critical when the service crashes without proper cleanup
            try:
                GPIO.cleanup()
            except:
                pass  # Ignore if GPIO was not previously initialized

            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            self._setup_controls()

    def _setup_controls(self):
        """Initialize all encoders and switches (gracefully handles partial hardware)"""
        print("Initializing control surface...")

        # Setup encoders - each one is optional for partial builds
        for name, (clk, dt) in self.ENCODER_PINS.items():
            try:
                callback = lambda direction, n=name: self._handle_encoder(n, direction)
                self.encoders[name] = RotaryEncoder(clk, dt, callback)
                print(f"  ✓ {name} initialized (GPIO {clk}, {dt})")
            except Exception as e:
                print(f"  ✗ {name} failed to initialize (GPIO {clk}, {dt}): {e}")
                print(f"    Continuing without {name}...")

        # Setup switches - each one is optional for partial builds
        # Main trigger button
        try:
            self.switches['trigger'] = MomentarySwitch(
                self.SWITCH_PINS['trigger'],
                press_callback=self._trigger_press,
                release_callback=self._trigger_release
            )
            print(f"  ✓ trigger button initialized (GPIO {self.SWITCH_PINS['trigger']})")
        except Exception as e:
            print(f"  ✗ trigger button failed (GPIO {self.SWITCH_PINS['trigger']}): {e}")

        # Pitch envelope button: cycles through none -> up -> down on press
        try:
            self.switches['pitch_env'] = MomentarySwitch(
                self.SWITCH_PINS['pitch_env'],
                press_callback=self._cycle_pitch_envelope,
                release_callback=None  # No action on release
            )
            print(f"  ✓ pitch_env button initialized (GPIO {self.SWITCH_PINS['pitch_env']})")
        except Exception as e:
            print(f"  ✗ pitch_env button failed (GPIO {self.SWITCH_PINS['pitch_env']}): {e}")

        # Shift button: switches banks
        try:
            self.switches['shift'] = MomentarySwitch(
                self.SWITCH_PINS['shift'],
                press_callback=self._shift_press,
                release_callback=self._shift_release
            )
            print(f"  ✓ shift button initialized (GPIO {self.SWITCH_PINS['shift']})")
        except Exception as e:
            print(f"  ✗ shift button failed (GPIO {self.SWITCH_PINS['shift']}): {e}")

        # Shutdown button (latching switch)
        try:
            self.switches['shutdown'] = MomentarySwitch(
                self.SWITCH_PINS['shutdown'],
                press_callback=self._handle_shutdown,
                release_callback=None  # No action on release for shutdown
            )
            print(f"  ✓ shutdown button initialized (GPIO {self.SWITCH_PINS['shutdown']})")
        except Exception as e:
            print(f"  ✗ shutdown button failed (GPIO {self.SWITCH_PINS['shutdown']}): {e}")

        # Summary
        num_encoders = len(self.encoders)
        num_switches = len(self.switches)
        print(f"\nControl surface ready: {num_encoders}/5 encoders, {num_switches}/4 buttons")

    def _cycle_pitch_envelope(self):
        """Cycle through pitch envelope modes and log the change"""
        new_mode = self.synth.cycle_pitch_envelope()
        print(f"Pitch envelope: {new_mode}")

    def _trigger_press(self):
        """Log trigger press and fire synth"""
        print("Trigger: PRESSED")
        self._last_trigger_press = time.time()
        if self._pending_trigger_release:
            self._pending_trigger_release.cancel()
            self._pending_trigger_release = None
        self.synth.trigger()

    def _trigger_release(self):
        """Log trigger release and stop synth"""
        print("Trigger: RELEASED")
        elapsed = time.time() - self._last_trigger_press
        remaining = self._trigger_min_gate - elapsed
        if remaining > 0:
            # Delay release to enforce minimum gate time
            try:
                import threading
                self._pending_trigger_release = threading.Timer(remaining, self.synth.release)
                self._pending_trigger_release.start()
            except Exception:
                time.sleep(remaining)
                self.synth.release()
        else:
            self.synth.release()

    def _shift_press(self):
        """Handle shift button press - switch to Bank B"""
        self.shift_pressed = True
        self.current_bank = 'B'
        print("Bank B active")

    def _shift_release(self):
        """Handle shift button release - switch back to Bank A"""
        self.shift_pressed = False
        self.current_bank = 'A'
        print("Bank A active")

    def _handle_shutdown(self):
        """Handle shutdown button press - safely shutdown the system"""
        print("\n" + "=" * 60)
        print("  SHUTDOWN BUTTON PRESSED")
        print("  Safely shutting down the system...")
        print("=" * 60)

        # Call the shutdown callback to stop the application gracefully
        if self.shutdown_callback:
            self.shutdown_callback()

        # Give the app a moment to clean up
        time.sleep(1)

        # Issue system shutdown command
        try:
            print("Executing system shutdown...")
            subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to shutdown system: {e}")
        except FileNotFoundError:
            print("WARNING: shutdown command not found (running in development mode?)")

    def _handle_encoder(self, encoder_name: str, direction: int):
        """Handle encoder rotation with bank switching support"""
        # Determine which parameter to control based on current bank
        if self.shift_pressed:
            param_name = self.BANK_B_PARAMS[encoder_name]
        else:
            param_name = self.BANK_A_PARAMS[encoder_name]

        current_value = self.param_values[param_name]

        # Update value based on parameter type
        if param_name == 'volume':
            step = 0.02 * direction
            new_value = max(0.0, min(1.0, current_value + step))
            self.param_values[param_name] = new_value
            self.synth.set_volume(new_value)

        elif param_name == 'filter_freq':
            # Logarithmic scale for frequency
            step = 50 * direction
            new_value = max(20.0, min(20000.0, current_value + step))
            self.param_values[param_name] = new_value
            self.synth.set_filter_frequency(new_value)

        elif param_name == 'delay_time':
            step = 0.05 * direction
            new_value = max(0.001, min(2.0, current_value + step))
            self.param_values[param_name] = new_value
            self.synth.set_delay_time(new_value)

        elif param_name == 'reverb_size':
            step = 0.02 * direction
            new_value = max(0.0, min(1.0, current_value + step))
            self.param_values[param_name] = new_value
            self.synth.set_reverb_size(new_value)

        elif param_name == 'release_time':
            step = 0.1 * direction
            new_value = max(0.001, min(5.0, current_value + step))
            self.param_values[param_name] = new_value
            self.synth.set_release_time(new_value)

        elif param_name == 'filter_res':
            step = 0.02 * direction
            new_value = max(0.0, min(0.95, current_value + step))
            self.param_values[param_name] = new_value
            self.synth.set_filter_resonance(new_value)

        elif param_name == 'delay_feedback':
            step = 0.02 * direction
            new_value = max(0.0, min(0.95, current_value + step))
            self.param_values[param_name] = new_value
            self.synth.set_delay_feedback(new_value)

        elif param_name == 'reverb_mix':
            step = 0.02 * direction
            new_value = max(0.0, min(1.0, current_value + step))
            self.param_values[param_name] = new_value
            self.synth.set_reverb_dry_wet(new_value)

        elif param_name == 'osc_waveform':
            # Discrete values 0-3
            new_value = int((current_value + direction) % 4)
            if new_value < 0:
                new_value = 3
            self.param_values[param_name] = new_value
            self.synth.set_oscillator_waveform(new_value)

        elif param_name == 'lfo_waveform':
            # Discrete values 0-3
            new_value = int((current_value + direction) % 4)
            if new_value < 0:
                new_value = 3
            self.param_values[param_name] = new_value
            self.synth.set_lfo_waveform(new_value)

        # Print status for debugging
        waveform_names = ['Sine', 'Square', 'Saw', 'Triangle']
        if param_name in ['osc_waveform', 'lfo_waveform']:
            value_str = waveform_names[int(self.param_values[param_name])]
        else:
            value_str = f"{self.param_values[param_name]:.3f}"

        print(f"[Bank {self.current_bank}] {param_name}: {value_str}")

    def start(self):
        """Start the control surface"""
        self.running = True
        print("Control surface started")

    def stop(self):
        """Stop the control surface and cleanup GPIO"""
        self.running = False

        if GPIO_AVAILABLE:
            # Stop all encoder polling threads first
            for encoder in self.encoders.values():
                encoder.stop()

            # Stop all switch polling threads
            for switch in self.switches.values():
                switch.stop()

            # Give threads a moment to exit
            time.sleep(0.05)

            # Now it's safe to cleanup GPIO
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
