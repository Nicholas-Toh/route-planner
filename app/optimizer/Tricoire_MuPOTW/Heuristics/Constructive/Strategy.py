from enum import Enum

class SolomonStrategy(Enum):
    HighestDemand = 1
    FarthestDistance = 2
    EarliestReadyTime = 3
    SortedHighestDemand = 4
