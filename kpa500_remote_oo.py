#
# Program to read QRG via rigctl and send band info to 
# KPA500 via COM port
# Show status information from the PA
# NOTE: This program DOES NOT read band changes from the PA
#
# Version history
#
# Version 0.0.2
#   First fully working version
#
# Version 0.0.3
#   Reorganized the threat handling
#   Added handling of the Fault conditions of the PA
#   First edition via Textastic +++
#   Cleaned the code a bit and added more comments
#
# Version 0.0.4
#   Fix bug: If the PA switch on with the button on the device, the band change
#            does not occure. How to wait for the startup delay, if we don't know
#            from the program here, that the PA is in switch on sequence.
#            Idea: Use the event to stop the threads ... Wait to start them again. How?
#   Fixing: Adding a flag KPA500_ready. The timing seems to be critical. Sometimes it works
#
# Version 0.0.5:
#   Fix from 0.0.4 still not perfect
#   Idea to implement: Set PWR of TRX according to status of the PA via rigctl
#                      ON and OPER: 30 W (30 m - 0.18)
#                      OFF or STBY: 100 W
#   Basically done - more to check
#
# Version 0.0.6:
#   - Starting with some classes for KPA500 and TRX
#   - Before setting the TRX output power in operate mode, save the old value and
#     restore it later
#   - Request PWR from TRX and show it on the screen (with colors > 30 W - red)
#
# Version 0.0.7:
#   - Added slider for fan control
#   - Formalize comm with ICOM 7610 more (setTXPWR(xxW), getTXPWR(xxW)), rename existing class
#     to TRXrigctl_class and import it.
#   - Fixed some unneeded imports
#
# Version 0.0.8:
#   - TRX PWR defined per band for OPER status
#
# Version 0.0.9:
#   - Add reset fault button
#   - Class to write and read program parameters to and from JSON file. Check existence on startup!
#     readConfig - looks for the file and reads it or sets default values 
#     writeConfig - takes the variables to write a parameters and writes the config file
#
# Version 0.1.0 (2024-10-15):
#   - Config edit window as part of the config class
#     Parameter saving works for pwr per band
#   - Read paramter -c <configFileName>
#   - Use the python hamlib interface for TRX control
# 
# Version 0.1.1 (2024-10-16)
#   - Change the power setting to sliders (0-40) in the config window
#     options: showvalue = 0 (and organize a label beside the slider to show the value)
#   - Continue the version history in HISTORY.md on github
#
# Future plans:
#   - See issues on github
#

import KPA500
import TRXhamlib
import ProgConfig

import socket
import sys
import getopt
import serial
import signal
import time
import threading
import os
import json
import os.path

from tkinter import *    # Doing this way, there is no need to write <module>.<class>

# How to react on SIGTERM and SIGINT

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, signum, frame):
    self.kill_now = True
    quit()

# Call if Exit is pressed or SIGTERM is received (GracefulKiller)

def quit():
  global root
  global thread1
  global thread2
  global stop_event
  global myConfig
  
  myConfig.writeConfig()
  
#  if not myKPA500.OperStat:
#    myTRX.restoreInitialPWR()
    
  stop_event.set()
  thread1.join(0.1)
  thread2.join(0.1)
  
  root.quit()

# Handle the slider change for fan control

def FANSpeed_Changed(event):
  myConfig.FanSpeed = FANCTRLSlider.get()
  myKPA500.setFanSpeed(FANCTRLSlider.get())
  
# Define teh config edit window

# Start the main program

if __name__ == '__main__':

# Make some basic definitions

  killer = GracefulKiller()
  version = '0.1.0'
 
#  if os.name == 'posix':     # Look were we are
#    COMPORT = '/dev/ttyUSB0'
#  elif os.name == 'nt':
#    COMPORT = 'COM11'
  
  myConfig = ProgConfig.ProgConfig()
 
