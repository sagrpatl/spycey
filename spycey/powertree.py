# import numpy as np
# import matplotlib.pyplot as plt
import uuid
import PySpice.Logging.Logging as Logging
# logger = Logging.setup_logging(logging_level='WARNING')
logger = Logging.setup_logging()
from anytree import RenderTree, NodeMixin
from anytree.exporter import DotExporter
from enum import Enum, auto
import copy
from engineering_notation import EngNumber
import math

from PySpice.Spice.Netlist import Circuit 
from PySpice.Unit import *
from . import models
from .helper import *
from typing import Type, Iterable
import inspect
from functools import partial

class paramStyle(Enum):
    DC = auto()
    AC3PH = auto()
class PNode(NodeMixin):
    def __init__(self, name, parent=None, children=None, model=None, multiplier=1, comment="", hideChildren=False, isModule=False, paramStyle = paramStyle.DC):
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
        self.hideChildren=hideChildren
        self.paramStyle = paramStyle
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
    def IN_DC(cls, name, voltage, parent=None, comment="", efficiency=1):
        return cls(name, model=models.INPUT(voltage, efficiency), parent=parent, comment=comment)
    @classmethod
    def IN_3PH(cls, name, voltage, pf=1, parent=None, comment=""):
        return cls(name, model=models.INPUT(voltage), parent=parent, comment=comment, paramStyle=paramStyle.AC3PH)
        # return cls(name, model=models.INPUT_3PH(voltage,pf), parent=parent, comment=comment)
    @classmethod
    def PASSTHRU(cls, name, parent=None, comment="", multiplier=1):
        return cls(name, model=models.PT(), parent=parent, multiplier=multiplier, comment=comment)
    @classmethod
    def UNREG(cls, name, ratio, efficiency=1, parent=None, comment="", multiplier=1):
        return cls(name, model=models.UNREG(ratio, efficiency), parent=parent, comment=comment, multiplier=multiplier)
    @classmethod
    def MODULE(cls, name, multiplier=1, comment="", parent=None):
        return cls(name, parent=parent, multiplier=multiplier, comment=comment, isModule=True)
    def toModule(self, name, parent=None, comment="", multiplier=1, hideChildren=True):
        
        # self.isModule = True
        # self.multiplier = multiplier
        # self.hideChildren=hideChildren
        if comment == "":
            try:
                if(self.injectedName is not None):
                    # self.comment =  self.injectedName
                    self.comment = self.injectedName
            except:
                pass
        moduleNode = self.PASSTHRU(name, multiplier=multiplier, parent=parent)
        # moduleNode.children = self.children
        moduleNode.isModule = True
        moduleNode.multiplier = multiplier
        moduleNode.hideChildren = hideChildren
        moduleNode.name = name
        self.parent = moduleNode
        return moduleNode
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
                    mycir.X(node.id, node.model.name, node.id, "VO-" + node.id, "IO-" + node.id, "EF-" + node.id)
        except Exception as e:
            print(e)
            print(node.name)
            # print(type(node.subcircuit))
            print("Couldn't find subcircuit model :(")
            pass
    # print(mycir)
    return mycir

def _Solve(node : PNode):
        # Bypass any IN_DC with a parent
    for pre, fill, inode in RenderTree(node):
        if inode.model.type == NodeType.INPUT:
            if inode.parent is not None:
                # print("found a node to bypass", inode.name, inode.parent)
                inode.model = models.PT()
    cir = _Netlist(node)
    # print(cir)
    simulator = cir.simulator()
    output = simulator.operating_point()
    # back anno parameters to tree from dc op simulation
    for pre, fill, node in RenderTree(node):
        # Hides children, Note: if solver is run again results will be incorrect because children are orphaned
        
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
                node.EF = float(output["ef-" + node.id])
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
    return style



def nodeVI(V,I,style=paramStyle.DC):
    if(style==paramStyle.AC3PH):
        P = V * I
        Iph = P / (math.sqrt(3) * V)
        output = "\n%sVφ/%sAφ → %sW" % (EngNumber(V), EngNumber(Iph), EngNumber(P))
        return output
    else: # DC Case
        P = V * I
        output = "\n%sV/%sA → %sW" % (EngNumber(V), EngNumber(I), EngNumber(P))
        return output
        
def nodeEffLoss(V,I,EF):
    if(EF < 1):
        P = V * I
        L = P  /EF * (1 - EF)
        output = "\nη=%.2f  ℓ=%sW" % (EF, EngNumber(L))
        return output
    else:
        return ""



def nodenamefunc(node): 
    output = ""
    output += "%s" % node.name
    if(node.multiplier > 1):
        output += " [x%d]" % node.multiplier

    if(node.isModule):
        V = node.VO
        I = node.IO 
        P = V * I
        L = P  / node.EF * (1 - node.EF)
        output += "\n%s\n%sV/%sA → %sW" % (node.model.label, EngNumber(V), EngNumber(I), EngNumber(P))
        # output += "\nη=%.2f  ℓ=%sW" % (node.EF, EngNumber(L))
    else:
        if(node.model.type == NodeType.XFMR):
            output += "\n%s" % (node.model.label)
            output += nodeVI(node.VO, node.IO, style=node.paramStyle)
            output += nodeEffLoss(node.VO, node.IO, node.EF)
        elif(node.model.type == NodeType.SINK):
            output += "\n%s" % (node.model.label)
            output += nodeVI(node.VI, node.II, style=node.paramStyle)
        elif(node.model.type == NodeType.INPUT):
            output += "\n%s" % (node.model.label)
            output += nodeVI(node.VO, node.IO, style=node.paramStyle)
            output += nodeEffLoss(node.VO, node.IO, node.EF)
        # else:
            # output += "%s" % (node.name)
    if(node.comment != ""):
        output += "\n%s" % node.comment
    return output

