#include "Hardware/GPIOController.h"
#include <iostream>
#include <cstring>
#include <vector>

#ifdef HAVE_GPIOD
#include <gpiod.h>
#endif

#ifdef HAVE_PIGPIO
#include <pigpio.h>
#endif

namespace DubSiren {

// ============================================================================
// Platform-specific GPIO helpers
// ============================================================================

namespace {

bool gpioInitialized = false;

#ifdef HAVE_GPIOD
struct gpiod_chip* gpioChip = nullptr;
struct gpiod_line_request* lineRequest = nullptr;

// All GPIO pins we need to monitor
const unsigned int ALL_PINS[] = {
    2, 3, 4, 10, 13, 14, 15, 17, 20, 22, 23, 24, 26, 27
};
const size_t NUM_PINS = sizeof(ALL_PINS) / sizeof(ALL_PINS[0]);

bool initPlatformGPIO() {
    if (gpioInitialized) return true;
    
    gpioChip = gpiod_chip_open("/dev/gpiochip0");
    if (!gpioChip) {
        std::cerr << "Failed to open GPIO chip" << std::endl;
        return false;
    }
    
    // Configure all pins at once for efficiency
    struct gpiod_line_settings* settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(settings, GPIOD_LINE_DIRECTION_INPUT);
    gpiod_line_settings_set_bias(settings, GPIOD_LINE_BIAS_PULL_UP);
    
    struct gpiod_line_config* config = gpiod_line_config_new();
    gpiod_line_config_add_line_settings(config, ALL_PINS, NUM_PINS, settings);
    
    struct gpiod_request_config* reqConfig = gpiod_request_config_new();
    gpiod_request_config_set_consumer(reqConfig, "dubsiren");
    
    lineRequest = gpiod_chip_request_lines(gpioChip, reqConfig, config);
    
    gpiod_request_config_free(reqConfig);
    gpiod_line_config_free(config);
    gpiod_line_settings_free(settings);
    
    if (!lineRequest) {
        std::cerr << "Failed to request GPIO lines" << std::endl;
        gpiod_chip_close(gpioChip);
        gpioChip = nullptr;
        return false;
    }
    
    gpioInitialized = true;
    std::cout << "libgpiod initialized successfully (" << NUM_PINS << " pins)" << std::endl;
    return true;
}

void cleanupPlatformGPIO() {
    if (lineRequest) {
        gpiod_line_request_release(lineRequest);
        lineRequest = nullptr;
    }
    if (gpioChip) {
        gpiod_chip_close(gpioChip);
        gpioChip = nullptr;
    }
    gpioInitialized = false;
}

int readPin(int pin) {
    if (!lineRequest) return 1;
    
    // Fast read - line is already requested
    int value = gpiod_line_request_get_value(lineRequest, static_cast<unsigned int>(pin));
    
    // With pull-up bias: ACTIVE = HIGH (not pressed), INACTIVE = LOW (pressed/grounded)
    // Our button logic expects: 0 = pressed, 1 = not pressed
    return value == GPIOD_LINE_VALUE_ACTIVE ? 1 : 0;
}

#elif defined(HAVE_PIGPIO)

bool initPlatformGPIO() {
    if (!gpioInitialized) {
        if (gpioInitialise() < 0) {
            std::cerr << "Failed to initialize pigpio" << std::endl;
            return false;
        }
        gpioInitialized = true;
    }
    return true;
}

void cleanupPlatformGPIO() {
    if (gpioInitialized) {
        gpioTerminate();
        gpioInitialized = false;
    }
}

int readPin(int pin) {
    return gpioRead(pin);
}

void setupInputPin(int pin) {
    gpioSetMode(pin, PI_INPUT);
    gpioSetPullUpDown(pin, PI_PUD_UP);
}

#else

bool initPlatformGPIO() {
    std::cout << "GPIO not available - running in simulation mode" << std::endl;
    return false;
}

void cleanupPlatformGPIO() {
}

int readPin(int pin) {
    (void)pin;
    return 1;  // Simulated: pulled up (not pressed)
}

void setupInputPin(int pin) {
    (void)pin;
}

#endif

} // anonymous namespace

// ============================================================================
// RotaryEncoder Implementation
// ============================================================================

RotaryEncoder::RotaryEncoder(int clkPin, int dtPin, Callback callback)
    : clkPin(clkPin)
    , dtPin(dtPin)
    , callback(std::move(callback))
    , position(0)
    , running(false)
    , lastClk(1)
    , lastDt(1)
{
}

RotaryEncoder::~RotaryEncoder() {
    stop();
}

void RotaryEncoder::start() {
    if (running.load()) return;
    
#ifdef HAVE_PIGPIO
    setupInputPin(clkPin);
    setupInputPin(dtPin);
    lastClk = readPin(clkPin);
    lastDt = readPin(dtPin);
#endif
    
    running.store(true);
    pollThread = std::thread(&RotaryEncoder::pollLoop, this);
}

void RotaryEncoder::stop() {
    running.store(false);
    if (pollThread.joinable()) {
        pollThread.join();
    }
}

void RotaryEncoder::pollLoop() {
    while (running.load()) {
        update();
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
}

void RotaryEncoder::update() {
    int clkState = readPin(clkPin);
    int dtState = readPin(dtPin);
    
    if (clkState != lastClk) {
        int direction;
        if (dtState != clkState) {
            position.fetch_add(1);
            direction = 1;
        } else {
            position.fetch_sub(1);
            direction = -1;
        }
        
        if (callback) {
            callback(direction);
        }
    }
    
    lastClk = clkState;
    lastDt = dtState;
}

// ============================================================================
// MomentarySwitch Implementation
// ============================================================================

MomentarySwitch::MomentarySwitch(int pin, PressCallback onPress, ReleaseCallback onRelease)
    : pin(pin)
    , pressCallback(std::move(onPress))
    , releaseCallback(std::move(onRelease))
    , pressed(false)
    , running(false)
    , lastState(1)
{
    lastChange = std::chrono::steady_clock::now();
    lastPressTime = lastChange;
}

MomentarySwitch::~MomentarySwitch() {
    stop();
}

void MomentarySwitch::start() {
    if (running.load()) return;
    
#ifdef HAVE_PIGPIO
    setupInputPin(pin);
    lastState = readPin(pin);
#endif
    
    running.store(true);
    pollThread = std::thread(&MomentarySwitch::pollLoop, this);
}

void MomentarySwitch::stop() {
    running.store(false);
    if (pollThread.joinable()) {
        pollThread.join();
    }
}

void MomentarySwitch::pollLoop() {
    while (running.load()) {
        int state = readPin(pin);
        auto now = std::chrono::steady_clock::now();
        
        // Debounce
        if (state != lastState) {
            lastState = state;
            lastChange = now;
        }
        
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - lastChange).count();
        if (elapsed < DEBOUNCE_MS) {
            std::this_thread::sleep_for(std::chrono::milliseconds(2));
            continue;
        }
        
        // Button is active low (pressed when pin reads 0)
        if (state == 0 && !pressed.load()) {
            pressed.store(true);
            lastPressTime = now;
            if (pressCallback) {
                pressCallback();
            }
        } else if (state == 1 && pressed.load()) {
            // Enforce minimum press duration
            auto pressDuration = std::chrono::duration_cast<std::chrono::milliseconds>(now - lastPressTime).count();
            if (pressDuration >= MIN_PRESS_MS) {
                pressed.store(false);
                if (releaseCallback) {
                    releaseCallback();
                }
            }
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(2));
    }
}

// ============================================================================
// GPIOController Implementation
// ============================================================================

GPIOController::GPIOController(AudioEngine& engine, ShutdownCallback shutdownCb)
    : engine(engine)
    , shutdownCallback(std::move(shutdownCb))
    , running(false)
    , currentBank(Bank::A)
    , shiftPressed(false)
{
}

GPIOController::~GPIOController() {
    stop();
}

bool GPIOController::initGPIO() {
    return initPlatformGPIO();
}

void GPIOController::cleanupGPIO() {
    cleanupPlatformGPIO();
}

void GPIOController::start() {
    if (running.load()) return;
    
    std::cout << "Initializing control surface..." << std::endl;
    
    bool hasGPIO = initGPIO();
    
    if (hasGPIO) {
        // Create encoders
        const int encoderPins[5][2] = {
            {GPIO::ENCODER_1_CLK, GPIO::ENCODER_1_DT},
            {GPIO::ENCODER_2_CLK, GPIO::ENCODER_2_DT},
            {GPIO::ENCODER_3_CLK, GPIO::ENCODER_3_DT},
            {GPIO::ENCODER_4_CLK, GPIO::ENCODER_4_DT},
            {GPIO::ENCODER_5_CLK, GPIO::ENCODER_5_DT}
        };
        
        for (int i = 0; i < 5; ++i) {
            encoders[i] = std::make_unique<RotaryEncoder>(
                encoderPins[i][0], encoderPins[i][1],
                [this, i](int dir) { handleEncoder(i, dir); }
            );
            encoders[i]->start();
            std::cout << "  ✓ encoder_" << (i+1) << " initialized (GPIO " 
                      << encoderPins[i][0] << ", " << encoderPins[i][1] << ")" << std::endl;
        }
        
        // Create buttons
        buttons[0] = std::make_unique<MomentarySwitch>(
            GPIO::TRIGGER_BTN,
            [this]() { onTriggerPress(); },
            [this]() { onTriggerRelease(); }
        );
        buttons[0]->start();
        std::cout << "  ✓ trigger button initialized (GPIO " << GPIO::TRIGGER_BTN << ")" << std::endl;
        
        buttons[1] = std::make_unique<MomentarySwitch>(
            GPIO::PITCH_ENV_BTN,
            [this]() { onPitchEnvPress(); },
            nullptr
        );
        buttons[1]->start();
        std::cout << "  ✓ pitch_env button initialized (GPIO " << GPIO::PITCH_ENV_BTN << ")" << std::endl;
        
        buttons[2] = std::make_unique<MomentarySwitch>(
            GPIO::SHIFT_BTN,
            [this]() { onShiftPress(); },
            [this]() { onShiftRelease(); }
        );
        buttons[2]->start();
        std::cout << "  ✓ shift button initialized (GPIO " << GPIO::SHIFT_BTN << ")" << std::endl;
        
        buttons[3] = std::make_unique<MomentarySwitch>(
            GPIO::SHUTDOWN_BTN,
            [this]() { onShutdownPress(); },
            nullptr
        );
        buttons[3]->start();
        std::cout << "  ✓ shutdown button initialized (GPIO " << GPIO::SHUTDOWN_BTN << ")" << std::endl;
    }
    
    // Apply initial parameters
    engine.setVolume(params.volume);
    engine.setFilterCutoff(params.filterFreq);
    engine.setFilterResonance(params.filterRes);
    engine.setDelayFeedback(params.delayFeedback);
    engine.setReverbMix(params.reverbMix);
    engine.setReleaseTime(params.release);
    engine.setDelayTime(params.delayTime);
    engine.setReverbSize(params.reverbSize);
    
    running.store(true);
    
    std::cout << "\n";
    std::cout << "============================================================" << std::endl;
    std::cout << "  Control Surface Ready" << std::endl;
    std::cout << "============================================================" << std::endl;
    std::cout << "\nBank A: Volume, Filter Freq, Filter Res, Delay FB, Reverb Mix" << std::endl;
    std::cout << "Bank B: Release, Delay Time, Reverb Size, Osc Wave, LFO Wave" << std::endl;
    std::cout << "\nButtons: Trigger, Pitch Env, Shift (Bank A/B), Shutdown" << std::endl;
    std::cout << "============================================================" << std::endl;
}

void GPIOController::stop() {
    if (!running.load()) return;
    
    running.store(false);
    
    for (auto& encoder : encoders) {
        if (encoder) encoder->stop();
    }
    
    for (auto& button : buttons) {
        if (button) button->stop();
    }
    
    cleanupGPIO();
    
    std::cout << "Control surface stopped" << std::endl;
}

void GPIOController::handleEncoder(int encoderIndex, int direction) {
    Bank bank = currentBank.load();
    
    // Bank A parameters
    const char* bankAParams[] = {"volume", "filter_freq", "filter_res", "delay_feedback", "reverb_mix"};
    // Bank B parameters
    const char* bankBParams[] = {"release", "delay_time", "reverb_size", "osc_waveform", "lfo_waveform"};
    
    const char* paramName = (bank == Bank::A) ? bankAParams[encoderIndex] : bankBParams[encoderIndex];
    
    // Update parameter based on type
    float step;
    float newValue;
    
    if (strcmp(paramName, "volume") == 0) {
        step = 0.02f * direction;
        params.volume = clamp(params.volume + step, 0.0f, 1.0f);
        engine.setVolume(params.volume);
        newValue = params.volume;
    }
    else if (strcmp(paramName, "filter_freq") == 0) {
        step = 50.0f * direction;
        params.filterFreq = clamp(params.filterFreq + step, 20.0f, 20000.0f);
        engine.setFilterCutoff(params.filterFreq);
        newValue = params.filterFreq;
    }
    else if (strcmp(paramName, "filter_res") == 0) {
        step = 0.02f * direction;
        params.filterRes = clamp(params.filterRes + step, 0.0f, 0.95f);
        engine.setFilterResonance(params.filterRes);
        newValue = params.filterRes;
    }
    else if (strcmp(paramName, "delay_feedback") == 0) {
        step = 0.02f * direction;
        params.delayFeedback = clamp(params.delayFeedback + step, 0.0f, 0.95f);
        engine.setDelayFeedback(params.delayFeedback);
        newValue = params.delayFeedback;
    }
    else if (strcmp(paramName, "reverb_mix") == 0) {
        step = 0.02f * direction;
        params.reverbMix = clamp(params.reverbMix + step, 0.0f, 1.0f);
        engine.setReverbMix(params.reverbMix);
        newValue = params.reverbMix;
    }
    else if (strcmp(paramName, "release") == 0) {
        step = 0.1f * direction;
        params.release = clamp(params.release + step, 0.01f, 5.0f);
        engine.setReleaseTime(params.release);
        newValue = params.release;
    }
    else if (strcmp(paramName, "delay_time") == 0) {
        step = 0.05f * direction;
        params.delayTime = clamp(params.delayTime + step, 0.001f, 2.0f);
        engine.setDelayTime(params.delayTime);
        newValue = params.delayTime;
    }
    else if (strcmp(paramName, "reverb_size") == 0) {
        step = 0.02f * direction;
        params.reverbSize = clamp(params.reverbSize + step, 0.0f, 1.0f);
        engine.setReverbSize(params.reverbSize);
        newValue = params.reverbSize;
    }
    else if (strcmp(paramName, "osc_waveform") == 0) {
        params.oscWaveform = (params.oscWaveform + direction + 4) % 4;
        engine.setWaveform(params.oscWaveform);
        newValue = static_cast<float>(params.oscWaveform);
    }
    else if (strcmp(paramName, "lfo_waveform") == 0) {
        params.lfoWaveform = (params.lfoWaveform + direction + 4) % 4;
        engine.setLfoWaveform(params.lfoWaveform);
        newValue = static_cast<float>(params.lfoWaveform);
    }
    else {
        return;
    }
    
    const char* bankName = (bank == Bank::A) ? "A" : "B";
    std::cout << "[Bank " << bankName << "] " << paramName << ": " << newValue << std::endl;
}

void GPIOController::onTriggerPress() {
    std::cout << "Trigger: PRESSED" << std::endl;
    engine.trigger();
}

void GPIOController::onTriggerRelease() {
    std::cout << "Trigger: RELEASED" << std::endl;
    engine.release();
}

void GPIOController::onPitchEnvPress() {
    const char* mode = engine.cyclePitchEnvelope();
    std::cout << "Pitch envelope: " << mode << std::endl;
}

void GPIOController::onShiftPress() {
    shiftPressed.store(true);
    currentBank.store(Bank::B);
    std::cout << "Bank B active" << std::endl;
}

void GPIOController::onShiftRelease() {
    shiftPressed.store(false);
    currentBank.store(Bank::A);
    std::cout << "Bank A active" << std::endl;
}

void GPIOController::onShutdownPress() {
    std::cout << "\n============================================================" << std::endl;
    std::cout << "  SHUTDOWN BUTTON PRESSED" << std::endl;
    std::cout << "  Safely shutting down the system..." << std::endl;
    std::cout << "============================================================" << std::endl;
    
    if (shutdownCallback) {
        shutdownCallback();
    }
    
    // Issue system shutdown command
    std::system("sudo shutdown -h now");
}

// ============================================================================
// SimulatedController Implementation
// ============================================================================

SimulatedController::SimulatedController(AudioEngine& engine)
    : engine(engine)
    , running(false)
{
}

void SimulatedController::start() {
    running.store(true);
    printHelp();
}

void SimulatedController::stop() {
    running.store(false);
}

void SimulatedController::processCommand(char cmd) {
    switch (cmd) {
        case 't':
            if (engine.isPlaying()) {
                std::cout << "Trigger: RELEASED" << std::endl;
                engine.release();
            } else {
                std::cout << "Trigger: PRESSED" << std::endl;
                engine.trigger();
            }
            break;
            
        case 'p': {
            const char* mode = engine.cyclePitchEnvelope();
            std::cout << "Pitch envelope: " << mode << std::endl;
            break;
        }
        
        case 's':
            std::cout << "\nStatus:" << std::endl;
            std::cout << "  Playing: " << (engine.isPlaying() ? "yes" : "no") << std::endl;
            std::cout << "  Volume: " << engine.getVolume() << std::endl;
            std::cout << "  Frequency: " << engine.getFrequency() << " Hz" << std::endl;
            break;
            
        case 'h':
        case '?':
            printHelp();
            break;
            
        case 'q':
            running.store(false);
            break;
            
        default:
            break;
    }
}

void SimulatedController::printHelp() {
    std::cout << "\nSimulated Control Surface" << std::endl;
    std::cout << "=========================" << std::endl;
    std::cout << "Commands:" << std::endl;
    std::cout << "  t - Trigger siren (toggle)" << std::endl;
    std::cout << "  p - Cycle pitch envelope mode" << std::endl;
    std::cout << "  s - Show status" << std::endl;
    std::cout << "  h - Show this help" << std::endl;
    std::cout << "  q - Quit" << std::endl;
    std::cout << std::endl;
}

} // namespace DubSiren
