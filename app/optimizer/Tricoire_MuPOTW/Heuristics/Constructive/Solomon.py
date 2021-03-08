from .Strategy import SolomonStrategy
from ...Data.Problem import *
from ...Data.Solution import *
from ...Visualization.GanttChart import *
import copy
from typing import List

class SolomonConstructive:
    def __init__(self):
        self.coefMu = 1
        self.coefLambda = 1 #1 or 2
        self.coefAlpha1 = 0 #distance-insertion
        self.coefAlpha2 = 1 #time-insertion
       

    def selectSeedCustomer(self, customers: List[Customer], depot: Customer, strategy: SolomonStrategy):
        if strategy == SolomonStrategy.HighestDemand:
            return self.searchHighestDemandCustomer(customers, depot)
        elif strategy == SolomonStrategy.SortedHighestDemand:
            return self.searchSortedHighestDemand(customers, depot)
        elif strategy == SolomonStrategy.FarthestDistance:
            return self.searchFarthestCustomer(customers, depot)
        elif strategy == SolomonStrategy.EarliestReadyTime:
            return self.searchEarliestCustomer(customers, depot)
        else:
            return -1

    def searchHighestDemandCustomer(self, customers: List[Customer], depot: Customer):
        highest = 0
        for i in range(1, len(customers)):
            if not highest or customers[i].info.id != depot.info.id:
                if customers[i].info.value > customers[highest].info.value:
                    highest = i

        return highest

    def searchSortedHighestDemand(self, customers: List[Customer], depot: Customer):
        return -1

    def searchFarthestCustomer(self, customers: List[Customer], depot: Customer):
        farthestCustomer = 0
        farthestDistance = 0
        for i in range(1, len(customers)):
            if customers[i].info.id != depot.info.id:
                distance = depot.getTravelTime(customers[i])
                if distance > farthestDistance:
                    farthestCustomer = i
                    farthestDistance = distance

        return farthestCustomer

    def searchEarliestCustomer(self, customers: List[Customer], depot: Customer):
        earliest = 0
        for i in range(1, len(customers)):
            if customers[i].info.id != depot.info.id:
                if customers[i].info.endTime < customers[earliest].info.endTime:
                    earliest = i

        return earliest
        
    def solve2(self, problem: Problem, strategy: SolomonStrategy = SolomonStrategy.EarliestReadyTime):
        solution = Solution(problem)
        unroutedCustomers = problem.getCustomers()
        seedId = self.selectSeedCustomer(unroutedCustomers, problem.depot, strategy)
        seed = unroutedCustomers[seedId]
        unroutedCustomers.pop(seedId)
        partialRoute = Route(problem, seed)
        #print(f'Started with: {len(unroutedCustomers)}')

        while (len(unroutedCustomers) > 0):
            newRoute = partialRoute.copy()
            bestU = []
            c1Vals = []
            for cust in unroutedCustomers:
                minC1 = float('inf')
                optimalU = -1
                feasible = False
                for i in range (1, len(newRoute.nodeList)):
                    c1 = self.CriterionC1(i-1, cust, i, newRoute)
                    #oldStartTimes = copy.deepcopy(newRoute.serviceStartTimes)
                    newRoute.insertCustomer(cust, i)
                    isFeasible = newRoute.isFeasible()
                    
                    if c1 < minC1 and isFeasible:#newRoute.isFeasible(i, oldStartTimes):
                        #print('feasible')
                        minC1 = c1
                        optimalU = i
                        feasible = True

                    #else:
                        #print('infeasible')

                    newRoute.deleteCustomer(i)
                        
                bestU.append(optimalU)
                c1Vals.append(minC1)

            #print(len(bestU))

            if not feasible:
                partialRoute.optimize()
                print([cust.info.id for cust in partialRoute.nodeList])
                print([cust.info.id for cust in partialRoute.solution])
                print('added')
                solution.addRoute(partialRoute)
                #return solution
                if len(unroutedCustomers) != 0: 
                    seedId = self.selectSeedCustomer(unroutedCustomers, problem.depot, strategy)
                    seed = unroutedCustomers[seedId]
                    unroutedCustomers.pop(seedId)
                    partialRoute = Route(problem, seed)
                    
            else:

                bestCust = 0
                minC2 = float('inf')
                for i in range(0, len(unroutedCustomers)):
                    if bestU[i] != -1:
                        c2 = self.CriterionC2(unroutedCustomers[i], c1Vals[i], newRoute)
                        if c2 < minC2:
                            minC2 = c2
                            bestCust = i                

                newCustomer = unroutedCustomers[bestCust]
                newRoute.insertCustomer(newCustomer, bestU[bestCust])
                unroutedCustomers.pop(bestCust)
                partialRoute = newRoute

            if len(unroutedCustomers) == 0:
                partialRoute.optimize()
                solution.addRoute(partialRoute)
        return solution

    def solve(self, problem: Problem, strategy: SolomonStrategy = SolomonStrategy.EarliestReadyTime, existingSolution: Solution = None):
        solution = Solution(problem)
        unroutedCustomers = problem.getCustomers()
        
        if existingSolution:
            solution = existingSolution
        else:  
            for i in range(problem.planningHorizon):
                seedId = self.selectSeedCustomer(unroutedCustomers, problem.depot, strategy)
                seed = unroutedCustomers[seedId]
                unroutedCustomers.pop(seedId)
                partialRoute = Route(problem, seed)
                if partialRoute.isFeasible():
                    solution.addRoute(partialRoute)

        while (len(unroutedCustomers) > 0):
            bestU = []
            bestRoute = []
            c1Vals = []
            for cust in unroutedCustomers:
                minC1 = float('inf')
                optimalU = -1
                optimalRoute = -1
                feasible = False
                for j in range(len(solution.routes)):
                    route = solution.routes[j]
                    for i in range (1, len(route.nodeList)):
                        c1 = self.CriterionC1(i-1, cust, i, route)
                        route.insertCustomer(cust, i)
                        isFeasible = route.isFeasible()
                        
                        if c1 < minC1 and isFeasible:
                            minC1 = c1
                            optimalU = i
                            optimalRoute = j
                            feasible = True

                        #else:
                            #print('infeasible')

                        route.deleteCustomer(i)
                        
                bestRoute.append(optimalRoute)     
                bestU.append(optimalU)
                c1Vals.append(minC1)

            #print(len(bestU))

            if not feasible:
                ##for route in solution.routes:
                    ##route.optimize()

                problem.unplannedCustomers = unroutedCustomers
                break
