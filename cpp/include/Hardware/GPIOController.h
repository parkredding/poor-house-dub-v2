#pragma once

#include "Common.h"
#include "Audio/AudioEngine.h"
#include <functional>
#include <thread>
#include <atomic>
#include <array>
#include <map>

namespace DubSiren {

/**
 * GPIO pin assignments (BCM numbering).
 * These pins avoid I2S pins (18, 19, 21) used by PCM5102 DAC.
 */
namespace GPIO {
    // Encoder pins (CLK, DT)
    constexpr int ENCODER_1_CLK = 17;
    constexpr int ENCODER_1_DT = 2;
    constexpr int ENCODER_2_CLK = 27;
    constexpr int ENCODER_2_DT = 22;
    constexpr int ENCODER_3_CLK = 23;
    constexpr int ENCODER_3_DT = 24;
    constexpr int ENCODER_4_CLK = 20;
    constexpr int ENCODER_4_DT = 26;
    constexpr int ENCODER_5_CLK = 14;
    constexpr int ENCODER_5_DT = 13;
    
    // Button pins
    constexpr int TRIGGER_BTN = 4;
    constexpr int PITCH_ENV_BTN = 10;
    constexpr int SHIFT_BTN = 15;
    constexpr int SHUTDOWN_BTN = 3;
}

/**
 * Parameter bank enumeration.
 */
enum class Bank {
    A,  // Normal mode
    B   // Shift held
};

/**
 * Rotary encoder handler with quadrature decoding.
 */
class RotaryEncoder {
public:
    using Callback = std::function<void(int direction)>;
    
    RotaryEncoder(int clkPin, int dtPin, Callback callback);
    ~RotaryEncoder();
    
    void start();
    void stop();
    int getPosition() const { return position.load(); }
    
private:
    int clkPin;
    int dtPin;
    Callback callback;
    std::atomic<int> position;
    std::atomic<bool> running;
    std::thread pollThread;
    
    int lastClk;
    int lastDt;
    
    void pollLoop();
    void update();
};

/**
 * Momentary switch handler with debouncing.
 */
class MomentarySwitch {
public:
    using PressCallback = std::function<void()>;
    using ReleaseCallback = std::function<void()>;
    
    MomentarySwitch(int pin, PressCallback onPress = nullptr, ReleaseCallback onRelease = nullptr);
    ~MomentarySwitch();
    
    void start();
    void stop();
    bool isPressed() const { return pressed.load(); }
    
private:
    int pin;
    PressCallback pressCallback;
    ReleaseCallback releaseCallback;
    std::atomic<bool> pressed;
    std::atomic<bool> running;
    std::thread pollThread;
    
    int lastState;
    std::chrono::steady_clock::time_point lastChange;
    std::chrono::steady_clock::time_point lastPressTime;
    
    static constexpr int DEBOUNCE_MS = 10;
    static constexpr int MIN_PRESS_MS = 30;
    
    void pollLoop();
};

/**
 * Control surface handler for the Dub Siren.
 * 
 * 5 Encoders with bank switching:
 * - Bank A: Volume, Filter Freq, Filter Res, Delay Feedback, Reverb Mix
 * - Bank B: Release Time, Delay Time, Reverb Size, Osc Waveform, LFO Waveform
 * 
 * 4 Buttons: Trigger, Pitch Envelope, Shift, Shutdown
 */
class GPIOController {
public:
    using ShutdownCallback = std::function<void()>;
    
    GPIOController(AudioEngine& engine, ShutdownCallback shutdownCb = nullptr);
    ~GPIOController();
    
    /**
     * Start the control surface.
     */
    void start();
    
    /**
     * Stop the control surface and cleanup GPIO.
     */
    void stop();
    
    /**
     * Get current bank.
     */
    Bank getCurrentBank() const { return currentBank.load(); }
    
    /**
     * Check if control surface is running.
     */
    bool isRunning() const { return running.load(); }
    
private:
    AudioEngine& engine;
    ShutdownCallback shutdownCallback;
    std::atomic<bool> running;
    std::atomic<Bank> currentBank;
    std::atomic<bool> shiftPressed;
    
    // Parameter values
    struct Parameters {
        // Bank A
        float volume = 0.7f;
        float filterFreq = 2000.0f;
        float filterRes = 1.0f;
        float delayFeedback = 0.5f;
        float reverbMix = 0.35f;
        
        // Bank B
        float release = 0.5f;
        float delayTime = 0.2f;
        float reverbSize = 0.5f;
        int oscWaveform = 0;
        int lfoWaveform = 0;
    };
    Parameters params;
    
    // Hardware components
    std::array<std::unique_ptr<RotaryEncoder>, 5> encoders;
    std::array<std::unique_ptr<MomentarySwitch>, 4> buttons;
    
    // Encoder handlers
    void handleEncoder(int encoderIndex, int direction);
    
    // Button handlers
    void onTriggerPress();
    void onTriggerRelease();
    void onPitchEnvPress();
    void onShiftPress();
    void onShiftRelease();
    void onShutdownPress();
    
    // Apply parameter to engine
    void applyParameter(const char* name, float value);
    
    // Initialize GPIO (platform-specific)
    bool initGPIO();
    void cleanupGPIO();
};

/**
 * Simulated control surface for testing without GPIO hardware.
 */
class SimulatedController {
public:
    SimulatedController(AudioEngine& engine);
    
    void start();
    void stop();
    void processCommand(char cmd);
    void printHelp();
    
private:
    AudioEngine& engine;
    std::atomic<bool> running;
};

} // namespace DubSiren
