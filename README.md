# hamlib2KPA500

This project started when I obtained an used KPA500 and thought about how to control it remote. I already own an ICOM 7610 
which is a perfect remote able radio using SDR-Control.

So based on this I started this python project. In my case the KPA500 and the ICOM 7610 are connected to a Rasperry 4. The script
runs on this Raspberry and via RVNC I'm able to control the KPA500 from remote. As I'm using the hamlib python modul to read the 
frequency from the TRX (and control its output power) this solution should work with every other TRX hamlib is able to control.

By today the following functions are available:
- Switch band of the KPA500 according to the frequency on the TRX
- Store the power output of the TRX toward the KPA500 on a band basis
- Show operational parameters of the KPA500 (temperature, voltage, current, fail)
- Ability to reset a hard failure from remote

Prerequisites:
- python3
- hamlib python modul installed ```sudo apt-get install python3-hamlib```
- KPA500 connected to the computer running the script via serial interface
- TRX connected either via a rigctld on another computer in the network or via USB/serial interface to the computer running the script
- KPA500 needs to be configured in a way that it changes to STBY mode on band change. Otherwise the power handling of the TRX does not work. See issue https://github.com/DM5EA/hamlib2KPA500/issues/15

Current limitations:
- This script DOES NOT update the band information FROM the KPA500 towards the TRX.
- The script is tested on LinuX only for the time being.

Below there is a screen shot of both windows.

![]()<img src=kpa500_remote.0.2.0.jpeg width=550>

