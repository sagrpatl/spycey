from device0 import Device0
import sys
sys.path.append("../../")

from spycey.powertree import PNode, PowerDotExporter

P12V = PNode.IN_DC("P12V0", 13)
# P5V0 = PNode.SMPS("P5V0-BUCK", 5, 0.9, P12V)
Device0.active().toModule("Device0", parent=P12V)



P12V.Solve()
# print(P12V.Netlist())
PowerDotExporter(P12V).to_picture("combined.png")