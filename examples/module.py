import sys
sys.path.append("../")

from spycey.powertree import PNode, PowerDotExporter


P12V = PNode.IN_DC("P12V0", 12)
P5V0 = PNode.SMPS("P5V0-BUCK", 5, 0.9, P12V)
LOAD = PNode.CC_LOAD("Load", 1, P5V0, multiplier=2)


P5V01 = PNode.SMPS("P5V0-BUCK2", 5, 0.9, P12V, multiplier=2)
# P5V01.isModule = True
LOAD2 = PNode.CC_LOAD("Load2", 1, P5V01)


P12V.Solve() ## TODO: if this isn't run division by zero error when generating node data. need to add excepctions for that 

PowerDotExporter(P12V).to_picture("module.png")
# print(P12V.Netlist())