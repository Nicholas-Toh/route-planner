from .DataStructures import OptCase
from ...Utils.RouteFunctions import *
##from DataStructures import OptCase
def possible_segments(N):
    """ Generate the combination of segments """
    segments = ((i, j, k) for i in range(N) for j in range(i + 1, N) for k in range(j + 1, N if N - (j+1) < 3 else j + 4 ))
    return segments

    
def get_solution_cost_change(route, case, i, j, k):
    """ Compare current solution with 7 possible 3-opt moves"""
    A, B, C, D, E, F = route[i - 1], route[i], route[j - 1], route[j], route[k - 1], route[k % len(route)]
##    if case == OptCase.opt_case_1:
##        # ABC 
##        return 0
##    elif case == OptCase.opt_case_2:
##        # A'BC
##        return A.getTravelTime(B) + E.getTravelTime(F) - (B.getTravelTime(F) + A.getTravelTime(E))
##    elif case == OptCase.opt_case_3:
##        # ABC'
##        return C.getTravelTime(D) + E.getTravelTime(F) - (D.getTravelTime(F) + C.getTravelTime(E))
##    elif case == OptCase.opt_case_4:
##        # A'BC'
##        return graph[A, B] + graph[C, D] + graph[E, F] - (graph[A, D] + graph[B, F] + graph[E, C])
##    elif case == OptCase.opt_case_5:
##        # A'B'C
##        return graph[A, B] + graph[C, D] + graph[E, F] - (graph[C, F] + graph[B, D] + graph[E, A])
##    elif case == OptCase.opt_case_6:
##        # AB'C
##        return graph[B, A] + graph[D, C] - (graph[C, A] + graph[B, D])
##    elif case == OptCase.opt_case_7:
##        # AB'C'
##        return graph[A, B] + graph[C, D] + graph[E, F] - (graph[B, E] + graph[D, F] + graph[C, A])
    if case == OptCase.opt_case_8:
        # A'B'C' = ACB
        return A.getTravelTime(B) + C.getTravelTime(D) + E.getTravelTime(F) - (A.getTravelTime(D) + C.getTravelTime(F) + B.getTravelTime(E))

def reverse_segments(route, case, i, j, k):
    """
    Create a new tour from the existing tour
    Args:
        route: existing tour
        case: which case of opt swaps should be used
        i:
        j:
        k:
    Returns:
        new route
    """
    if (i - 1) < (k % len(route)):
        first_segment = route[k% len(route):] + route[:i]
    else:
        first_segment = route[k % len(route):i]
    second_segment = route[i:j]
    third_segment = route[j:k]

##    if case == OptCase.opt_case_1:
##        # ABC
##        solution = first_segment + second_segment + third_segment
##        pass
##    elif case == OptCase.opt_case_2:
##        # A'BC
##        solution = list(reversed(first_segment)) + second_segment + third_segment
##    elif case == OptCase.opt_case_3:
##        # ABC'
##        solution = first_segment + second_segment + list(reversed(third_segment))
##    elif case == OptCase.opt_case_4:
##        # A'BC'
##        solution = list(reversed(first_segment)) + second_segment + list(reversed(third_segment))
##    elif case == OptCase.opt_case_5:
##        # A'B'C
##        solution = list(reversed(first_segment)) + list(reversed(second_segment)) + third_segment
##    elif case == OptCase.opt_case_6:
##        # AB'C
##        solution = first_segment + list(reversed(second_segment)) + third_segment
##    elif case == OptCase.opt_case_7:
##        # AB'C'
##        solution = first_segment + list(reversed(second_segment)) + list(reversed(third_segment))
    if case == OptCase.opt_case_8:
        # A'B'C' = ACB This is the only case that does not involve chain inversion
        solution = first_segment + third_segment + second_segment
    return solution

def cycle_to_depot(depot, route):
    for i in range(len(route)):
        if route[i].info.id == depot:
            return route[i:] + route[0:i]

def tsp_3_opt(depot, route):
    if route is None:
        raise ValueError("Route is empty")
    moves_cost = {OptCase.opt_case_8: 0}
    worst_infeasiblity = calculate_infeasibility(route)
    improved = True
    best_found_route = route
    while improved:
        #print('l')
        improved = False
        #infeasiblity = calculate_infeasibility(best_found_route)
        for (i, j, k) in possible_segments(len(route)):
            # we check all the possible moves and save the result into the dict
            for opt_case in OptCase:
                    moves_cost[opt_case] = get_solution_cost_change(best_found_route, opt_case, i, j, k)
            # we need the minimum value of substraction of old route - new route
            best_return = max(moves_cost, key=moves_cost.get)
            #print([cust.info.id for cust in best_found_route])
            candidate_route = reverse_segments(best_found_route, best_return, i, j, k)
            #print([cust.info.id for cust in candidate_route])
            candidate_infeasibility = calculate_infeasibility(candidate_route)
            #print(moves_cost[best_return])
            if moves_cost[best_return] >= 0 and candidate_infeasibility <= worst_infeasiblity:
                #print("hi")
                if moves_cost[best_return] > 0 or candidate_infeasibility < worst_infeasiblity:
                   
                    best_found_route = candidate_route
                    worst_infeasiblity = candidate_infeasibility
                    improved = True
                    break
                              
    # just to start with the same node -> we will need to cycle the results.
    best_found_route = cycle_to_depot(depot, best_found_route)
    return best_found_route

##r = [0, 1, 2, 3, 4, 5]
##a = possible_segments(len(r))
###for b in a:
##    #print(b)
##
##for i, j, k in a:
##    print(cycle_to_depot(0, reverse_segments(r, OptCase.opt_case_8, i, j, k)))
