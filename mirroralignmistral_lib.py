from sardana.macroserver.macro import Macro, Type
import numpy as np




class mirroralignmistral(Macro):
    """This macro is used to align the mirror M2 at Mistral in order to maximize the Energy received.
    
        
    # Used:
    #"Xmot", Type.Moveable, None, "Pseudomotor X of mirror m2"
    #"Pmot", Type.Moveable, None, "Pseudomotor Pitch of mirror m2"
    #"ExperChannel", Type.ExpChannel, None, "experimentalChannel0D"
    #"deltaX", Type.Float, None, "Increment in motor Xmot for the scans": 0.16mm    
    #"deltaP", Type.Float, None, "Increment in motor P for each diferent scan": 0.005mrad
    #"D1", Type.Float, None, "Lower position of motor Xmot for the scan":-0.3mm
    #"D2", Type.Float, None, "Higher position of motor Xmot for the scan":+0.3mm
    #"intervals", Type.Integer, None, "Number of intervals during the scan":100
    #"integtime", Type.Float, None, "Integration time for everty scan acquisition":1s"""


    #"X1", Type.Float, None, "Initial position for translation motor Xmot"
    #"P1", Type.Float, None, "Initial position for Pitch motor P"

    def run(self):
        #self.mirroralign("dummymotor03", "dummymotor04", "albaem01_i04", 0.16, 0.005, -0.3, 0.3, 5, 0.5) 
        #self.mirroralign("dummymotor03", "dummymotor04", "zerodimdum1", 0.16, 0.005, -0.3, 0.3, 5, 0.5) 
        self.mirroralign("m2_x", "m2_pitch", "albaem01_i04", 0.16, 0.005, -0.3, 0.3, 100, 1) 
