#!/usr/bin/env python3
"""
Dub Siren Synthesizer Engine
Main audio synthesis engine with oscillators, LFO, and DSP effects
"""

import numpy as np
import threading
import time
from collections import deque
from typing import Literal

WaveformType = Literal['sine', 'square', 'saw', 'triangle']

# Maximum safe amplitude for internal processing (prevents overflow to Inf/NaN)
# This is well above the final clipping level of 1.0 but safely below float overflow
_MAX_SAFE_AMPLITUDE = 10.0


def _clamp_sample(value: float) -> float:
    """Clamp a single sample to safe range, preventing overflow to Inf/NaN"""
    if value > _MAX_SAFE_AMPLITUDE:
        return _MAX_SAFE_AMPLITUDE
    elif value < -_MAX_SAFE_AMPLITUDE:
        return -_MAX_SAFE_AMPLITUDE
    return value


def _polyblep(t: float, dt: float) -> float:
    """Calculate PolyBLEP (Polynomial Band-Limited Step) residual

    PolyBLEP reduces aliasing in discontinuous waveforms (square, sawtooth)
    by applying a polynomial correction near discontinuities.

    Args:
        t: Current phase position (0.0 to 1.0)
        dt: Phase increment per sample (frequency / sample_rate)

    Returns:
        The PolyBLEP residual to subtract from the naive waveform
    """
    # Check if we're within one sample of a discontinuity
    if t < dt:
        # Just after the discontinuity (phase recently wrapped)
        t_norm = t / dt  # Normalize to 0-1 range
        return t_norm + t_norm - t_norm * t_norm - 1.0
    elif t > 1.0 - dt:
        # Just before the discontinuity (phase about to wrap)
        t_norm = (t - 1.0) / dt  # Normalize to -1 to 0 range
        return t_norm * t_norm + t_norm + t_norm + 1.0
    else:
        return 0.0


def sanitize_audio(audio: np.ndarray, fill_value: float = 0.0) -> np.ndarray:
    """Replace NaN and Inf values with a safe value (default: silence)

    NaN values can occur from:
    - Filter instabilities (feedback loops, high resonance)
    - Division by zero in DSP calculations
    - Overflow in delay/reverb feedback paths

    NaN is particularly problematic because:
    - np.clip(NaN, -1, 1) returns NaN (clipping doesn't help)
    - NaN * volume = NaN (volume control doesn't work)
    - NaN propagates through all subsequent calculations
    - DACs may interpret NaN as extreme values, causing "warbled" sounds

    Args:
        audio: Input audio array
        fill_value: Value to replace NaN/Inf with (default 0.0 = silence)

    Returns:
        Sanitized audio array with NaN/Inf replaced
    """
    # np.isfinite returns False for NaN, Inf, and -Inf
    mask = ~np.isfinite(audio)
    if np.any(mask):
        audio = np.where(mask, fill_value, audio)
    return audio


class Oscillator:
    """Audio oscillator with multiple waveform types and PolyBLEP anti-aliasing

    PolyBLEP (Polynomial Band-Limited Step) is applied to square and sawtooth
    waveforms to reduce aliasing artifacts. This is especially important at
    higher frequencies where harmonics would otherwise fold back into the
    audible range.
    """

    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.frequency = 440.0
        self.phase = 0.0  # Phase accumulator (0.0 to 1.0)
        self.waveform: WaveformType = 'sine'

    def generate(self, num_samples: int) -> np.ndarray:
        """Generate audio samples for the current waveform

        Square and sawtooth waveforms use PolyBLEP anti-aliasing for cleaner
        sound at high frequencies. Sine and triangle are naturally band-limited.
        """
        if self.waveform == 'sine':
            return self._generate_sine(num_samples)
        elif self.waveform == 'square':
            return self._generate_square_polyblep(num_samples)
        elif self.waveform == 'saw':
            return self._generate_saw_polyblep(num_samples)
        elif self.waveform == 'triangle':
            return self._generate_triangle(num_samples)
        else:
            return np.zeros(num_samples)

    def _generate_sine(self, num_samples: int) -> np.ndarray:
        """Generate sine wave (naturally band-limited, no anti-aliasing needed)"""
        output = np.zeros(num_samples)
        dt = self.frequency / self.sample_rate

        for i in range(num_samples):
            output[i] = np.sin(2.0 * np.pi * self.phase)
            self.phase += dt
            if self.phase >= 1.0:
                self.phase -= 1.0

        return output

    def _generate_square_polyblep(self, num_samples: int) -> np.ndarray:
        """Generate square wave with PolyBLEP anti-aliasing

        PolyBLEP is applied at both transitions (0->1 at phase=0, 1->0 at phase=0.5)
        to smooth the discontinuities and reduce aliasing.
        """
        output = np.zeros(num_samples)
        dt = self.frequency / self.sample_rate

        for i in range(num_samples):
            # Naive square wave: +1 for first half, -1 for second half
            if self.phase < 0.5:
                value = 1.0
            else:
                value = -1.0

            # Apply PolyBLEP correction at the rising edge (phase = 0)
            # Rising edge: add polyblep to smooth the upward step
            value += 2.0 * _polyblep(self.phase, dt)

            # Apply PolyBLEP correction at the falling edge (phase = 0.5)
            # Falling edge: subtract polyblep to smooth the downward step
            phase_shifted = self.phase + 0.5
            if phase_shifted >= 1.0:
                phase_shifted -= 1.0
            value -= 2.0 * _polyblep(phase_shifted, dt)

            output[i] = value

            # Advance phase
            self.phase += dt
            if self.phase >= 1.0:
                self.phase -= 1.0

        return output

    def _generate_saw_polyblep(self, num_samples: int) -> np.ndarray:
        """Generate sawtooth wave with PolyBLEP anti-aliasing

        PolyBLEP is applied at the phase reset (when saw jumps from +1 to -1)
        to smooth the discontinuity and reduce aliasing.
        """
        output = np.zeros(num_samples)
        dt = self.frequency / self.sample_rate

        for i in range(num_samples):
            # Naive sawtooth: ramps from -1 to +1 over one cycle
            value = 2.0 * self.phase - 1.0

            # Apply PolyBLEP correction at the discontinuity (phase = 0)
            # The discontinuity magnitude is 2.0 (from +1 to -1)
            value -= 2.0 * _polyblep(self.phase, dt)

            output[i] = value

            # Advance phase
            self.phase += dt
            if self.phase >= 1.0:
                self.phase -= 1.0

        return output

    def _generate_triangle(self, num_samples: int) -> np.ndarray:
        """Generate triangle wave (continuous, no anti-aliasing needed)

        Triangle waves have no discontinuities - they're continuous with
        continuous first derivative at peaks. This makes them naturally
        band-limited with harmonics that fall off as 1/n².
        """
        output = np.zeros(num_samples)
        dt = self.frequency / self.sample_rate

        for i in range(num_samples):
            # Triangle from phase: rises 0->0.5, falls 0.5->1
            if self.phase < 0.5:
                value = 4.0 * self.phase - 1.0  # -1 to +1
            else:
                value = 3.0 - 4.0 * self.phase  # +1 to -1

            output[i] = value

            self.phase += dt
            if self.phase >= 1.0:
                self.phase -= 1.0

        return output

    def set_frequency(self, freq: float):
        """Set oscillator frequency in Hz"""
        self.frequency = max(20.0, min(freq, 20000.0))

    def set_waveform(self, waveform: WaveformType):
        """Set oscillator waveform type"""
        if waveform in ['sine', 'square', 'saw', 'triangle']:
            self.waveform = waveform

    def reset_phase(self):
        """Reset oscillator phase to zero (for clean restarts and preventing clicks)"""
        self.phase = 0.0


