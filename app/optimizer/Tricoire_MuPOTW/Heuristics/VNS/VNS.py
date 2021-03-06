############################################################################

# Created by: Prof. Valdecy Pereira, D.Sc.
# UFF - Universidade Federal Fluminense (Brazil)
# email:  valdecy.pereira@gmail.com
# Course: Metaheuristics
# Lesson: Variable Neighborhood Search

# Citation: 
# PEREIRA, V. (2018). Project: Metaheuristic-Local_Search-Variable_Neighborhood_Search, File: Python-MH-Local Search-Variable Neighborhood Search.py, GitHub repository: <https://github.com/Valdecy/Metaheuristic-Local_Search-Variable_Neighborhood_Search>

############################################################################

import random

from ...Utils.RouteFunctions import *
from .TSP3Opt import tsp_3_opt
from ..Constructive.Solomon import SolomonConstructive

CROSS_EXCHANGE_START = 1
OPT_EXCHANGE_1_START = 9
OPT_EXCHANGE_2_START = 13
END = 18

# Function: Variable Neighborhood Search
def variable_neighborhood_search(solution, problem, max_last_accepted_dur=16000, max_iterations=20000): #max iterations without improvement
    count = 0
    lastAccepted = 0
    bestSolution = solution
    constructive = SolomonConstructive()
    while lastAccepted < max_last_accepted_dur and count < max_iterations:
        for i in range(CROSS_EXCHANGE_START, END):
            unroutedCustomers = problem.getUnplannedCustomers()
            candidate = bestSolution.copy()
            feasible = False
            if i < OPT_EXCHANGE_1_START:
                routeIdx1, routeIdx2 = crossExchange(candidate.routes, i)
                tsp_3_opt(problem.depot.info.id, candidate.routes[routeIdx1].nodeList[:-1])
                tsp_3_opt(problem.depot.info.id, candidate.routes[routeIdx2].nodeList[:-1])
                feasible = candidate.routes[routeIdx1].isFeasible() and candidate.routes[routeIdx2].isFeasible()
            if i < OPT_EXCHANGE_2_START and i >= OPT_EXCHANGE_1_START:
                #print("OPT1", "Neighborhood: ", i, len(unroutedCustomers))
                routeIdx = optExchange1(candidate.routes, unroutedCustomers, i)
                #print(len(unroutedCustomers), len(candidate.routes[routeIdx].nodeList))
                tsp_3_opt(problem.depot.info.id, candidate.routes[routeIdx].nodeList[:-1])
                feasible = candidate.routes[routeIdx].isFeasible()
            if i >= OPT_EXCHANGE_2_START and i < END:
                #print("OPT2",  "Neighborhood: ", i, len(unroutedCustomers))
                routeIdx = optExchange2(candidate.routes, unroutedCustomers, i)
                #print(len(unroutedCustomers), len(candidate.routes[routeIdx].nodeList))
                candidate, unroutedCustomers = constructive.sequentialBestInsert(unroutedCustomers, candidate, routeIdx)
                #print(len(unroutedCustomers), len(candidate.routes[routeIdx].nodeList))
                feasible = candidate.routes[routeIdx].isFeasible()

            if feasible:
                #print("feasible")
                ascending = True if lastAccepted >= 8000 else False
                if acceptanceDecision(bestSolution, candidate, i, "profit", ascending):
                    #print("Accepted")
                    #print(sum(candidate.calculateValue()), sum(bestSolution.calculateValue()))
                    bestSolution = candidate
                    lastAccepted = -1
                    #print(len(unroutedCustomers), len(problem.unplannedCustomers))
                    problem.setUnplannedCustomers(unroutedCustomers)
                    #print(len(unroutedCustomers), len(problem.unplannedCustomers))
                    break
            else:
                #print("infeasible")
                a = 1
                
        count = count + 1
        lastAccepted = lastAccepted + 1
        
        print("Iteration = ", count, "-> Distance ", sum(bestSolution.calculateDistance()), "Value", sum(bestSolution.calculateValue()))
    return bestSolution

def crossExchange(routes, neighborhood):
    if len(routes) < 2:
        raise ValueError("There must be at least 2 routes for cross exchange")

    if neighborhood < CROSS_EXCHANGE_START or neighborhood >= OPT_EXCHANGE_1_START:
        raise ValueError(f"Neighborhood size of cross exchange must be between {CROSS_EXCHANGE_START} and {OPT_EXCHANGE_1_START-1}")
    minLength1 = 1
    minLength2 = 0
    routeIdx1 = random.randint(0, len(routes)-1)
    routeIdx2 = random.randint(0, len(routes)-1)
    #print(len(routes))
    while (routeIdx2 == routeIdx1):
        routeIdx2 = random.randint(0, len(routes)-1)
        
    route1 = routes[routeIdx1]
    route2 = routes[routeIdx2]
    maxLength1 = min(len(route1.nodeList)-2, neighborhood)
    maxLength2 = min(len(route2.nodeList)-2, neighborhood)

    #If either routes are empty, there is a high possibility its because none of the customers are available for that route
    if maxLength1 < 1 or maxLength2 < 1: 
        return (routeIdx1, routeIdx2)

    newLength1 = random.randint(minLength1, maxLength1)
    newLength2 = random.randint(minLength2, maxLength2)
    exchangePt1 = random.randint(1, len(route1.nodeList)-1 - newLength1)
    exchangePt2 = random.randint(1, len(route2.nodeList)-1 - newLength2)
    temp = route1.nodeList[exchangePt1 : exchangePt1 + newLength1]
    route1.nodeList[exchangePt1 : exchangePt1 + newLength1] = route2.nodeList[exchangePt2 : exchangePt2 + newLength2]
    route2.nodeList[exchangePt2 : exchangePt2 + newLength2] = temp
    route1.resetServiceTimes()
    route2.resetServiceTimes()

    return (routeIdx1, routeIdx2)

