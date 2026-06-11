import gurobipy as gp
from gurobipy import Model, GRB
import numpy as np

def findDistance(first, second):
    X = first[0]
    Y = first[1]
    A = second[0]
    B = second[1]
    sum = (X - A) ** 2 + (Y - B) ** 2
    distance = sum ** 0.5
    return distance

# Depot requires two data - a unique ID and it's location!
depotID = 0
depotLocation = (0, 0)

# Customer requires three data - a unique ID, location and demand!
customerCount = 5
customerLocation = {}
for index in range(1, customerCount + 1):
    customerLocation[index] = (index - 3, index + 4)

customerDemand = {}
for index in range(1, customerCount + 1):
    customerDemand[index] = index + 2

# Vehicle requires two data - a unique ID and capacity!
vehicleCount = 3
vehicleCapacity = {}
for index in range(1, vehicleCount + 1):
    vehicleCapacity[index] = index + 7

totalDemand = 0
for index in range(1, customerCount + 1):
    totalDemand += customerDemand[index]

totalCapacity = 0
for index in range(1, vehicleCount + 1):
    totalCapacity += vehicleCapacity[index]

# Node(s) are simply re-presented by the depot ID and customer IDs!
# We first find the distance(s) between every pair of customer(s)!
nodes = [0, 1, 2, 3, 4, 5]
nodeCount = len(nodes)
nodeDistance = np.zeros((6, 6))
for row in range(1, nodeCount):
    for column in range(1, nodeCount):
        current = findDistance(customerLocation[row], customerLocation[column])
        nodeDistance[row][column] = current
        nodeDistance[column][row] = current

# We now find distance of each customer from the depot!
for index in range(1, nodeCount):
    current = findDistance(customerLocation[index], (0, 0))
    nodeDistance[index][0] = current
    nodeDistance[0][index] = current

# Decision variables are of the type x[i,j,k], being 1 if the vehicle with ID 'k' goes from node 'i' to node 'j', 0 other-wise!
model = Model('Vehicle')
X = {}
for vehicle in range(1, vehicleCount + 1):
    for source in range(nodeCount):
        for destination in range(nodeCount):
            current = f"X-{source}-{destination}-{vehicle}"
            key = (source, destination, vehicle)
            X[key] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=current)

# Defining the objective function - sum of product of distance(s) and decision variable(s)!
target = 0
for vehicle in range(1, vehicleCount + 1):
    for source in range(nodeCount):
        for destination in range(nodeCount):
            if source != destination:
                target += nodeDistance[source][destination] * X[(source, destination, vehicle)]

# Each customer must be visited exactly once!
# Do not count the depot in this, it must be handled separately!
for destination in range(1, nodeCount):
    sum = 0
    for source in range(nodeCount):
        for vehicle in range(1, vehicleCount + 1):
            if source != destination:
                sum += X[(source, destination, vehicle)]
    model.addConstr(sum <= 1)
    model.addConstr(sum >= 1)

# The number of in-coming and out-going edges must be the same, that is, 1!
for source in range(1, nodeCount):
    sum = 0
    for destination in range(nodeCount):
        for vehicle in range(1, vehicleCount + 1):
            if source != destination:
                sum += X[(source, destination, vehicle)]
    model.addConstr(sum <= 1)
    model.addConstr(sum >= 1)

# The number of out-going edges from the depot, and in-coming edges to the depot must be 1 for each vehicle!
for vehicle in range(1, vehicleCount + 1):
    sumIn = 0
    sumOut = 0
    for node in range(1, nodeCount):
        sumIn += X[(node, 0, vehicle)]
        sumOut += X[(0, node, vehicle)]
    model.addConstr(sumIn <= 1)
    model.addConstr(sumIn >= 1)
    model.addConstr(sumOut <= 1)
    model.addConstr(sumOut >= 1)

# We also need to ensure that the same vehicle entering a customer's node must also leave it!
for node in range(1, nodeCount):
    for vehicle in range(1, vehicleCount + 1):
        sumIn = 0
        sumOut = 0
        # Flow-conservation must include the depot too!
        for adjoint in range(nodeCount):
            sumOut += X[(node, adjoint, vehicle)]
            sumIn += X[(adjoint, node, vehicle)]
        model.addConstr(sumIn <= sumOut)
        model.addConstr(sumIn >= sumOut)

# We introduce additional variable(s) - one per customer, to indicate their position in a path!
U = {}
for index in range(1, customerCount + 1):
    current = f"U-{index}"
    U[index] = model.addVar(lb=1, ub=customerCount, vtype=GRB.INTEGER, name=current)

# Adding the M-T-Z constraint(s)!
for vehicle in range(1, vehicleCount + 1):
    for source in range(1, nodeCount):
        for destination in range(1, nodeCount):
            if source != destination:
                model.addConstr(U[source] - U[destination] + customerCount * X[(source, destination, vehicle)] <= customerCount - 1)

# Taking customer demand and vehicle capaity into account!
for vehicle in range(1, vehicleCount + 1):
    totalCustomerDemand = 0
    for destination in range(1, nodeCount):
        for source in range(nodeCount):
            if source != destination:
                totalCustomerDemand += customerDemand[destination] * X[(source, destination, vehicle)]
    model.addConstr(totalCustomerDemand <= vehicleCapacity[vehicle])

# The target must be minimized!
model.setObjective(target, GRB.MINIMIZE)
model.optimize()

if model.Status == GRB.OPTIMAL:
    print("Optimized Value:", model.ObjVal)
    for vehicle in range(1, vehicleCount + 1):
        for source in range(nodeCount):
            for destination in range(nodeCount):
                if X[(source, destination, vehicle)].X == True:
                    print(X[(source, destination, vehicle)])
    print()
else:
    print("No optimal value was found! Current status:", model.Status)