class LFO:
    """Low Frequency Oscillator for modulation"""

    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.frequency = 5.0  # Hz (matches browser test default)
        self.phase = 0.0
        self.waveform: WaveformType = 'sine'
        self.depth = 0.0  # 0.0 to 1.0 (matches browser test default)

    def generate(self, num_samples: int) -> np.ndarray:
        """Generate LFO modulation signal"""
        t = (np.arange(num_samples) + self.phase) / self.sample_rate

        if self.waveform == 'sine':
            output = np.sin(2 * np.pi * self.frequency * t)
        elif self.waveform == 'square':
            output = np.sign(np.sin(2 * np.pi * self.frequency * t))
        elif self.waveform == 'saw':
            output = 2 * (t * self.frequency - np.floor(0.5 + t * self.frequency))
        elif self.waveform == 'triangle':
            output = 2 * np.abs(2 * (t * self.frequency - np.floor(0.5 + t * self.frequency))) - 1
        else:
            output = np.zeros(num_samples)

        self.phase += num_samples
        self.phase = self.phase % self.sample_rate

        return output * self.depth

    def set_waveform(self, waveform: WaveformType):
        """Set LFO waveform type"""
        if waveform in ['sine', 'square', 'saw', 'triangle']:
            self.waveform = waveform


class Envelope:
    """Simple exponential envelope - matches reference dub siren implementation"""

    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.release_time = 0.05  # 50ms perceived decay time to silence
        self.current_value = 0.0
        self.is_active = False

        # Envelope coefficients
        self.attack_coeff = 0.1  # Fast attack
        # Scale release coefficient for perceived decay time (4.605 = -ln(0.01))
        decay_scale = 4.605
        self.release_coeff = decay_scale / (self.release_time * sample_rate)

    def trigger(self):
        """Trigger the envelope"""
        self.is_active = True

    def release_trigger(self):
        """Release the envelope"""
        # In this simple model, release just sets is_active = False
        # The envelope will decay to zero asymptotically
        self.is_active = False

    def generate(self, num_samples: int) -> np.ndarray:
        """Generate envelope values using exponential approach to target

        This matches the reference implementation:
        env += (env_target - env) * env_coeff
        """
        output = np.zeros(num_samples)

        for i in range(num_samples):
            if self.is_active:
                # Attack: approach 1.0
                env_target = 1.0
                env_coeff = self.attack_coeff
            else:
                # Release: approach 0.0
                env_target = 0.0
                env_coeff = self.release_coeff

            # Exponential approach to target (first-order filter)
            self.current_value += (env_target - self.current_value) * env_coeff
            output[i] = self.current_value

        return output

    def set_release(self, release_time: float):
        """Set release time in seconds (0.001 to 5.0)

        Args:
            release_time: Perceived decay time in seconds. Clamped to safe range.
                         0.001 = very fast (1ms to silence)
                         5.0 = very slow (5 seconds to silence)

        Note: Uses exponential decay scaling factor (4.605) so that release_time
              represents the actual time to reach 99% decay (perceived silence).
        """
        self.release_time = max(0.001, min(release_time, 5.0))
        # Scale coefficient so release_time represents time to 99% decay
        # Exponential decay: time to 1% = -ln(0.01) × τ ≈ 4.605 × τ
        # Therefore: τ = release_time / 4.605
        decay_scale = 4.605
        self.release_coeff = decay_scale / (self.release_time * self.sample_rate)


