#
# Program to read QRG via rigctl and send band info to 
# KPA500 via COM port
# Show status information from the PA
# NOTE: This program DOES NOT read band changes from the PA
#
# Version history - HSITORY.md
#
# Future plans - see issues on github
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
import ctypes

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
  global thread3
  global stop_event
  global myConfig
  
  myConfig.writeConfig()
      
  stop_event.set()
  thread1.join(0.1)
  thread2.join(0.1)
  thread3.join(0.1)
  
  root.quit()

# Handle the slider change for fan control

def FANSpeed_Changed(event):
  myConfig.FanSpeed = FANCTRLSlider.get()
  myKPA500.setFanSpeed(FANCTRLSlider.get())

# Start the main program

if __name__ == '__main__':

# Make some basic definitions

  killer = GracefulKiller()
  version = '0.2.2'
  
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

# Initialize TRX connection

  myTRX = TRXhamlib.TRXhamlib(myConfig.HAMLIBCONN,myConfig.HAMLIBRIG)
  myTRX.openConn()

# Make the TRX connection known to the config window

  myConfig.setHamlibContext(myTRX)
  
# Initialize KPA500

  myKPA500 = KPA500.KPA500()
  myKPA500.openSerialConn(myConfig.COMPORT)
  
  myConfig.setKPA500Context(myKPA500)

# Build the main window

  root = Tk()
  root.geometry("550x320")     # Build the root TK element 
  root.resizable(False, False)

  appDir = os.path.dirname(__file__)
  photo = PhotoImage(file = appDir + '/kpa500_remote_ico.png')
  root.wm_iconphoto(True, photo)

#  print(root.wm_sizefrom())
  
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

# Frame to show the current values

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

  BandLabel = Label(topBandframe, text = " Band (TRX): ", bg='yellow2')
  BandLabel.pack(side=LEFT)
  ActBandLabel = Label(topBandframe, text = '', bg='yellow2')
  ActBandLabel.pack(side=LEFT)
  Band1Label = Label(topBandframe, text = " Band (KPA500): ", bg='yellow2')
  Band1Label.pack(side=LEFT)
  ActBand1Label = Label(topBandframe, text = '', bg='yellow2')
  ActBand1Label.pack(side=LEFT)

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

  OperButton = Button(bottomframe, text = 'Oper', command = lambda: myKPA500.setKP500toOPER(), width = 6, bg='green') 
  OperButton.pack(padx=3, side=LEFT)

  StbyButton = Button(bottomframe, text = 'Stby', command = lambda: myKPA500.setKP500toSTBY(), width = 6, bg='orange') 
  StbyButton.pack(padx=3, side=LEFT)

  OnButton = Button(bottomframe, text = 'On', command = lambda: myKPA500.switchON(), width = 6, bg='green') 
  OnButton.pack(padx=3, side=LEFT)

  OffButton = Button(bottomframe, text = 'Off', command = lambda: myKPA500.switchOFF(), width = 6) 
  OffButton.pack(padx=3, side=LEFT)

  ConfigButton = Button(bottomframe, text = 'Settings', command = lambda: myConfig.openConfigWindow(root), width = 6) 
  ConfigButton.pack(padx=3, side=LEFT)
  
  ExitButton = Button(bottomframe, text = 'Exit', command = quit, width = 7) 
  ExitButton.pack(padx=3, side=LEFT)

  DefaultBtnColor = ExitButton.cget("background")
  
  root.title("KPA500 Remote V " + version + " © DM5EA")

# Loop until event is sent - frist thread - handle band changes and OperState changes

  def run_in_thread1(event):

    while not event.is_set():
      
#      tempLock = threading.Lock()           # This locking is essential. It otherwise may happen, that we switch
#      tempLock.acquire()                    # to the PWR stored as the initial PWR (STBY state)

      newBand = myTRX.getActBand()

      if myTRX.bandChanged():
        if myKPA500.KPA500_ready: 
          myKPA500.sendCMD((myKPA500.bandToCommand(newBand)))
          myKPA500.OperStat = False              # As per config of the KPA500 after band change it is set to STBY
          myTRX.ackBandChange()                  # |--> We set this explicit here to avoid problems in PWR handling
        ActBandLabel.configure(text = newBand)   # |--> The other thread might read to changed Oper State to late
 
