import time
import taurus
from sardana.macroserver.macro import *

MICRO        = 1.0E-6
MILI         = 1.0E-3

StrES        = 'bl09/di/locum4-02' 
StrM1PIT     = 'm1_z' 
StrM1Z       = 'm1_pitch' 

pM1          = 16.000
qM1          = 5.333

M1_Z_INI     = 0.22789415000007129  
M1_PITCH_INI = -0.040015545830278561
 

"""
MACRO THAT STEERS THE BEAM AT THE ENTRANCE SLIT
"""
@macro([["dZES", Type.Float, None, "displacement in microns"]])
def opzes(self,dZES):

    #self.output("you say %f" % dZES)
    dZES_SI = dZES*MICRO
    
    dZM1   = dZES_SI*(pM1/(pM1+qM1)) #
    dPITM1 = dZES_SI/(pM1+qM1)    # 

    #self.output( "dZ = %f dP = %f" % ((dZM1/MILI),dPITM1/MILI))

    self.execMacro('mvr m1_z %f' % (dZM1/MILI))
    self.execMacro('mvr m1_pitch %f' % (dPITM1/MILI))


@macro([["dTheta", Type.Float, None, "relative change in Incidence angle in microrad"]])
def opfoces(self,dTheta):

    #self.output("you say %f" % dZES)
    dTheta_SI = dTheta*MICRO
    
    dZM1   = -2*pM1*qM1/(pM1+qM1)*dTheta_SI #
    dPITM1 = (pM1-qM1)/(pM1+qM1)*dTheta_SI    # 

    self.output( "dZ = %f dP = %f" % ((dZM1/MILI),dPITM1/MILI))

    self.execMacro('mvr m1_z %f' % (dZM1/MILI))
    self.execMacro('mvr m1_pitch %f' % (dPITM1/MILI))

"""
MACRO THAT RETURNS THE BEAM POSITION AND FOCUS 
"""
@macro()
def wmesbeam(self):
    Z = taurus.Device('m1_z').Position
    P = taurus.Device('m1_pitch').Position
    
    Z = Z*MILI
    P = P*MILI

    Theta = P - Z/pM1
    zI    = 2.0*qM1*P + (1.0 - qM1/pM1)*Z
 
    self.output("zI = %f um   Theta = %f mrad "% (zI/MICRO,Theta/MILI))

@macro()
def sayhello(self):
    self.output("hello")
    self.output("hello")


@macro()
def wm_m1(self):
        
    posM1_z = taurus.Device('m1_z').Position
    posM1_pitch = taurus.Device('m1_pitch').Position

    posM1_zl = taurus.Device('m1_zl').Position
    posM1_zr = taurus.Device('m1_zr').Position
    posM1_zc = taurus.Device('m1_zc').Position

    encM1_zl = taurus.Device('m1_zl').encencin
    encM1_zr = taurus.Device('m1_zr').encencin
    encM1_zc = taurus.Device('m1_zc').encencin


    string1 = "%f %f %f %f %f %f %f %f" % (posM1_z, posM1_pitch, posM1_zl, posM1_zr, posM1_zc,encM1_zl, encM1_zr, encM1_zc)
    self.output(string1)
    

@macro()
def opreset(self):
    self.output("Reseting M1 position")
    self.execMacro('mv m1_z %f' % M1_Z_INI)
    self.execMacro('mv m1_pitch %f' % M1_PITCH_INI)


@macro()
def opCalibES(self):
    nDim = 40
    self.execMacro('opzes -20')
    
    DevES = taurus.Device('bl09/di/locum4-02')

    for it in range(nDim):
        self.execMacro('opzes +5')
    
        posM1_z = taurus.Device('m1_z').Position
        posM1_pitch = taurus.Device('m1_pitch').Position
        
        time.sleep(1)
        CurrentESUp = 0
        CurrentESDo = 0
        for kt in range(10):
            CurrentESUp  += DevES.i3
            CurrentESDo  += DevES.i4
        
        CurrentESUp = 0.1*CurrentESUp;
        CurrentESDo = 0.1*CurrentESDo;

        CurrentTotal = CurrentESUp + CurrentESDo
        CurrentDiff  = (CurrentESUp - CurrentESDo)/CurrentTotal
        self.output("%f %f %f %f %f %f" % (posM1_z/MICRO, posM1_pitch/MICRO, CurrentESUp/MICRO,CurrentESDo/MICRO,CurrentTotal/MICRO,CurrentDiff))

@macro()
def opSpotES(self):
    nDim = 40
    
    DevES = taurus.Device('bl09/di/locum4-02')
    self.execMacro('umv es 30')
    
    for it in range(100):
        SizeES = 30.0 + it*5.0
        self.execMacro('mvr es 5')
    
        time.sleep(1)
        CurrentESUp = 0
        CurrentESDo = 0
        for kt in range(10):
            CurrentESUp  += DevES.i3
            CurrentESDo  += DevES.i4
        
        CurrentESUp = 0.1*CurrentESUp;
        CurrentESDo = 0.1*CurrentESDo;

        CurrentTotal = CurrentESUp + CurrentESDo
        CurrentDiff  = (CurrentESUp - CurrentESDo)/CurrentTotal
        self.output("%f %f %f %f %f" % (SizeES, CurrentESUp/MICRO,CurrentESDo/MICRO,CurrentTotal/MICRO,CurrentDiff))


@macro()
def opScanSteer(self):
    self.execMacro('senv ActiveMntGrp es_mg')
    self.execMacro('senv ScanFile 20120511_ESTest01.dat')

    for it in range(15):
        self.execMacro('opzes +5')
        self.execMacro('ascan es 30 530 100 1.0')

@macro()
def opScanFocus(self):
    self.execMacro('senv ActiveMntGrp es_mg')
    #self.execMacro('senv ScanFile 20130703_ESTest02.dat')
    
    for it in range(10):
        self.execMacro('opfoces 10')
        self.execMacro('ascan es 100 400 100 1.0')

