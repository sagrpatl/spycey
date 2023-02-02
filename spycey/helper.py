import shortuuid
from enum import Enum

def hexID():
    return shortuuid.ShortUUID().random(length=4)

class NodeType(Enum):
    XFMR  = "XFMR"
    SINK  = "SINK"
    INPUT = "INPUT"