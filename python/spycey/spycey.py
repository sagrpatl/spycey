import numpy as np
import matplotlib.pyplot as plt
import uuid
import networkx as nx
import PySpice.Logging.Logging as Logging
# logger = Logging.setup_logging(logging_level='WARNING')
logger = Logging.setup_logging()
from anytree import Node, RenderTree, NodeMixin,LevelOrderGroupIter,PreOrderIter
from anytree.exporter import DotExporter
from enum import Enum
import copy
from engineering_notation import EngNumber

from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit , SubCircuit, SubCircuitFactory
from PySpice.Unit import *
from . import models




def hexID():
    return "N" + uuid.uuid4().hex

class NodeType(Enum):
    XFMR  = "XFMR"
    SINK  = "SINK"
    INPUT = "INPUT"


class PNode(NodeMixin):
    def __init__(self, name, parent=None, children=None, model=None, multiplier=1, comment=""):
        super(PNode, self).__init__()
        self.name = name
        self.id = hexID()
        self.parent = parent
        self.VI = 0
        self.II = 0
        self.VO = 0
        self.IO = 0
        self.EF = 0
        self.comment = comment
        self.multiplier = multiplier
        if children:
             self.children = children
        if model:
            self.model = model
            self.id = model.name
    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            # Avoid recursion error by not copying subcircuit object
            if(k != "model"):
                setattr(result, k, copy.deepcopy(v, memo))
            else:
                # print(v)
                setattr(result, k, v)
        return result
    def setParent(self, parent):
        self.parent = parent
        return self
    def setMultiplier(self, multiplier):
        self.multiplier = multiplier
        return self
    @classmethod
    def SMPS(cls, name, voltage, efficiency=1, parent=None, multiplier=1, comment=""):
        return cls(name, model=models.SMPS(voltage,efficiency), parent=parent, comment=comment, multiplier=multiplier)
    @classmethod
    def LDO(cls, name, voltage, parent=None, multiplier=1, comment=""):
        return cls(name, model=models.LDO(voltage), parent=parent, comment=comment, multiplier=multiplier)
    @classmethod
    def CP_LOAD(cls, name, power, parent=None, multiplier=1, comment=""):
        return cls(name, model=models.CP(power), parent=parent, comment=comment, multiplier=multiplier)
    @classmethod
    def RES(cls, name, resistance, parent=None, multiplier=1, comment=""):
        return cls(name, model=models.Res(resistance), parent=parent, comment=comment, multiplier=multiplier)
    @classmethod
    def IN_DC(cls, name, voltage, parent=None, comment=""):
        return cls(name, model=models.INPUT(voltage), parent=parent, comment=comment)
    @classmethod
    def UNREG(cls, name, ratio, efficiency=1, parent=None, comment=""):
        return cls(name, model=models.UNREG(ratio, efficiency), parent=parent, comment=comment)

def _Netlist(node):
    # Build up netlist
    # Build a flat netlist or heirarchical?
    mycir = Circuit(node.id)
    node: PNode

    # expand netlist for multipleir values
    nodeTemp = copy.deepcopy(node)
    def nodenamefunc(node): 
        # return "%s %s" % (node.name,node.id)
        return "%s" % (node.id)
    DotExporter(nodeTemp,  graph="digraph", nodenamefunc=nodenamefunc, options=[f"rankdir=LR; splines=true; labelloc=t; fontsize=72; nodesep=0.25; ranksep=\"1.2 equally\"; fontsize=48;"]).to_picture("testing2.png")
    for pre, fill, node in RenderTree(nodeTemp):
        # print("%s%s %s" % (pre, node.name, node.id))
        # print(type(node.subcircuit))
        try:
            if node.model is not None:
                # Catch duplicate subcircuits
                try:
                    mycir.subcircuit(node.model)
                except:
                    pass
                if(node.multiplier > 1):
                    mid = hexID()
                    subcon = hexID()
                    multi = models.Multiplier(node.multiplier)
                    mycir.subcircuit(multi)
                    mycir.X(mid, multi.name, node.parent.id, subcon)
                    pass
                else:
                    try:
                        subcon = node.parent.id
                    except:
                        pass
                if node.model.type == "XFMR":
                    mycir.X(node.id, node.model.name, subcon, node.id, "VO-" + node.id, "IO-" + node.id, "VI-" + node.id, "II-" + node.id, "EF-" + node.id)
                elif node.model.type == "SINK":
                    mycir.X(node.id, node.model.name, subcon, "VI-" + node.id, "II-" + node.id)
                elif node.model.type == "HEAD":
                    mycir.X(node.id, node.model.name, node.id, "VO-" + node.id, "IO-" + node.id)
        except Exception as e:
            print(e)
            print(node.name)
            # print(type(node.subcircuit))
            print("Couldn't find subcircuit model :(")
            pass
    # print(mycir)
    return mycir

