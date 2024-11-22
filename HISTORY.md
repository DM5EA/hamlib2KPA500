### Version 0.2.2 (2024-11-22)
- Changed how to check if the settings window is open
- Changed handling of band changes. It sometimes hapened, that the TRX PWR was not set correct after band changes.

### Version 0.2.0 (2024-11-19)
- Minor changes in KPA500 operation status handling

### Version 0.1.9 (2024-11-18)
- Added check, that avoids OPER state if TRX PWR > 39 W

### Version 0.1.8 (2024-11-15)
- Some reorgs between the different threads

### Version 0.1.7 (2024-11-14)
- Added 160 m to config file and config window
- Changed internal distribution of handling the GUI elements in different threads
- Made the serial communication towards the KPA500 thread save

### Version 0.1.6 (2024-11-07)
- Added an app icon

### Version 0.1.5 (2024-11-06)
- Added a sample config file ```example_config.json```
- Added handling of the window close button
- Prevent that the settings window duplicated over and over

### Version 0.1.4 (2024-11-01)
- While the KPA500 is in operate mode, moving the power slider for the band the TRX is on changes the output power of the TRX
- While the KPA500 is in operate mode, changing the output power of the TRX will move the slider in the config window
- Moving a slider in the config window will automatically change all internal variables
- Save button removed from the config window

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

