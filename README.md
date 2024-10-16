# hamlib2KPA500

Python script to synchronize the parameters read from TRX via hamlib to an Elecraft KPA500 PA.

The following functions are available:
- Switch band of the KPA500 according to the frequency on the TRX
- Store the power output of the TRX toward the KPA500 on a band basis
- Show operational parameters of the KPA500 (temperature, voltage, current, fail)

Prerequisites:
- python3
- hamlib python modul installed
- KPA500 connected to the computer running the script via serial interface
- TRX connected either via a rigctld on another computer in the network or via USB/serial interface to the computer running the script

Limitations:
- This script DOES NOT update the band information FROM the KPA500 towards the TRX

First version is running

