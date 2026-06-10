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
    vehicleCapacity[index] = index + 6

# print("Depot:")
# print(f"ID = {depotID}, location = {depotLocation}")

totalDemand = 0
# print("Customer(s):")
for index in range(1, customerCount + 1):
    # print(f"ID = {index}, location = {customerLocation[index]}, demand = {customerDemand[index]}")
    totalDemand += customerDemand[index]

totalCapacity = 0
# print("Vehicle(s):")
for index in range(1, vehicleCount + 1):
    # print(f"ID = {index}, capacity = {vehicleCapacity[index]}")
    totalCapacity += vehicleCapacity[index]

# if totalDemand > totalCapacity:
    # print("Overload!")
# else:
    # print("Normal!")

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

# print(nodeDistance)

# Decision variables are of the type x[i,j,k], being 1 if the vehicle with ID 'k' goes from node 'i' to node 'j', 0 other-wise!
model = Model('Vehicle')
X = {}
for vehicle in range(1, vehicleCount + 1):
    for source in range(nodeCount):
        for destination in range(nodeCount):
            current = f"X{source}{destination}{vehicle}"
            key = (source, destination, vehicle)
            X[key] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=current)
# print(len(X))

# Defining the objective function - sum of product of distance(s) and decision variable(s)!
target = 0
for vehicle in range(1, vehicleCount + 1):
    for source in range(nodeCount):
        for destination in range(nodeCount):
            if source != destination:
                target += nodeDistance[source][destination] * X[(source, destination, vehicle)]

# The target must be minimized!
model.setObjective(target, GRB.MINIMIZE)
model.optimize()

if model.Status == GRB.OPTIMAL:
    print("Optimized Value:", model.ObjVal)
else:
    print("No optimal value was found! Current status:", model.Status)

