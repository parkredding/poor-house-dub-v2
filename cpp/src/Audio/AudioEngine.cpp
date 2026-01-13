#include "Audio/AudioEngine.h"
#include <cstring>
#include <cmath>
#include <algorithm>

namespace DubSiren {

AudioEngine::AudioEngine(int sampleRate, int bufferSize)
    : sampleRate(sampleRate)
    , bufferSize(bufferSize)
    , oscillator(sampleRate)
    , lfo(sampleRate)
    , envelope(sampleRate)
    , filter(sampleRate)
    , delay(sampleRate)
    , reverb(sampleRate)
    , volume(0.7f)
    , baseFrequency(440.0f)
    , pitchEnvMode(PitchEnvelopeMode::None)
    , currentFrequency(440.0f)
    , frequencySmooth(440.0f, 0.02f)
{
    // Pre-allocate buffers
    oscBuffer.resize(bufferSize);
    envBuffer.resize(bufferSize);
    lfoBuffer.resize(bufferSize);
    filterBuffer.resize(bufferSize);
    delayBuffer.resize(bufferSize);
    
    // Set initial parameters
    oscillator.setWaveform(Waveform::Sine);
    lfo.setFrequency(4.0f);
    lfo.setDepth(0.0f);  // Disabled by default
    envelope.setAttack(0.01f);
    envelope.setRelease(0.5f);
    filter.setCutoff(2000.0f);
    delay.setDryWet(0.3f);
    delay.setFeedback(0.5f);
    reverb.setDryWet(0.35f);
}

void AudioEngine::process(float* output, int numFrames) {
    // Smooth frequency changes
    frequencySmooth.setTarget(baseFrequency.get());
    
    // Generate oscillator
    for (int i = 0; i < numFrames; ++i) {
        currentFrequency = frequencySmooth.getNext();
        oscillator.setFrequency(currentFrequency);
        oscBuffer[i] = oscillator.generateSample();
    }
    
    // Generate LFO modulation
    lfo.generate(lfoBuffer.data(), numFrames);
    
    // Generate envelope
    envelope.generate(envBuffer.data(), numFrames);
    
    // Apply LFO to filter cutoff and process
    float baseCutoff = filter.getCutoff();
    for (int i = 0; i < numFrames; ++i) {
        // LFO modulates filter cutoff by ±2 octaves
        float modCutoff = baseCutoff * std::pow(2.0f, lfoBuffer[i] * 2.0f);
        modCutoff = clamp(modCutoff, 100.0f, 8000.0f);
        filter.setCutoff(modCutoff);
        filterBuffer[i] = filter.processSample(oscBuffer[i]);
    }
    // Restore base cutoff
    filter.setCutoff(baseCutoff);
    
    // Apply envelope
    for (int i = 0; i < numFrames; ++i) {
        // Hard gate at very low levels (prevents delay noise)
        if (envBuffer[i] < 0.001f) {
            filterBuffer[i] = 0.0f;
        } else {
            filterBuffer[i] *= envBuffer[i];
        }
    }
    
    // Apply delay
    delay.process(filterBuffer.data(), delayBuffer.data(), numFrames);
    
    // Apply reverb
    reverb.process(delayBuffer.data(), filterBuffer.data(), numFrames);
    
    // Apply DC blocking
    dcBlocker.process(filterBuffer.data(), filterBuffer.data(), numFrames);
    
    // Apply volume and convert to stereo interleaved
    float vol = volume.get();
    for (int i = 0; i < numFrames; ++i) {
        float sample = clamp(filterBuffer[i] * vol, -1.0f, 1.0f);
        output[i * 2] = sample;      // Left
        output[i * 2 + 1] = sample;  // Right
    }
}

void AudioEngine::trigger() {
    std::lock_guard<std::mutex> lock(triggerMutex);
    oscillator.resetPhase();
    envelope.trigger();
}

void AudioEngine::release() {
    std::lock_guard<std::mutex> lock(triggerMutex);
    envelope.release();
}

const char* AudioEngine::cyclePitchEnvelope() {
    PitchEnvelopeMode current = pitchEnvMode.get();
    PitchEnvelopeMode next;
    
    switch (current) {
        case PitchEnvelopeMode::None:
            next = PitchEnvelopeMode::Up;
            break;
        case PitchEnvelopeMode::Up:
            next = PitchEnvelopeMode::Down;
            break;
        case PitchEnvelopeMode::Down:
        default:
            next = PitchEnvelopeMode::None;
            break;
    }
    
    pitchEnvMode.set(next);
    
    switch (next) {
        case PitchEnvelopeMode::None: return "none";
        case PitchEnvelopeMode::Up: return "up";
        case PitchEnvelopeMode::Down: return "down";
        default: return "none";
    }
}

// ============================================================================
// Parameter Setters
// ============================================================================

void AudioEngine::setVolume(float vol) {
    volume.set(clamp(vol, 0.0f, 1.0f));
}

void AudioEngine::setFrequency(float freq) {
    baseFrequency.set(clamp(freq, 20.0f, 20000.0f));
}

void AudioEngine::setWaveform(Waveform wf) {
    oscillator.setWaveform(wf);
}

void AudioEngine::setWaveform(int index) {
    setWaveform(static_cast<Waveform>(index % 4));
}

void AudioEngine::setAttackTime(float seconds) {
    envelope.setAttack(seconds);
}

void AudioEngine::setReleaseTime(float seconds) {
    envelope.setRelease(seconds);
}

void AudioEngine::setLfoRate(float rate) {
    lfo.setFrequency(rate);
}

void AudioEngine::setLfoDepth(float depth) {
    lfo.setDepth(depth);
}

void AudioEngine::setLfoWaveform(Waveform wf) {
    lfo.setWaveform(wf);
}

void AudioEngine::setLfoWaveform(int index) {
    setLfoWaveform(static_cast<Waveform>(index % 4));
}

void AudioEngine::setFilterCutoff(float freq) {
    filter.setCutoff(freq);
}

void AudioEngine::setFilterResonance(float res) {
    filter.setResonance(res);
}

void AudioEngine::setDelayTime(float seconds) {
    delay.setDelayTime(seconds);
}

void AudioEngine::setDelayFeedback(float feedback) {
    delay.setFeedback(feedback);
}

void AudioEngine::setDelayMix(float mix) {
    delay.setDryWet(mix);
}

void AudioEngine::setReverbSize(float size) {
    reverb.setSize(size);
}

void AudioEngine::setReverbMix(float mix) {
    reverb.setDryWet(mix);
}

void AudioEngine::setReverbDamping(float damping) {
    reverb.setDamping(damping);
}

void AudioEngine::setPitchEnvelopeMode(PitchEnvelopeMode mode) {
    pitchEnvMode.set(mode);
}

} // namespace DubSiren
