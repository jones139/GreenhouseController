tempDaemon
==========

Expects a 1-wire connection to the Raspberry Pi GPIO4 pin (pin 7), with a 4k7
pull up resistor connected to the 3.3V supply (pin 1) and Ground provided
to the 1-wire bus (pin 9)

Currently does nothing clever - just repeatedly polls one device, assuming
it is an DS18B20 temperature probe, and prints
out the temperature.

TODO
====
  * make this run as a daemon process on start up and continuously write
  temperatures to a file, along with date/time of reading.



Connections to Raspberry Pi

GPIO	       	Title	 Interface
1	    	3.3V	 1-Wire & flow meter +Vcc
2		+5V	 n/c
3		I2C SDA	 n/c
4		+5V 	 n/c
5		I2C SCL	 n/c
6		GND 	 n/c
7		GPIO4	1-Wire Data (with 4k7 pull up resistor to +Vcc)
8		TXD	n/c
9		GND	1-Wire, flow meter and relay GND
10		RXD	n/c
11		GPIO17	Flow Meter Pulses
12		GPIO18  Lamp Interlock Relay Control
13		GPIO27	K-Mirror Direction
15		GPIO22	K-Mirror Step
16		GPIO23	K-Mirror LS1 (internal pullup)
17		3.3V	n/c
18		GPIO24	KMirror LS2 (internal pullup)

External Connections
Thermometers - 1-wire interface - header pins.
Flow Meter - +vcc, gnd, data - header pins.
K-Mirror - GND, Step, Direction, LS1, LS2 - 9 pin 'D'.

USB - USB-Serial Converer to SBS power Supply
Ethernet - Ethernet to main lab network.

