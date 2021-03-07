from enum import Enum

class Zone(str, Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'

class TaskStatus(str, Enum):
    OPEN = "OPEN" #NOT ASSIGNED, NOT EXPIRED
    ASSIGNED = "ASSIGNED" #ASSIGNED, NOT EXPIRED
    EXPIRED = "EXPIRED" #NOT ASSIGNED, EXPIRED
    COMPLETED = "COMPLETED" #ASSIGNED, COMPLETED
    SCHEDULED = "SCHEDULED" #ASSIGNED, SCHEDULED BUT NOT COMPLETED
    INCOMPLETE = "INCOMPLETE" #ASSIGNED,  NOT COMPLETED AND EXPIRED

class Day(str, Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
    
class TaskType(str, Enum):
    MANDATORY = "Mandatory"
    CUSTOM = "Custom"
    

class Role(str, Enum):
    SALES_REP = "Sales Rep"
    SALES_REP_LEAD = "Sales Rep Lead"