# Soil Moisture Sensors

## Background
Last Year (2022) I started off using a resistance moisture sensor.   This was working remarkably well for a while, but I thought its output was starting to drift (I needed to change the moisture level demand to keep the soil at a good moisture level).   After a few weeks I had a failure where the sensor read low, so the system flooded the greenhouse trying to get the soil moist again.   
On investigation, there was a lot of corrosion of the sensor electrodes - this had happened a lot quicker than I had expected, so I lost confidence in resistance probes.

There are capacitance based probes readily available on Amazon and Ebay, so I tried some of those, but had very eratic results which I could not trace.   Someone else had done a lot of work on these for an automatic flower pot project (add reference), and he pointed out that although many of these probes are labelled "V1.2", they are different.   Sure enough, mine did not have a voltage regulator populated on the board, which could have accounted for some of the issues.

So this year I have bought some new ones from Amazon (ADD LINK), which do have an on-board regulator, so this page describes my attempt at calibrating them.....

## Electrical Details
The sensors are all powered from the same nominal 5V supply from an Arduino Nano, which is powered via USB from a Raspberry Pi Model 3.  The actual supply is 4.5V with four capacitance sensors powered at once.
The output of the sensors is measured by the Arduino Atmega processor ADC, which is 10 bits.   It is using a 5V reference, so as my boards are using an on-board 3.3V regulator, I am not going to be using all of the resolution of the ADC, so this is going to be a rather low resolution measurement for now.

Sensor outputs when in air:
  1 2.20V (498 counts)
  2 2.24V (506 counts)
  3 2.22V (504 counts)
  4 2.22V (506 counts)

## Calibration Set-Up

  - Two small flower pots filled with potting compost.  Masses measured using my best cheap ASDA digital kitchen scales.
  - Flower pots in plastic tray to catch water.
  - Mass of larger pot and tray is 33g.   Nominally dry compost makes it up to 103g, so 70g of dry compost.
  - Mass of smaller pot and tray is 29g.  Nominally dry compost makes it up to 80g, so 51g of dry compost.
  - Sensors placed at edge of pot, to simulate how they will be used when a plant is present.  This seemed to have very little effect on the reading.

## Intial Measurements (12 April 2023)
All four sensors in larger pot.  Took initial measurements with compost dry, then added water
to saturate the compost - water initially ran out into tray.   Sensor 1 reading initially erratic - disconnected and re-connected cable connection a few times and it seemed to stabilise - possible wiring issue with Sensor 1 though.  

Sensors 1-3 reacted much faster to adding water than sensor 4 which lagged behind (1-3 dropped to about 1.0 to 1.2V, but sensor 4 held up at 1.6V.  This migh tbe becase water was added pointing away from Sensor 4, so added more water to that side of pot.   Sensor 4 reading then fell down to be simlar to the other 4, but started to rise again as water drained.  Need to thoroughly saturate soil to check if this is a sensor issue or a true moisture distribution issue with initially very dry compost.)
With compost pretty well saturated, mass of pot and tray increased from 103g to 177g, so added 74g of water to the 70g of compost.

Added more compost up to top of pot so sensors are fully inserted and added water to saturate the new top layer.

(Volts followed by ADC counts in brackets)


| Sensor | In Air | Dry Compost | Wet Compost |  Wet Compost Topped up to Line |
| 1      | 2.20V (498) | 2.12V (479) | 0.93V (207) |  0.82V (183) |
| 2      | 2.24V (506) | 2.19V (496) | 0.96V (214) |  0.90V (201) |
| 3      | 2.22V (504) | 2.14V (483) | 0.96V (214) |  0.88V (197) |
| 4      | 2.22V (506) | 2.11V (476) | 1.04V (232) |  0.88V (197) |

So Dry is 2.20V (498 counts), wet is 0.82V (183 counts).   Use this for initial calibration, and plot measurement vs time and mass of pot as it dries out.

When tidying up the wiring I removed the sensors and decided the compost was not really saturated, so added water to the tray so it can soak it up over night to make sure it is really saturated at the start - so it is possible that the over-night readings may increase rather than decrease as the compost absorbs water.

## Measurements during Dry-Out
With sensors in initially saturated compost, monitored indicated soil moisture content as the pot of compost dries out.   Each day, the sensors are removed from the pot, and the pot, tray and compost weighed, then the sensors returned.

| Date           | Mass (g) | Sensor 1 | Sensor 2 | Sensor 3 | Sensor 4 | Notes |
| ---            | ---      | ---      | ---      | ---      | ---      | ---   |
| Fri 14/04/2023 | 368 g    | 96.0    | 90.2     | 93.7      |  91.4     | Compost saturated      |
| Sat 15/04/2023 | 351 g    |   95.4  |  91.4    |  96.0     |   92.5    | Compost very wet      |
| Sun 16/04/2023 | 339 g    |   95.0  |  91.5    |   96.1    |   92.0    | Compost still very wet      |
| Mon 17/04/2023 | 329 g    |   95.3  |  90.3    |   91.5    |   93.2    | Compost still very wet      |
| Tue 18/04/2023 | 323 g    |   93.4  |  90.0    | 94.6      |   89.6    | Compost damp.  Pot still feels heavy | 



The measurements became very unreliable after moving the system outside.
This was traced to be poor connections in the provided connectors between the
sensors and the cabling.
Soldered the cables onto the sensor circuit boards and the readings became more
reliable.

Step Changes during long term operation
---------------------------------------
During soak test using the ADC1115 for measurement it was noticed tha the
readings stepped down slightly at about 2230 on an evening and stepped back up around 0430.   This was repeatable (but exact times have not been checked).
All four sensors had a simlar step change from about 95% to 90% moisture.

