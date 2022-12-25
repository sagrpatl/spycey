import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()


from PySpice.Spice.Netlist import Circuit, SubCircuitFactory
from PySpice.Unit import *


class SubCircuit1(SubCircuitFactory):
    NAME = 'sub_circuit1'
    NODES = ('n1', 'n2')
    def __init__(self):
        super().__init__()
        self.R(1, 'n1', 'n2', 1@u_Ω)
        self.R(2, 'n1', 'n2', 2@u_Ω)


circuit = Circuit('Test')


C1 = circuit.C(1, 0, 1, 1@u_uF)

circuit.C(2, 1, 2, 2@u_uF)
circuit.subcircuit(SubCircuit1())
circuit.X('1', 'sub_circuit1', 2, 0)

print(circuit)

print (C1)