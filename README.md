# GreenhouseController
Esp32-cam based controller for greenhouse watering - monitors temperature, humidity and light level and waters plants using solenoid valve.


# Software Requirements
  * Arduino-Makefile (http://github.com/sudar/Arduino-Makefile)
  * Arduino IDE (but we only use that for the compiler and library manager)
  * FreeRTOS Arduino Library (in arduino ide, go to Tools->Manage Libraries and search for freeRTOS - install the FreeRTOS library)
  * pySerial library (pip install pyserial)

# Build
change directory to the waterController folder
type make

# Installation
type make upload

# Debugging
type make monitor
