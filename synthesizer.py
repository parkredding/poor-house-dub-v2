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
    """Audio oscillator with multiple waveform types"""

    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.frequency = 440.0
        self.phase = 0.0
        self.waveform: WaveformType = 'sine'

    def generate(self, num_samples: int) -> np.ndarray:
        """Generate audio samples for the current waveform"""
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

        # Update phase for continuity
        self.phase += num_samples
        self.phase = self.phase % self.sample_rate

        return output

    def set_frequency(self, freq: float):
        """Set oscillator frequency in Hz"""
        self.frequency = max(20.0, min(freq, 20000.0))

    def set_waveform(self, waveform: WaveformType):
        """Set oscillator waveform type"""
        if waveform in ['sine', 'square', 'saw', 'triangle']:
            self.waveform = waveform


class LFO:
    """Low Frequency Oscillator for modulation"""

    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.frequency = 2.0  # Hz
        self.phase = 0.0
        self.waveform: WaveformType = 'sine'
        self.depth = 0.5  # 0.0 to 1.0

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
    """ADSR Envelope Generator"""

    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.attack = 0.01   # seconds
        self.decay = 0.1     # seconds
        self.sustain = 0.7   # level (0.0 to 1.0)
        self.release = 0.5   # seconds
        self.current_sample = 0
        self.is_active = False
        self.is_releasing = False
        self.release_level = 0.0

    def trigger(self):
        """Trigger the envelope"""
        self.current_sample = 0
        self.is_active = True
        self.is_releasing = False

    def release_trigger(self):
        """Release the envelope"""
        if self.is_active:
            self.is_releasing = True
            # Capture current level for smooth release
            attack_samples = int(self.attack * self.sample_rate)
            decay_samples = int(self.decay * self.sample_rate)

            if self.current_sample < attack_samples:
                self.release_level = self.current_sample / attack_samples
            elif self.current_sample < attack_samples + decay_samples:
                progress = (self.current_sample - attack_samples) / decay_samples
                self.release_level = 1.0 - (1.0 - self.sustain) * progress
            else:
                self.release_level = self.sustain

            self.current_sample = 0

    def generate(self, num_samples: int) -> np.ndarray:
        """Generate envelope values"""
        if not self.is_active:
            return np.zeros(num_samples)

        output = np.zeros(num_samples)

        attack_samples = int(self.attack * self.sample_rate)
        decay_samples = int(self.decay * self.sample_rate)
        release_samples = int(self.release * self.sample_rate)

        for i in range(num_samples):
            if self.is_releasing:
                # Release phase
                if self.current_sample < release_samples:
                    progress = self.current_sample / release_samples
                    output[i] = self.release_level * (1.0 - progress)
                    self.current_sample += 1
                else:
                    output[i] = 0.0
                    self.is_active = False
                    self.is_releasing = False
            else:
                # Attack phase
                if self.current_sample < attack_samples:
                    output[i] = self.current_sample / attack_samples
                # Decay phase
                elif self.current_sample < attack_samples + decay_samples:
                    progress = (self.current_sample - attack_samples) / decay_samples
                    output[i] = 1.0 - (1.0 - self.sustain) * progress
                # Sustain phase
                else:
                    output[i] = self.sustain

                self.current_sample += 1

        return output

    def set_release(self, release_time: float):
        """Set release time in seconds"""
        self.release = max(0.001, min(release_time, 10.0))


class LowPassFilter:
    """Simple one-pole low-pass filter"""

    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.cutoff = 1000.0  # Hz
        self.resonance = 0.1  # 0.0 to 1.0
        self.prev_output = 0.0

    def process(self, input_signal: np.ndarray) -> np.ndarray:
        """Process audio through the filter"""
        # Calculate filter coefficient
        rc = 1.0 / (2.0 * np.pi * self.cutoff)
        dt = 1.0 / self.sample_rate
        alpha = dt / (rc + dt)

        # Add resonance (feedback)
        alpha = alpha * (1.0 + self.resonance * 2.0)
        alpha = min(alpha, 0.99)

        output = np.zeros_like(input_signal)

        for i in range(len(input_signal)):
            output[i] = self.prev_output + alpha * (input_signal[i] - self.prev_output)
            self.prev_output = output[i]

        return output

    def set_cutoff(self, freq: float):
        """Set filter cutoff frequency in Hz"""
        self.cutoff = max(20.0, min(freq, 20000.0))

    def set_resonance(self, res: float):
        """Set filter resonance (0.0 to 1.0)"""
        self.resonance = max(0.0, min(res, 0.95))


