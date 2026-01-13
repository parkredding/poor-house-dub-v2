#include "DSP/Reverb.h"
#include <cmath>
#include <algorithm>

namespace DubSiren {

// ============================================================================
// Comb Filter
// ============================================================================

void ReverbEffect::CombFilter::init(int size) {
    bufferSize = size;
    buffer.resize(size, 0.0f);
    index = 0;
    filterStore = 0.0f;
}

float ReverbEffect::CombFilter::process(float input, float feedback, float damp1, float damp2) {
    float output = buffer[index];
    
    // One-pole lowpass in feedback path (damping)
    filterStore = (output * damp2) + (filterStore * damp1);
    
    // Clamp tiny values to zero (prevent denormals)
    if (std::abs(filterStore) < 1e-10f) {
        filterStore = 0.0f;
    }
    
    // Write new sample
    buffer[index] = input + (filterStore * feedback);
    
    // Advance index
    if (++index >= bufferSize) {
        index = 0;
    }
    
    return output;
}

// ============================================================================
// Allpass Filter
// ============================================================================

void ReverbEffect::AllpassFilter::init(int size) {
    bufferSize = size;
    buffer.resize(size, 0.0f);
    index = 0;
}

float ReverbEffect::AllpassFilter::process(float input) {
    float bufOut = buffer[index];
    
    // Standard allpass with fixed feedback of 0.5
    float output = -input + bufOut;
    buffer[index] = input + (bufOut * 0.5f);
    
    // Clamp tiny values
    if (std::abs(buffer[index]) < 1e-10f) {
        buffer[index] = 0.0f;
    }
    
    if (++index >= bufferSize) {
        index = 0;
    }
    
    return output;
}

// ============================================================================
// ReverbEffect Implementation
// ============================================================================

ReverbEffect::ReverbEffect(int sampleRate)
    : sampleRate(sampleRate)
    , roomSize(0.5f)
    , damping(0.5f)
    , wet(0.0f)
    , wet1(0.0f)
    , wet2(0.0f)
    , dry(1.0f)
    , width(1.0f)
    , feedback(0.0f)
    , damp1(0.0f)
    , damp2(0.0f)
{
    // Scale delay lengths for sample rate
    float scale = static_cast<float>(sampleRate) / 44100.0f;
    
    // Initialize comb filters (left channel)
    for (int i = 0; i < NUM_COMBS; ++i) {
        int len = static_cast<int>(COMB_LENGTHS[i] * scale);
        combL[i].init(len);
        combR[i].init(len + STEREO_SPREAD);
    }
    
    // Initialize allpass filters
    for (int i = 0; i < NUM_ALLPASS; ++i) {
        int len = static_cast<int>(ALLPASS_LENGTHS[i] * scale);
        allpassL[i].init(len);
        allpassR[i].init(len + STEREO_SPREAD);
    }
    
    // Pre-allocate work buffer
    workBuffer.resize(1024);
    
    updateCoefficients();
}

void ReverbEffect::updateCoefficients() {
    // Calculate feedback from room size
    feedback = roomSize * SCALE_ROOM + OFFSET_ROOM;
    
    // Clamp feedback to prevent runaway
    if (feedback > 0.98f) feedback = 0.98f;
    
    // Calculate damping coefficients
    damp1 = damping * SCALE_DAMP;
    damp2 = 1.0f - damp1;
    
    // Calculate wet gains for stereo
    wet1 = wet * (width / 2.0f + 0.5f);
    wet2 = wet * ((1.0f - width) / 2.0f);
}

void ReverbEffect::process(const float* input, float* output, int numSamples) {
    // Process each sample
    for (int i = 0; i < numSamples; ++i) {
        float inSample = input[i];
        float outL = 0.0f;
        float outR = 0.0f;
        
        // Input gain
        float scaledInput = inSample * FIXED_GAIN;
        
        // Parallel comb filters
        for (int c = 0; c < NUM_COMBS; ++c) {
            outL += combL[c].process(scaledInput, feedback, damp1, damp2);
            outR += combR[c].process(scaledInput, feedback, damp1, damp2);
        }
        
        // Series allpass filters for diffusion
        for (int a = 0; a < NUM_ALLPASS; ++a) {
            outL = allpassL[a].process(outL);
            outR = allpassR[a].process(outR);
        }
        
        // Mix wet/dry (output is mono, so average L+R)
        float wetMix = (outL + outR) * 0.5f * wet * SCALE_WET;
        float dryMix = inSample * dry * SCALE_DRY * 0.5f;
        
        output[i] = wetMix + dryMix;
    }
}

void ReverbEffect::setSize(float size) {
    roomSize = std::clamp(size, 0.0f, 1.0f);
    updateCoefficients();
}

void ReverbEffect::setDryWet(float mix) {
    wet = std::clamp(mix, 0.0f, 1.0f);
    dry = 1.0f - wet;
    updateCoefficients();
}

void ReverbEffect::setDamping(float damp) {
    damping = std::clamp(damp, 0.0f, 1.0f);
    updateCoefficients();
}

void ReverbEffect::setWidth(float w) {
    width = std::clamp(w, 0.0f, 1.0f);
    updateCoefficients();
}

} // namespace DubSiren
