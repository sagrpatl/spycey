---
sidebar_position: 2
---

import LDO from "./img/LDO.svg"
import SMPS from "./img/SMPS.svg"
import OBS from "./img/observation.svg"

# Models

## LDO
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
B1: I=-I(V1) * V(n2)/V(n1) \\
B2: I=V(n2) * -I(V1) * \frac {(1-\eta)} {\eta} /V(n11)
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