# read command line

  argv = sys.argv[1:]
  try:
    opts, args = getopt.getopt(argv,"hc:")

  except getopt.GetoptError:
    pass 
  for opt, arg in opts:
    if opt == '-c':
      myConfig.confFileName = arg

  myConfig.readConfig()
  
  QRG = ''
  iQRG = 0

# Initialize TRX connection

  myTRX = TRXhamlib.TRXhamlib(myConfig.HAMLIBCONN,myConfig.HAMLIBRIG)
  myTRX.openConn()
  
# Initialize KPA500

  myKPA500 = KPA500.KPA500()
  myKPA500.openSerialConn(myConfig.COMPORT)

# Build the main window

  root = Tk()
  root.geometry("550x320")     # Build the root TK element 

  frame = Frame(root)
  frame.pack()

# Frame for band info

  topBandframe = Frame(root,  highlightbackground="blue", highlightthickness=1)
  topBandframe.pack(pady=5,side=TOP)

# Frame to show the power level

  topPWRframe = Frame(root)
  topPWRframe.pack(pady=2,side=TOP)
  
# Frame to show the SWR

  topSWRframe = Frame(root)
  topSWRframe.pack(pady=2,side=TOP)

# Frame to show the curren values

  topValuesframe = Frame(root, highlightbackground="orange", highlightthickness=1)
  topValuesframe.pack(pady=2,side=TOP)

# Frame to show fault info
  
  topFaultframe = Frame(root, highlightbackground="red", highlightthickness=1)
  topFaultframe.pack(pady=2,side=TOP)

# Frame to show FW rev and ser no

  topFWframe = Frame(root, highlightbackground="orange", highlightthickness=1)
  topFWframe.pack(pady=2,side=TOP)

# Frame to show TRX actual PWR set

  topTRXPWRframe = Frame(root, highlightbackground="orange", highlightthickness=1)
  topTRXPWRframe.pack(pady=2,side=TOP)

# Frame to show fan control

  topFANCTRLframe = Frame(root, highlightbackground="orange", highlightthickness=1)
  topFANCTRLframe.pack(pady=2,side=TOP)

# Bottom frame for all buttons

  bottomframe = Frame(root)
  bottomframe.pack(pady=3,side=BOTTOM)

# Now place all elements in the frames

  BandLabel = Label(topBandframe, text = " Band: ", bg='yellow2')
  BandLabel.pack(side=LEFT)
  ActBandLabel = Label(topBandframe, text = '', bg='yellow2')
  ActBandLabel.pack(side=LEFT)

# Define the canvas for power level display.
# Do this in 3 parts <= 500 W green, 500-650 yellow, > 650 W red
# Similary for the SWR
# Later we change the size of the rectangles according to the measured levels

  PwrLabel = Label(topPWRframe, text = "PWR ")
  PwrLabel.pack(padx=1,side=LEFT)
  PwrCanvas = Canvas(topPWRframe, bg='whitesmoke', width=460, height=20)
  PwrGreenRect = PwrCanvas.create_rectangle(0,0,0,20,fill='green',outline='green')
  PwrYellowRect = PwrCanvas.create_rectangle(368,0,368,20,fill='orange',outline='orange')
  PwrRedRect = PwrCanvas.create_rectangle(414,0,414,20,fill='red',outline='red')
  PwrCanvas.pack(side=LEFT)

  SwrLabel = Label(topSWRframe, text = "SWR ")
  SwrLabel.pack(padx=1,side=LEFT)
  SwrCanvas = Canvas(topSWRframe, bg='whitesmoke', width=200, height=20)
  SwrGreenRect = SwrCanvas.create_rectangle(0,0,0,20,fill='green',outline='green')
  SwrYellowRect = SwrCanvas.create_rectangle(80,0,80,20,fill='orange',outline='orange')
  SwrRedRect = SwrCanvas.create_rectangle(120,0,120,20,fill='red',outline='red')
  SwrCanvas.pack(side=LEFT)

