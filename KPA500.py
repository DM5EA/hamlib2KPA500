import serial
import time
import threading    # Needed for threat save locking the com port operations

# Deamon mode: This class is ready

class KPA500:
  def __init__(self):
    
# Fault list - as per elecraft documentation

    self.FaultArr = [
     'OK',                                                          # 0
     '',                                                            # 1
     'HI CURR - Excessive power amplifier current.',                # 2
     '',                                                            # 3
     'HI TEMP - Power amplifier temperature over limit.',           # 4
     '',                                                            # 5
     'PWRIN HI - Excessive driving power.',                         # 6
     '',                                                            # 7
     '60V HIGH - 60 volt supply over limit.',                       # 8
     'REFL HI - Excessive reflected power (high SWR).',             # 9
     '',                                                            # 10
     'PA DISS - Power amplifiers are dissipating excessive power.', # 11
     'POUT HI - Excessive power output.',                           # 12
     '60V FAIL - 60 volt supply failure.',                          # 13
     '270V ERR - 270 volt supply failure.',                         # 14
     'GAIN ERR - Excessive overall amplifier gain.'                 # 15
     ]

# Define the KPA500 commands

    self.OnCMD = 'P'            # Power on
    self.OffCMD = '^ON0;'       # Power off
    self.StbyCMD = '^OS0;'      # Go in Standby
    self.OperCMD = '^OS1;'      # Go in Operate state
    self.OSCMD = '^OS;'         # What is the current state?
    self.PwrCMD = '^WS;'        # Get the PWR and the SWR
    self.TempCMD = '^TM;'       # Get the temp of the finals
    self.VICMD = '^VI;'         # Get the voltage and the current
    self.FWCMD = '^RVM;'        # Get the FW release
    self.SerNCMD = '^SN;'       # Get the serial number of the unit
    self.FLCMD = '^FL;'         # Get the fault info
    self.FLresetCMD = '^FLC;'   # Reset fault
    self.FNCMD = '^FC'          # Get/Set minimum fan speed
    self.BNCMD = '^BN;'         # Get the current band
 
    self.KPA500_ready = False   # Shows, if the KPA500 is switched on
    self.OperStat = False       # Shows, if KPA500 is in Oper status
                                # Used to reduce the power of TRX
    self.OldOperStat = False
    
    self.COMPORT = ''
    self.COMSPEED = 38400
    self.COMTIMEOUT = 1
    self.ser = None
    
    self.oldBN = ''
    self.actBN = ''

# Use lock to make the access to the COM port thread save

    self.lock = threading.Lock()

  def __str__(self):
    return f"KPA500"
    
  def setComport(self,comport):
    self.COMPORT = comport
    
  def openSerialConn(self,comport):
    self.COMPORT = comport
    self.ser = serial.Serial(self.COMPORT, self.COMSPEED, timeout=self.COMTIMEOUT)
    self.ser.reset_input_buffer()
  
  def closeSerialConn(self):
    self.ser.close()
    print("KPA500 closed")
    
  def switchON(self):
    self.lock.acquire()
    self.ser.write(self.OnCMD.encode('utf-8'))
    self.lock.release()
    time.sleep(2)
    self.oldBN = ''
    self.actBN = ''
    
  def sendCMD(self,cmd):
    self.ser.write(cmd.encode('utf-8'))
    
  def getValue(self,cmd):
    self.lock.acquire()
    self.sendCMD(cmd)
    resp = self.ser.read_until(expected=b';')
    self.lock.release()
    return resp.decode()
    
  def setFanSpeed(self,speed):
    try:
      cmd = self.FNCMD + str(speed) + ';'
    except:
      pass
    self.lock.acquire()
    self.sendCMD(cmd)
    self.lock.release()
  
  def getFanSpeed(self):
    cmd = self.FNCMD  + ';'
    resp = self.getValue(cmd)
    return resp[3:5]
    
  def bandToCommand(self,band):
      BN = ''
      if band == '160 m ':
        BN = '^BN00;'
      elif band == '80 m ':
        BN = '^BN01;'
      elif band == '40 m ':
        BN = '^BN03;'
      elif band == '30 m ':
        BN = '^BN04;'
      elif band == '20 m ':
        BN = '^BN05;'
      elif band == '17 m ':
        BN = '^BN06;'
      elif band == '15 m ':
        BN = '^BN07;'
      elif band == '12 m ':
        BN = '^BN08;'
      elif band == '10 m ':
        BN = '^BN09;'
      elif band == '6 m ':
        BN = '^BN10;'
      self.actBN = BN
      return BN 

  def getBand(self):
      cmd = self.getValue(self.BNCMD)
      BN = ''
      if cmd == '^BN00;':
        BN = '160 m '
      elif cmd == '^BN01;':
        BN = '80 m '
      elif cmd == '^BN03;':
        BN = '40 m '
      elif cmd == '^BN04;':
        BN = '30 m '
      elif cmd == '^BN05;':
        BN = '20 m '
      elif cmd == '^BN06;':
        BN = '17 m '
      elif cmd == '^BN07;':
        BN = '15 m '
      elif cmd == '^BN08;':
        BN = '12 m '
      elif cmd == '^BN09;':
        BN = '10 m '
      elif cmd == '^BN10;':
        BN = '6 m '
      return BN 

  def ResetFault(self):
    self.sendCMD(self.FLresetCMD)
    
  
  