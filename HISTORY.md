### Version 0.1.3 (2024-10-18)
- Always open the settings window below the main window

### Version 0.1.2 (2024-10-17)
- Fixing some data conversion bugs

### Version 0.1.1 (2024-10-16)
- In the settings window changed the control of TRX output power to sliders.
- In case the band is switched manually on the KPA500 a check provides a warning now.

### Version 0.1.0 (2024-10-15)
- First reliable version loaded up to github.
- Config edit window as part of the config class
  Parameter saving works for pwr per band
- Read paramter -c <configFileName>
- Use the python hamlib interface for TRX control, those changed TRXrigctl_class to TRXhamlib

### Version 0.0.9:
- Add reset fault button for full remote control
- Class to write and read program parameters to and from JSON file. Check existence on startup!
<pre>     readConfig - looks for the file and reads it or sets default values 
     writeConfig - takes the variables to write a parameters and writes the config file</pre>
     
### Version 0.0.8:
- TRX PWR defined per band for OPER status

### Version 0.0.7:
- Added slider for fan control
- Formalize comm with ICOM 7610 more (setTXPWR(xxW), getTXPWR(xxW)), rename existing class to TRXrigctl_class and import it.
- Fixed some unneeded imports

### Version 0.0.6:
- Starting with some classes for KPA500 and TRX
- Before setting the TRX output power in operate mode, save the old value and restore it later
- Request PWR from TRX and show it on the screen (with colors > 30 W - red)

### Version 0.0.5:
- Fix from 0.0.4 still not perfect
- Idea to implement: Set PWR of TRX according to status of the PA via rigctl<br>
<pre>
     ON and OPER: 30 W (30 m - 0.18)
     OFF or STBY: 100 W
</pre>
- Basically done - more to check

### Version 0.0.4
- Fix bug: If the PA switch on with the button on the device, the band change
            does not occure. How to wait for the startup delay, if we don't know
            from the program here, that the PA is in switch on sequence.
            Idea: Use the event to stop the threads ... Wait to start them again. How?
- Fixing: Adding a flag KPA500_ready. The timing seems to be critical. Sometimes it works

### Version 0.0.3
- Reorganized the threat handling
- Added handling of the Fault conditions of the PA
- First edition via Textastic +++
- Cleaned the code a bit and added more comments

