from sardana.macroserver.macro import macro, Type, Optional
import PyTango


def set_offset(offset_attr_name, offset):
    if offset:
        attribute_1 = "pm/energycff_ctrl/1/" + offset_attr_name
        offset_1 = PyTango.AttributeProxy(attribute_1)
        offset_1.write(offset)
        
        attribute_2 = "pm/energycff_ctrl/2/" + offset_attr_name
        offset_2=PyTango.AttributeProxy(attribute_2)
        offset_2.write(offset)
        
        attribute_3 = "pm/energy_ctrl/1/" + offset_attr_name
        offset_3 = PyTango.AttributeProxy(attribute_3)
        offset_3.write(offset)

        attribute_4 = "pc/energyfromik_ctrl/1/" + offset_attr_name
        offset_4 = PyTango.AttributeProxy(attribute_4)
        offset_4.write(offset)
        
        attribute_5 = "pc/energyfromik_ctrl/2/" + offset_attr_name
        offset_5 = PyTango.AttributeProxy(attribute_5)
        offset_5.write(offset)
        return offset
    else:
        offset_attr_name = "pm/energycff_ctrl/1/" + offset_attr_name
        offset_attr = PyTango.AttributeProxy(offset_attr_name)
        offset_output = offset_attr.read().value
        return offset_output 

        
@macro([["offset", Type.Float, Optional, "set offset GrxHE"]])
def set_offset_GrxHE(self, offset):
    """Set offset GrxHE: indicate the value to be set"""
    offset_output = set_offset("offsetGrxHE", offset)
    if not offset:
        self.output(offset_output)
    
    
@macro([["offset", Type.Float, Optional, "set offset GrxLE"]])
def set_offset_GrxLE(self, offset):
    """Set offset GrxLE: indicate the value to be set"""
    offset_output = set_offset("offsetGrxLE", offset)
    if not offset:
        self.output(offset_output)
        
        
@macro([["offset", Type.Float, Optional, "set offset MxHE"]])
def set_offset_MxHE(self, offset):
    """Set offset MxHE: indicate the value to be set"""
    offset_output = set_offset("offsetMxHE", offset)
    if not offset:
        self.output(offset_output)
        
        
@macro([["offset", Type.Float, Optional, "set offset MxLE"]])
def set_offset_MxLE(self, offset):
    """Set offset MxLE: indicate the value to be set"""
    offset_output = set_offset("offsetMxLE", offset)
    if not offset:
        self.output(offset_output)
        
    
