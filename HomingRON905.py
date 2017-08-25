
import PyTango

#from macro import *
import math
import time
#from pool import PoolUtil
from sardana.macroserver.macro import *

class getRonHome(Macro):
    """Macro to get the encoder counts where the reference mark has been found """

    param_def = [
        ['motor', Type.Motor, None, 'Motor to move'],
        ['direction', Type.Integer, None, 'Motor direction. Possible values: -1 (going to the negative limit)| 1 (going to positive limit)'],
    ]

    def prepare(self, motor, direction):
        self.motor = self.findObjs(motor.getName(), type_class=Type.Motor)[0]
        if motor.getName() == 'gr_pitch':
            self.card = 0
        elif motor.getName() == 'm3_pitch':
            self.card = 2

    def run(self, motor, direction):
        incr = 1 * direction
        self.ik220 = PyTango.DeviceProxy('BL09/CT/IK220')
        self.startHomingCards(self.card)

        while(self.refActiveCards(self.card)):
            self.point_pos = self.motor['Position'].value
            self.point_pos = self.point_pos + incr
            self.motor.move(self.point_pos)
        self.checkStatus(self.card)

    def resetCards(self, card):
        self.ik220.ResetCtrRef([card, 0])
        self.ik220.ResetCtrRef([card, 1])
        self.ik220.ResetCtrRef([card+1, 0])
        self.ik220.ResetCtrRef([card+1, 1])

    def startHomingCards(self, card):
        self.ik220.StartHoming([card, 0])
        self.ik220.StartHoming([card, 1])
        self.ik220.StartHoming([card+1, 0])
        self.ik220.StartHoming([card+1, 1])

    def refActiveCards(self, card):
        i1 = self.ik220.RefActive([card, 0])
        i2 = self.ik220.RefActive([card, 1])
        i3 = self.ik220.RefActive([card+1, 0])
        i4 = self.ik220.RefActive([card+1, 1])
        itotal = i1 or i2 or i3 or i4
        return itotal

    def checkStatus(self,card):
        #card = 2*card
        self.info("Status in axis1: " + self.ik220.RefStatus([card,0]))
        self.info("Status in axis2: " + self.ik220.RefStatus([card,1]))
        self.info("Status in axis3: " + self.ik220.RefStatus([card+1,0]))
        self.info("Status in axis4: " + self.ik220.RefStatus([card+1,1]))

class setRonZeroOnRef(Macro):
    """Macro to set to zero the encoder counts when passing through the ref. mark """

    param_def = [
        ['motor', Type.Motor, None, 'Motor to move'],

    ]

    def prepare(self, motor):
        self.output("Macro: setRonZeroOnRef -- prepare")
        #self.motor = self.findObjs(motor.getName(), type_class=Type.Motor)[0]
        self.motor = motor
        if motor.getName() == 'gr_pitch':
            self.card = 0
            self.ignore_i3 = False
            self.ignore_i4 = True
        elif motor.getName() == 'm3_pitch':
            self.card = 2
            self.ignore_i3 = True
            self.ignore_i4 = True

    def run(self, motor):
        self.output("Macro: setRonZeroOnRef -- run")
        incr = 1
        self.ik220 = PyTango.DeviceProxy('BL09/CT/IK220')
        self.resetCards(self.card)
        self.startHomingCards(self.card)

        while(self.refActiveCards(self.card)):
            #self.point_pos = self.motor['Position'].value
            self.point_pos = self.motor.getPosition()
            self.output("      ... point_pos = %f" %self.point_pos)
            self.point_pos = self.point_pos + incr
            time.sleep(0.5)
            self.motor.move(self.point_pos)

        self.output("Macro: setRonZeroOnRef -- END")

    def resetCards(self, card):
        self.ik220.ResetCtrRef([self.card, 0])
        self.ik220.ResetCtrRef([self.card, 1])
        self.ik220.ResetCtrRef([self.card+1, 0])
        self.ik220.ResetCtrRef([self.card+1, 1])

    def startHomingCards(self, card):
        self.ik220.StartHoming([self.card, 0])
        self.ik220.StartHoming([self.card, 1])
        self.ik220.StartHoming([self.card+1, 0])
        self.ik220.StartHoming([self.card+1, 1])

    def refActiveCards(self, card):
        i1 = self.ik220.RefActive([self.card, 0])
        i2 = self.ik220.RefActive([self.card, 1])
        i3 = self.ik220.RefActive([self.card+1, 0])
        i4 = self.ik220.RefActive([self.card+1, 1])
        self.output("      While RefActive: %s, %s, %s, %s" %(i1, i2, i3, i4))
        if self.ignore_i3 and self.ignore_i4:
            itotal = i1 or i2
        elif self.ignore_i4:
            itotal = i1 or i2 or i3
        else:
            itotal = i1 or i2 or i3 or i4

        return itotal

