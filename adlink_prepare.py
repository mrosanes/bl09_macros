import os, sys, time, datetime, math
import PyTango

from sardana.macroserver.macro import *

class adlink_prepare(Macro):
    """ Macro to prepare the mode of acquisition of the adlink, in order
        to configure it for an scan mode or a continous mode.
    """

    param_def = [
                    ['AdlinkDevice', Type.String, None, 'Adlink/Device/Name'],
                    ['Mode', Type.String, None, 'integration|continuous']
    
    ]

    def prepare(self,AdlinkDevice,Mode):
        self._adlink = PyTango.DeviceProxy(AdlinkDevice)

    def run(self,AdlinkDevice,Mode):
        
        try:
            self.state = self._adlink.state()
            if self.state == PyTango.DevState.RUNNING or self.state == PyTango.DevState.ON:
                self._adlink.stop()

            if Mode.lower() == 'continuous':
                self._adlink['TriggerInfinite'] = 1

            elif Mode.lower() == 'integration':
                #bufferSize = self.integrationTime * self.SampleRate
                self._adlink['NumOfTriggers'] = 1
                self._adlink['TriggerInfinite'] = 0
                #self._adlink['SampleRate'] = self.SampleRate
                #self._adlink['ChannelSamplesPerTrigger'] = bufferSize

            else:
                self.info("Wrong parameters! Please introduce: Adlink/device/name Mode\n    where mode can be: integration or continous")

            self._adlink.start()
        except PyTango.DevFailed, e:
            self.error("Impossible to ask about the state of the device: %s , and/or stop it. \nException: %s" %(AdlinkDevice,e))

