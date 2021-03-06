import pickle
from .Solution import Solution
from .Problem import Problem

PATH = "Data\\Solutions\\"

def save_solution(solution: Solution, filename):
    full_path = PATH + filename
    with open(full_path, 'wb') as f:
        pickle.dump(solution, f)
    
def save_problem(problem: Problem, filename):
    full_path = PATH + filename
    with open(full_path, 'wb') as f:
        pickle.dump(problem, f)
