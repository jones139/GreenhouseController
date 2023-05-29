# GreenhouseController

## Overview
This is a Raspberry Pi based greenhouse watering system controller.
It will switch the irrigation system on and off periodically to control the
amount of water provided.

It measures the following parameters:
 * Light Level
 * Temperature
 * Humidity
 * Soil Resistance

The soil resistance measurements appear to be plausible, so the intention is
to implement PID control to vary the amount of water provided to control
soil conductivity.   The temperature, humidity and light level readings may
be used for a feed-forward component to anticipate high water demand rather than allow the error to build up too far.

# Hardware
  * Raspberry Pi Model 3 (this is overkill for what it is doing, but it is easy!)
  * BH1750 Light Sensor
  * SHT31 Temperature/Humidity Sensor
  * DS18B20 1 Wire Temperature Sensor
  * Generic soil resistance probe with associated module to give analogue outut.
  * 12V solenoid valve to control water

# Irrigation System
The irrigation system uses dripper heads conneced to small diameter (~8mm diameter) plastic hose.
Calibration tests in 2022 showed that  the system dispenses 0.074 l/min per head.
Each grow bag has two dripper heads so we dispense 0.148 l/min per grow bag.   Each grow bag needs around 2 l/day, so we need to water for about 17 sec per 30 minute cycle to give a totla of 2 l/day.


# Credits
  * BH1750 light sensor library: Ondřej Caletka: https://gist.github.com/oskar456/95c66d564c58361ecf9f
  * SHT3x temp/humidity library: Olivier den Ouden: https://github.com/OlivierdenOuden/Sensirion_SHT35
  * Adafruit ADS1x15 library for ADC.
  * simple-pid library: Martin Lundberg: https://simple-pid.readthedocs.io/en/latest/simple_pid.html#module-simple_pid.PID
  
