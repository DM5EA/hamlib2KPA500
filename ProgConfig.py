import json
import os.path
from sys import platform
from tkinter import *

# Class to handle all configuration parameters 

# Important: The order of key value pairs in PWRperBand array must match the order 
#            of the scale widgets in the bandPWRBox array

class ProgConfig:
  def __init__(self):
    self.HAMLIBRIG = 2
    self.HAMLIBCONN = '192.168.43.148:4533'
    self.COMPORT = '/dev/ttyUSB0'
    self.FanSpeed = 0
    self.ConfigWindow = None
    self.ButtonHeight = 3
    self.BarHeight = 40
    self.FGC = "White"
    self.BGC = "Gray10"
    self.entryBGC = "azure"

# Define input power per band

    self.PWRperBand = {'160 m ': 25,
                       '80 m ': 30, 
                       '40 m ': 30, 
                       '30 m ': 19, 
                       '20 m ': 35, 
                       '17 m ': 34, 
                       '15 m ': 34, 
                       '12 m ': 33, 
                       '10 m ': 33, 
                       '6 m ': 31}  
    
    self.confFileName = 'kpa500_remote_config.json'
    
    self.bandPWRBox = []
    self.bandWattLabel = []
    
    self.hamlibContext = None
    self.KPA500Context = None
    
  def __str__(self):
    return f"ProgConfig"

# Read the config from file (confFileName is a variable of this class)

  def readConfig(self):
    checkFile = os.path.exists(self.confFileName)

    if checkFile:
      with open(self.confFileName, 'r') as file:
        ConfigData = file.read()
      
      ReadConfig = json.loads(ConfigData)
      
      if 'hamlibRig' in ReadConfig:
        self.HAMLIBRIG=ReadConfig['hamlibRig']
      if 'hamlibConn' in ReadConfig:
        self.HAMLIBCONN = ReadConfig['hamlibConn']
      if 'KPA500ComPort' in ReadConfig:
        self.COMPORT = ReadConfig['KPA500ComPort']
      if 'FanSpeed' in ReadConfig:
        self.FanSpeed = ReadConfig['FanSpeed']
      if 'PWRperBand' in ReadConfig:
        self.PWRperBand = ReadConfig['PWRperBand']

# Write config to file (confFileName is a variable of this class)
    
  def writeConfig(self):
    ConfigJSON = {'PWRperBand': self.PWRperBand,
                  'hamlibRig': self.HAMLIBRIG,
                  'hamlibConn': self.HAMLIBCONN,
                  'KPA500ComPort': self.COMPORT,
                  'FanSpeed': self.FanSpeed}
                
    json_object = json.dumps(ConfigJSON, indent=3)
    
    with open(self.confFileName, "w") as outfile:
      outfile.write(json_object) 

# Build the config windows

  def openConfigWindow(self,rootWindow):

# V0.2.4 - Fullscreen one window

    if self.ConfigWindow == None:
    
#      self.ConfigWindow = Toplevel()
#      self.ConfigWindow.title("Settings")
#      self.ConfigWindow.config(width=700, height=450)
#      self.ConfigWindow.resizable(False, False)
#      self.ConfigWindow.minsize(700,450)
#      toplevel_offsetx, toplevel_offsety = rootWindow.winfo_x(), rootWindow.winfo_y() + rootWindow.winfo_height()
#      padx = 0
#      pady = 30
#      self.ConfigWindow.geometry(f"+{toplevel_offsetx + padx}+{toplevel_offsety + pady}")

# Use a frame inside the root window to be able to mix "pack" with "grid"
# 1st frame

      self.ConfigWindow=Frame(rootWindow, bg=self.BGC, highlightbackground="royalblue2", highlightthickness=2)
      
      Label00 = Label(self.ConfigWindow, text = " TRX power per band ", highlightbackground="orange", highlightthickness=2, fg=self.FGC, bg=self.BGC)
      Label00.grid(row=0, column=0, columnspan=3, padx=1, pady=3)

      Label10 = Label(self.ConfigWindow, text = "Band", fg=self.FGC, bg=self.BGC)
      Label10.grid(row=1, column=0, columnspan=1, padx=18, pady=1, sticky=W)
    
      Label11 = Label(self.ConfigWindow, text = "Power", fg=self.FGC, bg=self.BGC)
      Label11.grid(row=1, column=1, columnspan=2, padx=18, pady=1, sticky=W)
    
      i = 0
      bandArrLabel = []
      self.bandPWRBox = []
      self.bandWattLabel = []

      for key, value in self.PWRperBand.items():
        bandArrLabel.append(Label(self.ConfigWindow, text = key, fg=self.FGC, bg=self.BGC))
        bandArrLabel[i].grid(row=i+2, column=0, columnspan=1, padx=18, pady=1, sticky=W)
        self.bandPWRBox.append(Scale(self.ConfigWindow, from_=10, to=40, 
                             orient='horizontal', tickinterval=0, 
                             length = 400, width = 30, showvalue = 0, command = self.sliderMoved, fg=self.FGC, bg=self.BGC))
        self.bandPWRBox[i].set(value)
        self.bandPWRBox[i].grid(row=i+2, column=1, columnspan=1, padx=18, pady=1, sticky=W)
        self.bandWattLabel.append(Label(self.ConfigWindow, text = str(value-1) + ' W', fg=self.FGC, bg=self.BGC))
        self.bandWattLabel[i].grid(row=i+2, column=2, columnspan=1, padx=18, pady=1, sticky=W)
        i+=1