# Current values of the PA

  TempLabel = Label(topValuesframe, text = " Temp ")
  TempLabel.pack(padx=1,side=LEFT)
  TempValue = Label(topValuesframe, text = "-", width=3)
  TempValue.pack(padx=1,side=LEFT)
  CelsLabel = Label(topValuesframe, text = " C  |  ")
  CelsLabel.pack(padx=1,side=LEFT)

  VoltLabel = Label(topValuesframe, text = "HV ")
  VoltLabel.pack(padx=1,side=LEFT)
  VoltValue = Label(topValuesframe, text = "-", width=3)
  VoltValue.pack(padx=1,side=LEFT)
  VLabel = Label(topValuesframe, text = " V   |  ")
  VLabel.pack(padx=1,side=LEFT)

  AmpLabel = Label(topValuesframe, text = "Cur ")
  AmpLabel.pack(padx=1,side=LEFT)
  AmpValue = Label(topValuesframe, text = "-", width=3)
  AmpValue.pack(padx=1,side=LEFT)
  ALabel = Label(topValuesframe, text = " A ")
  ALabel.pack(padx=1,side=LEFT)

  FWLabel = Label(topFWframe, text = " FW Rev ")
  FWLabel.pack(padx=1,side=LEFT)
  FWValue = Label(topFWframe, text = "-")
  FWValue.pack(padx=1,side=LEFT)

  SerNLabel = Label(topFWframe, text = "  |  Ser # ")
  SerNLabel.pack(padx=1,side=LEFT)
  SerNValue = Label(topFWframe, text = "-")
  SerNValue.pack(padx=1,side=LEFT)

# Fault display

  FaultLabel = Label(topFaultframe, text = " Fault: ")
  FaultLabel.pack(padx=1,side=LEFT)
  FaultNo = Label(topFaultframe, text = " 0 ")
  FaultNo.pack(padx=1,side=LEFT)
  FaultText = Label(topFaultframe, text = " OK ", fg='green')
  FaultText.pack(padx=1,side=LEFT)
  FaultResetButton = Button(topFaultframe, text = 'Reset', command = lambda: myKPA500.ResetFault(), width = 4) 
  FaultResetButton.pack(padx=1, side=LEFT)

# TRX PWR display

  TRXPWRLabel = Label(topTRXPWRframe, text = " TRX PWR: ")
  TRXPWRLabel.pack(padx=1,side=LEFT)
  TRXPWRLevel = Label(topTRXPWRframe, text = " 0 ", fg='green')
  TRXPWRLevel.pack(padx=1,side=LEFT)
  TRXPWRUnit = Label(topTRXPWRframe, text = " W ", fg='green')
  TRXPWRUnit.pack(padx=1,side=LEFT)
  
# Fan control slider

  FANLabel = Label(topFANCTRLframe, text = " Fan control ")
  FANLabel.pack(padx=1,side=LEFT)
  FANCTRLSlider = Scale(topFANCTRLframe, 
                        from_=0, to=6, 
                        orient='horizontal', tickinterval=1, 
                        command = FANSpeed_Changed, 
                        length = 300)
  FANCTRLSlider.set(myConfig.FanSpeed)
  FANCTRLSlider.pack(padx=1,side=LEFT)

# All the buttons

  OperButton = Button(bottomframe, text = 'Oper', command = lambda: myKPA500.sendCMD(myKPA500.OperCMD), width = 7, bg='green') 
  OperButton.pack(padx=3, side=LEFT)

  StbyButton = Button(bottomframe, text = 'Stby', command = lambda: myKPA500.sendCMD(myKPA500.StbyCMD), width = 7, bg='orange') 
  StbyButton.pack(padx=3, side=LEFT)

  OnButton = Button(bottomframe, text = 'On', command = lambda: myKPA500.switchON(), width = 7, bg='green') 
  OnButton.pack(padx=3, side=LEFT)

  OffButton = Button(bottomframe, text = 'Off', command = lambda: myKPA500.sendCMD(myKPA500.OffCMD), width = 7) 
  OffButton.pack(padx=3, side=LEFT)

  ConfigButton = Button(bottomframe, text = 'Settings', command = lambda: myConfig.openConfigWindow(), width = 7) 
  ConfigButton.pack(padx=3, side=LEFT)
  
  ExitButton = Button(bottomframe, text = 'Exit', command = quit, width = 7) 
  ExitButton.pack(padx=3, side=LEFT)

  DefaultBtnColor = ExitButton.cget("background")
  
  root.title("KPA500 Remote V " + version + " © DM5EA")