def optExchange1(routes, unplannedCustomers, neighborhoodSize):
    if neighborhoodSize < OPT_EXCHANGE_1_START or neighborhoodSize >= OPT_EXCHANGE_2_START:
        raise ValueError(f"Neighborhood size of opt exchange 1 must be between {OPT_EXCHANGE_1_START} and {OPT_EXCHANGE_2_START-1}")
    
    p = 0
    q = 0
    
    if neighborhoodSize == OPT_EXCHANGE_1_START:
        p = 0
        q = 1
    elif neighborhoodSize == OPT_EXCHANGE_1_START + 1:
        p = 1
        q = 1
    elif neighborhoodSize == OPT_EXCHANGE_1_START + 2:
        p = 2
        q = 1
    elif neighborhoodSize == OPT_EXCHANGE_1_START + 3:
        p = 0
        q = 2

    routeIdx = random.randint(0, len(routes)-1)
    selectedRoute = routes[routeIdx]
    numOptCustomers = selectedRoute.calculateOptionalCustomers()
    route = selectedRoute.nodeList[1:-1]
    removedCustomers = []
    
    p = min(p, numOptCustomers)
    q = min(q, len(unplannedCustomers))

    max_position = len(route)-1-p
    if max_position < 0:
        position = 0
    else:
        position = random.randint(0, max_position) #the fact that the position is bounded by n-p is not in paper

    deletePosition = position
    for _ in range(p):
        #print(p, len(route))
        while route[deletePosition].info.mandatory:
            #print("before", position, len(route))
            deletePosition = (deletePosition + 1) % (len(route))
            #print(deletePosition, len(route))##prb
            
            #print("after", position, len(route))
        if not route[deletePosition].info.mandatory:
            cust = route.pop(deletePosition)
            removedCustomers.append(cust)
            if len(route) == 0:
                break

            deletePosition = deletePosition % (len(route))
    if len(unplannedCustomers) > 0:     
        i = random.randint(0, len(unplannedCustomers)-1)
        for _ in range(min(q, len(unplannedCustomers))):
            #print(unplannedCustomers)
            newCustomer = unplannedCustomers[i]
            while newCustomer.info.mandatory and i >= 0:
                i -= 1
                #print(i)
                newCustomer = unplannedCustomers[i]
                
            if i >= 0: 
                route.insert(position, newCustomer)
                unplannedCustomers.pop(i)
                i -= 1
            else:
                #all of the unplanned customers are mandatory customers
                break

    selectedRoute.nodeList[1:-1] = route
    selectedRoute.resetServiceTimes()
    unplannedCustomers += removedCustomers

    return routeIdx

def optExchange2(routes, unplannedCustomers, neighborhoodSize):          
    if neighborhoodSize < OPT_EXCHANGE_2_START or neighborhoodSize >= END:
        raise ValueError(f"Neighborhood size of opt exchange 2 must be between {OPT_EXCHANGE_2_START} and {END-1}")

    routeIdx = random.randint(0, len(routes)-1)
    selectedRoute = routes[routeIdx]
    numOptCustomers = selectedRoute.calculateOptionalCustomers()
    route = selectedRoute.nodeList[1:-1]
    removedCustomers = []
    
    p = min(neighborhoodSize - 12, numOptCustomers)
   
    max_position = len(route)-1-p
    if max_position < 0:
        position = 0
    else:
        position = random.randint(0, max_position) #the fact that the position is bounded by n-p is not in paper
    
    for _ in range(p):
        #print(position, len(route))
        while route[position].info.mandatory:
            #print("before", position, len(route))
            position = (position + 1) % (len(route))
            #print("after", position, len(route))
        if not route[position].info.mandatory:
            cust = route.pop(position)
            removedCustomers.append(cust)
            if len(route) == 0:
                break
            position = position % (len(route))

    selectedRoute.nodeList[1:-1] = route
    selectedRoute.resetServiceTimes()
    unplannedCustomers += removedCustomers

    return routeIdx
    
def acceptanceDecision(bestSolution, candidateSolution, neighborhood, mode, ascending=False):
    if neighborhood < CROSS_EXCHANGE_START or neighborhood >= END:
        raise ValueError("Invalid neighborhood")
    
    bestSolutionLength = sum(bestSolution.calculateDistance())
    candidateSolutionLength = sum(candidateSolution.calculateDistance())
    
    if mode == "profit":
        if sum(candidateSolution.calculateValue()) >  sum(bestSolution.calculateValue()):
            return True
        elif candidateSolutionLength < bestSolutionLength and (sum(candidateSolution.calculateValue()) ==  sum(bestSolution.calculateValue())):
                return True
    

    if mode == "distance":
        if candidateSolutionLength < bestSolutionLength:
            return True
    
    if ascending:
        if neighborhood < OPT_EXCHANGE_1_START:
            if candidateSolutionLength/bestSolutionLength < 1.005:
                return True
            else:
                return False
        else:
            return True
