from app.optimizer.Tricoire_MuPOTW.Data.Problem import Problem, Customer, Info
from app.optimizer.Tricoire_MuPOTW.Heuristics.Constructive.Solomon import SolomonConstructive
from app.optimizer.Tricoire_MuPOTW.Heuristics.Constructive.Strategy import SolomonStrategy
from app.optimizer.Tricoire_MuPOTW.Heuristics.VNS.VNS import variable_neighborhood_search
from app.optimizer.Tricoire_MuPOTW.Data.DistanceMatrixGenerator import generate_dist_matrix
from app.optimizer.Tricoire_MuPOTW.Visualization.GanttChart import plot
from flask import session

FILENAME = "c102_100"

info = Info()
info.id = 0 #0	40	50	0	0	480	0
info.x = 40
info.y = 50
info.value = 0
info.startTime = 60*9
info.endTime = 480+60*9
info.serviceTime = 0
depot = Customer(info)

def printCustomers(route):
    print([cust.info.id for cust in route])

def printSolutionCustomers(solution):
    for route in solution.routes:
        printCustomers(route.nodeList)

def solve(config):
    mandatory_customers = [depot] + config.mandatory_customers
    optional_customers = [depot] + config.optional_customers

    if (not mandatory_customers or len(mandatory_customers) < 2) and (not optional_customers or len(optional_customers) < 2):
        raise ValueError("No customers to solve")

    dist_matrix = generate_dist_matrix([depot] + config.mandatory_customers + config.optional_customers)
    print(dist_matrix)
    for cust in optional_customers:
        cust.timeMatrix = dist_matrix
        cust.info.mandatory = False
        print(cust.info.startTime)

    optional_customers.sort(key=lambda x: x.info.value)
    optional_problem = Problem()
    optional_problem.setCustomers(optional_customers, 0)
    constructive = SolomonConstructive()
    optional_problem.planningHorizon = 5
    
    solution = None
    if mandatory_customers and len(mandatory_customers) >= 2:
        for cust in mandatory_customers:
            cust.timeMatrix = dist_matrix
            cust.info.mandatory = True
            
        mandatory_problem = Problem()
        mandatory_problem.setCustomers(mandatory_customers, 0)
        mandatory_problem.planningHorizon = 5
        solution = constructive.solve(mandatory_problem, SolomonStrategy.FarthestDistance)
        solution = constructive.solveOptional(optional_problem, solution)   
        optional_problem.unplannedCustomers += mandatory_problem.getUnplannedCustomers()
    else:
        solution = constructive.solveOptional(optional_problem)

    solution.optimize()
 
    solution = variable_neighborhood_search(solution, optional_problem, max_iterations=300)
    solution.optimize()
    schedule = convert_solution(solution)
    
    return schedule

    
    print("Time taken for first solution:", solution.calculateTime())
    print("Distance of first solution:", sum(solution.calculateDistance()))
    print("Value of first solution:", solution.routes[0].calculateValue())
    print("Number of customers visited:", sum([len(route.solution) for route in solution.routes]))
def convert_solution(solution):
    schedule = {}
    for i, route in enumerate(solution.routes):
        schedule[i] = []
        for j in range(1, len(route.solution)-1):
            if len(route.dominantSolution) == len(route.nodeList)-2:
                customer = route.solution[j]
                schedule[i].append(
                {
                    'id': customer.info.id, #outlet ID
                    'task_id': customer.info.taskID,
                    'start_time': route.dominantSolution[j-1]-customer.info.serviceTime,
                    'end_time': route.dominantSolution[j-1],
                    'travel_time': customer.info.serviceTime - route.nodeList[j].info.serviceTime,
                    'total_service_time': customer.info.serviceTime,
                    'estimated_service_time': route.nodeList[j].info.serviceTime,
                    'value': customer.info.value
                })
    return schedule