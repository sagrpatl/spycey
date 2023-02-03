import sys
sys.path.append("../")

from spycey.powertree import PNode, PowerDotExporter


P12V = PNode.IN_DC("P12V0", 12)
P5V0 = PNode.SMPS("P5V0-BUCK", 5, 0.9, P12V)
LOAD = PNode.CC_LOAD("Load", 1, P5V0)

# P5V01 = PNode.IN_DC("P12V0", 12, parent=)
# P5V0 = PNode.SMPS("P5V0-BUCK", 5, 0.9, P12V)
# LOAD = PNode.CC_LOAD("Load", 1, P5V0)

P12V.Solve()
PowerDotExporter(P12V).to_picture("basic_tree.png")
print(P12V.Netlist())