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
  root.attributes('-fullscreen',True)
  root.configure(bg=myConfig.BGC)

  appDir = os.path.dirname(__file__)
  photo = PhotoImage(file = appDir + '/kpa500_remote_ico.png')
  root.wm_iconphoto(True, photo)

# Default font size

  import tkinter.font as tkFont
  def_font = tkFont.nametofont("TkDefaultFont")
  def_font.config(size=22)

#  print(root.wm_sizefrom())
  
  frame = Frame(root)
  frame.pack()

# Frame for band info

  topBandframe = Frame(root,  highlightbackground="royalblue2", highlightthickness=2, bg='orange')
  topBandframe.pack(pady=(30, 3),side=TOP, fill=X)

# Frame to show the power and SWR level

  topPWRframe = Frame(root, highlightbackground="orange", highlightthickness=2, bg=myConfig.BGCL)
  topPWRframe.pack(pady=(0,0),side=TOP, fill=X)
  
# Frame to show the current values

  topValuesframe = Frame(root, highlightbackground="orange", highlightthickness=2,bg=myConfig.BGC)
  topValuesframe.pack(pady=3,side=TOP, fill=X)

# Frame to show fault info
  
  topFaultframe = Frame(root, highlightbackground="red", highlightthickness=2, bg=myConfig.BGC)
  topFaultframe.pack(pady=3,side=TOP, fill=X)

# Frame to show FW rev and ser no

  topFWframe = Frame(root, highlightbackground="orange", highlightthickness=2, bg=myConfig.BGC)
  topFWframe.pack(pady=3,side=TOP, fill=X)

# Frame to show TRX actual PWR set

  topTRXPWRframe = Frame(root, highlightbackground="orange", highlightthickness=2, bg=myConfig.BGC)
  topTRXPWRframe.pack(pady=3,side=TOP, fill=X)

# Frame to show fan control

  topFANCTRLframe = Frame(root, highlightbackground="orange", highlightthickness=2, bg=myConfig.BGC)
  topFANCTRLframe.pack(pady=3,side=TOP, fill=X)

# Bottom frame for all buttons

  bottomframe = Frame(root, bg=myConfig.BGC)
  bottomframe.pack(pady=20,side=TOP)

# Now place all elements in the frames

  innertopBandframe = Frame(topBandframe, bg='orange')
  innertopBandframe.pack(side=TOP)
  BandLabel = Label(innertopBandframe, text = " Band (TRX): ", bg='orange')
  BandLabel.pack(side=LEFT)
  ActBandLabel = Label(innertopBandframe, text = '', bg='orange')
  ActBandLabel.pack(side=LEFT)
  Band1Label = Label(innertopBandframe, text = " Band (KPA500): ", bg='orange')
  Band1Label.pack(side=LEFT)
  ActBand1Label = Label(innertopBandframe, text = '', bg='orange')
  ActBand1Label.pack(side=LEFT)

# Define the canvas for power level display.
# Do this in 3 parts <= 500 W green, 500-650 yellow, > 650 W red
# Similary for the SWR
# Later we change the size of the rectangles according to the measured levels

  innertopPWRframe = Frame(topPWRframe, bg=myConfig.BGCL)
  innertopPWRframe.pack(side=TOP, pady=(10,3))
  PwrLabel = Label(innertopPWRframe, text = " PWR ", fg = myConfig.FGC, bg=myConfig.BGCL)
  PwrLabel.pack(padx=1,side=LEFT)
  PwrCanvas = Canvas(innertopPWRframe, bg=myConfig.BGCL, width=460, height=myConfig.BarHeight)
  PwrGreenRect = PwrCanvas.create_rectangle(0,0,0,myConfig.BarHeight,fill='green',outline='green')
  PwrYellowRect = PwrCanvas.create_rectangle(368,0,368,myConfig.BarHeight,fill='orange',outline='orange')
  PwrRedRect = PwrCanvas.create_rectangle(414,0,414,myConfig.BarHeight,fill='red',outline='red')
  PwrCanvas.pack(side=LEFT)
  PEPLabel = Label(innertopPWRframe, text = " 000 W ", width=7, fg = myConfig.FGC, bg=myConfig.BGCL)
  PEPLabel.pack(padx=1,side=LEFT)
  
  innertopSWRframe = Frame(topPWRframe, bg=myConfig.BGCL)
  innertopSWRframe.pack(side=TOP, pady=(3,10))
  SwrLabel = Label(innertopSWRframe, text = "SWR ", fg = myConfig.FGC, bg=myConfig.BGCL)
  SwrLabel.pack(padx=1,side=LEFT)
  SwrCanvas = Canvas(innertopSWRframe, bg=myConfig.BGCL, width=200, height=myConfig.BarHeight)
  SwrGreenRect = SwrCanvas.create_rectangle(0,0,0,myConfig.BarHeight,fill='green',outline='green')
  SwrYellowRect = SwrCanvas.create_rectangle(80,0,80,myConfig.BarHeight,fill='orange',outline='orange')
  SwrRedRect = SwrCanvas.create_rectangle(120,0,120,myConfig.BarHeight,fill='red',outline='red')
  SwrCanvas.pack(side=LEFT)

