def calculate_infeasibility(route):
    actualStartTime = 0 #start as early as possible pg. 355
    infeasibility = 0
    #print('**********')
    for i in range (1, len(route)):
        actualStartTime = max(route[i].info.startTime - route[i-1].getTravelTime(route[i]), actualStartTime + route[i-1].info.serviceTime + route[i-1].getTravelTime(route[i])) #first node is depot, service time should be 0 for accurate results
        #print("Actual start time vs start time:", actualStartTime, route[i].info.startTime)
        infeasibleTime = max(0, min(route[i].info.serviceTime, actualStartTime + route[i].info.serviceTime - route[i].info.endTime))
        ##print("Actual end time vs end time:", actualStartTime + route[i].info.serviceTime, route[i].info.endTime)
        infeasibility += infeasibleTime
        #print("Infeasible time: ", infeasibleTime)

    
    return infeasibility

def calculate_distance(route):
    distance = sum([route[i].getTravelTime(route[i+1]) for i in range(len(route)-1)])
    return distance

def calculate_time(route): #only useful for non-optimized routes
    actualStartTime = 0
    firstStartTime = 0
    #print('**********')
    for i in range (1, len(route)):
        actualStartTime = max(route[i].info.startTime - route[i-1].getTravelTime(route[i]), actualStartTime + route[i-1].info.serviceTime + route[i-1].getTravelTime(route[i])) #first node is depot, service time should be 0 for accurate results
        if not firstStartTime:
            firstStartTime = actualStartTime
    print(actualStartTime)
    return actualStartTime - firstStartTime
