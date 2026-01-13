#pragma once

#include "Common.h"
#include <vector>
#include <array>

namespace DubSiren {

/**
 * Freeverb-style reverb effect.
 * 
 * Classic Schroeder-Moorer reverb algorithm:
 * - 8 parallel comb filters for decay
 * - 4 series allpass filters for diffusion
 * - Smooth, lush sound perfect for dub
 */
class ReverbEffect {
public:
    explicit ReverbEffect(int sampleRate = DEFAULT_SAMPLE_RATE);
    
    void process(const float* input, float* output, int numSamples);
    
    // Parameters
    void setSize(float size);      // Room size (0.0 - 1.0)
    void setDryWet(float mix);     // Dry/wet mix (0.0 - 1.0)
    void setDamping(float damp);   // High-frequency damping (0.0 - 1.0)
    void setWidth(float width);    // Stereo width (0.0 - 1.0)
    
    float getSize() const { return roomSize; }
    float getDryWet() const { return wet; }
    
private:
    int sampleRate;
    
    // Freeverb uses 8 comb filters
    static constexpr int NUM_COMBS = 8;
    // And 4 allpass filters
    static constexpr int NUM_ALLPASS = 4;
    
    // Comb filter delay line lengths (in samples at 44100Hz, scaled for other rates)
    // These are tuned to avoid metallic resonances
    static constexpr int COMB_LENGTHS[NUM_COMBS] = {
        1116, 1188, 1277, 1356, 1422, 1491, 1557, 1617
    };
    
    // Allpass filter delay line lengths
    static constexpr int ALLPASS_LENGTHS[NUM_ALLPASS] = {
        556, 441, 341, 225
    };
    
    // Comb filter state
    struct CombFilter {
        std::vector<float> buffer;
        int bufferSize;
        int index;
        float filterStore;  // For damping lowpass
        
        CombFilter() : bufferSize(0), index(0), filterStore(0.0f) {}
        void init(int size);
        float process(float input, float feedback, float damp1, float damp2);
    };
    
    // Allpass filter state
    struct AllpassFilter {
        std::vector<float> buffer;
        int bufferSize;
        int index;
        
        AllpassFilter() : bufferSize(0), index(0) {}
        void init(int size);
        float process(float input);
    };
    
    std::array<CombFilter, NUM_COMBS> combL;
    std::array<CombFilter, NUM_COMBS> combR;
    std::array<AllpassFilter, NUM_ALLPASS> allpassL;
    std::array<AllpassFilter, NUM_ALLPASS> allpassR;
    
    // Parameters
    float roomSize;
    float damping;
    float wet, wet1, wet2;
    float dry;
    float width;
    
    // Derived coefficients
    float feedback;
    float damp1, damp2;
    
    // Pre-allocated work buffer
    std::vector<float> workBuffer;
    
    void updateCoefficients();
    
    // Stereo spread (slight offset for right channel)
    static constexpr int STEREO_SPREAD = 23;
    
    // Fixed gain to prevent clipping
    static constexpr float FIXED_GAIN = 0.015f;
    static constexpr float SCALE_WET = 3.0f;
    static constexpr float SCALE_DRY = 2.0f;
    static constexpr float SCALE_DAMP = 0.4f;
    static constexpr float SCALE_ROOM = 0.28f;
    static constexpr float OFFSET_ROOM = 0.7f;
};

} // namespace DubSiren