# Current values of the PA

  innertopValuesframe = Frame(topValuesframe, bg=myConfig.BGC)
  innertopValuesframe.pack(side=TOP)
  TempLabel = Label(innertopValuesframe, text = " Temp ", fg = myConfig.FGC, bg=myConfig.BGC)
  TempLabel.pack(padx=1,side=LEFT)
  TempValue = Label(innertopValuesframe, text = "-", width=3, fg = myConfig.FGC, bg=myConfig.BGC)
  TempValue.pack(padx=1,side=LEFT)
  CelsLabel = Label(innertopValuesframe, text = " C  |  ", fg = myConfig.FGC, bg=myConfig.BGC)
  CelsLabel.pack(padx=1,side=LEFT)

  VoltLabel = Label(innertopValuesframe, text = "HV ", fg = myConfig.FGC, bg=myConfig.BGC)
  VoltLabel.pack(padx=1,side=LEFT)
  VoltValue = Label(innertopValuesframe, text = "-", width=3, fg = myConfig.FGC, bg=myConfig.BGC)
  VoltValue.pack(padx=1,side=LEFT)
  VLabel = Label(innertopValuesframe, text = " V   |  ", fg = myConfig.FGC, bg=myConfig.BGC)
  VLabel.pack(padx=1,side=LEFT)

  AmpLabel = Label(innertopValuesframe, text = "Cur ", fg = myConfig.FGC, bg=myConfig.BGC)
  AmpLabel.pack(padx=1,side=LEFT)
  AmpValue = Label(innertopValuesframe, text = "-", width=3, fg = myConfig.FGC, bg=myConfig.BGC)
  AmpValue.pack(padx=1,side=LEFT)
  ALabel = Label(innertopValuesframe, text = " A ", fg = myConfig.FGC, bg=myConfig.BGC)
  ALabel.pack(padx=1,side=LEFT)

  innertopFWframe = Frame(topFWframe,  bg=myConfig.BGC)
  innertopFWframe.pack(side=TOP)
  FWLabel = Label(innertopFWframe, text = " FW Rev ", fg = myConfig.FGC, bg=myConfig.BGC)
  FWLabel.pack(padx=1,side=LEFT)
  FWValue = Label(innertopFWframe, text = "-", fg = myConfig.FGC, bg=myConfig.BGC)
  FWValue.pack(padx=1,side=LEFT)

  SerNLabel = Label(innertopFWframe, text = "  |  Ser # ", fg = myConfig.FGC, bg=myConfig.BGC)
  SerNLabel.pack(padx=1,side=LEFT)
  SerNValue = Label(innertopFWframe, text = "-", fg = myConfig.FGC, bg=myConfig.BGC)
  SerNValue.pack(padx=1,side=LEFT)

# Fault display

  innerFaultframe = Frame(topFaultframe, bg=myConfig.BGC)
  innerFaultframe.pack(side=TOP)

  FaultLabel = Label(innerFaultframe, text = " Fault: ", fg = myConfig.FGC, bg=myConfig.BGC)
  FaultLabel.pack(padx=1,side=LEFT)
  FaultNo = Label(innerFaultframe, text = " 0 ", fg = myConfig.FGC, bg=myConfig.BGC)
  FaultNo.pack(padx=1,side=LEFT)
  FaultText = Label(innerFaultframe, text = " OK ", fg='green', bg=myConfig.BGC)
  FaultText.pack(padx=1,side=LEFT)
  FaultResetButton = Button(topFaultframe, text = 'Reset', command = lambda: myKPA500.ResetFault(), width = 4) 
  FaultResetButton.pack(padx=1, anchor='center')

# TRX PWR display

  innerTRXPWRframe = Frame(topTRXPWRframe, bg=myConfig.BGC)
  innerTRXPWRframe.pack(side=TOP)
  TRXPWRLabel = Label(innerTRXPWRframe, text = " TRX PWR: ", fg='green', bg=myConfig.BGC)
  TRXPWRLabel.pack(padx=1,side=LEFT)
  TRXPWRLevel = Label(innerTRXPWRframe, text = " 0 ", fg='green', bg=myConfig.BGC)
  TRXPWRLevel.pack(padx=1,side=LEFT)
  TRXPWRUnit = Label(innerTRXPWRframe, text = " W ", fg='green', bg=myConfig.BGC)
  TRXPWRUnit.pack(padx=1,side=LEFT)

  
# Fan control slider

  innertopFANCTRLframe = Frame(topFANCTRLframe, bg=myConfig.BGC)
  innertopFANCTRLframe.pack(side=TOP)
  FANLabel = Label(innertopFANCTRLframe, text = " Fan control ", fg = myConfig.FGC, bg=myConfig.BGC)
  FANLabel.pack(padx=1,side=LEFT)
  FANCTRLSlider = Scale(innertopFANCTRLframe, 
                        from_=0, to=6, showvalue = 0,
                        orient='horizontal', tickinterval=1, 
                        command = FANSpeed_Changed, 
                        length = 400,
                        width = 30, fg = myConfig.FGC, bg=myConfig.BGC)
  FANCTRLSlider.set(myConfig.FanSpeed)
  FANCTRLSlider.pack(padx=1,pady=2, side=LEFT)

