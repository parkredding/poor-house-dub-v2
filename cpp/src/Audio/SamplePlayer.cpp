#define MINIMP3_IMPLEMENTATION
#include "Audio/SamplePlayer.h"
#include "minimp3.h"
#include <iostream>
#include <fstream>
#include <cstring>
#include <algorithm>

namespace DubSiren {

SamplePlayer::SamplePlayer(int sampleRate)
    : sampleRate(sampleRate)
    , sampleChannels(2)
    , sampleRateOriginal(sampleRate)
    , playing(false)
    , loop(false)
    , playbackPosition(0)
    , volume(1.0f)
{
}

bool SamplePlayer::loadMP3(const std::string& filepath) {
    std::lock_guard<std::mutex> lock(sampleMutex);

    // Read entire file into memory
    std::ifstream file(filepath, std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        std::cerr << "Failed to open MP3 file: " << filepath << std::endl;
        return false;
    }

    std::streamsize fileSize = file.tellg();
    file.seekg(0, std::ios::beg);

    std::vector<uint8_t> mp3Data(fileSize);
    if (!file.read(reinterpret_cast<char*>(mp3Data.data()), fileSize)) {
        std::cerr << "Failed to read MP3 file: " << filepath << std::endl;
        return false;
    }
    file.close();

    // Decode MP3 using minimp3
    mp3dec_t mp3d;
    mp3dec_init(&mp3d);

    std::vector<float> decodedSamples;
    mp3dec_frame_info_t info;

    const uint8_t* mp3Ptr = mp3Data.data();
    size_t mp3Size = mp3Data.size();

    short pcmBuffer[MINIMP3_MAX_SAMPLES_PER_FRAME];

    bool firstFrame = true;

    while (mp3Size > 0) {
        int samples = mp3dec_decode_frame(&mp3d, mp3Ptr, mp3Size, pcmBuffer, &info);

        if (samples == 0) {
            // No more frames
            break;
        }

        if (firstFrame) {
            sampleRateOriginal = info.hz;
            sampleChannels = info.channels;
            firstFrame = false;

            std::cout << "MP3 info: " << info.hz << " Hz, "
                      << info.channels << " channels, "
                      << info.bitrate_kbps << " kbps" << std::endl;
        }

        // Convert int16 PCM to float [-1.0, 1.0]
        for (int i = 0; i < samples * info.channels; ++i) {
            float sample = static_cast<float>(pcmBuffer[i]) / 32768.0f;
            decodedSamples.push_back(sample);
        }

        mp3Ptr += info.frame_bytes;
        mp3Size -= info.frame_bytes;
    }

    if (decodedSamples.empty()) {
        std::cerr << "Failed to decode any samples from MP3" << std::endl;
        return false;
    }

    std::cout << "Decoded " << decodedSamples.size() / sampleChannels
              << " frames from MP3" << std::endl;

    // Convert mono to stereo if needed
    if (sampleChannels == 1) {
        std::vector<float> stereoData;
        stereoData.reserve(decodedSamples.size() * 2);

        for (size_t i = 0; i < decodedSamples.size(); ++i) {
            stereoData.push_back(decodedSamples[i]);  // Left
            stereoData.push_back(decodedSamples[i]);  // Right
        }

        decodedSamples = std::move(stereoData);
        sampleChannels = 2;
    }

    // Resample if needed
    if (sampleRateOriginal != sampleRate) {
        std::cout << "Resampling from " << sampleRateOriginal
                  << " Hz to " << sampleRate << " Hz" << std::endl;

        std::vector<float> resampledData;
        resample(decodedSamples, resampledData, sampleRateOriginal, sampleRate, 2);
        sampleData = std::move(resampledData);
    } else {
        sampleData = std::move(decodedSamples);
    }

    playbackPosition.store(0);

    std::cout << "MP3 loaded successfully: " << filepath << std::endl;
    std::cout << "  Duration: " << getDuration() << " seconds" << std::endl;

    return true;
}

void SamplePlayer::trigger() {
    if (!isLoaded()) {
        std::cerr << "Cannot trigger: no sample loaded" << std::endl;
        return;
    }

    playbackPosition.store(0);
    playing.store(true);

    std::cout << "Sample playback started" << std::endl;
}

void SamplePlayer::stop() {
    playing.store(false);
    playbackPosition.store(0);

    std::cout << "Sample playback stopped" << std::endl;
}

void SamplePlayer::setVolume(float vol) {
    volume.store(std::clamp(vol, 0.0f, 1.0f));
}

float SamplePlayer::getDuration() const {
    if (sampleData.empty() || sampleRate == 0) return 0.0f;
    return static_cast<float>(sampleData.size() / 2) / static_cast<float>(sampleRate);
}

void SamplePlayer::process(float* output, int numFrames) {
    if (!playing.load() || !isLoaded()) {
        // Output silence
        std::memset(output, 0, numFrames * 2 * sizeof(float));
        return;
    }

    std::lock_guard<std::mutex> lock(sampleMutex);

    size_t pos = playbackPosition.load();
    float vol = volume.load();
    size_t totalSamples = sampleData.size();

    for (int frame = 0; frame < numFrames; ++frame) {
        if (pos >= totalSamples) {
            if (loop.load()) {
                pos = 0;  // Loop back to start
            } else {
                // End of sample, output silence for remaining frames
                playing.store(false);
                std::memset(&output[frame * 2], 0, (numFrames - frame) * 2 * sizeof(float));
                break;
            }
        }

        // Copy stereo samples with volume applied
        output[frame * 2 + 0] = sampleData[pos + 0] * vol;  // Left
        output[frame * 2 + 1] = sampleData[pos + 1] * vol;  // Right

        pos += 2;
    }

    playbackPosition.store(pos);
}

bool SamplePlayer::needsResampling() const {
    return sampleRateOriginal != sampleRate;
}

void SamplePlayer::resample(const std::vector<float>& input, std::vector<float>& output,
                             int inputRate, int outputRate, int channels) {
    if (inputRate == outputRate) {
        output = input;
        return;
    }

    // Simple linear interpolation resampling
    double ratio = static_cast<double>(outputRate) / static_cast<double>(inputRate);
    size_t inputFrames = input.size() / channels;
    size_t outputFrames = static_cast<size_t>(inputFrames * ratio);

    output.resize(outputFrames * channels);

    for (size_t outFrame = 0; outFrame < outputFrames; ++outFrame) {
        double srcPos = static_cast<double>(outFrame) / ratio;
        size_t srcFrame = static_cast<size_t>(srcPos);
        double frac = srcPos - static_cast<double>(srcFrame);

        if (srcFrame + 1 >= inputFrames) {
            srcFrame = inputFrames - 1;
            frac = 0.0;
        }

        for (int ch = 0; ch < channels; ++ch) {
            float sample1 = input[srcFrame * channels + ch];
            float sample2 = input[(srcFrame + 1) * channels + ch];
            float interpolated = sample1 + static_cast<float>(frac) * (sample2 - sample1);
            output[outFrame * channels + ch] = interpolated;
        }
    }
}

} // namespace DubSiren
