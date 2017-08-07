import os, sys, time, datetime, math
import PyTango

from sardana.macroserver.macro import *

class ipap_homing_axis(Macro):
    """Macro to do the homing procedure in more than one axis at the same time.
       Given a list of motors to do the home and the direction in which you want
       to move, this macro will move all the motors at the same time waiting to 
       recieve the home signal.
       The macro ends when the home signal is detected or any axis receive an alarm
    """

    param_def = [
        ['motor1', Type.Motor, None, 'Motor to perform the homing procedure.'],
        ['direction', Type.Integer, None, 'Direction in which you will look for the home signal <-1|1>']
    ]

    def prepare(self, motor1, direction):
        #Now it will be hardcoded but at some point it will be parameters
        self.pool = motor1.getPoolObj()
        self.ctrl_name = motor1.getControllerName()
        self.motor1_axis = motor1.getAxis()
        self.direction = direction
        self.home_pos_dict = {}
        self.info('Ready to perform the homing procedure in axis: %d' % self.motor1_axis)

    def run(self, motor1, direction):
        self.info('Starting the homing procedure')
        self.executeHoming(motor1, direction)

    def on_abort():
        self.info('Homing procedure aborted.')
        self.abort = True

    def executeHoming(self, motor1, direction):
        CMD_HOME_GROUP_STRICT = 'home group strict %d %d' % (self.motor1_axis, self.direction)
        CMD_HOME_STAT = '?homestat %d' % (self.motor1_axis)
        #CMD_HOME_POS = '?homepos %d %d' % (self.motor1_axis, self.motor2_axis) #only works if both motors have found the home
        CMD_HOME_POS_AXIS1 = '%d:?homepos' % self.motor1_axis
        #CMD_HOMEENC_ENCIN = '?homeenc encin %d %d' % (self.motor1_axis, self.motor2_axis) #only works if both motors have found the home
        CMD_HOMEENC_ENCIN_AXIS1 = '%d:?homeenc encin' % self.motor1_axis
        
        self.abort = False
        self.h1 = 0
        self.pool.SendToController([self.ctrl_name , CMD_HOME_GROUP_STRICT])
        home_detected = False

        while not home_detected or self.abort:
            ans = self.pool.SendToController([self.ctrl_name, CMD_HOME_STAT])
            home_stat = ans.split()
            
            if home_stat[1] == 'FOUND':
                ans = self.pool.SendToController([self.ctrl_name, CMD_HOME_POS_AXIS1])
                home_pos = int(ans.split()[1])
                ans = self.pool.SendToController([self.ctrl_name, CMD_HOMEENC_ENCIN_AXIS1])
                home_enc = int(ans.split()[1])
                self.home_pos_dict[self.motor1_axis] = (home_pos,home_enc)
                home_detected = True
                home_motor_pos = motor1.getPosition(force=True)
                if self.h1 == 0:
                    self.info('Home detected in axis: %d' % self.motor1_axis)
                    self.info('    HomePos: %d' % home_pos)
                    self.info('    HomeEncEncin: %d' % home_enc)
                    self.info('    HomePos (mm): %f' % home_motor_pos)
                self.h1 += 1
        
        time.sleep(0.5)


