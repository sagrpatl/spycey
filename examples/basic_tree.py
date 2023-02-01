import sys
sys.path.append("../spycey")

import spycey as spcy


P12V = spcy.PNode.IN_DC("P12V0", 12)
P5V0 = spcy.PNode.SMPS("P5V0-BUCK", 5, 0.9, P12V)
LOAD = spcy.PNode.CC_LOAD("Load", 1, P5V0)

spcy.Solve(P12V)
spcy.PowerDotExporter(P12V).to_picture("basic_tree.png")
print(P12V.Netlist())