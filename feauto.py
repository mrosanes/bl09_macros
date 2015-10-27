from sardana.macroserver.macro import macro, Type
import PyTango

@macro([["FEAUTO", Type.Float, None, "activate or deactivate FE_AUTO"]])
def feauto(self, FEAUTO):
	
	if FEAUTO>=1:
		FEAUTO=1		
	aa=PyTango.AttributeProxy("BL09/CT/EPS-PLC-01/FE_AUTO")
	aa.write(FEAUTO)



# @macro([["FEAUTO", bool, None, "activate or deactivate FE_AUTO"]])
# def feauto(self, FEAUTO):
	
# 	fe_auto = PyTango.AttributeProxy("BL09/CT/EPS-PLC-01/FE_AUTO")
# 	if FEAUTO:
# 		fe_auto.write(1.0)
# 	else:
# 		fe_auto.write(0.0)
