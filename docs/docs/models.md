---
sidebar_position: 4
---

import LDO from "./img/LDO.svg"
import SMPS from "./img/SMPS.svg"
import OBS from "./img/observation.svg"
import UNREG from "./img/unreg.svg"

# Models

Node and edge parameters are calculated using DC operating point analysis in SPICE. There are 3 basic primitives used to parse a netlist in **spycey**.

* **Transformer (XFMR)**: 
    Used to model power supply types. It has an input node to connect to parent supply and a output node to connect loads and supplies.
* **Sink (SINK)**:
    Used to model load types (constant current, constant power, resistance, etc.)
* **Input (INPUT)**: Specifies an input DC source.

Each model has *obersvation nodes* to capture input/output parameters which are used to annotate power trees. 

Currently there aren't any AC types. They can be incorporated, but would need to be modelled in DC for DC operating point analysis to work.


## LDO
### Parameters

$$
V_{out} : Output\space Voltage \\
$$
### Circuit Elements
$$
B1: I=-I(V1)
$$

### Observation Nodes
$$
\begin{aligned}
BVO&: V=V(n2) \\
BIO&: V=-I(V1) \\
BVI&: V=V(n1) \\
BII&: V=I(B1) \\
BEF&: V=V(n2)/V(n1) \\
\end{aligned}
$$

<LDO class="img-center" style={{ maxHeight: 200 }} />



## SMPS
### Parameters

$$
V_{out} : Output\space Voltage \\
\eta : Efficiency
$$

### Circuit Elements
$$
V1: V=V_{out} \\ 
B1: I=- \frac {I(V1) \cdot V(n2)} {V(n1)} \\
B2: I=- \frac{V(n2) \cdot I(V1)} {V(n11)} \cdot  \frac {(1-\eta)} {\eta} \\
$$

### Obervation Nodes
$$
\begin{aligned}
BVO&: V=V(n2) \\
BIO&: V=-I(V1) \\
BVI&: V=V(n1) \\
BII&: V=I(V2) \\
BEF&: V=\eta \\
\end{aligned}
$$

<SMPS class="img-center" style={{ maxHeight: 250 }} />

## Unregulated

### Parameters

$$
\begin{aligned}
n &: input\space to\space output\space ratio\\
\eta &: Efficiency
\end{aligned}
$$

### Circuit Elements
$$
\begin{aligned}
B1: I&=I(B3)/n \\ 
B2: I&=-\frac {V(n2) * I(B3)} {V(n11)} \cdot \frac {1-\eta} {\eta} \\
B3: V&=\frac {V(n11)} {n}
\end{aligned}
$$

### Obervation Nodes
$$
\begin{aligned}
BVO&: V=V(n2) \\
BIO&: V=-I(B3) \\
BVI&: V=V(n1) \\
BII&: V=I(V2) \\
BEF&: V=\eta \\
\end{aligned}
$$

<UNREG class="img-center" style={{ maxHeight: 250 }}/>