class LowPassFilter:
    """Simple one-pole low-pass filter with parameter smoothing

    Parameter smoothing prevents "zipper noise" and clicks when filter
    parameters change rapidly (e.g., from rotary encoder adjustments).
    """

    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.cutoff = 2000.0  # Hz (browser preset default)
        self.cutoff_current = 2000.0  # Current smoothed value
        self.resonance = 1.0  # Q value (browser preset default)
        self.resonance_current = 1.0  # Current smoothed value
        self.prev_output = 0.0
        # Smoothing coefficient: larger = smoother but slower response
        # Browser preset default smoothing
        self.smoothing = 0.001

    def process(self, input_signal: np.ndarray) -> np.ndarray:
        """Process audio through the filter with state clamping to prevent NaN"""
        output = np.zeros_like(input_signal)

        for i in range(len(input_signal)):
            # Smooth parameter changes to prevent zipper noise
            self.cutoff_current += (self.cutoff - self.cutoff_current) * self.smoothing
            self.resonance_current += (self.resonance - self.resonance_current) * self.smoothing

            # Calculate filter coefficient with smoothed cutoff
            rc = 1.0 / (2.0 * np.pi * self.cutoff_current)
            dt = 1.0 / self.sample_rate
            alpha = dt / (rc + dt)

            # Add resonance (feedback) with smoothed resonance
            # Scale Q value (0.1-20) to reasonable feedback range
            # Q=1 (no resonance) -> no extra feedback, Q=20 -> significant peaking
            resonance_factor = (self.resonance_current - 0.1) / 19.9  # Normalize to 0.0-1.0
            alpha = alpha * (1.0 + resonance_factor * 2.0)
            alpha = min(alpha, 0.99)

            output[i] = self.prev_output + alpha * (input_signal[i] - self.prev_output)
            # Clamp state to prevent runaway values that lead to NaN
            self.prev_output = _clamp_sample(output[i])

        return output

    def set_cutoff(self, freq: float):
        """Set filter cutoff frequency in Hz"""
        self.cutoff = max(20.0, min(freq, 20000.0))

    def set_resonance(self, res: float):
        """Set filter resonance / Q value (0.1 to 20, matches browser test range)"""
        self.resonance = max(0.1, min(res, 20.0))

    def reset(self):
        """Reset filter state to prevent buildup and self-oscillation"""
        self.prev_output = 0.0


class DCBlocker:
    """DC blocking filter to remove DC offset without affecting low frequencies

    DC offset can accumulate in feedback loops (filters, delay, reverb) and waste
    headroom, leading to asymmetric clipping and pops. This first-order high-pass
    filter at ~10Hz removes DC while preserving bass frequencies.
    """

    def __init__(self):
        self.x_prev = 0.0
        self.y_prev = 0.0
        self.coeff = 0.995  # High-pass at ~10Hz @ 48kHz

    def process(self, audio: np.ndarray) -> np.ndarray:
        """Remove DC offset from audio signal"""
        output = np.zeros_like(audio)
        for i in range(len(audio)):
            # First-order high-pass filter: y[n] = x[n] - x[n-1] + coeff * y[n-1]
            output[i] = audio[i] - self.x_prev + self.coeff * self.y_prev
            self.x_prev = audio[i]
            self.y_prev = output[i]
        return output

    def reset(self):
        """Reset filter state"""
        self.x_prev = 0.0
        self.y_prev = 0.0