class ipap_homing_2axis(Macro):
    """Macro to do the homing procedure in more than one axis at the same time.
       Given a list of motors to do the home and the direction in which you want
       to move, this macro will move all the motors at the same time waiting to 
       recieve the home signal.
       The macro ends when the home signal is detected or any axis receive an alarm
    """

    param_def = [
        ['motor1', Type.Motor, None, 'Motor to perform the homing procedure.'],
        ['motor2', Type.Motor, None, 'Motor to perform the homing procedure.'],
        ['direction', Type.Integer, None, 'Direction in which you will look for the home signal <-1|1>']
    ]

    def prepare(self, motor1, motor2, direction):
        #Now it will be hardcoded but at some point it will be parameters
        self.pool = motor1.getPoolObj()
        self.ctrl_name = motor1.getControllerName()
        self.motor1_axis = motor1.getAxis()
        self.motor2_axis = motor2.getAxis()
        self.direction = direction
        self.home_pos_dict = {}
        self.info('Ready to perform the homing procedure in axis: %d and %d' % (self.motor1_axis, self.motor2_axis))

    def run(self, motor1, motor2, direction):
        self.info('Starting the homing procedure')
        self.executeHoming(motor1, motor2, direction)

    def on_abort():
        self.info('Homing procedure aborted.')
        self.abort = True

    def executeHoming(self, motor1, motor2, direction):
        CMD_HOME_GROUP_STRICT = 'home group strict %d %d %d %d ' % (self.motor1_axis, self.direction, self.motor2_axis, self.direction)
        CMD_HOME_STAT = '?homestat %d %d' % (self.motor1_axis, self.motor2_axis)
        #CMD_HOME_POS = '?homepos %d %d' % (self.motor1_axis, self.motor2_axis) #only works if both motors have found the home
        CMD_HOME_POS_AXIS1 = '%d:?homepos' % self.motor1_axis
        CMD_HOME_POS_AXIS2 = '%d:?homepos' % self.motor2_axis
        #CMD_HOMEENC_ENCIN = '?homeenc encin %d %d' % (self.motor1_axis, self.motor2_axis) #only works if both motors have found the home
        CMD_HOMEENC_ENCIN_AXIS1 = '%d:?homeenc encin' % self.motor1_axis
        CMD_HOMEENC_ENCIN_AXIS2 = '%d:?homeenc encin' % self.motor2_axis

        self.abort = False
        self.h1 = 0
        self.h2 = 0
        while len(self.home_pos_dict)<2 or self.abort:
            
            self.pool.SendToController([self.ctrl_name , CMD_HOME_GROUP_STRICT])
            home_detected = False

            while not home_detected or self.abort:
                ans = self.pool.SendToController([self.ctrl_name, CMD_HOME_STAT])
                home_stat = ans.split()
                
                if home_stat[1] == 'FOUND':
                    ans = self.pool.SendToController([self.ctrl_name, CMD_HOME_POS_AXIS1])
                    home_pos = int(ans.split()[1])
                    ans = self.pool.SendToController([self.ctrl_name, CMD_HOMEENC_ENCIN_AXIS1])
                    home_enc = int(ans.split()[1])
                    self.home_pos_dict[self.motor1_axis] = (home_pos,home_enc)
                    home_detected = True
                    home_motor_pos = motor1.getPosition(force=True)
                    if self.h1 == 0:
                        self.info('Home detected in axis: %d' % self.motor1_axis)
                        self.info('    HomePos: %d' % home_pos)
                        self.info('    HomeEncEncin: %d' % home_enc)
                        self.info('    HomePos (mm): %f' % home_motor_pos)
                    self.h1 += 1

                elif home_stat[3] == 'FOUND':
                    ans = self.pool.SendToController([self.ctrl_name, CMD_HOME_POS_AXIS2])
                    home_pos = int(ans.split()[1])
                    ans = self.pool.SendToController([self.ctrl_name, CMD_HOMEENC_ENCIN_AXIS2])
                    home_enc = int(ans.split()[1])
                    self.home_pos_dict[self.motor2_axis] = (home_pos,home_enc)
                    home_detected = True
                    home_motor_pos = motor2.getPosition(force=True)
                    if self.h2 == 0:
                        self.info('Home detected in axis: %d' % self.motor2_axis)
                        self.info('    HomePos: %d' % home_pos)
                        self.info('    HomeEncEncin: %d' % home_enc)
                        self.info('    HomePos (mm): %f' % home_motor_pos)
                    self.h2 +=1

        time.sleep(0.5)
        