# Loop until event is sent - frist thread - handle band changes

  def run_in_thread1(event):
    global QRG
    global iQRG

    while not event.is_set():
      
      newBand = myTRX.getActBand()

      if myTRX.bandChanged():
        if myKPA500.KPA500_ready: 
          myKPA500.sendCMD((myKPA500.bandToCommand(newBand)))
          myTRX.ackBandChange()
        ActBandLabel.configure(text = newBand)
      
      if myKPA500.OldOperStat != myKPA500.OperStat:
        if myKPA500.OperStat:
          myTRX.getInitialPWR()
          try:
            newPWR = myConfig.PWRperBand[newBand]
          except:
            newPWR = 30
          myTRX.setTXPWR(newPWR)
        else:
          myTRX.restoreInitialPWR()
        myKPA500.OldOperStat = myKPA500.OperStat

      TRXActPWR = myTRX.getTXPWR()
      TRXPWRLevel.configure(text = TRXActPWR)
      if myKPA500.OperStat and TRXActPWR > 37:
        TRXPWRLevel.configure(foreground='red')
      else:
        TRXPWRLevel.configure(foreground='green')

      time.sleep(100/1000)

# Loop until event is sent - second thread - read all status

  def run_in_thread2(event):
    
    while not event.is_set():

# Read and display the current putput power and SWR
      
      Sresp = myKPA500.getValue(myKPA500.PwrCMD)
#      print(Sresp)
#      print(KPA500_ready)
      if Sresp[1:3] == 'WS' and Sresp[3:6] != ';':    # Second part checks, if the PA is really on
          myKPA500.KPA500_ready=True
          OnButton.configure(background='green',foreground='white')      # PA is on
          OnButton.config(activebackground=OnButton.cget('background'))  # set the button
          OnButton.config(activeforeground=OnButton.cget('foreground'))
          pwr = Sresp[3:6]
          ipwr = int(pwr)
          x1 = min(ipwr, 500) * 0.736
          PwrCanvas.coords(PwrGreenRect, 0, 0, x1, 20)
          if ipwr > 500:
            x1 = 368 + (min(ipwr,650)-500) * 0.307
            PwrCanvas.coords(PwrYellowRect, 368, 0, x1, 20)
          else:
            PwrCanvas.coords(PwrYellowRect, 368, 0, 368, 20)
          if ipwr > 650:
            x1 = 414 + (ipwr-650) * 0.307
            PwrCanvas.coords(PwrRedRect, 414, 0, x1, 20)
          else:
            PwrCanvas.coords(PwrRedRect, 414, 0, 414, 20)

          swr = Sresp[7:10]
          iswr = int(swr)
          x1 = min(iswr-10, 5) * 16
          SwrCanvas.coords(SwrGreenRect, 0, 0, x1, 20)
          if iswr > 15:
            x1 = 80 + (min(iswr,20)-15) * 8
            SwrCanvas.coords(SwrYellowRect, 80, 0, x1, 20)
          else:
            SwrCanvas.coords(SwrYellowRect, 80, 0, 80, 20)
          if iswr > 20:
            x1 = 120 + (iswr-20) * 2.67
            SwrCanvas.coords(SwrRedRect, 120, 0, x1, 20)
          else:
            SwrCanvas.coords(SwrRedRect, 120, 0, 120, 20)
 