def edgeCurrent(node, child):
    if(node.paramStyle == paramStyle.AC3PH):
        P = child.VI * child.II
        Iph = P / (math.sqrt(3) * child.VI)
        return  str(EngNumber(Iph)) + "Aφ"
    else: # DC default case
        return str(EngNumber(child.II)) + "A"

def edgeattrfunc(node, child):
    if child.multiplier > 1:
        return 'label="%s [x%d]"' % (edgeCurrent(node,child), child.multiplier)
        # return 'label="%sA [x%d]"' % (EngNumber(child.II), child.multiplier)
    
    return 'label="%s"' % (edgeCurrent(node,child))

class PowerDotExporter(DotExporter):
    
    def __init__(self, node):
        node.Solve()
        # Copy tree to perform any destructive actions (ex. pruning)
        _node = copy.deepcopy(node)
        __node : PNode
        for pre, fill, __node in RenderTree(_node):
            if __node.hideChildren:
                __node.children = []

        super(PowerDotExporter, self).__init__(_node,  graph="digraph",nodenamefunc=nodenamefunc, nodeattrfunc=nodeattrfunc, edgeattrfunc=edgeattrfunc, options=[f"rankdir=LR; splines=true; labelloc=t; fontsize=72; nodesep=0.25; ranksep=\"1.2 equally\"; fontsize=48;"])

def PowerDotOutput(node):
    src = ""
    for line in PowerDotExporter(node):
        src += line
    return src

def tagPState(input):
    def setPState(func):
        def wrapper(*args, **kwargs):
            # Check kwargs for any matches in input
            # Override matching attributes in input with kwargs 
            # Strip kwargs of matching keys with input
            undo = {}
            unionAttrs = set(dir(input)).intersection(set(kwargs.keys()))
            for key in unionAttrs:
                # Type check between kwargs and input
                if( type(kwargs[key]) == type(getattr(input,key))):
                    undo[key] = getattr(input,key)
                    setattr(input, key, kwargs[key])
                else:
                    raise TypeError("Type mismatch for injected parameter %s. Got %s, but was expecting %s" % (key, type(kwargs[key]), type(getattr(input,key))))
                del kwargs[key]
            result = func(*args, **kwargs)
            # Restore cls object
            for k,v in undo.items():
                setattr(input,k, v)
            if not isinstance(result, PNode):
                # Raise exception if return value is not PowerTreeNode
                raise TypeError("Return value of PowerTreeHook is not PNode. Please check function.")
            result.injectedName = input.name
            return result
        return wrapper
    return setPState

class PState:
    def __init__(self, name,**kwargs):
        self.__name = name
        self.__dict__.update(kwargs)
    def __str__(self):
        return self.__name
    def __eq__(self, other):
        return self.name == other.name
    @property
    def name(self):
        return self.__name
    def __repr__(self): 
        return "PowerState(%s)" % self.name
    def __call__(self, *args, **kwargs) -> PNode:
        return self.callback(*args, **kwargs)
    def callback(self, *args, **kwargs):
        pass

class DeviceMeta(type):
    def __new__(mcs, name, bases, attrs):
        if name == "PowerTreeDevice":
            return super().__new__(mcs, name, bases, attrs)
        
        if "PowerTreeHook"  not in attrs:
            raise TypeError(f"PowerTreeHook not defined in {name} class. Please add PowerTreeHook or refer to documentation.")
        else:
            # Decorate with staticmethod. Not an instance method
            attrs["PowerTreeHook"]=staticmethod(attrs["PowerTreeHook"])

        power_states = {}
        for k,v in attrs.items():
            if isinstance(v, PState):
                power_states[k] = v
        if(len(power_states) == 0):
            raise TypeError(f"{name} is missing PState(s). Please define at least 1. Refer to documentation.")                
        cls = type.__new__(mcs, name, bases, attrs)

        cls.__power_states = power_states
        
        
        # Attach Callback, and check all PowerState objects for consistency. TODO: Refactor by directly updating __call__ in PState.
        # TODO: Refactor pi into dictionary loop
        ukeys = []
        pi = 0
        pstate_keys = []
        for k,v in power_states.items():
            pstate = getattr(cls, k)
            if(pi == 0):
                pstate_keys = dir(pstate)
            else:
                symDiff = set(pstate_keys).symmetric_difference(set(dir(pstate)))
                ukeys.extend(list(symDiff))
            
            powerTree = partial(cls.PowerTreeHook,pstate)
            # Sets comment for return value 
            powerTree = tagPState(pstate)(powerTree)
            setattr(pstate, "callback", powerTree)
            
            pi+=1
        
        if(len(set(ukeys)) > 0):
            raise TypeError("Inconsistent entries for PowerState objects. Please check each have the same types of arguments.\n" \
                + "%s's PowerState objects have the following mismatches: %s" % (name, ukeys))
        
        # Check if PowerTreeHook's args don't mangle PowerState attributes
        _uVal = set(inspect.getfullargspec(cls.PowerTreeHook).args).intersection(set(pstate_keys))
        if(len(_uVal) > 0):
            raise TypeError("Arguments in PowerTreeHook intersect with PowerState objects. Please rename %s in PowerStateHook." % _uVal)
        return cls
                
    def __iter__(cls) -> Iterable[PNode]:
        # Get PState objects from class
        pstate = []
        for key in dir(cls):
            if(isinstance(getattr(cls,key), PState)):
                pstate.append(getattr(cls,key))
        return (item for item in pstate)

class PowerTreeDevice(metaclass=DeviceMeta):
    pass
