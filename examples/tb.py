import sys
sys.path.append("../spycey")

from spycey import *
import models

def tree(n):
    top = PNode.IN_DC("VIN", 52)
    n1  = PNode.LDO("P1V0", 1).setParent(top)
    n5  = PNode.LDO("P0V5", 0.5).setParent(n1)
    n7  = PNode.SMPS("P5V0-BUCK", 5, 0.9).setParent(top).setMultiplier(n)
    n16 = PNode.RES("333", 1).setParent(n7)

    n3 =  PNode.RES("LOAD2", 0.5).setParent(n1)
    n4 =  PNode.RES("LOAD3", 0.25).setParent(n1)

    n6 =  PNode.RES("LOAD4", 0.25).setParent(n5)
    n9 =  PNode.CP_LOAD("CP-LOAD", 100).setParent(n5)
    n10 = PNode.UNREG("UNREG", 4, 0.9).setParent(top)
    n15 = PNode.CP_LOAD("DD", 100).setParent(n10)
    n15 = PNode.RES("DD", 100).setParent(n10)

    n10 = PNode("PT", model=models.CCVS()).setParent(top).setMultiplier(3)
    n12 = PNode.UNREG("UNREG", 5).setParent(n10)

    n13 = PNode.CP_LOAD("loadd", 2000).setParent(n12)
    n11 = PNode.RES("loadd", 0.5).setParent(n10) # 48V
    
    # n7  = PNode.SMPS("P5V0-BUCK", 5, 0.9).setParent(top)
    # n11 = PNode.RES("loadd", 1).setParent(n7) # 48V
    return top

a = tree(3)
print(a)