class HomingRON905(Macro):
    """Macro to do the homing procedure using the RON905 encoder"""
    
    param_def = [
        ['motor',   Type.Motor,  None,   'Motor to move'],
        ['card',    Type.Integer,   None,   'Card of the IK220' ],
        ['axis',   Type.Integer,   None,   'Axis of the card'],
        ['direction',   Type.Integer,   None,   'Direction to start the homing proc. [1 positive | -1 negative]'],
    ]
    
    def prepare(self, motor, card, axis, direction):
        
        #self.motor = motor.getAxis()
        self.motor = self.findObjs(motor.getName(), type_class=Type.Motor)[0]
        self.card = card
        self.axis = axis
        self.direction = direction
        self.limits = []
    
    def run(self, motor, card, axis, direction):
        self.Ik220_dp = PyTango.DeviceProxy("BL09/CT/IK220")
        
        #self.motor = self.findObjs("gr_pitch", type_class=Type.Motor)[0]
        #self.card = 0
        #self.axis = 0
        self.point_pos = 0
        self.incr = self.direction * 1
        
        #vel = self.motor.getAttrObj("Velocity")
        #vel.write(4000)
        #self.motor['Velocity'] = 4000

        self.limits = self.motor["Limit_switches"].value
        
        #EncAxis = self.motor.getAttrObj("EncAxis")
        #self.point_pos = EncAxis.read()
        self.point_pos = self.motor['Position'].value
        self.info(self.point_pos)
        #self.point_pos = self.point_pos + 50000
        
        
        self.output("============START HOMING============")
        ################################################################################
        while(math.fabs(self.incr) >= 0.1):
	    self.Ik220_dp.StartHoming([self.card, self.axis])
            
            self.Move_to_Ref()
            self.point_pos = self.point_pos + self.incr
            self.motor.move([self.point_pos ]) #for backlash correction?
            self.incr = (-1) * self.incr
            self.info("~~~~Change Direction~~~~~")
            self.incr = self.incr / 2.0
            self.info("New increment: %f", self.incr)
            
            self.angle = self.Ik220_dp.read_attribute("Angles").value
            self.angleMean = self.Ik220_dp.read_attribute("AnglesMean").value
            self.info("Angles: " + str(self.angle[0]) + " , " + str(self.angle[1]) + " , " + str(self.angle[2]) + " , " + str(self.angle[3]) + "\n AnglesMean: " + str(self.angleMean[0]))
            
        self.angle = self.Ik220_dp.read_attribute("Angles").value
        self.angleMean = self.Ik220_dp.read_attribute("AnglesMean").value
        #pos_final = EncAxis.read()
        
        self.output("============END HOMING============")
        self.output("Angles: " + str(self.angle[0]) + " , " + str(self.angle[1]) + " , " + str(self.angle[2]) + " , " + str(self.angle[3]) + "\n AnglesMean: " + str(self.angleMean[0]))
        #self.info("Position: " + str(pos_final))
        self.output("============END HOMING============")
        ################################################################################
    
    def Move_to_Ref(self):
        
        while(self.Ik220_dp.RefActive([self.card, self.axis])):
            self.info("-----Looking home signal-----")
            
            self.point_init = self.point_pos
            self.point_pos = self.point_pos + self.incr
            self.info("from: %f to: %f", self.point_init, self.point_pos)
            #self.motor.waitMove()
            #self.motor['Position'] = self.point_pos
            self.motor.move(self.point_pos)
            #self.motor.waitMove()
            self.info("Active: "+ str( self.Ik220_dp.RefActive([self.card, self.axis])))
            self.info("Status: " + self.Ik220_dp.RefStatus([self.card, self.axis]))
            #time.sleep(4)#con 0.5 sigue moviendose
            
            
            #limits = self.limits.read()
            limits = self.motor["Limit_switches"].value
            self.info("Limits: " + str(limits[1])  + "," + str(limits[2]) )
            self.info("=========================")
            
            if((limits[1] == True and self.incr > 0) or (limits[2] == True and self.incr < 0)):
                self.info("~~~~Change Direction~~~~~")
                #self.motor.waitMove()
                self.incr = (-1) * self.incr
                self.info("~~~~~~~~~~~~~~~~~~~~~~~~~")
        
    
