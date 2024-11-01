import json
import os.path
from sys import platform
from tkinter import *

# Class to handle all configuration parameters 

# Important: The order of key value pairs in PWRperBand must much the order 
#            of the scale widgets in the bandPWRBox

class ProgConfig:
  def __init__(self):
    self.HAMLIBRIG = 2
    self.HAMLIBCONN = '192.168.43.148:4533'
    self.COMPORT = '/dev/ttyUSB0'
    self.FanSpeed = 0
    self.ConfigWindow = None

# Define input power per band

    self.PWRperBand = {'80 m ': 30, 
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
    self.windowOpen = False

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

    self.ConfigWindow = Toplevel()
    self.ConfigWindow.title("Settings")
    self.ConfigWindow.config(width=550, height=250)
    self.ConfigWindow.minsize(550,250)
    toplevel_offsetx, toplevel_offsety = rootWindow.winfo_x(), rootWindow.winfo_y() + rootWindow.winfo_height()
    padx = 0
    pady = 50
    self.ConfigWindow.geometry(f"+{toplevel_offsetx + padx}+{toplevel_offsety + pady}")
    
    Label00 = Label(self.ConfigWindow, text = "TRX power per band", highlightbackground="orange", highlightthickness=1)
    Label00.grid(row=0, column=0, columnspan=3, padx=1, pady=3)

    Label03 = Label(self.ConfigWindow, text = "Parameters", highlightbackground="orange", highlightthickness=1)
    Label03.grid(row=0, column=3, columnspan=2, padx=1, pady=3)
    
    Label10 = Label(self.ConfigWindow, text = "Band")
    Label10.grid(row=1, column=0, columnspan=1, padx=8, pady=1, sticky=W)
    
    Label11 = Label(self.ConfigWindow, text = "Power")
    Label11.grid(row=1, column=1, columnspan=2, padx=8, pady=1, sticky=W)
    
    Label13 = Label(self.ConfigWindow, text = "Key")
    Label13.grid(row=1, column=3, columnspan=1, padx=6, pady=1, sticky=W)
    
    Label14 = Label(self.ConfigWindow, text = "Parameter")
    Label14.grid(row=1, column=4, columnspan=1, padx=6, pady=1, sticky=W)
    
    i = 0
    bandArrLabel = []
    self.bandPWRBox = []
    self.bandWattLabel = []

    for key, value in self.PWRperBand.items():
      bandArrLabel.append(Label(self.ConfigWindow, text = key))
      bandArrLabel[i].grid(row=i+2, column=0, columnspan=1, padx=8, pady=1, sticky=W)
      self.bandPWRBox.append(Scale(self.ConfigWindow, from_=10, to=40, 
                             orient='horizontal', tickinterval=0, 
                             length = 80, showvalue = 0, command = self.sliderMoved))
      self.bandPWRBox[i].set(value)
      self.bandPWRBox[i].grid(row=i+2, column=1, columnspan=1, padx=8, pady=1, sticky=W)
      self.bandWattLabel.append(Label(self.ConfigWindow, text = str(value) + ' W'))
      self.bandWattLabel[i].grid(row=i+2, column=2, columnspan=1, padx=8, pady=1, sticky=W)
      i+=1

    Label23 = Label(self.ConfigWindow, text = "hamlib Rig ID")
    Label23.grid(row=2, column=3, columnspan=1, padx=6, pady=1, sticky=W)
    hamlibHostBox = Entry(self.ConfigWindow, width=17)
    hamlibHostBox.insert(0, self.HAMLIBRIG)
    hamlibHostBox.grid(row=2, column=4, columnspan=1, padx=6, pady=1, sticky=W)
    
    Label33 = Label(self.ConfigWindow, text = "hamlib Connection")
    Label33.grid(row=3, column=3, columnspan=1, padx=6, pady=1, sticky=W)
    hamlibPortBox = Entry(self.ConfigWindow, width=17)
    hamlibPortBox.insert(0, self.HAMLIBCONN)
    hamlibPortBox.grid(row=3, column=4, columnspan=1, padx=6, pady=1, sticky=W)
    
    Label43 = Label(self.ConfigWindow, text = "KPA500 COM port")
    Label43.grid(row=4, column=3, columnspan=1, padx=6, pady=1, sticky=W)
    comPortBox = Entry(self.ConfigWindow, width=17)
    comPortBox.insert(0, self.COMPORT)
    comPortBox.grid(row=4, column=4, columnspan=1, padx=6, pady=1, sticky=W)
    
    CloseButton = Button(
      self.ConfigWindow,
      text="Close",
      command=self.closeWindow,
      width = 6
    )
    CloseButton.grid(row=12, column=4, columnspan=1, padx=1, pady=5)
    
    self.windowOpen = True

# Close window

  def closeWindow(self):
    self.windowOpen = False
    self.ConfigWindow.destroy()
  
# Store the settings - limited currently to the power per band

  def sliderMoved(self, val):
    i = 0

    for key, value in self.PWRperBand.items():
      self.PWRperBand[key] = self.bandPWRBox[i].get()
      self.bandWattLabel[i].configure(text = str(self.bandPWRBox[i].get()) + ' W')

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
        if self.windowOpen:
          self.bandPWRBox[i].set(pwr)
          self.bandWattLabel[i].configure(text = str(self.bandPWRBox[i].get()) + ' W')

      i+=1
