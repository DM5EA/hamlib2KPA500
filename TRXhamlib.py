import socket
import sys
import Hamlib

class TRXhamlib:
  def __init__(self,connstring,rigmodel):
    self.CONNSTRING = connstring
    self.RIGMODEL = rigmodel
    self.myHamlib = None

    self.initialPWR = '1'
    self.actualPWR = 0
    
    self.oldBand = ''
    self.actBand = ''
    self.bandChange = True
    
    Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_NONE)

  def __str__(self):
    return f"TRXhamlib"
    
  def openConn(self):
  
    self.myHamlib = Hamlib.Rig(self.RIGMODEL)
    self.myHamlib.set_conf("rig_pathname", self.CONNSTRING)
    self.myHamlib.set_conf("rts_state", "off")
    self.myHamlib.set_conf("dtr_state", "off")
    self.myHamlib.set_conf("retry", "5")

    try:
      self.myHamlib.open()
    except:
      self.myHamlib = None

    if self.myHamlib is None:
      print('could not open socket')
      sys.exit(1)   
 
  def closeConn(self):
    self.myHamlib.close()
    print("TRX closed")
        
  def getInitialPWR(self):
    self.initialPWR = self.myHamlib.get_level_f(Hamlib.RIG_LEVEL_RFPOWER)

  def restoreInitialPWR(self):
    self.myHamlib.set_level(Hamlib.RIG_LEVEL_RFPOWER,  self.initialPWR)
    
  def getTXPWR(self):
    resp = self.myHamlib.get_level_f(Hamlib.RIG_LEVEL_RFPOWER)
    fPWR = 0
    try:
      fPWR = int(float(resp) * 100.)+1
    except:
      pass
    self.actualPWR = fPWR
    return self.actualPWR

  def setTXPWR(self,pwr):
    npwr = 0.
    try:
      npwr = float(pwr) / 100.
    except:
      pass
    self.myHamlib.set_level(Hamlib.RIG_LEVEL_RFPOWER, npwr)
    pass  
  
  def getActBand(self):
    qrg = self.myHamlib.get_freq()
    iqrg = int(qrg)
    band = ''
    if iqrg >= 1810000 and iqrg <= 2000000:
      band = '160 m '
    elif iqrg >= 3500000 and iqrg <= 3800000:
      band = '80 m '
    elif iqrg >= 7000000 and iqrg <= 7200000:
      band = '40 m '
    elif iqrg >= 10100000 and iqrg <= 10140000:
      band = '30 m '
    elif iqrg >= 14000000 and iqrg <= 14350000:
      band = '20 m '
    elif iqrg >= 18068000 and iqrg <= 18168000:
      band = '17 m '
    elif iqrg >= 21000000 and iqrg <= 21450000:
      band = '15 m '
    elif iqrg >= 24890000 and iqrg <= 24990000:
      band = '12 m '
    elif iqrg >= 28000000 and iqrg <= 29700000:
      band = '10 m '
    elif iqrg >= 50000000 and iqrg <= 52000000:
      band = '6 m '
    if band != self.oldBand:
      self.bandChange = True
    self.actBand = band
    return self.actBand
  
  def bandChanged(self):
    return self.bandChange
    
  def ackBandChange(self):
    self.oldBand = self.actBand
    self.bandChange = False
    
  
  

