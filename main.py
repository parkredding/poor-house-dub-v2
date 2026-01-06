#!/usr/bin/env python3
"""
Dub Siren Main Application
Raspberry Pi Zero 2 based dub siren with PCM5102 DAC
"""

import sys
import time
import signal
import argparse
from synthesizer import DubSiren
from audio_output import AudioOutput, SimulatedAudioOutput, SOUNDDEVICE_AVAILABLE, find_pcm5102_device
from gpio_controller import ControlSurface, SimulatedControlSurface, GPIO_AVAILABLE


class DubSirenApp:
    """Main application class for the Dub Siren"""

    def __init__(
        self,
        sample_rate: int = 48000,
        buffer_size: int = 256,
        audio_device: int = None,
        simulate: bool = False
    ):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.audio_device = audio_device
        self.simulate = simulate
        self.running = False

        # Create synthesizer
        print("Initializing Dub Siren...")
        self.synth = DubSiren(sample_rate=sample_rate, buffer_size=buffer_size)

        # Create audio output
        if simulate or not SOUNDDEVICE_AVAILABLE:
            self.audio = SimulatedAudioOutput(self.synth)
        else:
            self.audio = AudioOutput(
                self.synth,
                sample_rate=sample_rate,
                buffer_size=buffer_size,
                channels=2,
                device=audio_device
            )

        # Create control surface
        if simulate or not GPIO_AVAILABLE:
            self.controller = SimulatedControlSurface(self.synth)
        else:
            self.controller = ControlSurface(self.synth)

    def start(self):
        """Start the dub siren"""
        if self.running:
            print("Dub siren already running")
            return

        print("\n" + "=" * 60)
        print("  DUB SIREN V2")
        print("  Raspberry Pi Zero 2 + PCM5102 DAC")
        print("=" * 60)
        print()

        # Start audio output
        if not self.audio.start():
            print("ERROR: Failed to start audio output")
            return False

        # Start control surface
        self.controller.start()

        self.running = True
        print("\n✓ Dub Siren is running!")
        print()
        self._print_controls()
        return True

    def stop(self):
        """Stop the dub siren"""
        if not self.running:
            return

        print("\nStopping Dub Siren...")
        self.running = False

        # Stop components
        self.controller.stop()
        self.audio.stop()

        print("✓ Dub Siren stopped")

    def _print_controls(self):
        """Print control layout"""
        print("Control Layout:")
        print("-" * 60)
        print("Row 1:")
        print("  [Volume]  [Filter Freq]  [Delay Time]  [Reverb Size]")
        print()
        print("Row 2:")
        print("  [Release] [Filter Res]   [Delay FB]    [Reverb Mix]")
        print()
        print("Row 3:")
        print("  [Osc Wave] [LFO Wave]  [AIRHORN]  [SIREN]")
        print("-" * 60)
        print()
        print("Waveforms: 0=Sine, 1=Square, 2=Saw, 3=Triangle")
        print()

    def print_status(self):
        """Print current status"""
        print("\nCurrent Status:")
        print("-" * 60)

        # Controller status
        status = self.controller.get_status()
        if status:
            print("Control Values:")
            for param, value in status.items():
                if isinstance(value, int):
                    waveforms = ['Sine', 'Square', 'Saw', 'Triangle']
                    print(f"  {param:20s}: {waveforms[value]}")
                else:
                    print(f"  {param:20s}: {value:.3f}")

        # Audio status
        audio_stats = self.audio.get_stats()
        print("\nAudio Status:")
        for key, value in audio_stats.items():
            print(f"  {key:20s}: {value}")

        print("-" * 60)

    def run_interactive(self):
        """Run in interactive mode"""
        if not self.start():
            return

        try:
            print("Interactive mode. Commands:")
            print("  s - Print status")
            print("  1 - Trigger airhorn (simulation mode)")
            print("  2 - Trigger siren (simulation mode)")
            print("  q - Quit")
            print()

            while self.running:
                cmd = input("> ").strip().lower()

                if cmd == 'q':
                    break
                elif cmd == 's':
                    self.print_status()
                elif cmd == '1' and self.simulate:
                    print("Triggering airhorn...")
                    self.synth.trigger_airhorn()
                    time.sleep(0.1)
                elif cmd == '2' and self.simulate:
                    print("Triggering siren...")
                    self.synth.trigger_siren()
                    time.sleep(0.1)
                elif cmd == 'r' and self.simulate:
                    print("Releasing...")
                    self.synth.release_airhorn()
                    self.synth.release_siren()
                elif cmd == 'help':
                    print("Commands: s=status, 1=airhorn, 2=siren, r=release, q=quit")
                else:
                    print("Unknown command. Type 'help' for commands.")

        except KeyboardInterrupt:
            print("\nInterrupted")
        except EOFError:
            print("\nEOF")
        finally:
            self.stop()

    def run_daemon(self):
        """Run as daemon"""
        if not self.start():
            return

        # Setup signal handlers
        signal.signal(signal.SIGINT, lambda s, f: self.stop())
        signal.signal(signal.SIGTERM, lambda s, f: self.stop())

        try:
            print("Running as daemon. Press Ctrl+C to stop.")
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.stop()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Dub Siren V2 - Raspberry Pi Zero 2 + PCM5102 DAC"
    )
    parser.add_argument(
        '--sample-rate',
        type=int,
        default=48000,
        help='Audio sample rate in Hz (default: 48000)'
    )
    parser.add_argument(
        '--buffer-size',
        type=int,
        default=256,
        help='Audio buffer size in samples (default: 256)'
    )
    parser.add_argument(
        '--audio-device',
        type=int,
        default=None,
        help='Audio device index (default: auto-detect PCM5102)'
    )
    parser.add_argument(
        '--list-devices',
        action='store_true',
        help='List available audio devices and exit'
    )
    parser.add_argument(
        '--simulate',
        action='store_true',
        help='Run in simulation mode (no GPIO or audio hardware)'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode (default: daemon mode)'
    )

    args = parser.parse_args()

    # List devices and exit
    if args.list_devices:
        if SOUNDDEVICE_AVAILABLE:
            import sounddevice as sd
            print("\nAvailable audio devices:")
            print(sd.query_devices())
            print()
            device_idx = find_pcm5102_device()
            if device_idx is not None:
                print(f"Auto-detected PCM5102 at index: {device_idx}")
        else:
            print("sounddevice not available")
        return

    # Auto-detect audio device if not specified
    audio_device = args.audio_device
    if audio_device is None and not args.simulate:
        audio_device = find_pcm5102_device()
        if audio_device is not None:
            print(f"Auto-detected audio device: {audio_device}")

    # Create and run application
    app = DubSirenApp(
        sample_rate=args.sample_rate,
        buffer_size=args.buffer_size,
        audio_device=audio_device,
        simulate=args.simulate
    )

    if args.interactive or args.simulate:
        app.run_interactive()
    else:
        app.run_daemon()


if __name__ == "__main__":
    main()
