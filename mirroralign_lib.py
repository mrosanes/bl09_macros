from sardana.macroserver.macro import Macro, Type
from scipy.optimize import leastsq
import numpy as np
import time
import json


class mirroralign(Macro):
    """This macro is used to align a beamline mirror (X and Pitch) in order to 
    maximize the Energy received.
    """
    param_def = [ ["Xmot", Type.Moveable, None, "Pseudomotor X of mirror"],
                  ["Pmot", Type.Moveable, None, "Pseudomotor Pitch of mirror"],
                  ["ExperChannel", Type.ExpChannel, None, "experimentalChannel0D"],
                  ["deltaX", Type.Float, 0.16, "Increment in motor Xmot for the scans"],
                  ["deltaP", Type.Float, 0.005, "Increment in motor Pmot for each diferent scan"],
                  ["D1", Type.Float, -0.3, "Lower position of motor Xmot for the scan"],
                  ["D2", Type.Float, 0.3, "Higher position of motor Xmot for the scan"],
                  ["intervals", Type.Integer, 100, "Number of intervals during the scan"],
                  ["integtime", Type.Float, 1, "Integration time for everty scan acquisition"]  ]
                
    result_def = [['json_encoded_result', Type.String, None, 'The macro result encoded by json.']]

    def gaussian1D(self, x, v = [0.0, 0.0, 1.0, 0.0, 1.0]):
        """Returns 1D gaussian + slope values for the given x
        Gaussian parameters are offset, slope, height, center, sigma"""
        return v[0] + v[1] * np.array(x) + v[2] * np.exp(-((x - v[3]) / v[4]) ** 2 / 2)

    def gausianfit(self, X, Y):
        """ Fits 2D spread data to a gaussian + slope.
        Return values are offset, slope, height, center, sigma.
        """
         # guess values are the initial values taken to start the fit
        # A fraction of the Y data range is taken as initial gaussian height and \
        # X data range center is taken as initial gaussian center
        guess = [min(Y), 0.0, 0.6 * (max(Y)-min(Y)),(min(X)+max(X))/2, 1.0]
 
        # errfunc returns the difference between data and fitted function
        # at the given x for the given parameters v
        errfunc = lambda v, x, y: (self.gaussian1D(x,v) - y)

        # leastsq search the v parameters that minimizes the sum of squared errfunc values
        par, success = leastsq(errfunc, guess, args=(X,Y))
        par[4] = abs(par[4])
        return par

    def run(self, Xmot, Pmot, ExperChannel, deltaX, deltaP, D1, D2, intervals, integtime):      
        #Default values for MISTRAL are:
        #x_motor(mirror 2): Xmot
        #pitch_motor(mirror 2): Pmot
        #ExperChannel: Mistral case: Intensity
        #deltaP=5urad=0.005mrad (specific of Mistral)
        #deltaX=0.16mm (specific of Mistral)
        #D1=-0.3mm
        #D2= 0.3mm        
        #intervals=100 
        #integtime=1s 
        
        step = {}
        resultDictPart = {}
        objecteResultat=[0]
                            
        X1=Xmot.getPosition()
        P1=Pmot.getPosition()
        
        #dscan1   
        dscan1 = self.createMacro('dscan', Xmot, D1, D2, intervals, integtime ) 
        self.runMacro(dscan1[0])
        xx1 = [None]*len(dscan1[0].data) # motor positions during the scan (lineal translation).
        yy1= [None]*len(dscan1[0].data) # measurementes 0d during the scan (energies).
        for i in range(len(dscan1[0].data)):
            xx1[i]=dscan1[0].data[i].data[Xmot.getName()]
            yy1[i]=dscan1[0].data[i].data[ExperChannel.getFullName()]
        a, b, Y1, X1, sig1 =self.gausianfit(xx1,yy1) 
        
        resultDictPart['XData'] = xx1
        resultDictPart['YData'] = yy1
        resultDictPart['gaussParams'] = [a,b,Y1,X1,sig1]
        resultDictPart['Pitch']= P1
        
        objecteResultat[0]=resultDictPart
        step['step'] = 1*20
        self._macro_status['data'] = resultDictPart 
        yield step
                
        self.output("Pitch: %f" % (P1))        
        self.output("X: %f" % (X1))
        self.output("Intensity:")
        self.output(Y1)
        self.output("FWHM:")
        self.output(2.35482*sig1)
        #self.output("Intensity/FWHM : %f" % (Y1/(2.35482*sig1)) )
                
        #dscan2
        X016n=X1-deltaX 
        self.mv(Xmot, X016n)
        P2=P1+deltaP 
        self.mv(Pmot, P2)
        dscan2 = self.createMacro('dscan', Xmot, D1, D2, intervals, integtime ) 
        self.runMacro(dscan2[0])
        xx2 = [None]*len(dscan2[0].data) 
        yy2= [None]*len(dscan2[0].data) 
        for i in range(len(dscan2[0].data)):
            xx2[i]=dscan2[0].data[i].data[Xmot.getName()]
            yy2[i]=dscan2[0].data[i].data[ExperChannel.getFullName()]
        a, b, Y2, X2, sig2 =self.gausianfit(xx2,yy2) 
        
        resultDictPart=resultDictPart.copy()
        resultDictPart['XData'] = xx2
        resultDictPart['YData'] = yy2
        resultDictPart['gaussParams'] = [a,b,Y2,X2,sig2]
        resultDictPart['Pitch']= P2
        
        objecteResultat.append(resultDictPart)
        step['step'] = 2*20
        self._macro_status['data'] = resultDictPart
        yield step
        
        self.output("Pitch: %f" % (P2))        
        self.output("X: %f" % (X2))
        self.output("Intensity:")
        self.output(Y2)
        self.output("FWHM:")
        self.output(2.35482*sig2)
        #self.output("Intensity/FWHM : %f" % (Y2/(2.35482*sig2)) )
        
        #dscan3
        X016p=X1+deltaX
        self.mv(Xmot, X016p)
        P3=P1-deltaP
        self.mv(Pmot, P3)  
        dscan3 = self.createMacro('dscan', Xmot, D1,D2, intervals, integtime ) 
        self.runMacro(dscan3[0])
        xx3 = [None]*len(dscan3[0].data) 
        yy3= [None]*len(dscan3[0].data)  
        for i in range(len(dscan3[0].data)):
            xx3[i]=dscan3[0].data[i].data[Xmot.getName()]
            yy3[i]=dscan3[0].data[i].data[ExperChannel.getFullName()]
        a, b, Y3, X3, sig3 =self.gausianfit(xx3,yy3) 
        
        resultDictPart=resultDictPart.copy()
        resultDictPart['XData'] = xx3
        resultDictPart['YData'] = yy3
        resultDictPart['gaussParams'] = [a,b,Y3,X3,sig3]
        resultDictPart['Pitch']= P3     
        
        objecteResultat.append(resultDictPart)
        step['step'] = 3*20
        self._macro_status['data'] = resultDictPart 
        yield step
        
        self.output("Pitch: %f" % (P3))        
        self.output("X: %f" % (X3))
        self.output("Intensity:")
        self.output(Y3)
        self.output("FWHM:")
        self.output(2.35482*sig3)
        #self.output("Intensity/FWHM : %f" % (Y3/(2.35482*sig3)) )
        
        XA=X1; YA=Y1; sigA=sig1; XB=X1; YB=Y1; sigB=sig1
        if (Y2)<(Y1) and (Y3)<(Y1):
                #self.output('first value is the higher one')
                self.mv(Xmot, X1)
                self.mv(Pmot, P1) 
                self.output("\n")  
                self.output("Final value motor Pitch is:")            
                self.output(P1)
                self.output("Final value motor X is:")
                self.output(X1)
                self.output("Final value intensity is:") 
                self.output(Y1)
                self.output("Final value FWHM is:") 
                self.output(2.35482*sig1)
                
                del self._macro_status['data']
                step['step'] = 100
                #self._macro_status['fullResult']=objecteResultat
                yield step
                #del self._macro_status['fullResult']

                result_json_str = json.dumps(objecteResultat) 
                self.setResult(result_json_str)
                return 

        #This while will return YA and PA
        while (YA<=Y2):
            #self.output('first while loop, minus delta X')
            XA=X2
            YA=Y2
            PA=P2
            sigA=sig2
            X016n=XA-deltaX
            self.mv(Xmot, X016n) 
            P2=PA+deltaP   
            self.mv(Pmot, P2) 

            #dscan4
            dscan4 = self.createMacro('dscan', Xmot, D1, D2, intervals, integtime ) 
            self.runMacro(dscan4[0])
            xx4 = [None]*len(dscan4[0].data) 
            yy4= [None]*len(dscan4[0].data)  
            for i in range(len(dscan4[0].data)):
                xx4[i]=dscan4[0].data[i].data[Xmot.getName()]
                yy4[i]=dscan4[0].data[i].data[ExperChannel.getFullName()]
            a, b, Y2, X2, sig2 = self.gausianfit(xx4,yy4) 
            
            resultDictPart=resultDictPart.copy()
            resultDictPart['XData'] = xx4
            resultDictPart['YData'] = yy4
            resultDictPart['gaussParams'] = [a,b,Y2,X2,sig2]
            resultDictPart['Pitch']= P2
            
            objecteResultat.append(resultDictPart)
            self._macro_status['data'] = resultDictPart 
            yield step
            
            self.output("Pitch: %f" % (P2))        
            self.output("X: %f" % (X2))
            self.output("Intensity:")
            self.output(Y2)
            self.output("FWHM:")
            self.output(2.35482*sig2)
            #self.output("Intensity/FWHM : %f" % (Y2/(2.35482*sig2)) )


        #This while will return YB and PB
        while (YB<=Y3):
            #self.output('second while loop, plus delta X')
            XB=X3
            YB=Y3
            PB=P3
            sigB=sig3
            X016p=XB+deltaX
            self.mv(Xmot, X016p)
            P3=PB-deltaP    
            self.mv(Pmot, P3)   

            #dscan5
            dscan5 = self.createMacro('dscan', Xmot, D1, D2, intervals, integtime ) 
            self.runMacro(dscan5[0])
            xx5= [None]*len(dscan5[0].data) 
            yy5= [None]*len(dscan5[0].data)  
            for i in range(len(dscan5[0].data)):
                xx5[i]=dscan5[0].data[i].data[Xmot.getName()]
                yy5[i]=dscan5[0].data[i].data[ExperChannel.getFullName()]
            a, b, Y3, X3, sig3 = self.gausianfit(xx5,yy5)
            
            resultDictPart=resultDictPart.copy()
            resultDictPart['XData'] = xx5
            resultDictPart['YData'] = yy5
            resultDictPart['gaussParams'] = [a,b,Y3,X3,sig3]
            resultDictPart['Pitch']= P3
            
            objecteResultat.append(resultDictPart)
            self._macro_status['data'] = resultDictPart 
            yield step
            
            self.output("Pitch: %f" % (P3))        
            self.output("X: %f" % (X3))
            self.output("Intensity:")
            self.output(Y3)
            self.output("FWHM:")
            self.output(2.35482*sig3)
            #self.output("Intensity/FWHM : %f" % (Y3/(2.35482*sig3)) )

        if YA>YB:
            #self.output('if one, minus delta X')
            self.mv(Xmot, XA)
            self.mv(Pmot, PA) 
            self.output("\n")  
            self.output("Final value motor Pitch is:")            
            self.output(PA)
            self.output("Final value motor X is:")
            self.output(XA)
            self.output("Final value intensity is:") 
            self.output(YA)
            self.output("Final value FWHM is:") 
            self.output(2.35482*sigA)

        elif YB>=YA:
            #self.output('if two, plus delta X')
            self.mv(Xmot, XB)
            self.mv(Pmot, PB)
            self.output("\n")   
            self.output("Final value motor Pitch is:")            
            self.output(PB)
            self.output("Final value motor X is:")
            self.output(XB)
            self.output("Final value intensity is:") 
            self.output(YB)
            self.output("Final value FWHM is:") 
            self.output(2.35482*sigB)


        del self._macro_status['data']
        step['step'] = 100
        yield step
        
        #self._macro_status['fullResult']=objecteResultat
        
        #del self._macro_status['fullResult']

        result_json_str = json.dumps(objecteResultat) 
        self.setResult(result_json_str)
        return

       
