from sardana.macroserver.macro import Macro
import PyTango

class monosync(Macro):
    """ synchronize the mono motors with the readings of the encoders by
       setting(DefinePosition) the motor registers """

    def run(self):
        Energy = PyTango.DeviceProxy("Energy")
        Energy_enc = PyTango.DeviceProxy("Energy_enc")
        Cff_enc = PyTango.DeviceProxy("Cff_enc")
        m3_pitch = PyTango.DeviceProxy("m3_pitch")
        gr_pitch = PyTango.DeviceProxy("gr_pitch")
 
        calcval = Energy.calcallphysical( [Energy_enc.value,Cff_enc.value])
 
        self.output("setting m3_pitch to %s" % calcval[0] )
        self.output("setting gr_pitch to %s" % calcval[1] )
        m3_pitch.DefinePosition(calcval[0])
        gr_pitch.DefinePosition(calcval[1])

