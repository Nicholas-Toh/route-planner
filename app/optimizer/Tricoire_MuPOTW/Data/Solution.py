from .Problem import *

class Route:
    def __init__(self, problem: Problem, seed: Customer = None):
        self.problem = problem
        self.nodeList = []
        self.serviceStartTimes = []
        self.addDepot(problem.depot)
        self.setSeed(problem, seed)
        self.solution = []
        self.dominantSolution = []
        
    def setSeed(self, problem: Problem, seed: Customer):
        if seed:
            self.insertCustomer(seed, 1)

    def nextServiceStartTime(self, newCustomer: Customer, prevCustomer: Customer, prevTime: float):
        travelTime = prevCustomer.getTravelTime(newCustomer)
        serviceTime = prevCustomer.info.serviceTime
        startTime = newCustomer.info.startTime
        return max(startTime, prevTime + serviceTime + travelTime)

    def addDepot(self, depot: Customer):
        self.insertCustomer(depot, 0)
        self.insertCustomer(depot, 1)

    def addCustomer(self, customer: Customer):
        lastCustomer = customer if len(self.nodeList) == 0 else self.nodeList[-1]
        lastServiceTime =  0 if len(self.nodeList) == 0 else self.serviceStartTimes[-1]
        serviceBegins = self.nextServiceStartTime(customer, lastCustomer, lastServiceTime)
        self.serviceStartTimes.append(serviceBegins)
        self.nodeList.append(customer)
        
    def insertCustomer(self, customer: Customer, position: int, reset=True):
        self.nodeList.insert(position, customer)
        self.serviceStartTimes.insert(position, 0.0)
        if reset:
            for i in range(position, len(self.nodeList)):
                newTime = self.nextServiceStartTime(self.nodeList[i], self.nodeList[i-1], self.serviceStartTimes[i-1])
                self.serviceStartTimes[i] = newTime

    def deleteCustomer(self, position: int, reset=True):
        cust = self.nodeList.pop(position)
        self.serviceStartTimes.pop(position)
        if reset:
            for i in range(position, len(self.nodeList)):
                newTime = self.nextServiceStartTime(self.nodeList[i], self.nodeList[i-1], self.serviceStartTimes[i-1])
                self.serviceStartTimes[i] = newTime
        return cust

    def resetServiceTimes(self):
        self.serviceStartTimes = []
        self.serviceStartTimes.insert(0, 0.0)
        for i in range(1, len(self.nodeList)):
            newTime = self.nextServiceStartTime(self.nodeList[i], self.nodeList[i-1], self.serviceStartTimes[i-1])
            self.serviceStartTimes.append(newTime)
        
    def isFeasible(self):#, position, oldStartTimes):
        solution = []
        for route in self.nodeList:
            solution.append(route.copy())

            if (len(solution) > 1 and len(solution) < len(self.nodeList)):
                solution[-1].info.startTime = max(0, solution[-1].info.startTime - solution[-2].getTravelTime(solution[-1]))
                solution[-1].info.serviceTime += solution[-2].getTravelTime(solution[-1])

        solution[-2].info.startTime = max(0,  solution[-2].info.startTime - solution[-2].getTravelTime(solution[-1]))
        solution[-2].info.serviceTime += solution[-2].getTravelTime(solution[-1])
            
        feasible = self.tightenEndTimes(solution) and self.tightenStartTimes(solution)
        if feasible:
            self.solution = solution
        return feasible

    def optimize(self):  
        solution = []
        for route in self.nodeList:
            solution.append(route.copy())

            if (len(solution) > 1 and len(solution) < len(self.nodeList)):
                solution[-1].info.startTime = max(0, solution[-1].info.startTime - solution[-2].getTravelTime(solution[-1]))
                solution[-1].info.serviceTime += solution[-2].getTravelTime(solution[-1])

        solution[-2].info.startTime = max(0,  solution[-2].info.startTime - solution[-2].getTravelTime(solution[-1]))
        solution[-2].info.serviceTime += solution[-2].getTravelTime(solution[-1])
                    
                        
        feasible = self.tightenEndTimes(solution) and self.tightenStartTimes(solution)
        if feasible:
            self.solution = solution
            self.dominantSolution = self.minRouteDuration(self.solution)


