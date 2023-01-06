from PySpice.Spice.Netlist import SubCircuit
import uuid
from engineering_notation import EngNumber

def hexID():
    return "N" + uuid.uuid4().hex

class LDO(SubCircuit):
    __nodes__ = ('n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7')
    def __init__(self, outputVoltage=1):
        name = hexID()
        self.type = "XFMR"
        self.label = "LDO"
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.B("1",  "n1", 0, current_expression="-I(V1)")
        self.V('1', "n2", 0, outputVoltage)
        self.B('VO','n3', 0, voltage_expression="V(n2)")
        self.B('IO','n4', 0, voltage_expression="-I(V1)")
        self.B('VI','n5', 0, voltage_expression="V(n1)")
        self.B('II','n6', 0, voltage_expression="I(B1)")
        self.B('EF','n7', 0, voltage_expression="V(n2)/V(n1)")

class Multiplier(SubCircuit):
    __nodes__ = ('n1', 'n2')
    def __init__(self, multiplier=1):
        name = hexID()
        self.type = "XFMR"
        self.label = "Multiplier"
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.B("1", 0, "n1", current_expression=f"I(B2) * {multiplier}")
        self.B("2", "n2", 0, voltage_expression="V(n1)")
    


#
# n1 - parent connection
# n2 - children connection
# n3 - vout
# n4 - iout
# n5 - vin
# n6 - iin
# n7 - eff
#
class SMPS(SubCircuit):
    __nodes__ = ('n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7')
    def __init__(self, outputVoltage=1, efficiency=1):
        name = hexID()
        self.type = "XFMR"
        self.label = "SMPS"
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.V("2", "n1", "n11", 0)
        self.B("1", 0, "n11", current_expression="I(V1) * V(n2)/V(n1)")
        self.B("2", "n11", 0, current_expression=f"( V(n2) * -I(V1) * (1-{efficiency}) ) / {efficiency} / V(n11)")
        self.V('1', "n2", 0, outputVoltage)
        self.B('VO','n3', 0, voltage_expression="V(n2)")
        self.B('IO','n4', 0, voltage_expression="-I(V1)")
        self.B('VI','n5', 0, voltage_expression="V(n1)")
        self.B('II','n6', 0, voltage_expression="I(V2)")
        self.B('EF','n7', 0, voltage_expression=f"{efficiency}")

class UNREG(SubCircuit):
    __nodes__ = ('n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7')
    def __init__(self, ratio=1, efficiency=1):
        name = hexID()
        self.type = "XFMR"
        self.label = "Unregulated %d:1" % (ratio)
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.V("2", "n1", "n11", 0)
        # self.B("333", 0, 'n11', current_expression="-I(V3)")
        # self.R("111", "n11", 0, 0.25)

        # self.B("1", 0, "n11", current_expression="I(B3) * V(n2)/V(n1)")
        self.B("1", 0, "n11", current_expression=f"I(B3)/{ratio}")
        # self.R("111", 'n55', 0, 0.001)
        
        self.B("2", "n11", 0, current_expression=f"( V(n2) * -I(B3) * (1-{efficiency}) ) / {efficiency} / V(n11)")
        self.B('3', "n2", 0, voltage_expression=f"V(n11)/{ratio}")
        # self.V('3', 'n22', 'n2', 0)
        # self.R('3', "n22", "n2", 0) # help with convergence (otherwise singular matrix)
        self.B('VO','n3', 0, voltage_expression="V(n2)")
        self.B('IO','n4', 0, voltage_expression="-I(B3)")
        self.B('VI','n5', 0, voltage_expression="V(n1)")
        self.B('II','n6', 0, voltage_expression="I(V2)")
        # self.B('II','n6', 0, voltage_expression="10")
        self.B('EF','n7', 0, voltage_expression=f"{efficiency}")

class INPUT(SubCircuit):
    __nodes__ = ('n1', 'n3', 'n4')
    def __init__(self, outputVoltage=1):
        name = hexID()
        self.type = "HEAD"
        self.label = "Input"
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.V('1', "n1", 0, outputVoltage)
        self.B('VO','n3', 0, voltage_expression="V(n1)")
        self.B('IO','n4', 0, voltage_expression="-I(V1)")

class Res(SubCircuit):
    __nodes__ = ('n1', 'n5', 'n6')
    def __init__(self, resistance=1):
        name = hexID()
        self.type = "SINK"
        self.label = "Resistor %sΩ" % (EngNumber(resistance))
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.R("1", "n1", 0, resistance)
        self.B('VI','n5', 0, voltage_expression="V(n1)")
        self.B('II','n6', 0, voltage_expression="I(R1)")

class CP(SubCircuit):
    __nodes__ = ('n1', 'n5', 'n6')
    def __init__(self, power=1):
        name = hexID()
        self.type = "SINK"
        self.label = "Constant Power"
        self.label = "Constant Power"
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.B("1", "n1", 0, current_expression=f"{power}/V(n1)")
        # self.R("n1", "n11", 0, 1e-6)
        self.B('VI','n5', 0, voltage_expression="V(n1)")
        self.B('II','n6', 0, voltage_expression="I(B1)")

class CC(SubCircuit):
    __nodes__ = ('n1', 'n5', 'n6')
    def __init__(self, current=1):
        name = hexID()
        self.type = "SINK"
        self.label = "Constant Power"
        self.label = "Constant Power"
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.B("1", "n1", 0, current_expression=f"{current}")
        # self.R("n1", "n11", 0, 1e-6)
        self.B('VI','n5', 0, voltage_expression="V(n1)")
        self.B('II','n6', 0, voltage_expression="I(B1)")

class CCVS(SubCircuit):
    __nodes__ = ('n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7')
    def __init__(self):
        name = hexID()
        self.type = "XFMR"
        self.label = "CCVS Example"
        SubCircuit.__init__(self, name, *self.__nodes__)
        efficiency = 1
        ratio = 1
        self.V("2", "n11", "n1", 0)
        self.B("1",  0, 'n11', current_expression="I(B3) * V(n22)/V(n11)")
        self.B("2", "n11", 0, current_expression=f"( V(n2) * I(B3) * (1-{efficiency}) ) / {efficiency} / V(n11)")
        self.B('3', "n22", 0, voltage_expression=f"pwl(I(V3),0,52,140,48, 200, 36,1e6, 36)")
        # self.B('3', "n22", 0, voltage_expression=f"50")
        self.V('3', 'n22', 'n2', 0)
        self.B('VO','n3', 0, voltage_expression="V(n2)")
        self.B('IO','n4', 0, voltage_expression="I(V3)")
        self.B('VI','n5', 0, voltage_expression="V(n1)")
        self.B('II','n6', 0, voltage_expression="-I(V2)")
        self.B('EF','n7', 0, voltage_expression=f"{efficiency}")    