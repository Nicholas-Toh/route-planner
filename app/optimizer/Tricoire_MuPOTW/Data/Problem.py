from typing import List
import copy

class Info:
    def __init__(self):
        self.id = 0
        self.x = 0
        self.y = 0
        self.value = 0
        self.startTime = 0
        self.endTime = 0
        self.serviceTime = 0
        self.taskID = None
        self.mandatory = True
        #self.timeWindows #TODO: Implement multiple time windows
        
class Customer:
    timeMatrix = []
    def __init__(self, info: Info):
        self.info = info
        
    def getTravelTime(self, node: 'Customer'): #get travel times
        return self.timeMatrix[self.info.id][node.info.id]

    def shallowCopy(self, customer: 'Customer'):
        info = Info()
        info.id = self.info.id
        info.x = self.info.x
        info.y = self.info.y
        info.value = self.info.value
        info.startTime = self.info.startTime
        info.endTime = self.info.endTime
        info.serviceTime = self.info.serviceTime
        info.mandatory = self.info.mandatory
        info.taskID = self.info.taskID
        
        temp = Customer(info)
        temp.timeMatrix = self.timeMatrix
        return temp
    
    def copy(self):
        return self.shallowCopy(self)

class Problem:
    def __init__(self):
        self.depot = None
        self.customers = []
        self.unplannedCustomers = []
        self.routeDurationConstraint = None
        self.planningHorizon = 7

    def setCustomers(self, customers: List[Customer], depot = 0):
        self.customers = customers
        self.depot = customers[depot]
        self.customers.pop(depot)

    def getCustomer(self, id: int):
        for cust in self.customers:
            if cust.id == id:
                return cust
        raise CustomerNotFoundException("Customer not found")

    def getCustomers(self):
        customers = []
        for customer in self.customers:
            customers.append(customer.copy())
    
        return customers

    def getUnplannedCustomers(self):
        customers = []
        for customer in self.unplannedCustomers:
            customers.append(customer.copy())
    
        return customers

    def setUnplannedCustomers(self, customers):
        self.unplannedCustomers = customers
        
    class CustomerNotFoundException:
        def __init__(self, message):
            self.message = message
