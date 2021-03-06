import pickle
import re
from pathlib import Path

DATASET_PATH = Path(__file__).parent.absolute() / "Datasets"

def generate_dist_matrix(customers):
    dist_matrix = []
    for customer in customers:
        temp = []
        for customer2 in customers:
            dist = round(((customer.info.x - customer2.info.x)**2 + (customer.info.y - customer2.info.y)**2)**(1/2),3) 
            temp.append(dist)
        dist_matrix.append(temp)
    return dist_matrix

def output_dist_matrix(data, filename):
    full_path = DATASET_PATH / filename
    with open(full_path, 'r+b') as f:
        pickle.dump(data, f)

def read_dist_matrix(filename):
    full_path = DATASET_PATH / filename
    print(full_path)

    with open(full_path, 'rb') as fp:
        itemList = pickle.load(fp)

    return itemList

def read_customers_zhang(filename):
    customers = []
    full_path = DATASET_PATH / filename
    try:
        with open(full_path) as f:
            for _ in range(6):
                next(f)
            for line in f:
                match = re.findall(r"(\d+)", line)
                info = Info()
                info.id = int(match[0])
                info.x = int(match[1])
                info.y = int(match[2])
                info.value = int(match[3])
                info.startTime = int(match[4])
                info.serviceTime = int(match[6])
                if info.id != 0:
                    info.endTime = int(match[5])+info.serviceTime
                else:
                    info.endTime = int(match[5])
                    
                
                customer = Customer(info)

                ##if not is_customer_useless(customer):
                customers.append(customer)
                    
        return customers
    except FileNotFoundError:
        print(full_path)
        return None

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
        
        temp = Customer(info)
        temp.timeMatrix = self.timeMatrix
        return temp
    
    def copy(self):
        return self.shallowCopy(self)
    
cust = read_customers_zhang('c102_100.txt')
mat = generate_dist_matrix(cust)

output_dist_matrix(mat, 'c102_100_distmatrix.txt')