class DelayEffect:
    """Tape-style Delay/Echo effect with authentic analog behavior

    Features:
    - Dry/Wet mix control
    - Tape-style high-frequency damping (5kHz LP) for natural degradation of repeats
    - High-pass filter in feedback path (removes mud buildup)
    - Tape saturation for warmth and harmonic richness
    - Dual time modulation: slow wobble + fast flutter for authentic tape character
    - Analog repitch behavior: changing delay time causes pitch-shifting of repeats
      (like real tape delays where the audio "smears" when you change time)
    """

    def __init__(self, sample_rate: int = 48000, max_delay: float = 2.0):
        self.sample_rate = sample_rate
        self.max_delay_samples = int(max_delay * sample_rate)
        self.buffer = np.zeros(self.max_delay_samples)
        self.write_pos = 0

        # Core delay parameters (match browser test defaults)
        self.delay_time = 0.3  # seconds (target delay time - matches browser test)
        self.feedback = 0.3    # 0.0 to 1.0 (matches browser test)
        self.dry_wet = 0.0     # 0.0 = dry, 1.0 = wet (matches browser test)

        # Analog repitch behavior - smoothly slide to new delay time
        # This creates pitch shifting when delay time changes (like BBD/tape)
        self._current_delay_samples = self.delay_time * sample_rate  # actual read offset
        self.repitch_rate = 0.5  # 0.0 = instant (digital), 1.0 = very slow/dramatic pitch shift
        # Internal: samples to move per sample (derived from repitch_rate)
        self._slew_rate = self._calculate_slew_rate()

        # Feedback filter parameters (tape-style)
        self.filter_hp_freq = 80.0     # High-pass cutoff Hz (removes mud)
        self.filter_lp_freq = 5000.0   # Low-pass cutoff Hz (tape-like high-frequency loss)

        # Filter states for feedback path
        self._hp_state = 0.0
        self._lp_state = 0.0

        # Time modulation (for tape-like wobble and flutter)
        self.mod_depth = 0.003    # primary wobble depth in seconds (increased for tape feel)
        self.mod_rate = 0.5       # primary wobble rate in Hz
        self._mod_phase = 0.0

        # Flutter modulation (faster, secondary modulation for tape character)
        self.flutter_depth = 0.001  # flutter depth in seconds
        self.flutter_rate = 3.5     # flutter rate in Hz (faster than main wobble)
        self._flutter_phase = 0.0

        # Tape saturation
        self.tape_saturation = 0.3  # 0.0 = clean, 1.0 = heavy saturation

    def _calculate_slew_rate(self) -> float:
        """Calculate slew rate from repitch_rate parameter

        repitch_rate of 0.0 = instant jump (digital behavior)
        repitch_rate of 1.0 = very slow slew (dramatic pitch effects)

        Returns samples to move toward target per sample processed.
        """
        if self.repitch_rate <= 0.0:
            return float('inf')  # Instant - no slewing
        # Map repitch_rate to a reasonable slew time
        # At 0.5, we want to traverse ~1 second of delay in ~0.5 seconds
        # This gives noticeable but not extreme pitch shifts
        max_slew_time = 2.0 * self.repitch_rate  # seconds to traverse max delay
        samples_per_second = self.sample_rate
        max_delay_samples = self.max_delay_samples
        # How many samples to move per sample to traverse max_delay in max_slew_time
        return max_delay_samples / (max_slew_time * samples_per_second)

    def _process_feedback_filters(self, sample: float) -> float:
        """Apply HP and LP filters to feedback path, plus tape-style saturation

        Filter states are clamped to prevent runaway values that lead to NaN.
        Adds gentle saturation for tape warmth and character.
        """
        # High-pass filter (removes mud/low-end buildup)
        hp_rc = 1.0 / (2.0 * np.pi * self.filter_hp_freq)
        hp_alpha = hp_rc / (hp_rc + 1.0 / self.sample_rate)
        hp_out = hp_alpha * (self._hp_state + sample - self._hp_state)
        self._hp_state = _clamp_sample(sample)
        filtered = sample - (sample - hp_out)

        # Simplified HP: subtract LP of low frequencies
        hp_cutoff_norm = self.filter_hp_freq / self.sample_rate
        hp_coeff = 1.0 - np.exp(-2.0 * np.pi * hp_cutoff_norm)
        self._hp_state = _clamp_sample(self._hp_state + hp_coeff * (sample - self._hp_state))
        filtered = sample - self._hp_state

        # Low-pass filter (tape-like high-frequency loss)
        lp_cutoff_norm = self.filter_lp_freq / self.sample_rate
        lp_coeff = 1.0 - np.exp(-2.0 * np.pi * lp_cutoff_norm)
        self._lp_state = _clamp_sample(self._lp_state + lp_coeff * (filtered - self._lp_state))

        # Tape-style saturation (gentle warmth)
        # Blend between clean and saturated signal based on tape_saturation amount
        saturated = np.tanh(self._lp_state * (1.0 + self.tape_saturation * 2.0))
        result = self._lp_state * (1.0 - self.tape_saturation) + saturated * self.tape_saturation

        return result

    def _lerp_read(self, delay_samples: float) -> float:
        """Read from delay buffer with linear interpolation for sub-sample accuracy

        This is essential for smooth pitch-shifting during analog-style time changes.
        """
        # Calculate read position (floating point for interpolation)
        read_pos = self.write_pos - delay_samples
        if read_pos < 0:
            read_pos += self.max_delay_samples

        # Integer and fractional parts for linear interpolation
        read_pos_int = int(read_pos)
        frac = read_pos - read_pos_int

        # Get two adjacent samples
        idx0 = read_pos_int % self.max_delay_samples
        idx1 = (read_pos_int + 1) % self.max_delay_samples

        # Linear interpolation between samples
        return self.buffer[idx0] * (1.0 - frac) + self.buffer[idx1] * frac

    def process(self, input_signal: np.ndarray) -> np.ndarray:
        """Process audio through the delay with analog-style time behavior

        When delay_time changes, the read position smoothly slides toward the
        new target, causing pitch-shifting of the audio in the buffer - just
        like real analog BBD delays or tape delays.
        """
        output = np.zeros_like(input_signal)
        wet = np.zeros_like(input_signal)

        # Target delay in samples (where we want to be)
        target_delay_samples = self.delay_time * self.sample_rate

        for i in range(len(input_signal)):
            # Analog behavior: smoothly slew toward target delay time
            # This creates pitch shifting when delay time changes
            if self._slew_rate == float('inf'):
                # Digital mode: instant jump
                self._current_delay_samples = target_delay_samples
            else:
                # Analog mode: smooth slew toward target
                diff = target_delay_samples - self._current_delay_samples
                if abs(diff) > self._slew_rate:
                    # Move toward target by slew_rate
                    if diff > 0:
                        self._current_delay_samples += self._slew_rate
                    else:
                        self._current_delay_samples -= self._slew_rate
                else:
                    # Close enough, snap to target
                    self._current_delay_samples = target_delay_samples

            # Add tape wobble modulation (slow) and flutter (fast) on top of current delay
            mod = np.sin(2.0 * np.pi * self.mod_rate * self._mod_phase / self.sample_rate)
            mod_samples = self.mod_depth * self.sample_rate * mod

            flutter = np.sin(2.0 * np.pi * self.flutter_rate * self._flutter_phase / self.sample_rate)
            flutter_samples = self.flutter_depth * self.sample_rate * flutter

            delay_samples = self._current_delay_samples + mod_samples + flutter_samples

            # Clamp to valid range (keep as float for interpolation)
            delay_samples = max(1.0, min(delay_samples, self.max_delay_samples - 2.0))

            self._mod_phase += 1
            if self._mod_phase >= self.sample_rate:
                self._mod_phase = 0

            self._flutter_phase += 1
            if self._flutter_phase >= self.sample_rate:
                self._flutter_phase = 0

            # Read from delay buffer with linear interpolation
            # This is crucial for smooth pitch-shifting
            delayed = self._lerp_read(delay_samples)

            # Process feedback through filters
            feedback_signal = self._process_feedback_filters(delayed)

            # Write to buffer: input + filtered/saturated feedback
            # Clamp buffer write to prevent runaway values that lead to NaN
            self.buffer[self.write_pos] = _clamp_sample(input_signal[i] + feedback_signal * self.feedback)

            # Advance write position
            self.write_pos = (self.write_pos + 1) % self.max_delay_samples

            # Store wet signal (just the delayed part)
            wet[i] = delayed

        # Mix dry and wet signals
        output = input_signal * (1.0 - self.dry_wet) + wet * self.dry_wet

        return output

    def set_delay_time(self, time: float):
        """Set delay time in seconds

        In analog mode (repitch_rate > 0), changing this will cause pitch-shifting
        as the delay smoothly slides to the new time.
        """
        self.delay_time = max(0.001, min(time, 2.0))

    def set_repitch_rate(self, rate: float):
        """Set analog repitch rate (0.0 to 1.0)

        Controls how the delay behaves when time is changed:
        - 0.0 = Digital mode: instant time changes (no pitch shifting)
        - 0.5 = Moderate: noticeable pitch wobble when changing time
        - 1.0 = Maximum: dramatic pitch sweeps, slow response

        Higher values = slower slew = more dramatic pitch effects when
        turning the delay time knob.
        """
        self.repitch_rate = max(0.0, min(rate, 1.0))
        self._slew_rate = self._calculate_slew_rate()

    def set_feedback(self, feedback: float):
        """Set delay feedback (0.0 to 1.0)"""
        self.feedback = max(0.0, min(feedback, 0.95))

    def set_dry_wet(self, dry_wet: float):
        """Set dry/wet mix (0.0 = dry, 1.0 = wet)"""
        self.dry_wet = max(0.0, min(dry_wet, 1.0))

    def set_filter_hp(self, freq: float):
        """Set feedback high-pass filter frequency"""
        self.filter_hp_freq = max(20.0, min(freq, 2000.0))

    def set_filter_lp(self, freq: float):
        """Set feedback low-pass filter frequency"""
        self.filter_lp_freq = max(200.0, min(freq, 20000.0))

    def set_mod_depth(self, depth: float):
        """Set time modulation depth in seconds"""
        self.mod_depth = max(0.0, min(depth, 0.01))

    def set_mod_rate(self, rate: float):
        """Set time modulation rate in Hz"""
        self.mod_rate = max(0.1, min(rate, 5.0))

    def set_flutter_depth(self, depth: float):
        """Set flutter modulation depth in seconds (fast tape variations)"""
        self.flutter_depth = max(0.0, min(depth, 0.005))

    def set_flutter_rate(self, rate: float):
        """Set flutter modulation rate in Hz (typically faster than main wobble)"""
        self.flutter_rate = max(0.5, min(rate, 10.0))

    def set_tape_saturation(self, amount: float):
        """Set tape saturation amount (0.0 = clean, 1.0 = heavy saturation)"""
        self.tape_saturation = max(0.0, min(amount, 1.0))