Because all four sensors changed by a similar amount at the same time, this
does not appear to be a sensor issue (such as change in temperature etc.),
so suspect the ADC gain to be varying.   Set up a stand-alone arduino to
monitor the sensor output voltages independently.   The independent measurements
also showed a step change at the same time, so it is not the ADC.

It could be a power supply issue, so set up to monitor sensor power supply voltage.   Unfortunately the power supply is 5V so full scale on the arduino so
no change detected.   Set a 26k-26k potential divider to divide power supply
voltage by two and set the system monitoring for another night....

Overnight 25-26 May 2023, Channel 4 of the diferse arduino based monitor was connected to the power supply via a 50% potential divider.   Channels 1-3 were connected to sensors 1-3.  Channels 1-4 of the main ADC were connected to the sensors.
FIXME:  NEED TO ANALYSE RESULTS, but initial observation is that the power supply was stable and the sensor outputs changed approximately coincident with it getting dark.

26 May 2023 Connected Channel 1 of the main ADC and the Arduino diverse monitor to the power supply via a 50% potential divider (indicates -25.4% moisture).   Removed sensor 4 from the grow bag and confirmed that with it in dry air indicated about 0% moisture.   Inserted into separate pot of damp compost with no plants.    Indicating 66.3% moisture [Note - when I first inserted it, it read over 90%, so not sure if the sensor is very slow to respond to reducing moisture level - might need to check - after inserting following dry air check, value is gradually rising (67.0% after ~3 minutes cf 66.3% immediately after inserting).


27 May 2023
The 'control' inputs (power supply monitor and sensor in pot containing only wet compost) showed constant readings overnight, but the two remaining grow-bag sensors showed the same behaviour as previously, dipping down by about 4% between dusk and dawn.
Therefore it appears to be a genuine issue to do with the sensors being in the grow bag - either the type of soil in the grow bag or the plant affecting the soil capacitance during periods of darkness.

Watered the control pot which increased the moisture indication from about 61% to 91% - still less than the grow bag sensors which were indicating about 99% moisture.
Watering the growbag had no appreciable effect on indicated moisture content.

Around 17:00 removed each of the grow-bag sensors, wiped it clean and replaced it.   The indications fell from about 97% to 80% and 72% for sensors 2 and 3 respectively - ie a very significant change from removing, cleaning and re-inserting the sensors.

Removed the additional ADC as we have now demonstrated that the installed ADC is working correctly - kept channel 1 monitoring the soil sensors power supply to be sure that there is no effect htere.

So, the fact that the indication dips during periods of darkness and returns to normal is suggesting that there is something physical happening, not an electronics issue.  BUT, the fact that removing, wiping and replacing the sensors changed the indication so much suggests an instrument issue.
Could the sensors be building up a film of bacteria etc that is increasing the indication?   It is a pitty we cleaned all of the installed sensors otherwise we could have tried powering the system down for a period to ensure everything is discharged then re-starting to see if it is a sensor issue or something attached to the sensor.   See if we still see the night-time dip after cleaning....


28 May 2023
Control pot remained stable overnight while the growbag moisture indications stepped down then back up.

29 May 2023
Planted a tomato plant in the control pot and watered it.
Growbags had been on timed watering at 10s per 30 min cycle, but they were drying out so watered manually and
increaed watering time.
Re-connected input 1 to sensor 1 rather than the power supply now we are confident that we do not have a power
supply issue causing the odd radings.
In suspense to see if adding the tomato plant to the control pot changes the overnight behaviour of the readings or not.

Initial readings suggested that the separate tomato plant pot behaved in a similar manner, but it stopped.  The plant is not looking well, which might account for it.

Returned all four sensors to service in the grow bag and ran the system on moisture control, cleaning the sensors weekly.  This resulted in step changes in the readings, so we adjusted the set point based on Sandie's calibrated finger test.



~19 June 2023, Sensor 3 failed, reading low.   

21 June 2023, Inspected Sensor 3.  Hole in glue on back of board noted, which could allow water to short between output and +vcc, which could give the low reading effect.    Exchanged for new sensor with varnished edges and varnished connector on the back.
Working ok after that.

22 June 2023, just after manual watering of plants, Sensors 2 and 4 failed low.  System put into time rather than moisture control.

23 June 2023
Removed all sensors and dried them.
Sensors 1, 3 and 4 reading sensible zero.
Sensor 2 reading -108% - measured output 3.9V

In water: 	1 -> 98%
		2 -> -109%
		3 -> 93% (0.87 V)
		4 -> 8% (2.0 to 2.6V, eratic)

So sensors 2 and 4 are faulty.

Sensor 2 showing corrosion at connector.   Powered down to clean it.  Now indicaes 0% when dry, 99% in water, so corrosion products/debris giving conduction path between +vcc and output.   Dried and varnished both connector and edges of board.

No obvous fault on sensor 4, other than the output pin is not fully encapsulated in glue on the back - could it have got damp and conducted to +vcc under the glue maybe.   Re-checked and it appears to be working correctly, which implies it was a moisture ingress issue and drying it out has cured it.   Dried it and varnished more thoroughly.

Also improved varnishing of the other (working) sensors.


Calibration Check after varnishing

		Dry		In Water
Sensor 1	2.196		0.811
Sensor 2	2.209		0.788
Sensor 3	2.224		0.860
Sensor 4	2.219		0.840


All sensors now read in 90-95% range.

Manual watering before going away resulted in Sensor 1 readign -110% (and sensor 4 briefly fell to 75% before recovering - suggests connections wetted with fertilser dosed water?   Inspecting it appears to show soil splashed into connector.  Dried out and reading correct zero level.   Replaced without inserting quite so far - indicating about 85% and gradually increasing as soilmoves around it?  Settled at 101% - will have to see if it is responding to moisture changes correclty or not.