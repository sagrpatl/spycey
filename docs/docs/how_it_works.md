---
sidebar_position: 2
---

# How It Works

The **spycey** module works by creating a parent/child tree and builds a SPICE netlist for DC operating point analysis. 

Consider the following power tree:
```py
P12V = PNode.IN_DC("P12V0", 12)
P5V0 = PNode.SMPS("P5V0-BUCK", 5, 0.9, P12V)
LOAD = PNode.CC_LOAD("Load", 1, P5V0)

print(P12V.Netlist())
```

Below is the generated netlist. Every node instantiates a subcircuit model for a specific power supply type. Refer to [Models](./models.md) section to see details for the SPICE models. 
```py
.title INPUT_12V_5jA3
.subckt INPUT_12V_5jA3 n1 n3 n4
V1 n1 0 12
BVO n3 0 v=V(n1)
BIO n4 0 v=-I(V1)
.ends INPUT_12V_5jA3

.subckt SMPS_5V_4Fdk n1 n2 n3 n4 n5 n6 n7
V2 n1 n11 0
B1 n11 0 i=-I(V1) * V(n2)/V(n1)
B2 n11 0 i=( V(n2) * -I(V1) * (1-0.9) ) / 0.9 / V(n11)
V1 n2 0 5
BVO n3 0 v=V(n2)
BIO n4 0 v=-I(V1)
BVI n5 0 v=V(n1)
BII n6 0 v=I(V2)
BEF n7 0 v=0.9
.ends SMPS_5V_4Fdk

.subckt LOAD_CC_1A_77Dn n1 n5 n6
B1 n1 0 i=1
BVI n5 0 v=V(n1)
BII n6 0 v=I(B1)
.ends LOAD_CC_1A_77Dn
XINPUT_12V_5jA3 INPUT_12V_5jA3 VO-INPUT_12V_5jA3 IO-INPUT_12V_5jA3 INPUT_12V_5jA3
XSMPS_5V_4Fdk INPUT_12V_5jA3 SMPS_5V_4Fdk VO-SMPS_5V_4Fdk IO-SMPS_5V_4Fdk VI-SMPS_5V_4Fdk II-SMPS_5V_4Fdk EF-SMPS_5V_4Fdk SMPS_5V_4Fdk
XLOAD_CC_1A_77Dn SMPS_5V_4Fdk VI-LOAD_CC_1A_77Dn II-LOAD_CC_1A_77Dn LOAD_CC_1A_77Dn
```

This netlist could be copied into LTspice with the *.op* command and would yield the following output.

**INSERT LTSPICE Screenshot**

The edge and node parameters can also be solved using spycey which is using pyspice and ngspice under the hood.

```py
P12
```