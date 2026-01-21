# Custom Audio Files

This directory contains custom audio files for the Custom Audio secret mode.

## Custom Audio Secret Mode

**Activation**: Perform 10 pitch envelope cycles within 5 seconds

A cycle is moving the pitch envelope switch: **Up → Off → Down → Off** OR **Down → Off → Up → Off**

When activated, pressing the TRIGGER button will play your custom MP3 file instead of the synth.

## Upload Your MP3

Place your custom MP3 file here:
```
assets/audio/custom.mp3
```

### Requirements:
- **Format**: MP3 (any bitrate, mono or stereo)
- **Sample Rate**: Any (will be automatically resampled to 44.1kHz)
- **Channels**: Mono or stereo (mono will be converted to stereo)
- **Duration**: Any length (looping is disabled by default)

### How to Upload to Raspberry Pi:

Using `scp` from your computer:
```bash
scp /path/to/your/audio.mp3 pi@raspberrypi.local:~/poor-house-dub-v2/assets/audio/custom.mp3
```

Or using the Raspberry Pi directly:
```bash
# Copy from USB drive
cp /media/usb/myaudio.mp3 ~/poor-house-dub-v2/assets/audio/custom.mp3

# Or download from URL
wget -O ~/poor-house-dub-v2/assets/audio/custom.mp3 https://example.com/myaudio.mp3
```

## Usage

1. Upload your `custom.mp3` file to this directory
2. Start the dub siren
3. Rapidly cycle the pitch envelope switch 10 times (Up-Off-Down-Off or Down-Off-Up-Off)
4. You'll see: "🎵 10 pitch envelope cycles detected!"
5. Then: "🎵 SECRET MODE ACTIVATED! 🎵 - CUSTOM AUDIO"
6. Press TRIGGER to play your custom audio
7. Exit by rapidly cycling the pitch envelope 10 times again OR press SHIFT 3-5 times to enter a different secret mode

## Tips

- The audio will play at 80% volume by default
- Playback stops when the sample ends (no looping)
- You can trigger it multiple times - each press restarts playback
- Works with any MP3 file - get creative!

## Examples

Great uses for custom audio mode:
- Classic dub siren samples (NJD, Kingstec, etc.)
- Air horn samples
- Custom vocal samples ("Rewind!")
- Sound effects
- Custom drops
- Anything you want!
