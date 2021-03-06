def diff(list1, list2):
    d = ""
    s1 = ""
    s2 = ""
    if len(list2) > len(list1):
        list1, list2 = list2, list1
        print("List 2 is now List 1, and vice versa")
    for i, j in zip(list1, list2):
        s1 += f"{i}\t"
        s2 += f"{j}\t"
        if i != j:
            d +=  f"x\t"
        else:
            d +=  f" \t"
    for i in range(len(list2), len(list1)):
        s1 += f"{list1[i]}\t"
    print(s1)
    print(s2)
    print(d)
    print("")

def printCustomers(route):
    print([cust.info.id for cust in route])

def printSolCustomers(solution):
    for route in solution.routes:
        printCustomers(route.nodeList)
