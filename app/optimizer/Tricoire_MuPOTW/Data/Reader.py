import re
import pickle
import os
from .Problem import Customer, Info
from pathlib import Path
from .t import *

DATASET_PATH = Path(__file__).parent.absolute() / "Datasets"
SOLUTION_PATH = Path(__file__).parent.absolute() / "Solution"
def read_customers(filename):
    customers = []
    full_path = os.path.join(DATASET_PATH, filename)
    try:
        with open(full_path) as f:
            for _ in range(9):
                next(f)
            for line in f:
                match = re.findall(r"(\d+)", line)
                info = Info()
                info.id = int(match[0])
                info.x = int(match[1])
                info.y = int(match[2])
                info.value = float(match[3])
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

def is_customer_useless(customer: Customer):
    startTime = customer.info.startTime
    endTime = customer.info.endTime
    serviceTime = customer.info.serviceTime

    if startTime + serviceTime > endTime or endTime - serviceTime < startTime:
        return True
    else:
        return False
        
def read_dist_matrix(filename):
    full_path = DATASET_PATH / filename
    with open(full_path, 'rb') as fp:
        itemList = pickle.load(fp)

    return itemList

def read_solution(filename):
    full_path = SOLUTION_PATH / filename
    with open(full_path, 'rb') as fp:
        itemList = pickle.load(fp)

    return itemList