class AllpassFilter:
    """Allpass filter for reverb diffusion

    Creates density and smoothness in reverb without coloring the frequency response.
    """

    def __init__(self, delay_samples: int):
        self.delay_samples = delay_samples
        self.buffer = np.zeros(delay_samples)
        self.write_pos = 0
        self.feedback = 0.5  # Diffusion amount

    def process(self, input_val: float) -> float:
        """Process one sample through the allpass filter

        Buffer writes are clamped to prevent runaway values that lead to NaN.
        """
        # Read from delay buffer
        read_pos = (self.write_pos - self.delay_samples + len(self.buffer)) % len(self.buffer)
        delayed = self.buffer[read_pos]

        # Allpass formula: y = -x + d + g*(x - d)
        # where g is feedback coefficient, d is delayed signal
        output = -input_val + delayed + self.feedback * (input_val - delayed)

        # Write to buffer with clamping to prevent NaN
        self.buffer[self.write_pos] = _clamp_sample(input_val + self.feedback * delayed)
        self.write_pos = (self.write_pos + 1) % len(self.buffer)

        return output


class DampedCombFilter:
    """Comb filter with frequency-dependent damping for warm, chamber-like reverb

    Features high-frequency damping to simulate air absorption and wall materials.
    """

    def __init__(self, sample_rate: int, delay_time: float):
        self.sample_rate = sample_rate
        self.delay_samples = int(delay_time * sample_rate)
        self.buffer = np.zeros(self.delay_samples)
        self.write_pos = 0

        self.feedback = 0.7
        self.damping = 0.5  # 0.0 = no damping (bright), 1.0 = heavy damping (dark/warm)
        self._damper_state = 0.0  # One-pole lowpass filter state

        # Modulation for natural sound (very subtle)
        self.mod_depth_samples = 2.0  # Small modulation in samples
        self.mod_rate = 0.3  # Hz
        self._mod_phase = np.random.rand() * 2 * np.pi  # Random starting phase

    def process(self, input_val: float) -> float:
        """Process one sample through the damped comb filter

        State and buffer writes are clamped to prevent runaway values that lead to NaN.
        """
        # Calculate modulated read position
        mod_offset = self.mod_depth_samples * np.sin(self._mod_phase)
        self._mod_phase += 2 * np.pi * self.mod_rate / self.sample_rate
        if self._mod_phase > 2 * np.pi:
            self._mod_phase -= 2 * np.pi

        # Read from buffer with interpolation
        read_pos_float = self.write_pos - self.delay_samples + mod_offset
        read_pos_int = int(read_pos_float) % len(self.buffer)
        read_pos_next = (read_pos_int + 1) % len(self.buffer)
        frac = read_pos_float - int(read_pos_float)

        delayed = self.buffer[read_pos_int] * (1 - frac) + self.buffer[read_pos_next] * frac

        # Apply damping (one-pole lowpass filter in feedback path)
        # This simulates high-frequency absorption in the room
        damping_coeff = 1.0 - self.damping * 0.5  # Convert to filter coefficient
        # Clamp damper state to prevent runaway values
        self._damper_state = _clamp_sample(damping_coeff * delayed + (1.0 - damping_coeff) * self._damper_state)

        # Comb filter formula with damped feedback
        output = delayed
        # Clamp buffer write to prevent NaN
        self.buffer[self.write_pos] = _clamp_sample(input_val + self._damper_state * self.feedback)
        self.write_pos = (self.write_pos + 1) % len(self.buffer)

        return output