# Need to do this here and not in the other thread. Otherwise we might not get the
# right power setting because of the wrong band used.
# BUT: We might want to redo this part as it is a bit ugly
 
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

# Handle the screen elements

      TRXActPWR = myTRX.getTXPWR()
      TRXPWRLevel.configure(text = TRXActPWR-1)
      
      if myKPA500.OperStat:
        myConfig.setPWRSliderForBand(newBand, TRXActPWR)
        if TRXActPWR > 39:
          TRXPWRLevel.configure(foreground='red')
          myKPA500.setKP500toSTBY()
        elif TRXActPWR > 37:
          TRXPWRLevel.configure(foreground='yellow')
        else:
          TRXPWRLevel.configure(foreground='green')
      else:
        TRXPWRLevel.configure(foreground='green')

#      tempLock.release()

# Redo until here (sometime)

      time.sleep(100/1000)

# Loop until event is sent - second thread - read PWR for bar

  def run_in_thread2(event):
    
    while not event.is_set():

# Read and display the current putput power and SWR

      Sresp = myKPA500.getValue(myKPA500.PwrCMD)
#      print(Sresp)
#      print(KPA500_ready)
      if Sresp[1:3] == 'WS' and Sresp[3:6] != ';':    # Second part checks, if the PA is really on
          myKPA500.KPA500_ready=True
          pwr = Sresp[3:6]
          try:
            ipwr = int(pwr)
          except:
            pass
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
          try:
            iswr = int(swr)
          except:
            pass
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
          else:
            myKPA500.OperStat=False

# We assume the else part as the PA is switched off

      else:
          myKPA500.KPA500_ready=False
          myKPA500.OperStat=False

# Do the next part because after switch off and on the band of the PA is reset
# to 10 MHz and not switched to the right band otherwise

          myKPA500.oldBand = ''
          myKPA500.actBand = ''
          myKPA500.OperStat = False
          myKPA500.OldOperStat = False
          myTRX.bandChange = True
          
          time.sleep(1)
          
      time.sleep(5/1000)

# Loop until event is sent - third thread - read all status - handle GUI elements

  def run_in_thread3(event):
      
    while not event.is_set():
      if myKPA500.KPA500_ready:

          OnButton.configure(background='green',foreground='white')      # PA is on
          OnButton.config(activebackground=OnButton.cget('background'))  # set the button
          OnButton.config(activeforeground=OnButton.cget('foreground'))
          
          if myKPA500.OperStat:
            OperButton.configure(background='green',foreground='white')
            OperButton.config(activebackground=OperButton.cget('background'))
            OperButton.config(activeforeground=OperButton.cget('foreground'))
            StbyButton.configure(background=DefaultBtnColor)
            StbyButton.config(activebackground=StbyButton.cget('background'))
          else:
            OperButton.configure(background=DefaultBtnColor,foreground='black')
            OperButton.config(activebackground=OperButton.cget('background'))
            OperButton.config(activeforeground=OperButton.cget('foreground'))
            StbyButton.configure(background='orange')
            StbyButton.config(activebackground=StbyButton.cget('background'))

# Look for the temp

          Sresp = myKPA500.getValue(myKPA500.TempCMD)
          if Sresp[3:6] != ';' and Sresp[3:6] != '':
            try:
              Temp = int(Sresp[3:6])
            except:
              pass
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

# Get actual band from KPA500

          resp = myKPA500.getBand()
          ActBand1Label.configure(text = resp)
          if resp != myTRX.actBand:
            ActBandLabel.configure(foreground='red')
            ActBand1Label.configure(foreground='red')
          else:
            ActBandLabel.configure(foreground='black')
            ActBand1Label.configure(foreground='black')
      else:
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
          ActBand1Label.configure(text = '-')

      time.sleep(100/1000)


# prepare the event for stopping the background threads

  stop_event = threading.Event() 
  
  thread1 = threading.Thread(target=run_in_thread1, args=(stop_event,), daemon=True)
  thread1.start()
  
  thread2 = threading.Thread(target=run_in_thread2, args=(stop_event,), daemon=True)
  thread2.start()
  
  thread3 = threading.Thread(target=run_in_thread3, args=(stop_event,), daemon=True)
  thread3.start()
  
  root.mainloop()

  print("End of the program. Cleaning all up...")

  myKPA500.closeSerialConn()
  myTRX.closeConn()
  
