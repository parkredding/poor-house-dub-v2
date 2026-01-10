#!/usr/bin/env python3
"""
Pi Zero 2W Audio Test for PCM5102 DAC
Tests volume control and delay wet/dry mix to verify audio output
"""

import numpy as np
import time
import argparse
from audio_output import AudioOutput, find_pcm5102_device
from synthesizer import DubSiren

def print_banner():
    """Print test banner"""
    print("\n" + "="*60)
    print("  Pi Zero 2W Audio Test - PCM5102 DAC Verification")
    print("="*60 + "\n")

def test_volume_sweep(synth, duration=2.0):
    """
    Test volume control by sweeping from 0% to 100%
    This verifies audio is reaching the PCM5102
    """
    print("\n[TEST 1] Volume Sweep Test")
    print("-" * 40)
    print("Testing volume control: 0% → 100%")
    print("You should hear a tone getting progressively louder\n")

    # Set up a simple test tone
    synth.set_filter_cutoff(2000.0)  # Mid-range frequency
    synth.set_filter_resonance(1.0)  # Minimal resonance
    synth.set_delay_dry_wet(0.0)     # Pure dry signal for volume test
    synth.set_reverb_dry_wet(0.0)    # No reverb

    steps = 10
    for i in range(steps + 1):
        volume = i / steps
        synth.set_volume(volume)

        print(f"  Volume: {int(volume * 100):3d}% ", end='', flush=True)

        # Trigger a note
        synth.trigger()
        time.sleep(duration / steps)
        synth.release()
        time.sleep(0.1)

        print("✓")

    print("\n✓ Volume sweep complete!")
    print("  If you heard increasing volume, audio is reaching PCM5102\n")
    time.sleep(1.0)

def test_delay_wetdry(synth, duration=3.0):
    """
    Test delay wet/dry mix
    This verifies the signal path through the delay effect
    """
    print("\n[TEST 2] Delay Wet/Dry Test")
    print("-" * 40)
    print("Testing delay mix: 0% (dry) → 100% (wet)")
    print("You should hear increasing echo/delay effect\n")

    # Configure delay for clear audible effect
    synth.set_volume(0.7)
    synth.set_delay_time(0.3)          # 300ms delay
    synth.set_delay_feedback(0.5)      # 50% feedback
    synth.set_filter_cutoff(3000.0)    # Brighter tone
    synth.set_filter_resonance(2.0)    # Slight resonance
    synth.set_reverb_dry_wet(0.0)      # No reverb to isolate delay

    steps = 5
    for i in range(steps + 1):
        wet_dry = i / steps
        synth.set_delay_dry_wet(wet_dry)

        print(f"  Delay Wet/Dry: {int(wet_dry * 100):3d}% ", end='', flush=True)

        # Trigger a note
        synth.trigger()
        time.sleep(duration / steps)
        synth.release()
        time.sleep(0.3)

        print("✓")

    print("\n✓ Delay wet/dry test complete!")
    print("  If you heard increasing echo, delay is working correctly\n")
    time.sleep(1.0)

def test_continuous_tone(synth, duration=5.0):
    """
    Play a continuous tone with delay for final verification
    """
    print("\n[TEST 3] Continuous Tone with Delay")
    print("-" * 40)
    print(f"Playing continuous tone for {duration} seconds")
    print("Volume: 80%, Delay: 50% wet, Feedback: 60%\n")

    synth.set_volume(0.8)
    synth.set_delay_time(0.4)
    synth.set_delay_feedback(0.6)
    synth.set_delay_dry_wet(0.5)
    synth.set_filter_cutoff(1500.0)
    synth.set_filter_resonance(3.0)
    synth.set_reverb_dry_wet(0.2)  # Slight reverb

    print("  Playing... ", end='', flush=True)
    synth.trigger()

    # Show countdown
    for i in range(int(duration)):
        time.sleep(1.0)
        print(".", end='', flush=True)

    synth.release()
    time.sleep(1.0)

    print(" Done!\n")
    print("✓ Continuous tone test complete!\n")

def main():
    parser = argparse.ArgumentParser(description='Pi Zero 2W Audio Test for PCM5102')
    parser.add_argument('--device', type=int, default=None,
                       help='Audio device index (auto-detect PCM5102 if not specified)')
    parser.add_argument('--list-devices', action='store_true',
                       help='List available audio devices and exit')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick tests (shorter duration)')

    args = parser.parse_args()

    # List devices if requested
    if args.list_devices:
        import sounddevice as sd
        print("\nAvailable audio devices:")
        print(sd.query_devices())
        return

    print_banner()

    # Auto-detect PCM5102 or use specified device
    if args.device is None:
        print("Auto-detecting PCM5102 DAC...")
        device = find_pcm5102_device()
        if device is None:
            print("⚠ Warning: Could not auto-detect PCM5102")
            print("Using default audio device")
            print("Use --list-devices to see available devices\n")
        else:
            print(f"✓ Found PCM5102 on device {device}\n")
    else:
        device = args.device
        print(f"Using specified device: {device}\n")

    # Initialize audio output
    print("Initializing audio output...")
    try:
        audio_output = AudioOutput(device=device)
        print("✓ Audio output initialized")
        print(f"  Sample rate: {audio_output.sample_rate} Hz")
        print(f"  Channels: {audio_output.channels}")
        print(f"  Buffer size: {audio_output.buffer_size} samples\n")
    except Exception as e:
        print(f"✗ Failed to initialize audio output: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure I2S is enabled in /boot/config.txt")
        print("2. Check PCM5102 wiring connections")
        print("3. Run: aplay -l  to list audio devices")
        print("4. Use --list-devices to see available devices\n")
        return 1

    # Initialize synthesizer
    print("Initializing DubSiren synthesizer...")
    synth = DubSiren(sample_rate=audio_output.sample_rate)
    print("✓ Synthesizer initialized\n")

    # Start audio output
    print("Starting audio stream...")
    audio_output.start(synth)
    print("✓ Audio stream started\n")

    time.sleep(0.5)

    try:
        # Adjust test duration based on quick flag
        volume_duration = 1.0 if args.quick else 2.0
        delay_duration = 2.0 if args.quick else 3.0
        tone_duration = 3.0 if args.quick else 5.0

        # Run tests
        test_volume_sweep(synth, duration=volume_duration)
        test_delay_wetdry(synth, duration=delay_duration)
        test_continuous_tone(synth, duration=tone_duration)

        # Test summary
        print("="*60)
        print("  Test Summary")
        print("="*60)
        print("\n✓ All tests completed successfully!\n")
        print("Verification checklist:")
        print("  [ ] Did you hear the volume sweep from quiet to loud?")
        print("  [ ] Did you hear the delay effect increase from dry to wet?")
        print("  [ ] Did the continuous tone sound clean with echo?")
        print("\nIf you answered YES to all questions:")
        print("  → PCM5102 DAC is working correctly!")
        print("\nIf you heard nothing or distorted audio:")
        print("  → Check wiring connections and I2S configuration")
        print("  → Run: sudo aplay -l")
        print("  → Check /boot/config.txt for dtparam=i2s=on")
        print("\n" + "="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        print("Stopping audio stream...")
        audio_output.stop()
        print("✓ Audio stream stopped\n")
        print("Test complete!\n")

    return 0

if __name__ == "__main__":
    exit(main())