# All the buttons

  OperButton = Button(bottomframe, text = 'Oper', command = lambda: myKPA500.setKP500toOPER(), width = 4, height = myConfig.ButtonHeight, bg='green') 
  OperButton.pack(padx=3, side=LEFT)

  StbyButton = Button(bottomframe, text = 'Stby', command = lambda: myKPA500.setKP500toSTBY(), width = 4, height = myConfig.ButtonHeight, bg='orange') 
  StbyButton.pack(padx=3, side=LEFT)

  OnButton = Button(bottomframe, text = 'On', command = lambda: myKPA500.switchON(), width = 4, height = myConfig.ButtonHeight, bg='green') 
  OnButton.pack(padx=3, side=LEFT)

  OffButton = Button(bottomframe, text = 'Off', command = lambda: myKPA500.switchOFF(), width = 4, height = myConfig.ButtonHeight ) 
  OffButton.pack(padx=3, side=LEFT)

  ConfigButton = Button(bottomframe, text = 'Settings', command = lambda: myConfig.openConfigWindow(root), width = 6, height = myConfig.ButtonHeight ) 
  ConfigButton.pack(padx=3, side=LEFT)
  
  ExitButton = Button(bottomframe, text = 'Exit', command = quit, width = 5, height = myConfig.ButtonHeight) 
  ExitButton.pack(padx=3, side=LEFT)

  DefaultBtnColor = ExitButton.cget("background")
  
  root.title("KPA500 Remote V " + myConfig.version + " © DM5EA")

# Loop until event is sent - frist thread - handle band changes and OperState changes

  def run_in_thread1(event):

    while not event.is_set():
      
      tempLock = threading.Lock()           # This locking is essential. It otherwise may happen, that we switch
      tempLock.acquire()                    # to the PWR stored as the initial PWR (STBY state)

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
 
# Now read the operating state

      if myKPA500.KPA500_ready:
        Sresp = myKPA500.getValue(myKPA500.OSCMD)
        if Sresp[3:4] == '1':
          myKPA500.OperStat=True
        else:
          myKPA500.OperStat=False

      tempLock.release()

# Redo until here (sometime)

      time.sleep(100/1000)

# Loop until event is sent - second thread - read PWR for bar

  def run_in_thread2(event):
    
    cnt = 0
    ioldpwr = 0
    while not event.is_set():

# Read and display the current putput power and SWR

      Sresp = myKPA500.getValue(myKPA500.PwrCMD)
      if Sresp[1:3] == 'WS' and Sresp[3:6] != ';':    # Second part checks, if the PA is really on
          myKPA500.KPA500_ready=True
          pwr = Sresp[3:6]
          try:
            ipwr = int(pwr)
          except:
            pass
          x1 = min(ipwr, 500) * 0.736
          PwrCanvas.coords(PwrGreenRect, 0, 0, x1, myConfig.BarHeight)
          if ipwr > 500:
            x1 = 368 + (min(ipwr,650)-500) * 0.307
            PwrCanvas.coords(PwrYellowRect, 368, 0, x1, myConfig.BarHeight)
          else:
            PwrCanvas.coords(PwrYellowRect, 368, 0, 368, myConfig.BarHeight)
          if ipwr > 650:
            x1 = 414 + (ipwr-650) * 0.307
            PwrCanvas.coords(PwrRedRect, 414, 0, x1, myConfig.BarHeight)
          else:
            PwrCanvas.coords(PwrRedRect, 414, 0, 414, myConfig.BarHeight)
          if ipwr > ioldpwr:
            PEPLabel.configure(text = ' ' + pwr + ' W')
            ioldpwr = ipwr
            cnt = 0
          else:
            cnt += 1
            if cnt > 50:
              PEPLabel.configure(text = ' ' + pwr + ' W')
              cnt = 0

          swr = Sresp[7:10]
          try:
            iswr = int(swr)
          except:
            pass
          x1 = min(iswr-10, 5) * 16
          SwrCanvas.coords(SwrGreenRect, 0, 0, x1, myConfig.BarHeight)
          if iswr > 15:
            x1 = 80 + (min(iswr,20)-15) * 8
            SwrCanvas.coords(SwrYellowRect, 80, 0, x1, myConfig.BarHeight)
          else:
            SwrCanvas.coords(SwrYellowRect, 80, 0, 80, myConfig.BarHeight)
          if iswr > 20:
            x1 = 120 + (iswr-20) * 2.67
            SwrCanvas.coords(SwrRedRect, 120, 0, x1, myConfig.BarHeight)
          else:
            SwrCanvas.coords(SwrRedRect, 120, 0, 120, myConfig.BarHeight)

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
          SerNValue.configure(text = SerN + ' ')

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
  