class ipap_homing_3axis(Macro):
    """Macro to do the homing procedure in more than one axis at the same time.
       Given a list of motors to do the home and the direction in which you want
       to move, this macro will move all the motors at the same time waiting to 
       recieve the home signal.
       The macro ends when the home signal is detected or any axis receive an alarm
    """

    param_def = [
        ['motor1', Type.Motor, None, 'Motor to perform the homing procedure.'],
        ['motor2', Type.Motor, None, 'Motor to perform the homing procedure.'],
        ['motor3', Type.Motor, None, 'Motor to perform the homing procedure.'],
        ['direction', Type.Integer, None, 'Direction in which you will look for the home signal <-1|1>']
    ]

    def prepare(self, motor1, motor2, motor3, direction):
        #Now it will be hardcoded but at some point it will be parameters
        self.pool = motor1.getPoolObj()
        self.ctrl_name = motor1.getControllerName()
        self.motor1_axis = motor1.getAxis()
        self.motor2_axis = motor2.getAxis()
        self.motor3_axis = motor3.getAxis()
        self.direction = direction
        self.home_pos_dict = {}
        self.info('Ready to perform the homing procedure in axis: %d, %d and %d' % (self.motor1_axis, self.motor2_axis, self.motor3_axis))

    def run(self, motor1, motor2, motor3, direction):
        self.info('Starting the homing procedure')
        self.executeHoming(motor1, motor2, motor3, direction)

    def on_abort():
        self.info('Homing procedure aborted.')
        self.abort = True

    def executeHoming(self, motor1, motor2, motor3, direction):
        CMD_HOME_GROUP_STRICT = 'home group strict %d %d %d %d %d %d' % (self.motor1_axis, self.direction, self.motor2_axis, self.direction, self.motor3_axis, self.direction)
        CMD_HOME_STAT = '?homestat %d %d %d' % (self.motor1_axis, self.motor2_axis, self.motor3_axis)
        #CMD_HOME_POS = '?homepos %d %d %d' % (self.motor1_axis, self.motor2_axis, self.motor3_axis)
        #CMD_HOMEENC_ENCIN = '?homeenc encin %d %d %d' % (self.motor1_axis, self.motor2_axis, self.motor3_axis)
        CMD_HOME_POS_AXIS1 = '%d:?homepos' % self.motor1_axis
        CMD_HOME_POS_AXIS2 = '%d:?homepos' % self.motor2_axis
        CMD_HOME_POS_AXIS3 = '%d:?homepos' % self.motor3_axis
        CMD_HOMEENC_ENCIN_AXIS1 = '%d:?homeenc encin' % self.motor1_axis
        CMD_HOMEENC_ENCIN_AXIS2 = '%d:?homeenc encin' % self.motor2_axis
        CMD_HOMEENC_ENCIN_AXIS3 = '%d:?homeenc encin' % self.motor3_axis

        self.abort = False
        self.h1 = 0
        self.h2 = 0
        self.h3 = 0
        while len(self.home_pos_dict)<3 or self.abort:
            
            self.pool.SendToController([self.ctrl_name , CMD_HOME_GROUP_STRICT])
            home_detected = False
            
            while not home_detected or self.abort:
                ans = self.pool.SendToController([self.ctrl_name, CMD_HOME_STAT])
                home_stat = ans.split()
                
                if home_stat[1] == 'FOUND':
                    ans = self.pool.SendToController([self.ctrl_name, CMD_HOME_POS_AXIS1])
                    home_pos = int(ans.split()[1])
                    ans = self.pool.SendToController([self.ctrl_name, CMD_HOMEENC_ENCIN_AXIS1])
                    home_enc = int(ans.split()[1])
                    self.home_pos_dict[self.motor1_axis] = (home_pos,home_enc)
                    home_detected = True
                    home_motor_pos = motor1.getPosition(force=True)
                    if self.h1 == 0:
                        self.info('Home detected in axis: %d' % self.motor1_axis)
                        self.info('    HomePos: %d' % home_pos)
                        self.info('    HomeEncEncin: %d' % home_enc)
                        self.info('    HomePos (mm): %f' % home_motor_pos)
                    self.h1 += 1

                if home_stat[3] == 'FOUND':
                    ans = self.pool.SendToController([self.ctrl_name, CMD_HOME_POS_AXIS2])
                    home_pos = int(ans.split()[1])
                    ans = self.pool.SendToController([self.ctrl_name, CMD_HOMEENC_ENCIN_AXIS2])
                    home_enc = int(ans.split()[1])
                    self.home_pos_dict[self.motor2_axis] = (home_pos,home_enc)
                    home_detected = True
                    home_motor_pos = motor2.getPosition(force=True)
                    if self.h2 == 0:
                        self.info('Home detected in axis: %d' % self.motor2_axis)
                        self.info('    HomePos: %d' % home_pos)
                        self.info('    HomeEncEncin: %d' % home_enc)
                        self.info('    HomePos (mm): %f' % home_motor_pos)
                    self.h2 += 1

                if home_stat[5] == 'FOUND':
                    ans = self.pool.SendToController([self.ctrl_name, CMD_HOME_POS_AXIS3])
                    home_pos = int(ans.split()[1])
                    ans = self.pool.SendToController([self.ctrl_name, CMD_HOMEENC_ENCIN_AXIS3])
                    home_enc = int(ans.split()[1])
                    self.home_pos_dict[self.motor3_axis] = (home_pos,home_enc)
                    home_detected = True
                    home_motor_pos = motor3.getPosition(force=True)
                    if self.h3 == 0:
                        self.info('Home detected in axis: %d' % self.motor3_axis)
                        self.info('    HomePos: %d' % home_pos)
                        self.info('    HomeEncEncin: %d' % home_enc)
                        self.info('    HomePos (mm): %f' % home_motor_pos)
                    self.h3 += 1

        time.sleep(0.5) #adding this time sleep makes the homepos in mm not useful.


