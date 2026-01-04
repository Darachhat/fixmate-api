from enum import Enum

class DisputeStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
