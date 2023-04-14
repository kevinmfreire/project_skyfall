# Height Sensing Subsystem (HSS)

## Requirements
* Python 3.8.x
* Linux OS

## Table of Content
* Overview
* Goals
* Assumptions
* Usage
* Conclusion
* Afterword

## Overview
I've been chosen to implement the Height Sensing System (HSS) for a Lunar Lander for the first Canadian-led soft landing on the moon.  The subsystem engages during the last 50 meters of the descent towards the lunar surface. It's used to determine the current spacecraft altitude and to signal to other subsystems when we have landed.  The spacecraft has a laser altimeter sensor that is used to compute the height of the spacecraft, and the HSS should read the raw altimeter measurements and calculate the height.

The complex nature of the Lander flight software enables all subsytems to execute in a distrubuted context where each communicates with one another through the use of a message bus called MoonWire.  Subsystems send data by sending specially farmatted UDP packets onto the bus and receive data by listening for specifically formatted UDP pcakets on this bus from other subsytems.  The MoonWires specification is used to determine how to read and send data from the message bus.

## Goals
* The HSS must create a UDP socket and bound to port 12778
* Once the HSS must communicate through the bus router thats bound to port 12777.
* For each LASER_ALTIMETER message received, send a HEIGHT message containing the current space craft height.
* once landing even is detected, send an ENGINE_CUTOFF message to indicate to all other subsytems that we touched down.

## Assumtions
* All sensors are always working, we determine height of spacecraft through the average height of all three sensors.
* Landing ground is not flat.
* Speed is irrelevant to safety of landing event.
* All other subsytems are functioning according to specifications.
* Max total number of accepted bytes to receive in the HSS is 4102 in order to ensure there is no data loss (type = 2 bytes, time = 4 bytes, payload = 0 - 4096).

## Usage
Open two command prompts, in one of the prompts run the python script:
```
python3 HSS.py
```

Then on the other one run:
```
./build/simulator
```

To run a basic unit test run:
```
python3 -m unittest hss_test.py
```

## Conclusion
The HSS runs as expected and once it detects a landing event it sends out an ENGINE_CUTOFF message to all other subsytems.  Improvements can be made to the system and features can be added.  For example the height sensing subsytems can be used to determine the rate of descent for the spacecraft.  In addition, the unittest can be improved to test each HSS function individually. 

## Afterword
I used Python language because it's the language I am most comfortable with as I've worked on various Machine Learning projects using python. 