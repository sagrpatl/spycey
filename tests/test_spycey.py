import sys
sys.path.append("../spycey")
print(sys.path)

from powertree import *


def inRange(inputVal, val, tol=0.01):
	min = val * (1.0 - tol)
	max = val * (1.0 + tol)
	if(inputVal == val):
		return True
	if( inputVal > min and inputVal < max):
		return True
	else:
		return False

def test_customNodeTest():
	assert True
	pass

def test_complexTree():
	VIN  =  PNode.IN_DC("VIN", 50)
	
	IMB  =  PNode.UNREG("IMB", 4, 0.9).setParent(VIN)
	SMPS =  PNode.SMPS("SMPS", 10, 0.9).setParent(VIN)
	LDO  =  PNode.LDO("LDO", 10).setParent(VIN)
	CPL4 =  PNode.CP_LOAD("CP-LOAD4", 100).setParent(VIN)
	CCL5 =  PNode.CC_LOAD("CC-LOAD5", 100).setParent(VIN)

	CPL1 =   PNode.CP_LOAD("CP-LOAD1", 100).setParent(IMB)
	CCL1 =   PNode.CC_LOAD("CC-LOAD1", 100).setParent(IMB)
	SMPS1 =  PNode.SMPS("SMPS1", 10, 0.9).setParent(IMB)
	LDO1 =   PNode.LDO("LDO1", 10).setParent(IMB)
	CPL2 =   PNode.CP_LOAD("CP-LOAD2", 100).setParent(SMPS)
	CCL2 =   PNode.CC_LOAD("CC-LOAD2", 100).setParent(SMPS)
	IMB2 =   PNode.UNREG("IMB2", 4, 0.9).setParent(SMPS)
	LDO2 =   PNode.LDO("LDO2", 10).setParent(SMPS)
	CPL3 =   PNode.CP_LOAD("CP-LOAD3", 100).setParent(LDO)
	CCL3 =   PNode.CC_LOAD("CC-LOAD3", 100).setParent(LDO)
	SMPS3 =  PNode.SMPS("SMPS3", 10, 0.9).setParent(LDO)
	IMB3  =  PNode.UNREG("IMB3", 4, 0.9).setParent(LDO)

	CPL21 = PNode.CP_LOAD("CP-LOAD21", 100).setParent(SMPS1)
	CCL21 = PNode.CC_LOAD("CC-LOAD21", 100).setParent(SMPS1)
	CPL31 = PNode.CP_LOAD("CP-LOAD31", 100).setParent(LDO1)
	CCL31 = PNode.CC_LOAD("CC-LOAD31", 100).setParent(LDO1)
	CPL12 = PNode.CP_LOAD("CP-LOAD12", 100).setParent(IMB2)
	CCL12 = PNode.CC_LOAD("CC-LOAD12", 100).setParent(IMB2)
	CPL32 = PNode.CP_LOAD("CP-LOAD32", 100).setParent(LDO2)
	CCL32 = PNode.CC_LOAD("CC-LOAD32", 100).setParent(LDO2)
	CPL23 = PNode.CP_LOAD("CP-LOAD23", 100).setParent(SMPS3)
	CCL23 = PNode.CC_LOAD("CC-LOAD23", 100).setParent(SMPS3)
	CPL13 = PNode.CP_LOAD("CP-LOAD13", 100).setParent(IMB3)
	CCL13 = PNode.CC_LOAD("CC-LOAD13", 100).setParent(IMB3)
	
	# PowerDotExporter(VIN, prune=False).to_picture("myTree2.png")
	VIN.Solve()
	PowerDotExporter(VIN).to_picture("complex_tree.png")
	print(VIN.Netlist())

	assert inRange(VIN.Power()  ,25.918e+3 )
	assert inRange(VIN.Voltage(), 50)
	assert inRange(VIN.Current(), 518.360E+0)
	assert inRange(VIN.Loss()   , 0)
    
	assert inRange(IMB.Power()  , 3947.2)
	assert inRange(IMB.Voltage(), 12.5)
	assert inRange(IMB.Current(), 315.78)
	assert inRange(IMB.Loss()   , 438.58)

	assert inRange(SMPS.Power()  , 2588.9)
	assert inRange(SMPS.Voltage(), 10)
	assert inRange(SMPS.Current(), 258.89)
	assert inRange(SMPS.Loss()   , 287.65)

	assert inRange(LDO.Power()  , 2711.1)
	assert inRange(LDO.Voltage(), 10)
	assert inRange(LDO.Current(), 271.11)
	assert inRange(LDO.Loss()   , 10844)

	
	assert inRange(SMPS1.Power()  , 1100 )
	assert inRange(SMPS1.Voltage(), 10 )
	assert inRange(SMPS1.Current(), 110 )
	assert inRange(SMPS1.Loss()   , 122.22)

	assert inRange(LDO1.Power()  ,1100 )
	assert inRange(LDO1.Voltage(), 10 )
	assert inRange(LDO1.Current(), 110 )
	assert inRange(LDO1.Loss()   ,275 )  

	assert inRange(IMB2.Power()  , 350)
	assert inRange(IMB2.Voltage(), 2.5)
	assert inRange(IMB2.Current(), 140)
	assert inRange(IMB2.Loss()   , 38.889)

	assert inRange(LDO2.Power()  , 1100)
	assert inRange(LDO2.Voltage(), 10)
	assert inRange(LDO2.Current(), 110)
	assert inRange(LDO2.Loss()   , 0)

	assert inRange(SMPS3.Power()  , 1100 )
	assert inRange(SMPS3.Voltage(), 10)
	assert inRange(SMPS3.Current(), 110)
	assert inRange(SMPS3.Loss()   , 122.22)

	assert inRange(IMB3.Power()  , 350)
	assert inRange(IMB3.Voltage(), 2.5)
	assert inRange(IMB3.Current(), 140)
	assert inRange(IMB3.Loss()   , 38.889)


test_complexTree()