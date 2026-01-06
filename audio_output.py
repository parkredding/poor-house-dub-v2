#!/usr/bin/env python3
"""
Audio Output Handler for PCM5102 I2S DAC
Manages real-time audio streaming to the DAC
"""

import numpy as np
import threading
import queue
import time

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    print("WARNING: sounddevice not available. Audio output disabled.")
    SOUNDDEVICE_AVAILABLE = False


class AudioOutput:
    """Real-time audio output handler for PCM5102 DAC"""

    def __init__(
        self,
        synth,
        sample_rate: int = 48000,
        buffer_size: int = 256,
        channels: int = 2,
        device: str = None
    ):
        self.synth = synth
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.channels = channels
        self.device = device
        self.stream = None
        self.running = False
        self.audio_thread = None

        # Performance monitoring
        self.buffer_underruns = 0
        self.total_buffers = 0

    def _audio_callback(self, outdata, frames, time_info, status):
        """Audio callback function called by sounddevice"""
        if status:
            print(f"Audio status: {status}")
            if status.output_underflow:
                self.buffer_underruns += 1

        try:
            # Generate audio from synthesizer
            audio = self.synth.generate_audio(frames)

            # Convert mono to stereo if needed
            if self.channels == 2:
                audio = np.column_stack([audio, audio])
            elif self.channels == 1:
                audio = audio.reshape(-1, 1)

            # Copy to output buffer
            outdata[:] = audio.reshape(-1, self.channels).astype(np.float32)

            self.total_buffers += 1

        except Exception as e:
            print(f"Error in audio callback: {e}")
            # Output silence on error
            outdata.fill(0)

    def start(self):
        """Start audio output stream"""
        if not SOUNDDEVICE_AVAILABLE:
            print("Cannot start audio output: sounddevice not available")
            return False

        if self.running:
            print("Audio output already running")
            return True

        try:
            # List available devices for debugging
            if self.device is None:
                print("\nAvailable audio devices:")
                print(sd.query_devices())
                print()

            # Create and start the audio stream
            self.stream = sd.OutputStream(
                device=self.device,
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                channels=self.channels,
                dtype=np.float32,
                callback=self._audio_callback,
                finished_callback=self._stream_finished
            )

            self.stream.start()
            self.running = True
            print(f"Audio output started: {self.sample_rate}Hz, {self.buffer_size} samples, {self.channels} channels")
            return True

        except Exception as e:
            print(f"Failed to start audio output: {e}")
            return False

    def stop(self):
        """Stop audio output stream"""
        if not self.running:
            return

        self.running = False

        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                print(f"Error stopping audio stream: {e}")

        # Print performance stats
        if self.total_buffers > 0:
            underrun_rate = (self.buffer_underruns / self.total_buffers) * 100
            print(f"\nAudio performance:")
            print(f"  Total buffers: {self.total_buffers}")
            print(f"  Buffer underruns: {self.buffer_underruns} ({underrun_rate:.2f}%)")

        print("Audio output stopped")

    def _stream_finished(self):
        """Called when stream is finished"""
        print("Audio stream finished")

    def get_stats(self) -> dict:
        """Get audio output statistics"""
        return {
            'running': self.running,
            'sample_rate': self.sample_rate,
            'buffer_size': self.buffer_size,
            'channels': self.channels,
            'total_buffers': self.total_buffers,
            'buffer_underruns': self.buffer_underruns,
        }


class SimulatedAudioOutput:
    """Simulated audio output for testing without audio hardware"""

    def __init__(self, synth, **kwargs):
        self.synth = synth
        self.running = False
        self.thread = None
        print("Running in SIMULATION mode (no audio output)")

    def _simulation_thread(self):
        """Simulate audio callback at regular intervals"""
        buffer_duration = 256 / 48000.0  # ~5.3ms
        while self.running:
            # Generate audio (but don't output it)
            self.synth.generate_audio(256)
            time.sleep(buffer_duration)

    def start(self):
        """Start simulated audio output"""
        self.running = True
        self.thread = threading.Thread(target=self._simulation_thread, daemon=True)
        self.thread.start()
        print("Simulated audio output started")
        return True

    def stop(self):
        """Stop simulated audio output"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        print("Simulated audio output stopped")

    def get_stats(self) -> dict:
        return {'running': self.running, 'simulated': True}


def list_audio_devices():
    """List all available audio devices"""
    if not SOUNDDEVICE_AVAILABLE:
        print("sounddevice not available")
        return

    print("Available audio devices:")
    print(sd.query_devices())


def find_pcm5102_device():
    """Try to automatically find the PCM5102 device"""
    if not SOUNDDEVICE_AVAILABLE:
        return None

    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        # Look for common PCM5102 device names
        name = device['name'].lower()
        if any(keyword in name for keyword in ['pcm5102', 'i2s', 'hifiberry', 'dac']):
            if device['max_output_channels'] > 0:
                print(f"Found potential PCM5102 device: {device['name']} (index {idx})")
                return idx

    return None


if __name__ == "__main__":
    # Test audio output
    from synthesizer import DubSiren

    print("Audio Output Test")
    print("=" * 50)

    # List available devices
    list_audio_devices()
    print()

    # Try to find PCM5102
    device_idx = find_pcm5102_device()
    if device_idx is not None:
        print(f"Using device index: {device_idx}")
    else:
        print("Using default audio device")

    # Create synthesizer and audio output
    synth = DubSiren()

    if SOUNDDEVICE_AVAILABLE:
        audio = AudioOutput(synth, device=device_idx)
    else:
        audio = SimulatedAudioOutput(synth)

    # Start audio
    if audio.start():
        try:
            print("\nPlaying test tone for 5 seconds...")
            synth.trigger_airhorn()
            time.sleep(5)
            synth.release_airhorn()
            time.sleep(1)

            print("\nAudio stats:")
            print(audio.get_stats())

        except KeyboardInterrupt:
            print("\nInterrupted")
        finally:
            audio.stop()
    else:
        print("Failed to start audio output")
