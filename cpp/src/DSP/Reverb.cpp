#include "DSP/Reverb.h"
#include <cmath>
#include <algorithm>
#include <random>

namespace DubSiren {

// ============================================================================
// AllpassFilter Implementation
// ============================================================================

AllpassFilter::AllpassFilter(int delaySamples)
    : buffer(delaySamples, 0.0f)
    , writePos(0)
    , delaySamples(delaySamples)
    , feedback(0.5f)
{
}

// Tiny constant to prevent denormal numbers
static constexpr float ANTI_DENORMAL = 1e-20f;

float AllpassFilter::process(float input) {
    int readPos = (writePos - delaySamples + static_cast<int>(buffer.size())) % static_cast<int>(buffer.size());
    float delayed = buffer[readPos];
    
    // Allpass formula: y = -x + d + g*(x - d)
    float output = -input + delayed + feedback * (input - delayed);
    
    // Write to buffer with clamping and anti-denormal
    buffer[writePos] = clampSample(input + feedback * delayed) + ANTI_DENORMAL;
    writePos = (writePos + 1) % static_cast<int>(buffer.size());
    
    return output;
}

// ============================================================================
// DampedCombFilter Implementation
// ============================================================================

DampedCombFilter::DampedCombFilter(int sampleRate, float delayTime)
    : sampleRate(sampleRate)
    , buffer(static_cast<int>(delayTime * sampleRate), 0.0f)
    , writePos(0)
    , delaySamples(static_cast<int>(delayTime * sampleRate))
    , feedback(0.7f)
    , damping(0.5f)
    , damperState(0.0f)
    , modDepthSamples(2.0f)
    , modRate(0.3f)
{
    // Random starting phase for natural sound
    static std::random_device rd;
    static std::mt19937 gen(rd());
    std::uniform_real_distribution<float> dist(0.0f, TWO_PI);
    modPhase = dist(gen);
}

float DampedCombFilter::process(float input) {
    // Calculate modulated read position
    float modOffset = modDepthSamples * std::sin(modPhase);
    modPhase += TWO_PI * modRate / static_cast<float>(sampleRate);
    if (modPhase > TWO_PI) {
        modPhase -= TWO_PI;
    }
    
    // Read from buffer with interpolation
    float readPosFloat = static_cast<float>(writePos) - static_cast<float>(delaySamples) + modOffset;
    if (readPosFloat < 0) {
        readPosFloat += static_cast<float>(buffer.size());
    }
    
    int readPosInt = static_cast<int>(readPosFloat) % static_cast<int>(buffer.size());
    int readPosNext = (readPosInt + 1) % static_cast<int>(buffer.size());
    float frac = readPosFloat - std::floor(readPosFloat);
    
    float delayed = buffer[readPosInt] * (1.0f - frac) + buffer[readPosNext] * frac;
    
    // Apply damping (one-pole lowpass in feedback path)
    float dampingCoeff = 1.0f - damping * 0.5f;
    damperState = clampSample(dampingCoeff * delayed + (1.0f - dampingCoeff) * damperState) + ANTI_DENORMAL;
    
    // Comb filter formula
    float output = delayed;
    buffer[writePos] = clampSample(input + damperState * feedback) + ANTI_DENORMAL;
    writePos = (writePos + 1) % static_cast<int>(buffer.size());
    
    return output;
}

// ============================================================================
// ReverbEffect Implementation
// ============================================================================

ReverbEffect::ReverbEffect(int sampleRate)
    : sampleRate(sampleRate)
    , earlyReflectionTimes({0.013f, 0.019f, 0.023f, 0.029f, 0.037f, 0.043f, 0.051f, 0.059f})
    , earlyLevel(0.15f)
    , inputDiffusion({
        AllpassFilter(static_cast<int>(0.005f * sampleRate)),
        AllpassFilter(static_cast<int>(0.0089f * sampleRate))
    })
    , outputDiffusion(static_cast<int>(0.0067f * sampleRate))
    , size(0.5f)
    , dryWet(0.0f)
    , damping(0.5f)
{
    // Initialize early reflection buffers
    for (int i = 0; i < NUM_EARLY_REFLECTIONS; ++i) {
        earlyBuffers[i].resize(static_cast<int>(earlyReflectionTimes[i] * sampleRate), 0.0f);
        earlyWritePos[i] = 0;
    }
    
    // Initialize comb filters with different delay times
    const std::array<float, NUM_COMB_FILTERS> combDelayTimes = {
        0.0297f, 0.0371f, 0.0411f, 0.0437f, 0.0503f, 0.0571f
    };
    
    for (int i = 0; i < NUM_COMB_FILTERS; ++i) {
        combFilters[i] = std::make_unique<DampedCombFilter>(sampleRate, combDelayTimes[i]);
    }
    
    // Pre-allocate work buffers (avoid allocation in audio thread!)
    // Use a reasonable max buffer size
    const int maxBufferSize = 1024;
    earlyBuffer.resize(maxBufferSize, 0.0f);
    diffusedBuffer.resize(maxBufferSize, 0.0f);
    combOutputBuffer.resize(maxBufferSize, 0.0f);
    
    updateParameters();
}

void ReverbEffect::updateParameters() {
    // Size controls feedback (decay time)
    float baseFeedback = 0.4f + size * 0.45f;  // Range: 0.4 to 0.85
    
    for (auto& comb : combFilters) {
        comb->setFeedback(baseFeedback);
        comb->setDamping(damping);
    }
}

void ReverbEffect::processEarlyReflections(const float* input, float* output, int numSamples) {
    for (int i = 0; i < numSamples; ++i) {
        float earlySum = 0.0f;
        
        for (int j = 0; j < NUM_EARLY_REFLECTIONS; ++j) {
            auto& buf = earlyBuffers[j];
            int& wPos = earlyWritePos[j];
            
            // Read delayed sample
            earlySum += buf[wPos];
            
            // Write input with attenuation
            float attenuation = 0.7f - static_cast<float>(j) * 0.05f;
            buf[wPos] = clampSample(input[i] * attenuation);
            
            // Advance write position
            wPos = (wPos + 1) % static_cast<int>(buf.size());
        }
        
        output[i] = earlySum / static_cast<float>(NUM_EARLY_REFLECTIONS);
    }
}

void ReverbEffect::process(const float* input, float* output, int numSamples) {
    // Resize work buffers if needed (rare, only on buffer size change)
    if (static_cast<size_t>(numSamples) > earlyBuffer.size()) {
        earlyBuffer.resize(numSamples);
        diffusedBuffer.resize(numSamples);
        combOutputBuffer.resize(numSamples);
    }
    
    // Early reflections
    processEarlyReflections(input, earlyBuffer.data(), numSamples);
    
    // Copy input for diffusion processing
    std::copy(input, input + numSamples, diffusedBuffer.begin());
    
    // Process through input diffusion (allpass filters)
    for (int i = 0; i < numSamples; ++i) {
        for (auto& allpass : inputDiffusion) {
            diffusedBuffer[i] = allpass.process(diffusedBuffer[i]);
        }
    }
    
    // Process through parallel comb filters
    for (int i = 0; i < numSamples; ++i) {
        float combSum = 0.0f;
        for (auto& comb : combFilters) {
            combSum += comb->process(diffusedBuffer[i]);
        }
        combOutputBuffer[i] = combSum / static_cast<float>(NUM_COMB_FILTERS);
    }
    
    // Output diffusion
    for (int i = 0; i < numSamples; ++i) {
        combOutputBuffer[i] = outputDiffusion.process(combOutputBuffer[i]);
    }
    
    // Combine early reflections and reverb tail, mix with dry
    for (int i = 0; i < numSamples; ++i) {
        float wet = earlyBuffer[i] * earlyLevel + combOutputBuffer[i];
        output[i] = input[i] * (1.0f - dryWet) + wet * dryWet;
    }
}

void ReverbEffect::setSize(float s) {
    size = std::clamp(s, 0.0f, 1.0f);
    updateParameters();
}

void ReverbEffect::setDryWet(float mix) {
    dryWet = std::clamp(mix, 0.0f, 1.0f);
}

void ReverbEffect::setDamping(float damp) {
    damping = std::clamp(damp, 0.0f, 1.0f);
    updateParameters();
}

} // namespace DubSiren