class DelayEffect:
    """Analog-style Delay/Echo effect with BBD/tape-like behavior

    Features:
    - Dry/Wet mix control
    - High-pass and low-pass filters in feedback path (prevents mud and harsh highs)
    - Soft saturation for analog warmth
    - Time modulation for tape-like wobble
    - Analog repitch behavior: changing delay time causes pitch-shifting of repeats
      (like real BBD or tape delays where the audio "smears" when you change time)
    """

    def __init__(self, sample_rate: int = 48000, max_delay: float = 2.0):
        self.sample_rate = sample_rate
        self.max_delay_samples = int(max_delay * sample_rate)
        self.buffer = np.zeros(self.max_delay_samples)
        self.write_pos = 0

        # Core delay parameters
        self.delay_time = 0.5  # seconds (target delay time)
        self.feedback = 0.5    # 0.0 to 1.0
        self.dry_wet = 0.5     # 0.0 = dry, 1.0 = wet

        # Analog repitch behavior - smoothly slide to new delay time
        # This creates pitch shifting when delay time changes (like BBD/tape)
        self._current_delay_samples = self.delay_time * sample_rate  # actual read offset
        self.repitch_rate = 0.5  # 0.0 = instant (digital), 1.0 = very slow/dramatic pitch shift
        # Internal: samples to move per sample (derived from repitch_rate)
        self._slew_rate = self._calculate_slew_rate()

        # Feedback filter parameters (Ableton-style)
        self.filter_hp_freq = 80.0     # High-pass cutoff Hz (removes mud)
        self.filter_lp_freq = 8000.0   # Low-pass cutoff Hz (tames highs)

        # Filter states for feedback path
        self._hp_state = 0.0
        self._lp_state = 0.0

        # Saturation/warmth
        self.saturation = 0.2  # 0.0 = clean, 1.0 = saturated

        # Time modulation (for tape-like wobble)
        self.mod_depth = 0.002    # modulation depth in seconds
        self.mod_rate = 0.5       # modulation rate in Hz
        self._mod_phase = 0.0

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

    def _soft_clip(self, x: float, amount: float) -> float:
        """Soft saturation for warmth (tanh-style)"""
        if amount <= 0:
            return x
        # Mix between clean and saturated based on amount
        drive = 1.0 + amount * 3.0
        saturated = np.tanh(x * drive) / drive
        return x * (1.0 - amount) + saturated * amount

    def _process_feedback_filters(self, sample: float) -> float:
        """Apply HP and LP filters to feedback path (prevents buildup)"""
        # High-pass filter (removes mud/low-end buildup)
        hp_rc = 1.0 / (2.0 * np.pi * self.filter_hp_freq)
        hp_alpha = hp_rc / (hp_rc + 1.0 / self.sample_rate)
        hp_out = hp_alpha * (self._hp_state + sample - self._hp_state)
        self._hp_state = sample
        filtered = sample - (sample - hp_out)

        # Simplified HP: subtract LP of low frequencies
        hp_cutoff_norm = self.filter_hp_freq / self.sample_rate
        hp_coeff = 1.0 - np.exp(-2.0 * np.pi * hp_cutoff_norm)
        self._hp_state = self._hp_state + hp_coeff * (sample - self._hp_state)
        filtered = sample - self._hp_state

        # Low-pass filter (tames harsh highs)
        lp_cutoff_norm = self.filter_lp_freq / self.sample_rate
        lp_coeff = 1.0 - np.exp(-2.0 * np.pi * lp_cutoff_norm)
        self._lp_state = self._lp_state + lp_coeff * (filtered - self._lp_state)

        return self._lp_state

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

            # Add tape wobble modulation on top of current delay
            mod = np.sin(2.0 * np.pi * self.mod_rate * self._mod_phase / self.sample_rate)
            mod_samples = self.mod_depth * self.sample_rate * mod
            delay_samples = self._current_delay_samples + mod_samples

            # Clamp to valid range (keep as float for interpolation)
            delay_samples = max(1.0, min(delay_samples, self.max_delay_samples - 2.0))

            self._mod_phase += 1
            if self._mod_phase >= self.sample_rate:
                self._mod_phase = 0

            # Read from delay buffer with linear interpolation
            # This is crucial for smooth pitch-shifting
            delayed = self._lerp_read(delay_samples)

            # Process feedback through filters and saturation
            feedback_signal = self._process_feedback_filters(delayed)
            feedback_signal = self._soft_clip(feedback_signal, self.saturation)

            # Write to buffer: input + filtered/saturated feedback
            self.buffer[self.write_pos] = input_signal[i] + feedback_signal * self.feedback

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

    def set_saturation(self, amount: float):
        """Set saturation/warmth amount (0.0 to 1.0)"""
        self.saturation = max(0.0, min(amount, 1.0))

    def set_mod_depth(self, depth: float):
        """Set time modulation depth in seconds"""
        self.mod_depth = max(0.0, min(depth, 0.01))

    def set_mod_rate(self, rate: float):
        """Set time modulation rate in Hz"""
        self.mod_rate = max(0.1, min(rate, 5.0))


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
        """Process one sample through the allpass filter"""
        # Read from delay buffer
        read_pos = (self.write_pos - self.delay_samples + len(self.buffer)) % len(self.buffer)
        delayed = self.buffer[read_pos]

        # Allpass formula: y = -x + d + g*(x - d)
        # where g is feedback coefficient, d is delayed signal
        output = -input_val + delayed + self.feedback * (input_val - delayed)

        # Write to buffer
        self.buffer[self.write_pos] = input_val + self.feedback * delayed
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
        """Process one sample through the damped comb filter"""
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
        self._damper_state = damping_coeff * delayed + (1.0 - damping_coeff) * self._damper_state

        # Comb filter formula with damped feedback
        output = delayed
        self.buffer[self.write_pos] = input_val + self._damper_state * self.feedback
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

        # Control parameters
        self.size = 0.5       # Room size / decay time (0.0 to 1.0)
        self.dry_wet = 0.3    # Mix (0.0 = dry, 1.0 = wet)
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
        """Process early reflections - simulates initial bounces off chamber walls"""
        output = np.zeros_like(input_signal)

        for i in range(len(input_signal)):
            early_sum = 0.0
            for buf_idx, buf in enumerate(self.early_buffers):
                # Read delayed sample
                read_pos = self.early_write_pos[buf_idx]
                early_sum += buf[read_pos]

                # Write input with slight attenuation and variation
                attenuation = 0.7 - buf_idx * 0.05  # Earlier reflections are stronger
                buf[read_pos] = input_signal[i] * attenuation

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

    def __init__(self, sample_rate: int = 48000, buffer_size: int = 256):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size

        # Audio components
        self.oscillator = Oscillator(sample_rate)
        self.lfo = LFO(sample_rate)
        self.envelope = Envelope(sample_rate)
        self.filter = LowPassFilter(sample_rate)
        self.delay = DelayEffect(sample_rate)
        self.reverb = ReverbEffect(sample_rate)

        # Control parameters
        self.volume = 0.5
        self.is_running = False

        # Preset frequencies for triggers
        self.airhorn_freq = 150.0  # Hz
        self.siren_freq = 800.0    # Hz

        # NaN protection monitoring
        self._nan_events = 0  # Count of NaN occurrences for debugging

    def trigger_airhorn(self):
        """Trigger airhorn sound"""
        self.oscillator.set_frequency(self.airhorn_freq)
        self.envelope.trigger()

    def release_airhorn(self):
        """Release airhorn sound"""
        self.envelope.release_trigger()

    def trigger_siren(self):
        """Trigger siren sound"""
        self.oscillator.set_frequency(self.siren_freq)
        self.envelope.trigger()

    def release_siren(self):
        """Release siren sound"""
        self.envelope.release_trigger()

    def generate_audio(self, num_samples: int) -> np.ndarray:
        """Generate audio buffer with NaN protection

        NaN values can propagate from filter instabilities, feedback loops,
        or DSP edge cases. They bypass volume control and clipping, causing
        "warbled" sounds that don't respond to controls. This method sanitizes
        audio after each effect stage to prevent NaN propagation.
        """
        # Generate oscillator output
        audio = self.oscillator.generate(num_samples)

        # Apply LFO modulation to frequency
        lfo_signal = self.lfo.generate(num_samples)
        # Modulate oscillator frequency (this is a simplified approach)
        # In a real-time system, you'd apply this per-sample

        # Apply envelope
        env = self.envelope.generate(num_samples)
        audio = audio * env

        # Apply filter (can produce NaN from high resonance/instability)
        audio = self.filter.process(audio)
        audio = sanitize_audio(audio)

        # Apply delay (feedback loops can produce NaN/Inf)
        audio = self.delay.process(audio)
        audio = sanitize_audio(audio)

        # Apply reverb (multiple feedback paths can accumulate errors)
        audio = self.reverb.process(audio)
        audio = sanitize_audio(audio)

        # Apply volume
        audio = audio * self.volume

        # Final safety check: sanitize and clip
        # Check for NaN before clipping (for monitoring)
        if not np.all(np.isfinite(audio)):
            self._nan_events += 1
            audio = sanitize_audio(audio)

        # Ensure output is within range
        audio = np.clip(audio, -1.0, 1.0)

        return audio

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

    def set_delay_saturation(self, amount: float):
        """Set delay saturation/warmth amount"""
        self.delay.set_saturation(amount)

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
    synth.trigger_airhorn()

    # Generate a few buffers
    for i in range(10):
        audio = synth.generate_audio(256)
        has_nan = not np.all(np.isfinite(audio))
        print(f"Buffer {i}: min={audio.min():.3f}, max={audio.max():.3f}, mean={audio.mean():.3f}, NaN={has_nan}")

    print(f"\nNaN events detected: {synth.get_nan_events()}")
    print("Test complete!")
