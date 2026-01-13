#include "Audio/AudioOutput.h"
#include <iostream>
#include <chrono>
#include <cstring>
#include <algorithm>

#ifdef HAVE_ALSA
#include <alsa/asoundlib.h>
#endif

namespace DubSiren {

// ============================================================================
// AudioOutput Implementation (ALSA)
// ============================================================================

AudioOutput::AudioOutput(AudioEngine& engine, 
                         int sampleRate,
                         int bufferSize,
                         int channels,
                         const char* device)
    : engine(engine)
    , sampleRate(sampleRate)
    , bufferSize(bufferSize)
    , channels(channels)
    , deviceName(device ? device : "default")
    , running(false)
    , totalBuffers(0)
    , underruns(0)
    , lastCpuUsage(0.0f)
{
}

AudioOutput::~AudioOutput() {
    stop();
}

bool AudioOutput::start() {
#ifdef HAVE_ALSA
    if (running.load()) {
        std::cout << "Audio output already running" << std::endl;
        return true;
    }
    
    running.store(true);
    audioThread = std::thread(&AudioOutput::audioLoop, this);
    
    std::cout << "Audio output started: " << sampleRate << "Hz, " 
              << bufferSize << " samples, " << channels << " channels, "
              << "device=" << deviceName << std::endl;
    
    return true;
#else
    std::cerr << "ALSA not available - audio output disabled" << std::endl;
    return false;
#endif
}

void AudioOutput::stop() {
    if (!running.load()) {
        return;
    }
    
    running.store(false);
    
    if (audioThread.joinable()) {
        audioThread.join();
    }
    
    // Print statistics
    uint64_t total = totalBuffers.load();
    uint64_t under = underruns.load();
    
    if (total > 0) {
        float underrunRate = static_cast<float>(under) / static_cast<float>(total) * 100.0f;
        std::cout << "\nAudio performance:" << std::endl;
        std::cout << "  Total buffers: " << total << std::endl;
        std::cout << "  Buffer underruns: " << under << " (" << underrunRate << "%)" << std::endl;
    }
    
    std::cout << "Audio output stopped" << std::endl;
}

void AudioOutput::audioLoop() {
#ifdef HAVE_ALSA
    snd_pcm_t* pcm = nullptr;
    int err;
    
    // Open PCM device
    err = snd_pcm_open(&pcm, deviceName.c_str(), SND_PCM_STREAM_PLAYBACK, 0);
    if (err < 0) {
        std::cerr << "Cannot open audio device " << deviceName << ": " 
                  << snd_strerror(err) << std::endl;
        running.store(false);
        return;
    }
    
    // Set hardware parameters
    snd_pcm_hw_params_t* hwParams;
    snd_pcm_hw_params_alloca(&hwParams);
    snd_pcm_hw_params_any(pcm, hwParams);
    
    snd_pcm_hw_params_set_access(pcm, hwParams, SND_PCM_ACCESS_RW_INTERLEAVED);
    snd_pcm_hw_params_set_format(pcm, hwParams, SND_PCM_FORMAT_S16_LE);
    snd_pcm_hw_params_set_channels(pcm, hwParams, channels);
    
    unsigned int actualRate = sampleRate;
    snd_pcm_hw_params_set_rate_near(pcm, hwParams, &actualRate, nullptr);
    
    snd_pcm_uframes_t periodSize = bufferSize;
    snd_pcm_hw_params_set_period_size_near(pcm, hwParams, &periodSize, nullptr);
    
    err = snd_pcm_hw_params(pcm, hwParams);
    if (err < 0) {
        std::cerr << "Cannot set hardware parameters: " << snd_strerror(err) << std::endl;
        snd_pcm_close(pcm);
        running.store(false);
        return;
    }
    
    // Prepare the PCM for playback
    err = snd_pcm_prepare(pcm);
    if (err < 0) {
        std::cerr << "Cannot prepare PCM: " << snd_strerror(err) << std::endl;
        snd_pcm_close(pcm);
        running.store(false);
        return;
    }
    
    std::cout << "[ALSA] PCM prepared successfully, state=" << snd_pcm_state_name(snd_pcm_state(pcm)) << std::endl;
    
    // Allocate buffers
    std::vector<float> floatBuffer(bufferSize * channels);
    std::vector<int16_t> intBuffer(bufferSize * channels);
    
    // Calculate expected buffer duration for CPU usage estimation
    double bufferDuration = static_cast<double>(bufferSize) / static_cast<double>(sampleRate);
    
    while (running.load()) {
        auto startTime = std::chrono::high_resolution_clock::now();
        
        // Generate audio
        engine.process(floatBuffer.data(), bufferSize);
        
        // Convert to int16
        for (size_t i = 0; i < floatBuffer.size(); ++i) {
            float sample = clamp(floatBuffer[i], -1.0f, 1.0f);
            intBuffer[i] = static_cast<int16_t>(sample * 32767.0f);
        }
        
        auto processTime = std::chrono::high_resolution_clock::now();
        
        // Write to ALSA
        snd_pcm_sframes_t frames = snd_pcm_writei(pcm, intBuffer.data(), bufferSize);
        
        if (frames < 0) {
            // Handle underrun
            underruns.fetch_add(1);
            std::cerr << "[ALSA] Write returned " << frames << ": " << snd_strerror(static_cast<int>(frames)) << std::endl;
            frames = snd_pcm_recover(pcm, static_cast<int>(frames), 0);
            if (frames < 0) {
                std::cerr << "[ALSA] Recovery failed: " << snd_strerror(static_cast<int>(frames)) << std::endl;
            }
        }
        
        totalBuffers.fetch_add(1);
        
        // Debug: periodically print ALSA write info
        static int alsaDebugCounter = 0;
        int16_t maxSample = *std::max_element(intBuffer.begin(), intBuffer.end());
        alsaDebugCounter++;
        if (alsaDebugCounter >= 187) {  // ~1 second at 48kHz/256
            alsaDebugCounter = 0;
            if (maxSample > 100) {  // Only print when there's actual audio
                std::cout << "[ALSA] Writing: " << frames << " frames, max int16=" << maxSample << std::endl;
            }
        }
        
        // Also print immediately when audio starts (first non-silent write)
        static bool hadAudio = false;
        if (!hadAudio && maxSample > 1000) {
            hadAudio = true;
            std::cout << "[ALSA] Audio detected! max int16=" << maxSample << std::endl;
        }
        
        // Calculate CPU usage
        auto endTime = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> processDuration = processTime - startTime;
        float cpuUsage = static_cast<float>(processDuration.count() / bufferDuration * 100.0);
        lastCpuUsage.store(cpuUsage);
    }
    
    // Drain and close
    snd_pcm_drain(pcm);
    snd_pcm_close(pcm);
#endif
}

AudioOutput::Stats AudioOutput::getStats() const {
    return {
        totalBuffers.load(),
        underruns.load(),
        lastCpuUsage.load()
    };
}

// ============================================================================
// SimulatedAudioOutput Implementation
// ============================================================================

SimulatedAudioOutput::SimulatedAudioOutput(AudioEngine& engine, int bufferSize)
    : engine(engine)
    , bufferSize(bufferSize)
    , running(false)
    , buffer(bufferSize * 2)  // Stereo
{
    std::cout << "Running in SIMULATION mode (no audio output)" << std::endl;
}

SimulatedAudioOutput::~SimulatedAudioOutput() {
    stop();
}

bool SimulatedAudioOutput::start() {
    if (running.load()) {
        return true;
    }
    
    running.store(true);
    simulationThread = std::thread(&SimulatedAudioOutput::simulationLoop, this);
    
    std::cout << "Simulated audio output started" << std::endl;
    return true;
}

void SimulatedAudioOutput::stop() {
    if (!running.load()) {
        return;
    }
    
    running.store(false);
    
    if (simulationThread.joinable()) {
        simulationThread.join();
    }
    
    std::cout << "Simulated audio output stopped" << std::endl;
}

void SimulatedAudioOutput::simulationLoop() {
    // Simulate audio callback at regular intervals
    double bufferDuration = static_cast<double>(bufferSize) / static_cast<double>(DEFAULT_SAMPLE_RATE);
    auto sleepDuration = std::chrono::duration<double>(bufferDuration);
    
    while (running.load()) {
        // Generate audio (but don't output it)
        engine.process(buffer.data(), bufferSize);
        
        // Sleep to simulate real-time behavior
        std::this_thread::sleep_for(sleepDuration);
    }
}

} // namespace DubSiren
