#!/bin/bash
# GPIO Cleanup Script
# Clears kernel-level GPIO edge detection state before starting the dubsiren service
# This is necessary when the service crashes without proper GPIO cleanup

# All GPIO pins used by the Dub Siren (from gpio_controller.py)
# Encoder pins: (clk, dt) pairs
ENCODER_PINS=(17 18 27 22 23 24 25 8 7 12 16 20 21 26 19 13 6 5 11 9)
# Switch pins
SWITCH_PINS=(10 4 3)

# Combine all pins
ALL_PINS=("${ENCODER_PINS[@]}" "${SWITCH_PINS[@]}")

# Function to cleanup a GPIO pin via sysfs
cleanup_gpio_pin() {
    local pin=$1
    local gpio_path="/sys/class/gpio/gpio${pin}"
    local export_path="/sys/class/gpio/export"
    local unexport_path="/sys/class/gpio/unexport"

    # If the pin is already exported, unexport it (this clears edge detection)
    if [ -d "$gpio_path" ]; then
        echo "$pin" > "$unexport_path" 2>/dev/null || true
    fi
}

# Cleanup all GPIO pins used by the Dub Siren
for pin in "${ALL_PINS[@]}"; do
    cleanup_gpio_pin "$pin"
done

exit 0