##                partialRoute.optimize()
##                print([cust.info.id for cust in partialRoute.nodeList])
##                print([cust.info.id for cust in partialRoute.solution])
##                print('added')
##                solution.addRoute(partialRoute)
##                #return solution
##                if len(unroutedCustomers) != 0: 
##                    seedId = self.selectSeedCustomer(unroutedCustomers, problem.depot, strategy)
##                    seed = unroutedCustomers[seedId]
##                    unroutedCustomers.pop(seedId)
##                    partialRoute = Route(problem, seed)
                    
            else:

                bestCust = 0
                minC2 = float('inf')
                for i in range(0, len(unroutedCustomers)):
                    if bestU[i] != -1 and bestRoute[i] != -1:
                        c2 = self.CriterionC2(unroutedCustomers[i], c1Vals[i], solution.routes[bestRoute[i]])
                        if c2 < minC2:
                            minC2 = c2
                            bestCust = i
                            route = solution.routes[bestRoute[i]]

                newCustomer = unroutedCustomers[bestCust]
                route.insertCustomer(newCustomer, bestU[bestCust])
                unroutedCustomers.pop(bestCust)

            if len(unroutedCustomers) == 0:
                ##for route in solution.routes:
                    ##route.optimize()
                break
        return solution

    def solveOptional(self, problem: Problem, existingSolution: Solution = None):
        unroutedCustomers = sorted(problem.getCustomers(), key=lambda x: x.info.value, reverse = True)
        solution = Solution(problem)
        
        if existingSolution:
            solution = existingSolution
        else:  
            for i in range(problem.planningHorizon):
                solution.addRoute(Route(problem))
            
        i = 0        
        while i < len(unroutedCustomers):
            cust = unroutedCustomers[i]
            bestU = []
            c1Vals = []
            feasible = False
            for j in range(0, len(solution.routes)):
                route = solution.routes[j]
                minC1 = float('inf')
                optimalU = -1
                for k in range (1, len(route.nodeList)):
                    c1 = self.CriterionC1(k-1, cust, k, route)
                    route.insertCustomer(cust, k)
                    isFeasible = route.isFeasible()
                    
                    if c1 < minC1 and isFeasible:
                        minC1 = c1
                        optimalU = k
                        feasible = True

                    #else:
                        #print('infeasible')

                    route.deleteCustomer(k)
                    
                bestU.append(optimalU)
                c1Vals.append(minC1)
                #print(bestU)

            if feasible:

                minC2 = float('inf')
                for j in range(0, len(solution.routes)):
                    if bestU[j] != -1:
                        c2 = self.CriterionC2(cust, c1Vals[j], solution.routes[j])
                        if c2 < minC2:
                            minC2 = c2
                            bestInsert = j

                route = solution.routes[bestInsert]
                route.insertCustomer(cust, bestU[bestInsert])
                unroutedCustomers.pop(i)
                #print(route.isFeasible())

            i = i + 1
            #print(i, len(unroutedCustomers))
        
        for route in solution.routes:
                route.optimize()

        problem.unplannedCustomers = unroutedCustomers

        return solution

    def sequentialBestInsert(self, unroutedCustomers, solution: Solution, routeIdx):    #pg. 354
        i = 0
        route = solution.routes[routeIdx]
        while i < len(unroutedCustomers):
            cust = unroutedCustomers[i]
            feasible = False
            
            minC1 = float('inf')
            optimalU = -1
            for k in range (1, len(route.nodeList)):
                c1 = self.CriterionC1(k-1, cust, k, route)
                
                if c1 < minC1:
                    route.insertCustomer(cust, k, False)
                    if route.isFeasible():
                        minC1 = c1
                        optimalU = k
                        feasible = True
                    route.deleteCustomer(k, False)
     
            if feasible:
                route.insertCustomer(cust, optimalU, False)
                unroutedCustomers.pop(i)
                #print(route.isFeasible())

            else:
                if len(unroutedCustomers) > 1:
                    unroutedCustomers = unroutedCustomers[1:] + unroutedCustomers[0:1]

            i = i + 1
            #print(i, len(unroutedCustomers))
        
        #for route in solution.routes:
                #route.optimize()
        route.resetServiceTimes()
        return solution, unroutedCustomers

    def CriterionC1(self, i: int, u: Customer, j: int, route: Route):
        return self.coefAlpha1*self.CriterionC11(i, u, j, route) + self.coefAlpha2*self.CriterionC12(i, u, j, route)

    def CriterionC11(self, i: int, u: Customer, j: int, route: Route):
        custI = route.nodeList[i]
        custJ = route.nodeList[j]
        distIu = custI.getTravelTime(u)
        distUj = u.getTravelTime(custJ)
        distJi = custJ.getTravelTime(custI)
        return distIu + distUj - self.coefMu*distJi

    def CriterionC12(self, i: int, u: Customer, j: int, route: Route):
        custI = route.nodeList[i]
        custJ = route.nodeList[j]
        bI = route.serviceStartTimes[i]
        bU = route.nextServiceStartTime(u, custI, bI)
        bJ = route.serviceStartTimes[j]
        bJu = route.nextServiceStartTime(custJ, u, bU)
        return bJu - bJ

    def CriterionC2(self, u: Customer, c1Value: float, route):
        d0U = route.nodeList[0].getTravelTime(u)
        return self.coefLambda * d0U - c1Value
