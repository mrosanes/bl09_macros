from sardana.macroserver.macro import Macro, Type
import numpy as np
import time
import PyTango

class close_beamline(Macro):
    """This macro is used close the beamline (deactivate FE_AUTO, CLOSE_FE, Close valves).
    """

    param_def = [ ["frontend", Type.IORegister, None, "FEIORegister managing the FrontEnd"] ] 


    def run(self, frontend):    
           
        # TURN OFF FRONTEND AUTO (FE_AUTO=0)
        FEAUTO=0		
        feauto_proxy = PyTango.AttributeProxy("BL09/CT/EPS-PLC-01/FE_AUTO")
        feauto_proxy.write(FEAUTO)
        time.sleep(0.2)
        self.output('FE_AUTO is: ' + str(feauto_proxy.read().value))

        # CLOSING FRONT END
        frontend.write_attribute('value', 0)
        self.output('Trying to close FrontEnd')
        time.sleep(10)
                                
        
       

        
        # CLOSING VALVES
        feopen_proxy = PyTango.AttributeProxy("BL09/CT/EPS-PLC-01/fe_open")
        if (FEAUTO == 0 and feopen_proxy.read().value == False and frontend.value == 0):

            self.output('FrontEnd is closed\n')
            self.output('Proceeding to close valves\n')
            valvesOrder = self.getEnv("_ValvesOrder")
                
            for valve in valvesOrder:
                valve_proxy = PyTango.DeviceProxy(valve)
                
                if (valve_proxy.State() != PyTango.DevState.CLOSE):
                    valve_proxy.Close()
                    self.output('Closing valve '+ valve + '\n')
                    time.sleep(1)    
            time.sleep(3)  

            for valve in valvesOrder:
                valve_proxy = PyTango.DeviceProxy(valve)
                if (valve_proxy.State() == PyTango.DevState.CLOSE):
                    self.output('Valve '+ valve +' closed.\n')
                else:
                    self.output('Problem when trying to close valve '+ valve + '.' + '\n' + 'Valve ' + valve + ' could not be closed')



        else:
 
            self.output('ERROR: FrontEnd could NOT be closed.')
            self.output('Valves will NOT be closed because FE could not be closed.')




       
