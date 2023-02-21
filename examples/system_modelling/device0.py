import sys
sys.path.append("../../")

from spycey.powertree import PowerTreeDevice, PState,PNode,PowerDotExporter


class Device0(PowerTreeDevice):
    active = PState("Active", freq=11)
    idle = PState("Idle", freq=111)

    def PowerTreeHook(inputState,BLEEP=11):
        P12V = PNode.IN_DC("P12V0", 12)
        # P12V = PNode.SMPS("P12V0", 12)
        P5V0 = PNode.SMPS("P5V0-BUCK", 5, 0.9, P12V)
        if(inputState == Device0.active):
            LOAD = PNode.CC_LOAD("Load", 10, P5V0)
        if(inputState == Device0.idle):
            LOAD = PNode.CC_LOAD("Load", 1, P5V0)
        return P12V
        

if __name__ == "__main__":
    print("Hello")
    for state in MyDevice:
        tree = state()
        tree.Solve()
        print(tree.Power())
        PowerDotExporter(tree).to_picture("MyDevice - %s.png" % state.name)
