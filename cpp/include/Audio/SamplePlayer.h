#pragma once

#include "Common.h"
#include <vector>
#include <string>
#include <atomic>
#include <mutex>

namespace DubSiren {

/**
 * Simple sample player for playing back pre-recorded audio files.
 * Supports MP3 format via minimp3 library.
 */
class SamplePlayer {
public:
    explicit SamplePlayer(int sampleRate = DEFAULT_SAMPLE_RATE);
    ~SamplePlayer() = default;

    /**
     * Load an MP3 file into memory.
     * @param filepath Path to the MP3 file
     * @return true if loaded successfully, false otherwise
     */
    bool loadMP3(const std::string& filepath);

    /**
     * Start playback from the beginning.
     */
    void trigger();

    /**
     * Stop playback.
     */
    void stop();

    /**
     * Check if currently playing.
     */
    bool isPlaying() const { return playing.load(); }

    /**
     * Set playback volume (0.0 to 1.0).
     */
    void setVolume(float vol);

    /**
     * Set whether to loop the sample.
     */
    void setLoop(bool shouldLoop) { loop.store(shouldLoop); }

    /**
     * Process audio samples.
     * @param output Stereo interleaved buffer to fill
     * @param numFrames Number of frames to process
     */
    void process(float* output, int numFrames);

    /**
     * Check if a sample is loaded.
     */
    bool isLoaded() const { return !sampleData.empty(); }

    /**
     * Get the length of the loaded sample in seconds.
     */
    float getDuration() const;

private:
    int sampleRate;
    std::vector<float> sampleData;  // Interleaved stereo samples
    int sampleChannels;             // 1 for mono, 2 for stereo
    int sampleRateOriginal;         // Original sample rate from file

    std::atomic<bool> playing;
    std::atomic<bool> loop;
    std::atomic<size_t> playbackPosition;
    std::atomic<float> volume;

    std::mutex sampleMutex;

    // Resample buffer for on-the-fly resampling if needed
    bool needsResampling() const;
    void resample(const std::vector<float>& input, std::vector<float>& output,
                  int inputRate, int outputRate, int channels);
};

} // namespace DubSiren