# 2nd Frame

      self.ConfigWindow2=Frame(rootWindow, bg=self.BGC, highlightbackground="royalblue2", highlightthickness=2)
      self.ConfigWindow.pack(side=TOP,fill=X, padx=4)
      self.ConfigWindow2.pack(side=TOP,fill=X, pady=(10,1), padx=4)

      Label03 = Label(self.ConfigWindow2, text = " Parameters ", highlightbackground="orange", highlightthickness=2, fg=self.FGC, bg=self.BGC)
      Label03.grid(row=0, column=0, columnspan=2, padx=1, pady=5)
    
      Label13 = Label(self.ConfigWindow2, text = "Key", fg=self.FGC, bg=self.BGC)
      Label13.grid(row=1, column=0, columnspan=1, padx=18, pady=1, sticky=W)
    
      Label14 = Label(self.ConfigWindow2, text = "Parameter", fg=self.FGC, bg=self.BGC)
      Label14.grid(row=1, column=1, columnspan=1, padx=18, pady=1, sticky=W)

# Default font size

      import tkinter.font as tkFont
      def_font = tkFont.nametofont("TkTextFont")
      def_font.config(size=22)
     
      Label23 = Label(self.ConfigWindow2, text = "hamlib Rig ID", fg=self.FGC, bg=self.BGC)
      Label23.grid(row=2, column=0, columnspan=1, padx=18, pady=1, sticky=W)
      hamlibHostBox = Entry(self.ConfigWindow2, width=17, bg=self.entryBGC)
      hamlibHostBox.insert(0, self.HAMLIBRIG)
      hamlibHostBox.grid(row=2, column=1, columnspan=1, padx=18, pady=1, sticky=W)
    
      Label33 = Label(self.ConfigWindow2, text = "hamlib Connection", fg=self.FGC, bg=self.BGC)
      Label33.grid(row=3, column=0, columnspan=1, padx=18, pady=1, sticky=W)
      hamlibPortBox = Entry(self.ConfigWindow2, width=17, bg=self.entryBGC)
      hamlibPortBox.insert(0, self.HAMLIBCONN)
      hamlibPortBox.grid(row=3, column=1, columnspan=1, padx=18, pady=1, sticky=W)
    
      Label43 = Label(self.ConfigWindow2, text = "KPA500 COM Port", fg=self.FGC, bg=self.BGC)
      Label43.grid(row=4, column=0, columnspan=1, padx=18, pady=1, sticky=W)
      comPortBox = Entry(self.ConfigWindow2, width=17, bg=self.entryBGC)
      comPortBox.insert(0, self.COMPORT)
      comPortBox.grid(row=4, column=1, columnspan=1, padx=18, pady=1, sticky=W)
    
      CloseButton = Button(
        self.ConfigWindow2,
        text="Hide settings",
        command=self.closeWindow,
        height = self.ButtonHeight
      )
      CloseButton.grid(row=6, column=1, columnspan=1, padx=(1,18), pady=5, sticky=E)
      
# Handle the default close window button 

#      self.ConfigWindow.protocol("WM_DELETE_WINDOW", self.closeWindow)

# Close window

  def closeWindow(self):
    self.ConfigWindow.destroy()
    self.ConfigWindow = None
    self.ConfigWindow2.destroy()
    self.ConfigWindow2 = None
  
# Store the settings - limited currently to the power per band

  def sliderMoved(self, val):
    i = 0

    for key, value in self.PWRperBand.items():
      self.PWRperBand[key] = self.bandPWRBox[i].get()
      self.bandWattLabel[i].configure(text = str(self.bandPWRBox[i].get()-1) + ' W')

# Set the PWR for the TRX on the band it is currently

      if key == self.hamlibContext.getActBand() and self.KPA500Context.OperStat:
        self.hamlibContext.setTXPWR(self.PWRperBand[key])
        
      i+=1
  
  def saveSettings(self):
  
    i = 0
    for key, value in self.PWRperBand.items():
      self.PWRperBand[key] = self.bandPWRBox[i].get()
      i+=1
    
  def setHamlibContext(self, TRXconn):
    self.hamlibContext = TRXconn
    
  def setKPA500Context(self, KPA500conn):
    self.KPA500Context = KPA500conn
    
  def setPWRSliderForBand(self, band, pwr):
    i = 0
    for key, value in self.PWRperBand.items():
      if band == key:
        self.PWRperBand[key] = pwr
        if self.ConfigWindow != None:
          self.bandPWRBox[i].set(pwr)
          self.bandWattLabel[i].configure(text = str(self.bandPWRBox[i].get()-1) + ' W')

      i+=1
