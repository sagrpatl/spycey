# import numpy as np
# import matplotlib.pyplot as plt
import uuid
import PySpice.Logging.Logging as Logging
# logger = Logging.setup_logging(logging_level='WARNING')
logger = Logging.setup_logging()
from anytree import RenderTree, NodeMixin
from anytree.exporter import DotExporter
from enum import Enum
import copy
from engineering_notation import EngNumber

from PySpice.Spice.Netlist import Circuit 
from PySpice.Unit import *
from . import models
from .helper import *
from typing import Type


class PNode(NodeMixin):
    def __init__(self, name, parent=None, children=None, model=None, multiplier=1, comment="", hideChildren=False, isModule=False):
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
        self.isModule = isModule
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
    def CC_LOAD(cls, name, current, parent=None, multiplier=1, comment=""):
        return cls(name, model=models.CC(current), parent=parent, comment=comment, multiplier=multiplier)    
    @classmethod
    def RES(cls, name, resistance, parent=None, multiplier=1, comment=""):
        return cls(name, model=models.Res(resistance), parent=parent, comment=comment, multiplier=multiplier)
    @classmethod
    def IN_DC(cls, name, voltage, parent=None, comment=""):
        return cls(name, model=models.INPUT(voltage), parent=parent, comment=comment)
    @classmethod
    def UNREG(cls, name, ratio, efficiency=1, parent=None, comment=""):
        return cls(name, model=models.UNREG(ratio, efficiency), parent=parent, comment=comment)
    @classmethod
    def MODULE(cls, name, multiplier=1, comment="", parent=None):
        return cls(name, parent=parent, multiplier=multiplier, comment=comment, isModule=True)
    # def toModule(self, name, comment=None, multiplier=1, parent=None, hideChildren=True):
    #     module = PNode()
    def Power(self):
        return self.VO * self.IO
    def PowerIn(self):
        return self.VI * self. II
    def Loss(self):
        return (self.VI * self.II) * (1 - self.EF)
    def Voltage(self):
        return self.VO
    def Current(self):
        return self.IO
    def Netlist(self):
        return _Netlist(self)
    def Solve(self):
        return _Solve(self)

def _Netlist(node):
    # Build up netlist
    mycir = Circuit(node.id)
    node: PNode

    # expand netlist for multiplier values
    nodeTemp = copy.deepcopy(node)
    # def nodenamefunc(node): 
        # return "%s %s" % (node.name,node.id)
        # return "%s" % (node.id)
    # DotExporter(nodeTemp,  graph="digraph", nodenamefunc=nodenamefunc, options=[f"rankdir=LR; splines=true; labelloc=t; fontsize=72; nodesep=0.25; ranksep=\"1.2 equally\"; fontsize=48;"]).to_picture("testing2.png")
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
                if node.model.type == NodeType.XFMR:
                    mycir.X(node.id, node.model.name, subcon, node.id, "VO-" + node.id, "IO-" + node.id, "VI-" + node.id, "II-" + node.id, "EF-" + node.id)
                elif node.model.type == NodeType.SINK:
                    mycir.X(node.id, node.model.name, subcon, "VI-" + node.id, "II-" + node.id)
                elif node.model.type == NodeType.INPUT:
                    mycir.X(node.id, node.model.name, node.id, "VO-" + node.id, "IO-" + node.id)
        except Exception as e:
            print(e)
            print(node.name)
            # print(type(node.subcircuit))
            print("Couldn't find subcircuit model :(")
            pass
    # print(mycir)
    return mycir

def _Solve(node):
    cir = _Netlist(node)
    # print(cir)
    simulator = cir.simulator()
    output = simulator.operating_point()
    # back anno parameters to tree from dc op simulation
    for pre, fill, node in RenderTree(node):
        if(node.model.type == NodeType.XFMR):
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
            if(node.model.type == NodeType.SINK):
                node.II = float(output["ii-" + node.id]) 
                node.VI = float(output["vi-" + node.id]) 
        except Exception as e:
                print(e)
                print("Couldn't find parameter")
                pass
        try:
            if(node.model.type == NodeType.INPUT):
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
    # if node.model.type == "XFMR":
    #     style += "fillcolor=lightpink; style=filled"
    # elif node.model.type in ["HEAD"]:
    #     style += "fillcolor=lightpink; style=filled"
    # elif node.model.type == "SINK":
    #     style += "fillcolor=plum; style=filled"
    return style

def nodenamefunc(node): 
    output = ""
    output += "%s" % node.name
    if(node.multiplier > 1):
        output += " [x%d]" % node.multiplier
    if(node.model.type == NodeType.XFMR):
        V = node.VO
        I = node.IO 
        P = V * I
        L = P  / node.EF * (1 - node.EF)
        output += "\n%s\n%sV/%sA → %sW" % (node.model.label, EngNumber(V), EngNumber(I), EngNumber(P))
        output += "\nη=%.2f  ℓ=%sW" % (node.EF, EngNumber(L))
    elif(node.model.type == NodeType.SINK):
        V = node.VI
        I = node.II 
        P = V * I
        output += "\n%s\n%sV/%sA → %sW" % (node.model.label, EngNumber(V), EngNumber(I), EngNumber(P))
    elif(node.model.type == NodeType.INPUT):
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