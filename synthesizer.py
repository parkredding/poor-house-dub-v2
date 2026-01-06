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
    """Delay/Echo effect"""

    def __init__(self, sample_rate: int = 48000, max_delay: float = 2.0):
        self.sample_rate = sample_rate
        self.max_delay_samples = int(max_delay * sample_rate)
        self.buffer = deque([0.0] * self.max_delay_samples, maxlen=self.max_delay_samples)
        self.delay_time = 0.5  # seconds
        self.feedback = 0.3    # 0.0 to 1.0

    def process(self, input_signal: np.ndarray) -> np.ndarray:
        """Process audio through the delay"""
        output = np.zeros_like(input_signal)
        delay_samples = int(self.delay_time * self.sample_rate)
        delay_samples = min(delay_samples, self.max_delay_samples - 1)

        for i in range(len(input_signal)):
            # Get delayed sample
            delayed = self.buffer[-delay_samples] if delay_samples < len(self.buffer) else 0.0

            # Mix with input and feedback
            output[i] = input_signal[i] + delayed * self.feedback

            # Add to buffer
            self.buffer.append(output[i])

        return output

    def set_delay_time(self, time: float):
        """Set delay time in seconds"""
        self.delay_time = max(0.001, min(time, 2.0))

    def set_feedback(self, feedback: float):
        """Set delay feedback (0.0 to 1.0)"""
        self.feedback = max(0.0, min(feedback, 0.95))


class ReverbEffect:
    """Simple reverb effect using multiple delays"""

    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        # Schroeder reverb with 4 comb filters
        self.delays = [
            DelayEffect(sample_rate, max_delay=0.1),
            DelayEffect(sample_rate, max_delay=0.1),
            DelayEffect(sample_rate, max_delay=0.1),
            DelayEffect(sample_rate, max_delay=0.1),
        ]
        self.delays[0].delay_time = 0.0297
        self.delays[1].delay_time = 0.0371
        self.delays[2].delay_time = 0.0411
        self.delays[3].delay_time = 0.0437

        self.size = 0.5      # Room size (0.0 to 1.0)
        self.dry_wet = 0.3   # Mix (0.0 = dry, 1.0 = wet)
        self._update_delays()

    def _update_delays(self):
        """Update delay parameters based on size"""
        base_feedback = 0.3 + self.size * 0.5
        for delay in self.delays:
            delay.feedback = base_feedback

    def process(self, input_signal: np.ndarray) -> np.ndarray:
        """Process audio through the reverb"""
        # Sum all comb filter outputs
        wet = np.zeros_like(input_signal)
        for delay in self.delays:
            wet += delay.process(input_signal) / len(self.delays)

        # Mix dry and wet
        return input_signal * (1.0 - self.dry_wet) + wet * self.dry_wet

    def set_size(self, size: float):
        """Set reverb size (0.0 to 1.0)"""
        self.size = max(0.0, min(size, 1.0))
        self._update_delays()

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
        """Generate audio buffer"""
        # Generate oscillator output
        audio = self.oscillator.generate(num_samples)

        # Apply LFO modulation to frequency
        lfo_signal = self.lfo.generate(num_samples)
        # Modulate oscillator frequency (this is a simplified approach)
        # In a real-time system, you'd apply this per-sample

        # Apply envelope
        env = self.envelope.generate(num_samples)
        audio = audio * env

        # Apply filter
        audio = self.filter.process(audio)

        # Apply delay
        audio = self.delay.process(audio)

        # Apply reverb
        audio = self.reverb.process(audio)

        # Apply volume
        audio = audio * self.volume

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


if __name__ == "__main__":
    # Test the synthesizer
    print("Dub Siren Synthesizer Engine")
    print("Testing audio generation...")

    synth = DubSiren()
    synth.trigger_airhorn()

    # Generate a few buffers
    for i in range(10):
        audio = synth.generate_audio(256)
        print(f"Buffer {i}: min={audio.min():.3f}, max={audio.max():.3f}, mean={audio.mean():.3f}")

    print("Test complete!")