class ReverbEffect:
    """Hybrid chamber reverb effect inspired by Ableton Live

    Combines:
    - Early reflections for spatial character
    - Allpass filters for diffusion and density
    - Damped comb filters for warm, chamber-like tail
    - Subtle modulation for natural, non-metallic sound

    This creates a rich, smooth reverb suitable for dub music.
    """

    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate

        # Early reflections - simulates first bounces off chamber walls
        # Times chosen to suggest medium-large chamber (4-5 meters)
        self.early_reflection_times = [0.013, 0.019, 0.023, 0.029, 0.037, 0.043, 0.051, 0.059]
        self.early_buffers = [np.zeros(int(t * sample_rate)) for t in self.early_reflection_times]
        self.early_write_pos = [0] * len(self.early_reflection_times)
        self.early_level = 0.15  # Mix level of early reflections

        # Allpass filters for diffusion (creates density and smoothness)
        # Prime-number delays to avoid resonances
        self.input_diffusion = [
            AllpassFilter(int(0.005 * sample_rate)),   # 5ms
            AllpassFilter(int(0.0089 * sample_rate)),  # 8.9ms
        ]

        # Damped comb filters - these create the reverb tail
        # Delay times chosen for chamber character (avoiding harsh resonances)
        self.comb_filters = [
            DampedCombFilter(sample_rate, 0.0297),
            DampedCombFilter(sample_rate, 0.0371),
            DampedCombFilter(sample_rate, 0.0411),
            DampedCombFilter(sample_rate, 0.0437),
            DampedCombFilter(sample_rate, 0.0503),  # Added two more for richer sound
            DampedCombFilter(sample_rate, 0.0571),
        ]

        # Output diffusion (smooths the sound)
        self.output_diffusion = AllpassFilter(int(0.0067 * sample_rate))  # 6.7ms

        # Control parameters (match browser test defaults)
        self.size = 0.5       # Room size / decay time (0.0 to 1.0 - matches browser test)
        self.dry_wet = 0.0    # Mix (0.0 = dry, 1.0 = wet - matches browser test)
        self.damping = 0.5    # High-frequency damping / warmth (0.0 = bright, 1.0 = dark)

        self._update_parameters()

    def _update_parameters(self):
        """Update filter parameters based on size and damping controls"""
        # Size controls feedback (decay time)
        base_feedback = 0.4 + self.size * 0.45  # Range: 0.4 to 0.85
        for comb in self.comb_filters:
            comb.feedback = base_feedback
            # Damping simulates air absorption and chamber wall materials
            comb.damping = self.damping

    def _process_early_reflections(self, input_signal: np.ndarray) -> np.ndarray:
        """Process early reflections - simulates initial bounces off chamber walls

        Buffer writes are clamped to prevent runaway values that lead to NaN.
        """
        output = np.zeros_like(input_signal)

        for i in range(len(input_signal)):
            early_sum = 0.0
            for buf_idx, buf in enumerate(self.early_buffers):
                # Read delayed sample
                read_pos = self.early_write_pos[buf_idx]
                early_sum += buf[read_pos]

                # Write input with slight attenuation and variation
                # Clamp buffer write to prevent NaN
                attenuation = 0.7 - buf_idx * 0.05  # Earlier reflections are stronger
                buf[read_pos] = _clamp_sample(input_signal[i] * attenuation)

                # Advance write position
                self.early_write_pos[buf_idx] = (read_pos + 1) % len(buf)

            output[i] = early_sum / len(self.early_buffers)

        return output

    def process(self, input_signal: np.ndarray) -> np.ndarray:
        """Process audio through the hybrid chamber reverb"""
        # Early reflections
        early = self._process_early_reflections(input_signal)

        # Process through input diffusion (allpass filters)
        diffused = input_signal.copy()
        for i in range(len(diffused)):
            for allpass in self.input_diffusion:
                diffused[i] = allpass.process(diffused[i])

        # Process through parallel comb filters (creates reverb tail)
        comb_output = np.zeros_like(input_signal)
        for i in range(len(input_signal)):
            comb_sum = 0.0
            for comb in self.comb_filters:
                comb_sum += comb.process(diffused[i])
            comb_output[i] = comb_sum / len(self.comb_filters)

        # Output diffusion (final smoothing)
        for i in range(len(comb_output)):
            comb_output[i] = self.output_diffusion.process(comb_output[i])

        # Combine early reflections and reverb tail
        wet = early * self.early_level + comb_output

        # Mix dry and wet
        return input_signal * (1.0 - self.dry_wet) + wet * self.dry_wet

    def set_size(self, size: float):
        """Set reverb size / decay time (0.0 to 1.0)"""
        self.size = max(0.0, min(size, 1.0))
        self._update_parameters()

    def set_dry_wet(self, dry_wet: float):
        """Set dry/wet mix (0.0 to 1.0)"""
        self.dry_wet = max(0.0, min(dry_wet, 1.0))