# Now read the operating state

          Sresp = myKPA500.getValue(myKPA500.OSCMD)
          if Sresp[3:4] == '1':
            myKPA500.OperStat=True
            OperButton.configure(background='green',foreground='white')
            OperButton.config(activebackground=OperButton.cget('background'))
            OperButton.config(activeforeground=OperButton.cget('foreground'))
            StbyButton.configure(background=DefaultBtnColor)
            StbyButton.config(activebackground=StbyButton.cget('background'))
          else:
            myKPA500.OperStat=False
            OperButton.configure(background=DefaultBtnColor,foreground='black')
            OperButton.config(activebackground=OperButton.cget('background'))
            OperButton.config(activeforeground=OperButton.cget('foreground'))
            StbyButton.configure(background='orange')
            StbyButton.config(activebackground=StbyButton.cget('background'))

# Look for the temp

          Sresp = myKPA500.getValue(myKPA500.TempCMD)
          if Sresp[3:6] != ';' and Sresp[3:6] != '':
            Temp = int(Sresp[3:6])
            TempValue.configure(text = Temp)

# Read voltage and current

          Sresp = myKPA500.getValue(myKPA500.VICMD)
          try:
            Volt = float(Sresp[3:6])/10
          except:
            pass
          VoltValue.configure(text = Volt)
          try:
            Amp = float(Sresp[7:10])/10
          except:
            pass
          AmpValue.configure(text = Amp)

# Read Ser No and FW Rev

          Sresp = myKPA500.getValue(myKPA500.FWCMD)
          FW = Sresp[4:-1]
          FWValue.configure(text = FW)
          
          Sresp = myKPA500.getValue(myKPA500.SerNCMD)
          SerN = Sresp[4:-1]
          SerNValue.configure(text = SerN)

# Read Fault value

          Sresp = myKPA500.getValue(myKPA500.FLCMD)
          FaultN = Sresp[3:5]
          iFaultN = 0
          try:
            iFaultN = int(FaultN)
          except:
            pass
          FaultNo.configure(text = FaultN + ' ')
          FaultText.configure(text = myKPA500.FaultArr[iFaultN] + ' ')
          if iFaultN != 0:
            FaultText.configure(foreground='red')
          else:
            FaultText.configure(foreground='green')

# Get fan speed
          try:
            FANCTRLSlider.set(int(myKPA500.getFanSpeed()))
          except:
            FANCTRLSlider.set(0)
            
# We assume the else part as the PA is switched off

      else:
          myKPA500.KPA500_ready=False
          myKPA500.OperStat=False
          OnButton.configure(background=DefaultBtnColor,foreground='black')
          OnButton.config(activebackground=OnButton.cget('background'))
          OnButton.config(activeforeground=OnButton.cget('foreground'))
          OperButton.configure(background=DefaultBtnColor,foreground='black')
          OperButton.config(activebackground=OperButton.cget('background'))
          OperButton.config(activeforeground=OperButton.cget('foreground'))
          StbyButton.configure(background=DefaultBtnColor,foreground='black')
          StbyButton.config(activebackground=StbyButton.cget('background'))
          TempValue.configure(text = '-')
          VoltValue.configure(text = '-')
          AmpValue.configure(text = '-')
          FWValue.configure(text = '-')
          SerNValue.configure(text = '-')

# Do the next part because after switch off and on the band of the PA is reset
# to 10 MHz and not switched to the right band otherwise

          myKPA500.oldBand = ''
          myKPA500.actBand = ''
          myKPA500.OperStat = False
          myKPA500.OldOperStat = False
          myTRX.bandChange = True
          
          time.sleep(1)
          
      time.sleep(5/1000)
   
# prepare the event for stopping the background threads

  stop_event = threading.Event() 
  
  thread1 = threading.Thread(target=run_in_thread1, args=(stop_event,), daemon=True)
  thread1.start()
  
  thread2 = threading.Thread(target=run_in_thread2, args=(stop_event,), daemon=True)
  thread2.start()
  
  root.mainloop()

  print("End of the program. Cleaning all up...")

  myKPA500.closeSerialConn()
  myTRX.closeConn()
  
