#pragma once

#include "Common.h"
#include <vector>
#include <array>
#include <memory>

namespace DubSiren {

/**
 * Allpass filter for reverb diffusion.
 * Creates density and smoothness without coloring frequency response.
 */
class AllpassFilter {
public:
    explicit AllpassFilter(int delaySamples);
    float process(float input);
    void setFeedback(float fb) { feedback = fb; }
    
private:
    std::vector<float> buffer;
    int writePos;
    int delaySamples;
    float feedback;
};

/**
 * Damped comb filter for warm, chamber-like reverb.
 * Features high-frequency damping to simulate air absorption.
 */
class DampedCombFilter {
public:
    DampedCombFilter(int sampleRate, float delayTime);
    float process(float input);
    
    void setFeedback(float fb) { feedback = fb; }
    void setDamping(float damp) { damping = damp; }
    
private:
    int sampleRate;
    std::vector<float> buffer;
    int writePos;
    int delaySamples;
    
    float feedback;
    float damping;
    float damperState;
    
    // Subtle modulation for natural sound
    float modDepthSamples;
    float modRate;
    float modPhase;
};

/**
 * Hybrid chamber reverb effect inspired by Ableton Live.
 * 
 * Combines:
 * - Early reflections for spatial character
 * - Allpass filters for diffusion and density
 * - Damped comb filters for warm, chamber-like tail
 * - Subtle modulation for natural, non-metallic sound
 */
class ReverbEffect {
public:
    explicit ReverbEffect(int sampleRate = DEFAULT_SAMPLE_RATE);
    
    /**
     * Process audio through the reverb.
     * @param input Input buffer
     * @param output Output buffer (can be same as input)
     * @param numSamples Number of samples to process
     */
    void process(const float* input, float* output, int numSamples);
    
    // Parameter setters
    void setSize(float size);
    void setDryWet(float mix);
    void setDamping(float damp);
    
    // Getters
    float getSize() const { return size; }
    float getDryWet() const { return dryWet; }
    
private:
    int sampleRate;
    
    // Early reflections
    static constexpr int NUM_EARLY_REFLECTIONS = 8;
    std::array<float, NUM_EARLY_REFLECTIONS> earlyReflectionTimes;
    std::array<std::vector<float>, NUM_EARLY_REFLECTIONS> earlyBuffers;
    std::array<int, NUM_EARLY_REFLECTIONS> earlyWritePos;
    float earlyLevel;
    
    // Allpass diffusion filters
    std::array<AllpassFilter, 2> inputDiffusion;
    AllpassFilter outputDiffusion;
    
    // Damped comb filters
    static constexpr int NUM_COMB_FILTERS = 6;
    std::array<std::unique_ptr<DampedCombFilter>, NUM_COMB_FILTERS> combFilters;
    
    // Control parameters
    float size;     // Room size / decay time (0.0 to 1.0)
    float dryWet;   // Mix (0.0 = dry, 1.0 = wet)
    float damping;  // High-frequency damping
    
    // Pre-allocated work buffers (avoid allocation in audio thread!)
    std::vector<float> earlyBuffer;
    std::vector<float> diffusedBuffer;
    std::vector<float> combOutputBuffer;
    
    void updateParameters();
    void processEarlyReflections(const float* input, float* output, int numSamples);
};

} // namespace DubSiren
