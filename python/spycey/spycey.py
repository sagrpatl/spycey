import numpy as np
import matplotlib.pyplot as plt
import uuid
import networkx as nx
import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()
from anytree import Node, RenderTree, NodeMixin
from enum import Enum


from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit , SubCircuit, SubCircuitFactory
from PySpice.Unit import *


def hexID():
    return "N" + uuid.uuid4().hex

class NodeType(Enum):
    XFMR  = "XFMR"
    SINK  = "SINK"
    INPUT = "INPUT"

#
# n1 - parent connection
# n2 - children connection
# n3 - vout
# n4 - iout
# n5 - vin
# n6 - iin
# n7 - eff
#
class LDO(SubCircuit):
    __nodes__ = ('n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7')
    def __init__(self, outputVoltage=1):
        name = hexID()
        self.type = "XFMR"
        SubCircuit.__init__(self, name, *self.__nodes__)
        #V('input', 'N1', 0, 10)
        self.B("1", 0, "n1", current_expression="I(V1)")
        self.V('1', "n2", 0, outputVoltage)
        self.B('VO','n3', 0, voltage_expression="V(n2)")
        self.B('IO','n4', 0, voltage_expression="I(V1)")
        self.B('VI','n5', 0, voltage_expression="V(n1)")
        self.B('II','n6', 0, voltage_expression="I(B1)")
        self.B('EF','n7', 0, voltage_expression="V(n2)/V(n1)")

class INPUT(SubCircuit):
    __nodes__ = ('n1', 'n3', 'n4')
    def __init__(self, outputVoltage=1):
        name = hexID()
        self.type = "INPUT"
        SubCircuit.__init__(self, name, *self.__nodes__)
        #V('input', 'N1', 0, 10)
        self.V('1', "n1", 0, outputVoltage)
        self.B('VO','n3', 0, voltage_expression="V(n1)")
        self.B('IO','n4', 0, voltage_expression="I(V1)")

class Res(SubCircuit):
    __nodes__ = ('n1', 'n5', 'n6')
    def __init__(self, resistance=1):
        name = hexID()
        self.type = "SINK"
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.R("1", "n1", 0, resistance)
        self.B('VI','n5', 0, voltage_expression="V(n1)")
        self.B('II','n6', 0, voltage_expression="I(R1)")

class PNODE(NodeMixin):
    def __init__(self, name, parent=None, children=None, subcircuit=None):
        super(PNODE, self).__init__()
        self.name = name
        self.id = hexID()
        self.parent = parent
        if children:
             self.children = children
        if subcircuit:
            self.subcircuit = subcircuit
            self.id = subcircuit.name
    def circuit(self):
        # Perform search and build up netlist
        # Build a flat netlist or heirarchical?
        mycir = Circuit(self.id)
        # mycir.V(self.id, self.id, 0, 10)
        node: PNODE
        for pre, fill, node in RenderTree(self):
            # print("%s%s %s" % (pre, node.name, node.id))
            try:
                if node.subcircuit is not None:
                    mycir.subcircuit(node.subcircuit)
                    if node.subcircuit.type == "XFMR":
                        mycir.X(node.id, node.subcircuit.name, node.parent.id, node.id, "VO-" + node.id, "IO-" + node.id, "VI-" + node.id, "II-" + node.id, "EE-" + node.id)
                    elif node.subcircuit.type == "SINK":
                        mycir.X(node.id, node.subcircuit.name, node.parent.id, "VI-" + node.id, "II-" + node.id)
                        # sink.minus.add_current_probe(mycir) # to get positive value
                    elif node.subcircuit.type == "INPUT":
                        mycir.X(node.id, node.subcircuit.name, node.id, "VO-" + node.id, "IO-" + node.id)

                    # print(node.subcircuit)
            except:
                pass
        return mycir