##        #print(self.serviceStartTimes)
##        startTime = self.serviceStartTimes[position-1]
##        oldStartTime = oldStartTimes[position-1]
##        endTime = self.nodeList[position].info.endTime
##        #print(f'Customer no. {self.nodeList[position].info.id}, {startTime}, {oldStartTime}, {endTime}')
##
##        if startTime > endTime:
##            return False
##        #nextStartTime = self.serviceStartTimes[position+1]
##        pushForward = startTime - oldStartTime
##        for i in range(position+1, len(self.nodeList)-1):
##            waitingTime =  max(0, self.nodeList[i].info.startTime - self.serviceStartTimes[i-1])
##            pushForward = max(0, pushForward - waitingTime)
##            if self.serviceStartTimes[i-1] + pushForward > self.nodeList[i].info.endTime:
##                return False
##
##        return True
        

    def tightenStartTimes(self, solution):    #preprocessing step 1
        i = 1
        while i < len(self.nodeList) - 1: ##and self.nodeList[i].timeWindows != 0: ##TODO: Implement multi time windowszz
            startTime = solution[i].info.startTime# - solution[i-1].getTravelTime(solution[i]))# - solution[i].getTravelTime(solution[i+1]) if i == len(self.nodeList) - 2 else 0
            endTime = solution[i].info.endTime
            serviceTime = solution[i].info.serviceTime# + solution[i-1].getTravelTime(solution[i])# + solution[i].getTravelTime(solution[i+1]) if i == len(self.nodeList) - 2 else 0
            #print(f'Start Customer no. {solution[i].info.id}, {startTime}, {serviceTime}, {endTime}')
            if startTime + serviceTime > endTime: ##TODO or next time window is feasible
                return False #if that one time window doesnt work, the route is infeasible
            else:
                nextStartTime = solution[i+1].info.startTime# - solution[i].getTravelTime(solution[i+1]))# - solution[i+1].getTravelTime(solution[i+2]) if i == len(self.nodeList) - 3 else 0)
                
                if startTime + serviceTime < nextStartTime:
                    #print('***********')
                    #if solution[i].info.id == 13:
                        #print(f'Start Customer no. {solution[i].info.id}, {solution[i].info.startTime}, {solution[i].info.startTime - solution[i].getTravelTime(solution[i-1])}, {serviceTime}, {nextStartTime}, {endTime}')
            
                    solution[i].info.startTime = min(nextStartTime - serviceTime, endTime - serviceTime)# + solution[i-1].getTravelTime(solution[i])# + solution[i].getTravelTime(solution[i+1]) if i == len(self.nodeList) - 2 else 0
                    #if solution[i].info.id == 13:
                        #print(f'End Customer no. {solution[i].info.id}, {solution[i].info.startTime}, {solution[i].info.startTime - solution[i].getTravelTime(solution[i-1])}, {serviceTime}, {nextStartTime}, {endTime}')
                elif startTime + serviceTime > nextStartTime:
                    nextCustomer = solution[i+1]
                    nextCustomer.info.startTime = max(startTime + serviceTime, nextStartTime)# + solution[i].getTravelTime(solution[i+1])# + solution[i+1].getTravelTime(solution[i+2]) if i == len(self.nodeList) - 3 else 0
                    ##for window in solution[i].timeWindows:
                        ##window.startTime = max(startTime + serviceTime, window.startTime)
                #if int(solution[i].info.id) == 15:
                    #print(f'Start Customer no. {solution[i].info.id}, {startTime}, {serviceTime}, {endTime}')
            i += 1

        if solution[-2].info.startTime + solution[-2].info.serviceTime > solution[-1].info.endTime:
            return False #reject any solution that has the last node's earliest departure exceed the maximum time allowed
        
        return True

    def tightenEndTimes(self, solution):    #preprocessing step 1
        i = len(solution) - 2
        while i > 0: ##and solution[i].timeWindows != 0: ##TODO: Implement multi time windows
            startTime = solution[i].info.startTime# - solution[i-1].getTravelTime(solution[i]))
            endTime = solution[i].info.endTime
            serviceTime = solution[i].info.serviceTime# + solution[i-1].getTravelTime(solution[i])
            #print(f'End Customer no. {solution[i].info.id}, {startTime}, {serviceTime}, {endTime}')
            if endTime - serviceTime < startTime: ##TODO or previous time window is feasible
                return False #if that one time window doesnt work, the route is infeasible
            else:
                previousEndTime = solution[i-1].info.endTime
                #print(f'End Customer no. {solution[i].info.id}, {endTime}, {serviceTime}, {previousEndTime}')
                
                if endTime - serviceTime > previousEndTime:
                    #if solution[i].info.id == 22:
                        #print(f'1 End Customer no. {solution[i].info.id}, {endTime}, {previousEndTime + serviceTime}, {startTime + serviceTime}')
                    #print(f'End Customer no. {solution[i].info.id}, {solution[i].info.endTime}, {previousEndTime + serviceTime}, {startTime + serviceTime}')
                
                    solution[i].info.endTime = max(previousEndTime + serviceTime, startTime + serviceTime)
                    #print(f'End Customer no. {solution[i].info.id}, {solution[i].info.endTime}, {previousEndTime + serviceTime}, {startTime + serviceTime}')
                
                elif endTime - serviceTime < previousEndTime:
                    previousCustomer = solution[i-1]
                    #if previousCustomer.info.id == 22:
                        #print(f'2 End Customer no. {previousCustomer.info.id}, {previousCustomer.info.endTime}, {endTime - serviceTime}')
                
                    
                    previousCustomer.info.endTime = min(endTime - serviceTime, previousCustomer.info.endTime)
                    
                    ##for window in solutionx[i].timeWindows:
                        ##window.endTime = max(endTime - serviceTime, window.endTime)
            #if startTime + serviceTime > solution[i].info.endTime:
               #print(f'End Customer no. {solution[i].info.id}, {endTime}, {endTime - serviceTime}, {previousCustomer.info.endTime}')
                
            i -= 1
        return True
    
