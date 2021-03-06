from ..Data.Problem import *
from ..Data.Solution import *
from ..Data.Reader import *

#def plot(route: Route):
    
import matplotlib.pyplot as plt
##names = ['group_a', 'group_b', 'group_c']
##values = [1, 10, 100]
##
##plt.figure(figsize=(9, 3))
##
##plt.subplot(141)
##plt.bar(names, values)
##plt.subplot(142)
##plt.scatter(names, values)
##plt.subplot(143)
##plt.plot(names, values)
###plt.subplot(154)
###plt.plot(names, values)
##plt.suptitle('Categorical Plotting')
##plt.show()


def plot(solution, show=True, dominantSolution=True):
    
    for i in range (0, len(solution.routes)):
        fig, gnt = plt.subplots(1, 1, figsize=(5, 100))
        if dominantSolution:
            plot_solution(gnt, solution.routes[i])
        else:
            plot_customers(gnt, solution.routes[i])

    if show:
        plt.show()

def plot_solution(ax, route):
    ax.set_ylim(0, 20)
    ax.set_xlim(0, 1600)
    ax.set_xlabel("Time")
    ax.set_ylabel("Customer")
    ax.grid(True)
    ax.set_xticks([i*100 for i in range (12)], [i*100 for i in range (12)])
    ax.set_yticks([3*i for i in range(1, len(route.nodeList)-1)])
    ax.set_yticklabels([str(customer.info.id) for customer in (route.nodeList[1:-1])])

    #print('**************')
    for i in range(1, len(route.solution)-1):
        customer = route.solution[i]
        
##        print(len(route.nodeList)-1)
##        print(customer.info.startTime)
##       print(f'Customer no. {customer.info.id}')
##        print(customer.info.serviceTime)
##        print(customer.info.endTime)
##        print(customer.info.startTime - customer.getTravelTime(route.nodeList[i-1]))
##        print(customer.info.endTime - customer.info.startTime)
##        print(customer.info.startTime - customer.getTravelTime(route.nodeList[i-1]))
        #ax.broken_barh([(max(0, customer.info.startTime - customer.getTravelTime(route.nodeList[i-1])), customer.info.endTime - customer.info.startTime + customer.getTravelTime(route.nodeList[i-1]))], (2+3*(i-1), 2), facecolors='tab:blue')
        
        ax.broken_barh([(max(0, customer.info.startTime - customer.getTravelTime(route.nodeList[i-1])), customer.info.endTime - customer.info.startTime + customer.getTravelTime(route.nodeList[i-1]))], (2+3*(i-1), 2), facecolors='tab:blue')
        
##        print(i)
##        print(len(route.dominantSolution))
        if len(route.dominantSolution) == len(route.nodeList)-2:
##            if i == len(route.nodeList)-2:
##                
##            #print(f'{route.dominantSolution[i-1]-customer.info.serviceTime-customer.getTravelTime(route.nodeList[i-1])}, {customer.info.startTime - customer.getTravelTime(route.nodeList[i-1])}')
##            #print(f'{route.dominantSolution[i-1]-customer.info.serviceTime-customer.getTravelTime(route.nodeList[i-1]) + customer.info.serviceTime+customer.getTravelTime(route.nodeList[i-1])}, {route.dominantSolution[i-1]}')
##                ax.broken_barh([(route.dominantSolution[i-1]-customer.info.serviceTime-customer.getTravelTime(route.nodeList[i-1]) - customer.getTravelTime(route.nodeList[i+1]), customer.info.serviceTime + customer.getTravelTime(route.nodeList[i-1]) + customer.getTravelTime(route.nodeList[i+1]))], (2.5+3*(i-1), 1), facecolors='xkcd:yellow')
##                ax.broken_barh([(route.dominantSolution[i-1]-customer.info.serviceTime-customer.getTravelTime(route.nodeList[i-1]) - customer.getTravelTime(route.nodeList[i+1]), customer.getTravelTime(route.nodeList[i-1]) + customer.getTravelTime(route.nodeList[i+1]))], (2.5+3*(i-1), 1), facecolors='xkcd:green')
##
##            else:
            #print(customer.info.serviceTime)
            ax.broken_barh([(route.dominantSolution[i-1]-customer.info.serviceTime, customer.info.serviceTime)], (2.5+3*(i-1), 1), facecolors='xkcd:yellow')
            ax.broken_barh([(route.dominantSolution[i-1]-customer.info.serviceTime, customer.getTravelTime(route.nodeList[i-1]))], (2.5+3*(i-1), 1), facecolors='xkcd:green')

##                ax.broken_barh([(route.dominantSolution[i-1]-customer.info.serviceTime-customer.getTravelTime(route.nodeList[i-1]), customer.info.serviceTime+customer.getTravelTime(route.nodeList[i-1]))], (2.5+3*(i-1), 1), facecolors='xkcd:yellow')
##                ax.broken_barh([(route.dominantSolution[i-1]-customer.info.serviceTime-customer.getTravelTime(route.nodeList[i-1]), customer.getTravelTime(route.nodeList[i-1]))], (2.5+3*(i-1), 1), facecolors='xkcd:green')
        #print(customer.info.startTime - customer.getTravelTime(route.nodeList[i-1]))
        #ax.broken_barh([(max(0, customer.info.startTime - customer.getTravelTime(route.nodeList[i-1])), customer.info.serviceTime + customer.getTravelTime(route.nodeList[i-1]))], (2.75+3*(i-1), 0.5), facecolors='xkcd:green')
    #print(route.problem.depot.info.endTime)
    ax.broken_barh([(route.problem.depot.info.endTime, 4)], (0, 1000), facecolors='tab:red')
    ax.broken_barh([(route.problem.depot.info.startTime, 4)], (0, 1000), facecolors='tab:red')

def plot_customers(ax, route):
    ax.set_ylim(0, 20)
    ax.set_xlim(0, 1600)
    ax.set_xlabel("Time")
    ax.set_ylabel("Customer")
    ax.grid(True)
    ax.set_xticks([i*100 for i in range (12)], [i*100 for i in range (12)])
    ax.set_yticks([3*i for i in range(1, len(route.nodeList)-1)])
    ax.set_yticklabels([str(customer.info.id) for customer in (route.nodeList[1:])])
    #print('**************')
    for i in range(1, len(route.nodeList)):
        customer = route.nodeList[i]
        ax.broken_barh([(customer.info.startTime, customer.info.endTime - customer.info.startTime)], (2+3*(i-1), 2), facecolors='tab:blue')
        #print(route.serviceStartTimes[i] + customer.info.serviceTime)
        ax.broken_barh([(route.serviceStartTimes[i], customer.info.serviceTime)], (2.5+3*(i-1), 1), facecolors='xkcd:yellow')
        ax.broken_barh([(route.serviceStartTimes[i]-customer.getTravelTime(route.nodeList[i-1]), customer.getTravelTime(route.nodeList[i-1]))], (2.5+3*(i-1), 1), facecolors='xkcd:green')

    ax.broken_barh([(route.problem.depot.info.endTime, 4)], (0, 1000), facecolors='tab:red')
    ax.broken_barh([(route.problem.depot.info.startTime, 4)], (0, 1000), facecolors='tab:red')
