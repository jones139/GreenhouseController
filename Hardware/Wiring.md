# Greenhouse Controller Wiring

_Note:_ This description is for the V2 controller that is currently under construction, so may change :).

Enclosure Terminal Block

| Terminal | Description | Notes |
| ---      | ---         | ---   |
| 1         | Power Supply Input | 12V DC |
| 2         | Power 12V DC Output | 12V DC |
| 3         | Ground | |
| 4         | Ground ||
| 5         | Ground ||
| 6         | 5V Output | |
| 7         | Earth | Not Used (double insulated) |
| 8        | Soil 1 | Soil Sensor analogue output |
| 9        | Soil 2 | Soil Sensor analogue output |
| 10        | Soil 3 | Soil Sensor analogue output |
| 11        | Soil 4 |Soil Sensor analogue output  |
| 12        | Temp Vdd | +5V for DS18B20 Temperature Sensor |
| 13        | Temp GND | GND for DS18B20 Temperature Sensor |
| 14        | Temp DQ  | Data for DS18B20 Temperature Sensor |
| 15        | n/c | |
| 16        | n/c | |
| 17        | Dosing + | For 12V diaphragm pump |
| 18        | Dosing - | For 12V diaphragm pump |
| 19         | Solenoid + | Controls water (12V DC) |
| 20         | Solenoid - | Controls water (12V DC) |



The soil moisture sensors were provided with connectors for the wiring.
This makes it easy to switch out sensors, but I found that the connectors
suffered from corrosion in greenhouse conditions so they became unreliable.

So the sensors are soldered to the wiring harness rather than using the
provided connectors.
Calibrated by measuring voltage produced by each one in dry air and immersed to the insertion line in water.
Installed all four in one Growbag because of the reliability issues we have had - will calculate an average (may calculate a Median rather than a mean in case one goes faulty?).
After a warm day the average was 73% and Sandie watered them which brought the average up to 84% moisture.   Will track for a week without automatic watering to see how they behave.

I had issues with the ADC1115 being unreliable initially so used an Arduino with the Firmata firmware to provide ADC for the sensors.   This did however
increase the power consumption, so once I became more confident in the ADC1115 I removed the Arduino board from the system.

The dosing control output is GPIO #24

Calibration of dosing system.  30 sec of full seed running pumped:
30s = 190ml
30s = 190ml
70s = 370ml
100s = 570ml