##    def isFeasible(self):#, position, oldStartTimes):
##        solution = []#copy.deepcopy(self.nodeList)
##        feasible = self.tightenStartTimes(solution) and self.tightenEndTimes(solution)
##        if feasible:
##            self.solution = solution
##        return feasible
##
##    def optimize(self):
##        solution = []#copy.deepcopy(self.nodeList)
##        feasible = self.tightenStartTimes(solution) and self.tightenEndTimes(solution)
##        if feasible:
##            self.solution = solution
##            self.dominantSolution = self.minRouteDuration(solution)
##
##
####        #print(self.serviceStartTimes)
####        startTime = self.serviceStartTimes[position-1]
####        oldStartTime = oldStartTimes[position-1]
####        endTime = self.nodeList[position].info.endTime
####        #print(f'Customer no. {self.nodeList[position].info.id}, {startTime}, {oldStartTime}, {endTime}')
####
####        if startTime > endTime:
####            return False
####        #nextStartTime = self.serviceStartTimes[position+1]
####        pushForward = startTime - oldStartTime
####        for i in range(position+1, len(self.nodeList)-1):
####            waitingTime =  max(0, self.nodeList[i].info.startTime - self.serviceStartTimes[i-1])
####            pushForward = max(0, pushForward - waitingTime)
####            if self.serviceStartTimes[i-1] + pushForward > self.nodeList[i].info.endTime:
####                return False
####
####        return True
##        
##
##    def tightenStartTimes(self, solution):    #preprocessing step 1
##        i = 1
##
##        if len(solution) != len(self.nodeList):
##            solution.clear()
##            solution.append(self.problem.depot)
##            solution.append(self.problem.depot)
##        
##        while i < len(self.nodeList) - 1: ##and self.nodeList[i].timeWindows != 0: ##TODO: Implement multi time windows
##            currentNode = solution[i] if solution[i].info.id == self.nodeList[i].info.id else self.nodeList[i].copy()
##            if len(solution) != len(self.nodeList):
##                solution.insert(i, currentNode)
##            
##            startTime = max(0, solution[i].info.startTime - solution[i-1].getTravelTime(solution[i]))
##            endTime = solution[i].info.endTime
##            serviceTime = solution[i].info.serviceTime + solution[i-1].getTravelTime(solution[i])
##            #print(f'Start Customer no. {solution[i].info.id}, {startTime}, {serviceTime}, {endTime}')
##            if startTime + serviceTime > endTime: ##TODO or next time window is feasible
##                return False #if that one time window doesnt work, the route is infeasible
##            else:
##                nextStartTime = max(0, self.nodeList[i+1].info.startTime - solution[i].getTravelTime(self.nodeList[i+1]))
##                
##                if startTime + serviceTime < nextStartTime:
##                    #print('***********')
##                    #print(f'Start Customer no. {solution[i].info.id}, {solution[i].info.startTime}, {serviceTime}, {nextStartTime}, {endTime}')
##            
##                    solution[i].info.startTime = min(nextStartTime - serviceTime, endTime - serviceTime)
##                    #print(f'Start Customer no. {solution[i].info.id}, {solution[i].info.startTime}, {serviceTime}, {nextStartTime}, {endTime}')
##                elif startTime + serviceTime > nextStartTime:
##                    nextCustomer = solution[i+1] if solution[i+1].info.id == self.nodeList[i+1].info.id else self.nodeList[i+1].copy()
##                    
##                    if len(solution) != len(self.nodeList):
##                        solution.insert(i+1, nextCustomer)
##                        
##                    nextCustomer.info.startTime = max(startTime + serviceTime, nextStartTime) + solution[i].getTravelTime(solution[i+1])
##
##                    
##                    ##for window in solution[i].timeWindows:
##                        ##window.startTime = max(startTime + serviceTime, window.startTime)
##                #if int(solution[i].info.id) == 15:
##                    #print(f'Start Customer no. {solution[i].info.id}, {startTime}, {serviceTime}, {endTime}')
##            i += 1
##        
##        return True
##
##    def tightenEndTimes(self, solution):    #preprocessing step 1
##        i = len(self.nodeList) - 2
##        
##        if len(solution) != len(self.nodeList):
##            solution.clear()
##            solution.append(self.problem.depot)
##            solution.append(self.problem.depot)
##        
##        while i > 0: ##and solution[i].timeWindows != 0: ##TODO: Implement multi time windows
##            currentNode = solution[i] if solution[i].info.id == self.nodeList[i].info.id else self.nodeList[i].copy()
##            if len(solution) != len(self.nodeList):
##                solution.insert(i, currentNode)
##            
##            startTime = max(0, solution[i].info.startTime - solution[i-1].getTravelTime(solution[i]))
##            endTime = solution[i].info.endTime
##            serviceTime = solution[i].info.serviceTime + solution[i-1].getTravelTime(solution[i])
##            #print(f'End Customer no. {solution[i].info.id}, {startTime}, {serviceTime}, {endTime}')
##            if endTime - serviceTime < startTime: ##TODO or previous time window is feasible
##                return False #if that one time window doesnt work, the route is infeasible
##            else:
##                previousEndTime = solution[i-1].info.endTime
##                #print(f'End Customer no. {solution[i].info.id}, {endTime}, {serviceTime}, {previousEndTime}')
##                
##                if endTime - serviceTime > previousEndTime:
##                    #if solution[i].info.id == 22:
##                        #print(f'1 End Customer no. {solution[i].info.id}, {endTime}, {previousEndTime + serviceTime}, {startTime + serviceTime}')
##                    #print(f'End Customer no. {solution[i].info.id}, {solution[i].info.endTime}, {previousEndTime + serviceTime}, {startTime + serviceTime}')
##                    print('Starting', solution[i].info.endTime, self.nodeList[i].info.endTime)
##                    solution[i].info.endTime = max(previousEndTime + serviceTime, startTime + serviceTime)
##                    print('Ending', solution[i].info.endTime, self.nodeList[i].info.endTime)
##                    #print(f'End Customer no. {solution[i].info.id}, {solution[i].info.endTime}, {previousEndTime + serviceTime}, {startTime + serviceTime}')
##                
##                elif endTime - serviceTime < previousEndTime:
##                    previousCustomer = solution[i-1] if solution[i-1].info.id == self.nodeList[i-1].info.id else self.nodeList[i-1].copy()
##                    #if previousCustomer.info.id == 22:
##                        #print(f'2 End Customer no. {previousCustomer.info.id}, {previousCustomer.info.endTime}, {endTime - serviceTime}')
##                
##                    if len(solution) != len(self.nodeList):
##                        solution.insert(i-1, previousCustomer)
##                        
##                    previousCustomer.info.endTime = min(endTime - serviceTime, previousCustomer.info.endTime)
##                    
##                    ##for window in solutionx[i].timeWindows:
##                        ##window.endTime = max(endTime - serviceTime, window.endTime)
##            #if startTime + serviceTime > solution[i].info.endTime:
##               #print(f'End Customer no. {solution[i].info.id}, {endTime}, {endTime - serviceTime}, {previousCustomer.info.endTime}')
##                
##            i -= 1
##        return True

    def minRouteFeasible(self, solution):
        departureTimes = []
        for i in range (1, len(self.nodeList)-1):
            startTime = solution[i].info.startTime
            serviceTime = solution[i].info.serviceTime
            departureTimes.append(startTime + serviceTime)

        def calculateFeasible(departureTimes, solution):
            firstDepartureTime = 0
            for i in range(len(solution)-3, 0, -1):
            #starting from the second last customer till the first,
            #drag the starting time to the latest possible time of the time window
                #print(i)
                #print(j)
                nextServiceTime = solution[i+1].info.serviceTime
                nextStartTime = departureTimes[j+1] - nextServiceTime# - solution[i].getTravelTime(solution[i+1])
                endTime = solution[i].info.endTime ##Departure time is bordered by end time of the time window
                #print(f'{dominantSolution[j] - solution[i].info.serviceTime - solution[i].getTravelTime(solution[i-1])}')
                firstDepartureTime = min(nextStartTime, endTime) ##either drag it behind the starting time of the next service or the end of the time window
                #print(f'{dominantSolution[j]}, {departureTimes[j+1]}, {solution[i+1].info.startTime - solution[i].getTravelTime(solution[i+1])}')
                #print(f'{dominantSolution[j] - solution[i].info.serviceTime - solution[i].getTravelTime(solution[i-1])}')

            lastDeparture = departureTimes[-1]
            firstStartTime = firstDepartureTime - solution[1].info.serviceTime + solution[1].getTravelTime(solution[0])

            #return lastDeparture - firstStartTime >= 
        
    def minRouteDuration(self, solution):
        departureTimes = []
        for i in range (1, len(self.nodeList)-1):
            startTime = solution[i].info.startTime
            serviceTime = solution[i].info.serviceTime
            departureTimes.append(startTime + serviceTime)

        def calculateDominantSolution(departureTimes, solution):
            dominantSolution = [s for s in departureTimes]
            for i, j in zip(range(len(solution)-3, 0, -1), range(len(departureTimes)-2, -1, -1)):
            #starting from the second last customer till the first,
            #drag the starting time to the latest possible time of the time window
                #print(i)
                #print(j)
                nextServiceTime = solution[i+1].info.serviceTime
                nextStartTime = dominantSolution[j+1] - nextServiceTime# - solution[i].getTravelTime(solution[i+1])
                endTime = solution[i].info.endTime ##Departure time is bordered by end time of the time window
                #print(f'{dominantSolution[j] - solution[i].info.serviceTime - solution[i].getTravelTime(solution[i-1])}')
                dominantSolution[j] = min(nextStartTime, endTime) ##either drag it behind the starting time of the next service or the end of the time window
                #print(f'{dominantSolution[j]}, {departureTimes[j+1]}, {solution[i+1].info.startTime - solution[i].getTravelTime(solution[i+1])}')
                #print(f'{dominantSolution[j] - solution[i].info.serviceTime - solution[i].getTravelTime(solution[i-1])}')
            return dominantSolution

        #def latestWaitingCustomer(departureTimes, solution):
            #for i, j in zip(range(len(solution)-3, 0, -1), range(len(departureTimes)-2, -1, -1)):
                
        
        departureTimes = calculateDominantSolution(departureTimes, solution)
        return departureTimes
        
    def copy(self):
        newRoute = Route(self.problem)
        newRoute.nodeList = [customer.copy() for customer in self.nodeList]
        newRoute.serviceStartTimes = [time for time in self.serviceStartTimes]
        return newRoute

    def calculateTime(self):
        if len(self.dominantSolution) != len(self.nodeList):
            self.optimize()

        if len(self.dominantSolution) < 1:
            return 0

        time = self.dominantSolution[-1] - self.dominantSolution[0] + self.solution[0].info.serviceTime + self.solution[0].getTravelTime(self.solution[1])

        return time
        

    def calculateDistance(self):
        distance = 0
        for i in range(0, len(self.nodeList)-1):
            distance += self.nodeList[i].getTravelTime(self.nodeList[i+1])

        return distance

    def calculateValue(self):
        value = 0
        for cust in self.nodeList:
            if not cust.info.mandatory:
                value += cust.info.value

        return value

    def calculateOptionalCustomers(self):
        num = 0
        for i in range(1, len(self.nodeList)-1):
            if not self.nodeList[i].info.mandatory:
                num += 1

        return num

    def calculateMandatoryCustomers(self):
        num = 0
        for i in range(1, len(self.nodeList)-1):
            if self.nodeList[i].info.mandatory:
                num += 1

        return num

class Solution:
    def __init__(self, problem: Problem):
        self.routes = []
        self.problem = problem


    def addRoute(self, route: Route):
        self.routes.append(route)

    def getCustomerList(self):
        customers = []
        for route in routes:
            customers.append(route.customers)

    def calculateTime(self):
        times = []
        for route in self.routes:
            times.append(route.calculateTime())

        return times

    def calculateDistance(self):
        distances = []
        for route in self.routes:
            distances.append(route.calculateDistance())

        return distances

    def calculateValue(self):
        values = []
        for route in self.routes:
            values.append(route.calculateValue())

        return values

    def optimize(self):
        for route in self.routes:
            route.optimize()

    def copy(self):
        newSolution = Solution(self.problem)
        newSolution.routes = [route.copy() for route in self.routes]

        return newSolution
