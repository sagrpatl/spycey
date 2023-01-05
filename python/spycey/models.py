from PySpice.Spice.Netlist import Circuit , SubCircuit, SubCircuitFactory
import uuid

def hexID():
    return "N" + uuid.uuid4().hex

class LDO(SubCircuit):
    __nodes__ = ('n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7')
    def __init__(self, outputVoltage=1):
        name = hexID()
        self.type = "XFMR"
        self.label = "LDO"
        SubCircuit.__init__(self, name, *self.__nodes__)
        #V('input', 'N1', 0, 10)
        self.B("1", 0, "n1", current_expression="I(V1)")
        self.V('1', "n2", 0, outputVoltage)
        self.B('VO','n3', 0, voltage_expression="V(n2)")
        self.B('IO','n4', 0, voltage_expression="-I(V1)")
        self.B('VI','n5', 0, voltage_expression="V(n1)")
        self.B('II','n6', 0, voltage_expression="-I(B1)")
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
        #V('input', 'N1', 0, 10)
        self.V("2", "n1", "n11", 0)
        self.B("1", 0, "n11", current_expression="I(V1) * V(n2)/V(n1)")
        self.B("2", "n11", 0, current_expression=f"( V(n2) * -I(V1) * (1-{efficiency}) ) / {efficiency} / V(n11)")
        self.V('1', "n2", 0, outputVoltage)
        self.B('VO','n3', 0, voltage_expression="V(n2)")
        self.B('IO','n4', 0, voltage_expression="-I(V1)")
        self.B('VI','n5', 0, voltage_expression="V(n1)")
        self.B('II','n6', 0, voltage_expression="I(V2)")
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
        self.label = "Resistor"
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.R("1", "n1", 0, resistance)
        self.B('VI','n5', 0, voltage_expression="V(n1)")
        self.B('II','n6', 0, voltage_expression="I(R1)")

class CP(SubCircuit):
    __nodes__ = ('n1', 'n5', 'n6')
    def __init__(self, power=1):
        name = hexID()
        self.type = "SINK"
        self.label = "Resistor"
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.B("1", "n1", 0, current_expression=f"{power}/V(n1)")
        self.B('VI','n5', 0, voltage_expression="V(n1)")
        self.B('II','n6', 0, voltage_expression="I(B1)")
