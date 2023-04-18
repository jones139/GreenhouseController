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

