cmake_minimum_required(VERSION 3.16)
project(DubSirenV2 VERSION 2.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Build options
option(BUILD_WITH_JUCE "Build with JUCE framework (for full features)" OFF)
option(BUILD_FOR_PI "Build optimizations for Raspberry Pi" OFF)
option(BUILD_STANDALONE "Build standalone ALSA version (no JUCE)" ON)

# Compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")

# Raspberry Pi specific optimizations
if(BUILD_FOR_PI)
    message(STATUS "Building with Raspberry Pi optimizations")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mcpu=cortex-a53 -mfpu=neon-fp-armv8 -mfloat-abi=hard")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -ffast-math")
endif()

# Find required packages
find_package(Threads REQUIRED)

# ALSA for standalone build
if(BUILD_STANDALONE)
    find_package(ALSA)
    if(ALSA_FOUND)
        message(STATUS "ALSA found: ${ALSA_LIBRARIES}")
    else()
        message(WARNING "ALSA not found - audio output will be simulated")
    endif()
endif()

# Source files
set(DSP_SOURCES
    src/DSP/Oscillator.cpp
    src/DSP/Envelope.cpp
    src/DSP/Filter.cpp
    src/DSP/Delay.cpp
    src/DSP/Reverb.cpp
    src/DSP/LFO.cpp
)

set(AUDIO_SOURCES
    src/Audio/AudioEngine.cpp
    src/Audio/AudioOutput.cpp
)

set(HARDWARE_SOURCES
    src/Hardware/GPIOController.cpp
)

set(MAIN_SOURCES
    src/main.cpp
)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Create the executable
add_executable(dubsiren
    ${DSP_SOURCES}
    ${AUDIO_SOURCES}
    ${HARDWARE_SOURCES}
    ${MAIN_SOURCES}
)

# Link libraries
target_link_libraries(dubsiren
    PRIVATE
    Threads::Threads
    m  # math library
)

if(ALSA_FOUND)
    target_link_libraries(dubsiren PRIVATE ${ALSA_LIBRARIES})
    target_compile_definitions(dubsiren PRIVATE HAVE_ALSA=1)
    target_include_directories(dubsiren PRIVATE ${ALSA_INCLUDE_DIRS})
endif()

# Raspberry Pi GPIO library (wiringPi or pigpio)
if(BUILD_FOR_PI)
    # Try to find pigpio (preferred for low-latency)
    find_library(PIGPIO_LIBRARY pigpio)
    if(PIGPIO_LIBRARY)
        message(STATUS "pigpio found: ${PIGPIO_LIBRARY}")
        target_link_libraries(dubsiren PRIVATE ${PIGPIO_LIBRARY})
        target_compile_definitions(dubsiren PRIVATE HAVE_PIGPIO=1)
    else()
        message(WARNING "pigpio not found - GPIO will be simulated")
    endif()
endif()

# Install target
install(TARGETS dubsiren
    RUNTIME DESTINATION bin
)

# Print configuration summary
message(STATUS "")
message(STATUS "=== DubSiren V2 Build Configuration ===")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Build for Pi: ${BUILD_FOR_PI}")
message(STATUS "Build standalone: ${BUILD_STANDALONE}")
message(STATUS "ALSA support: ${ALSA_FOUND}")
message(STATUS "========================================")
message(STATUS "")
