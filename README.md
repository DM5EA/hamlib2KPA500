# hamlib2KPA500

This project started when I obtained an used elecraft KPA500 and thought about how to control it remote. I already own an ICOM 7610 
which is a perfect remote able radio using SDR-Control.

So based on this I started this python project. In my case the elecraft KPA500 and the ICOM 7610 are connected to a Rasperry 4. The script
runs on this Raspberry and via RVNC I'm able to control the KPA500 from remote. As I'm using the hamlib python modul to read the 
frequency from the TRX (and control its output power) this solution should work with every other TRX hamlib is able to control.

The current implementation is fixed on a small display with 720x1560 connected directly to the Raspberry 4 HDMI. Nevertheless it can
be used via RVNC as well. The window opened by the program is fullscreen. See photos below.

More details about the display user may be fount here:

[6.25inch Capacitive Touch Display](https://www.waveshare.com/product/raspberry-pi/displays/lcd-oled/6.25inch-720x1560-lcd.htm)

By today the following functions are available:
- Switch band of the KPA500 according to the frequency on the TRX
- Store the power output of the TRX toward the KPA500 on a band basis
- Show operational parameters of the KPA500 (temperature, voltage, current, fail)
- Ability to reset a hard failure from remote

Prerequisites:
- python3
- hamlib python modul installed, for example:  ```sudo apt-get install python3-hamlib```
- KPA500 connected to the computer running the script via serial interface
- TRX connected either via a rigctld on another computer in the network or via USB/serial interface to the computer running the script

Current limitations:
- This script DOES NOT update the band information FROM the KPA500 towards the TRX.
- The script is tested on LinuX only for the time being.

Below there is a screenshot and a photo of the display.

![]()<img src=hamlib2kpa500.0.4.0.jpeg height=503> ![]()<img src=hamlib2kpa500_display.JPG height=503>