class DubSiren:
    """Main Dub Siren Synthesizer"""

    def __init__(self, sample_rate: int = 48000, buffer_size: int = 512):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size

        # Audio components
        self.oscillator = Oscillator(sample_rate)
        self.lfo = LFO(sample_rate)
        self.envelope = Envelope(sample_rate)
        self._env_lock = threading.Lock()
        self.filter = LowPassFilter(sample_rate)
        self.delay = DelayEffect(sample_rate)
        self.reverb = ReverbEffect(sample_rate)
        self.dc_blocker = DCBlocker()  # Removes DC offset before output

        # Control parameters (match browser test defaults)
        self.volume = 0.7  # Browser preset default
        self.is_running = False

        # Frequency control
        self.base_frequency = 440.0  # A4 - good test tone for pitch oscillator

        # LFO defaults (disabled for stable pitch; browser-style wobble can be re-enabled via UI)
        self.lfo.set_waveform('sine')
        self.lfo.frequency = 4.0
        self.lfo.depth = 0.0  # disable wobble by default

        # Pitch envelope: 'none', 'up', 'down'
        self.pitch_envelope = 'none'  # keep off for stability
        self._pitch_env_modes = ['none', 'up', 'down']

        # NaN protection monitoring
        self._nan_events = 0  # Count of NaN occurrences for debugging
        
        # Diagnostic monitoring
        self._buffer_count = 0
        self._last_log_time = 0.0

    def trigger(self):
        """Trigger sound at current base_frequency"""
        with self._env_lock:
            self.oscillator.set_frequency(self.base_frequency)
            self.envelope.trigger()

    def release(self):
        """Release sound (pitch envelope will be applied during generate_audio)"""
        with self._env_lock:
            self.envelope.release_trigger()

    def cycle_pitch_envelope(self):
        """Cycle through pitch envelope modes: none -> up -> down -> none"""
        current_index = self._pitch_env_modes.index(self.pitch_envelope)
        next_index = (current_index + 1) % len(self._pitch_env_modes)
        self.pitch_envelope = self._pitch_env_modes[next_index]
        return self.pitch_envelope

    def set_pitch_envelope(self, mode: str):
        """Set pitch envelope mode ('none', 'up', 'down')"""
        if mode in self._pitch_env_modes:
            self.pitch_envelope = mode

    def set_frequency(self, freq: float):
        """Set base frequency for triggering and during playback/release

        This allows real-time frequency control even during the decay/release phase.
        The pitch envelope (if active) will be applied as a multiplier on top of this.
        """
        self.base_frequency = max(20.0, min(freq, 20000.0))
        # Update live oscillator frequency directly
        # This gives real-time pitch control via encoder
        self.oscillator.set_frequency(self.base_frequency)

    # Legacy methods for backwards compatibility with gpio_controller
    def trigger_airhorn(self):
        """Legacy: Trigger at base frequency"""
        self.trigger()

    def release_airhorn(self):
        """Legacy: Release sound"""
        self.release()

    def trigger_siren(self):
        """Legacy: Trigger at base frequency"""
        self.trigger()

    def release_siren(self):
        """Legacy: Release sound"""
        self.release()

    def generate_audio(self, num_samples: int) -> np.ndarray:
        """Generate audio buffer with stable filtering

        Processing chain:
        1. Generate anti-aliased oscillator (PolyBLEP square wave)
        2. Process through stable one-pole low-pass filter
        3. Apply envelope
        4. DC blocker
        5. Volume control
        """
        output = np.zeros(num_samples, dtype=np.float32)

        # Get envelope state
        env_target = 1.0 if self.envelope.is_active else 0.0
        env_coeff = self.envelope.attack_coeff if self.envelope.is_active else self.envelope.release_coeff

        # Generate anti-aliased square wave using PolyBLEP
        self.oscillator.waveform = 'square'
        raw_buffer = self.oscillator.generate(num_samples)

        # Process through stable low-pass filter (vectorized)
        filtered = self.filter.process(raw_buffer)

        # Sample-by-sample envelope, DC blocking, and volume
        for i in range(num_samples):
            # === Envelope ===
            self.envelope.current_value += (env_target - self.envelope.current_value) * env_coeff
            env = self.envelope.current_value

            # Apply envelope to filtered signal
            voice = filtered[i] * env

            # === DC Blocker ===
            dc_out = voice - self.dc_blocker.x_prev + self.dc_blocker.coeff * self.dc_blocker.y_prev
            self.dc_blocker.x_prev = voice
            self.dc_blocker.y_prev = dc_out

            # === Volume ===
            output[i] = dc_out * self.volume

        # Diagnostic logging
        self._buffer_count += 1
        if self._buffer_count % 100 == 0:
            current_time = time.time()
            if current_time - self._last_log_time >= 2.0:
                filtered_rms = np.sqrt(np.mean(filtered**2))
                output_rms = np.sqrt(np.mean(output**2))
                print(f"[DEBUG] env={self.envelope.current_value:.4f}, "
                      f"filter_state={self.filter.prev_output:.4f}, "
                      f"filtered_rms={filtered_rms:.4f}, "
                      f"output_rms={output_rms:.4f}, "
                      f"cutoff={self.filter.cutoff:.1f}Hz")
                self._last_log_time = current_time

        # Final clipping
        return np.clip(output, -1.0, 1.0)

    # Control setters
    def set_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(volume, 1.0))

    def set_filter_frequency(self, freq: float):
        """Set low-pass filter cutoff frequency"""
        self.filter.set_cutoff(freq)

    def set_filter_resonance(self, res: float):
        """Set filter resonance"""
        self.filter.set_resonance(res)

    def set_delay_time(self, time: float):
        """Set delay time"""
        self.delay.set_delay_time(time)

    def set_delay_feedback(self, feedback: float):
        """Set delay feedback"""
        self.delay.set_feedback(feedback)

    def set_delay_dry_wet(self, dry_wet: float):
        """Set delay dry/wet mix"""
        self.delay.set_dry_wet(dry_wet)

    def set_delay_filter_hp(self, freq: float):
        """Set delay feedback high-pass filter frequency"""
        self.delay.set_filter_hp(freq)

    def set_delay_filter_lp(self, freq: float):
        """Set delay feedback low-pass filter frequency"""
        self.delay.set_filter_lp(freq)

    def set_delay_repitch_rate(self, rate: float):
        """Set delay analog repitch rate (0.0 to 1.0)

        Controls how the delay responds to time changes:
        - 0.0 = Digital: instant time changes
        - 0.5 = Moderate analog behavior with pitch wobble
        - 1.0 = Maximum: dramatic pitch sweeps like tape/BBD delays
        """
        self.delay.set_repitch_rate(rate)

    def set_reverb_size(self, size: float):
        """Set reverb size"""
        self.reverb.set_size(size)

    def set_reverb_dry_wet(self, dry_wet: float):
        """Set reverb dry/wet mix"""
        self.reverb.set_dry_wet(dry_wet)

    def set_release_time(self, release: float):
        """Set oscillator envelope release time"""
        self.envelope.set_release(release)

    def set_oscillator_waveform(self, waveform_index: int):
        """Set oscillator waveform (0=sine, 1=square, 2=saw, 3=triangle)"""
        waveforms: list[WaveformType] = ['sine', 'square', 'saw', 'triangle']
        index = waveform_index % len(waveforms)
        self.oscillator.set_waveform(waveforms[index])

    def set_lfo_waveform(self, waveform_index: int):
        """Set LFO waveform (0=sine, 1=square, 2=saw, 3=triangle)"""
        waveforms: list[WaveformType] = ['sine', 'square', 'saw', 'triangle']
        index = waveform_index % len(waveforms)
        self.lfo.set_waveform(waveforms[index])

    def get_nan_events(self) -> int:
        """Get count of NaN events detected during audio generation

        Useful for debugging audio issues. A high count may indicate
        filter instability or problematic parameter settings.
        """
        return self._nan_events

    def reset_nan_events(self):
        """Reset the NaN event counter"""
        self._nan_events = 0


if __name__ == "__main__":
    # Test the synthesizer
    print("Dub Siren Synthesizer Engine")
    print("Testing audio generation...")

    synth = DubSiren()
    synth.set_frequency(440.0)
    synth.set_pitch_envelope('down')
    synth.trigger()

    # Generate a few buffers during sustain
    print("\nSustain phase:")
    for i in range(5):
        audio = synth.generate_audio(256)
        has_nan = not np.all(np.isfinite(audio))
        print(f"Buffer {i}: min={audio.min():.3f}, max={audio.max():.3f}, freq={synth.oscillator.frequency:.1f}Hz")

    # Release and generate during release (pitch envelope active)
    synth.release()
    print("\nRelease phase (pitch envelope: down):")
    for i in range(10):
        audio = synth.generate_audio(256)
        has_nan = not np.all(np.isfinite(audio))
        print(f"Buffer {i}: min={audio.min():.3f}, max={audio.max():.3f}, freq={synth.oscillator.frequency:.1f}Hz")

    print(f"\nNaN events detected: {synth.get_nan_events()}")
    print("Test complete!")