def Solve(node):
    cir = _Netlist(node)
    print(cir)
    simulator = cir.simulator()
    output = simulator.operating_point()
    # back anno parameters to tree from dc op simulation
    for pre, fill, node in RenderTree(node):
        if(node.model.type == "XFMR"):
            try:
                node.IO = float(output["io-" + node.id])
                node.VO = float(output["vo-" + node.id]) 
                node.II = float(output["ii-" + node.id]) 
                node.VI = float(output["vi-" + node.id]) 
                node.EF = float(output["ef-" + node.id])
                
            except Exception as e:
                print(e)
                print("Couldn't find parameter")
                pass
        try:
            if(node.model.type == "SINK"):
                node.II = float(output["ii-" + node.id]) 
                node.VI = float(output["vi-" + node.id]) 
        except Exception as e:
                print(e)
                print("Couldn't find parameter")
                pass
        try:
            if(node.model.type == "HEAD"):
                node.IO = float(output["io-" + node.id]) 
                node.VO = float(output["vo-" + node.id])
        except Exception as e:
                print(e)
                print("Couldn't find parameter")
                pass
    return output

def nodeattrfunc(node: PNode):
    style = "fixedsize=false; width=2.25;"
    if node.multiplier > 1:
        style += "shape=box3d;"
    else:
        style += "shape=box;"
    if node.model.type == "XFMR":
        style += "fillcolor=lightpink; style=filled"
    elif node.model.type in ["HEAD"]:
        style += "fillcolor=lightpink; style=filled"
    elif node.model.type == "SINK":
        style += "fillcolor=plum; style=filled"
    return style

def nodenamefunc(node): 
    output = ""
    output += "%s" % node.name
    if(node.multiplier > 1):
        output += " [x%d]" % node.multiplier
    if(node.model.type == "XFMR"):
        V = node.VO
        I = node.IO 
        P = V * I
        L = P  / node.EF * (1 - node.EF)
        output += "\n%s\n%sV/%sA → %sW" % (node.model.label, EngNumber(V), EngNumber(I), EngNumber(P))
        output += "\nη=%.2f  ℓ=%sW" % (node.EF, EngNumber(L))
    elif(node.model.type == "SINK"):
        V = node.VI
        I = node.II 
        P = V * I
        output += "\n%s\n%sV/%sA → %sW" % (node.model.label, EngNumber(V), EngNumber(I), EngNumber(P))
    elif(node.model.type == "HEAD"):
        V = node.VO
        I = node.IO 
        P = V * I
        output += "\n%s\n%sV/%sA → %sW" % (node.model.label, EngNumber(V), EngNumber(I), EngNumber(P))
    # else:
        # output += "%s" % (node.name)
    return output
def edgeattrfunc(node, child):
    if child.multiplier > 1:
        return 'label="%sA [x%d]"' % (EngNumber(child.II), child.multiplier)
    
    return 'label="%sA"' % (EngNumber(child.II))

class PowerDotExporter(DotExporter):
    def __init__(self, node):
        super(PowerDotExporter, self).__init__(node,  graph="digraph",nodenamefunc=nodenamefunc, nodeattrfunc=nodeattrfunc, edgeattrfunc=edgeattrfunc, options=[f"rankdir=LR; splines=true; labelloc=t; fontsize=72; nodesep=0.25; ranksep=\"1.2 equally\"; fontsize=48;"])