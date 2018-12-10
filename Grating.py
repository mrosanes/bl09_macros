from sardana.macroserver.macro import macro, Type
import PyTango

@macro([["lines", Type.Float, None, 
         "set grating lines; use negative number to ask for current grating lines"]])
def gratinglines(self, lines):
    
    if lines > 0:
        energy_1=PyTango.AttributeProxy("pm/energycff_ctrl/1/Lines")
        energy_1.write(lines)
        
        energy_2=PyTango.AttributeProxy("pm/energycff_ctrl/2/Lines")
        energy_2.write(lines)
        
        energy_3=PyTango.AttributeProxy("pm/energy_ctrl/1/Lines")
        energy_3.write(lines)
        
        energy_4=PyTango.AttributeProxy("pc/energyfromik_ctrl/1/Lines")
        energy_4.write(lines)
        
        energy_5=PyTango.AttributeProxy("pc/energyfromik_ctrl/2/Lines")
        energy_5.write(lines)
    else:
        energy_1=PyTango.AttributeProxy("pm/energycff_ctrl/1/Lines")
        lines_output = energy_1.read().value
        self.output(lines_output)