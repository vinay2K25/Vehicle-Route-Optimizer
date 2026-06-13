import gurobipy as gp
from gurobipy import Model, GRB
import numpy as np
from visualise import plotRoutes
import csv

def findDistance(first, second):
    X = first[0]
    Y = first[1]
    A = second[0]
    B = second[1]
    sum = (X - A) ** 2 + (Y - B) ** 2
    distance = sum ** 0.5
    return distance

# Node(s) are simply re-presented by the depot ID and customer IDs!
nodes = []

# Depot requires two data - a unique ID and it's location!
depotID = 0
depotLocation = (-1, -1)
with open('depot.csv') as depotFile:
    content = csv.reader(depotFile)
    for row in content:
        if row[0] != 'id':
            ID = int(row[0])
            X = int(row[1])
            Y = int(row[2])
            depotID = ID
            depotLocation = (X, Y)
            nodes.append(ID)

# Customer requires three data - a unique ID, location and demand!
customerCount = 0
customerLocation = {}
customerDemand = {}
with open('customer.csv') as customerFile:
    content = csv.reader(customerFile)
    for row in content:
        if row[0] != 'id':
            ID = int(row[0])
            X = int(row[1])
            Y = int(row[2])
            Demand = int(row[3])
            customerCount += 1
            customerLocation[ID] = (X, Y)
            customerDemand[ID] = Demand
            nodes.append(ID)

# Vehicle requires two data - a unique ID and capacity!
vehicleCount = 0
vehicleCapacity = {}
with open('vehicle.csv') as vehicleFile:
    content = csv.reader(vehicleFile)
    for row in content:
        if row[0] != 'id':
            ID = int(row[0])
            Capacity = int(row[1])
            vehicleCount += 1
            vehicleCapacity[ID] = Capacity

totalDemand = sum(customerDemand.values())
totalCapacity = sum(vehicleCapacity.values())

# Mapping node to index and index to node!
nodeToIndex = {}
indexToNode = {}
for index, node in enumerate(nodes):
    nodeToIndex[node] = index
    indexToNode[index] = node

# We first find the distance(s) between every pair of customer(s)!
nodeCount = len(nodes)
nodeDistance = np.zeros((nodeCount, nodeCount))
for row in range(1, nodeCount):
    rowID = indexToNode[row]
    for column in range(1, nodeCount):
        columnID = indexToNode[column]
        current = findDistance(customerLocation[rowID], customerLocation[columnID])
        nodeDistance[row][column] = current
        nodeDistance[column][row] = current

# We now find distance of each customer from the depot!
for index in range(1, nodeCount):
    customerID = indexToNode[index]
    current = findDistance(customerLocation[customerID], depotLocation)
    nodeDistance[index][0] = current
    nodeDistance[0][index] = current

# Decision variables are of the type x[i,j,k], being 1 if the vehicle with ID 'k' goes from node 'i' to node 'j', 0 other-wise!
model = Model('Vehicle')
X = {}
for vehicle in vehicleCapacity.keys():
    for source in range(nodeCount):
        for destination in range(nodeCount):
            current = f"X-{source}-{destination}-{vehicle}"
            key = (source, destination, vehicle)
            X[key] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=current)

# Defining the objective function - sum of product of distance(s) and decision variable(s)!
target = 0
for vehicle in vehicleCapacity.keys():
    for source in range(nodeCount):
        for destination in range(nodeCount):
            if source != destination:
                target += nodeDistance[source][destination] * X[(source, destination, vehicle)]

# Each customer must be visited exactly once!
# Do not count the depot in this, it must be handled separately!
for destination in customerDemand.keys():
    sum = 0
    destinationIndex = nodeToIndex[destination]
    for source in range(nodeCount):
        for vehicle in vehicleCapacity.keys():
            if source != destinationIndex:
                sum += X[(source, destinationIndex, vehicle)]
    model.addConstr(sum == 1)

# The number of in-coming and out-going edges must be the same, that is, 1!
for source in customerDemand.keys():
    sum = 0
    sourceIndex = nodeToIndex[source]
    for destination in range(nodeCount):
        for vehicle in vehicleCapacity.keys():
            if sourceIndex != destination:
                sum += X[(sourceIndex, destination, vehicle)]
    model.addConstr(sum == 1)

# The number of out-going edges from the depot, and in-coming edges to the depot must be 1 for each vehicle!
for vehicle in vehicleCapacity.keys():
    sumIn = 0
    sumOut = 0
    for node in customerDemand.keys():
        nodeIndex = nodeToIndex[node]
        depotIndex = nodeToIndex[depotID]
        sumIn += X[(nodeIndex, depotIndex, vehicle)]
        sumOut += X[(depotIndex, nodeIndex, vehicle)]
    model.addConstr(sumIn == 1)
    model.addConstr(sumOut == 1)

# We also need to ensure that the same vehicle entering a customer's node must also leave it!
for node in customerDemand.keys():
    for vehicle in vehicleCapacity.keys():
        sumIn = 0
        sumOut = 0
        # Flow-conservation must include the depot too!
        for adjoint in range(nodeCount):
            nodeIndex = nodeToIndex[node]
            sumOut += X[(nodeIndex, adjoint, vehicle)]
            sumIn += X[(adjoint, nodeIndex, vehicle)]
        model.addConstr(sumIn == sumOut)

# We introduce additional variable(s) - one per customer, to indicate their position in a path!
U = {}
for customer in customerDemand.keys():
    current = f"U-{customer}"
    U[customer] = model.addVar(lb=1, ub=customerCount, vtype=GRB.INTEGER, name=current)

# Adding the M-T-Z constraint(s)!
for vehicle in vehicleCapacity.keys():
    for source in customerDemand.keys():
        for destination in customerDemand.keys():
            if source != destination:
                sourceIndex = nodeToIndex[source]
                destinationIndex = nodeToIndex[destination]
                model.addConstr(U[source] - U[destination] + customerCount * X[(sourceIndex, destinationIndex, vehicle)] <= customerCount - 1)

# Taking customer demand and vehicle capaity into account!
for vehicle in vehicleCapacity.keys():
    totalCustomerDemand = 0
    for destination in customerDemand.keys():
        for source in range(nodeCount):
            if source != destination:
                destinationIndex = nodeToIndex[destination]
                totalCustomerDemand += customerDemand[destination] * X[(source, destinationIndex, vehicle)]
    model.addConstr(totalCustomerDemand <= vehicleCapacity[vehicle])

# The target must be minimized!
model.setObjective(target, GRB.MINIMIZE)
model.optimize()

if model.Status == GRB.OPTIMAL:
    vehicleRoute = {}
    vehiclePath = {}
    print("Optimized Value:", model.ObjVal)
    for vehicle in vehicleCapacity.keys():
        vehicleRoute[vehicle] = []
        nextNode = {}
        for source in range(nodeCount):
            for destination in range(nodeCount):
                if X[(source, destination, vehicle)].X == True:
                    vehicleRoute[vehicle].append((indexToNode[source], indexToNode[destination]))
                    nextNode[indexToNode[source]] = indexToNode[destination]
        nodeOrder = []
        nodeOrder.append(depotID)
        current = nextNode[depotID]
        while current != depotID:
            nodeOrder.append(current)
            current = nextNode[current]
        nodeOrder.append(current)
        vehiclePath[vehicle] = nodeOrder
    # Print the path and related-details for each vehicle!
    for key, value in vehiclePath.items():
        print(f"Vehicle {key}: {value}")
        # Load = Customer Demand/Vehicle Capacity!
        demandMet = 0
        for index in range(1, len(value) - 1):
            demandMet += customerDemand[value[index]]
        print(f"Load: {demandMet}/{vehicleCapacity[key]}")
        # Total Distance covered in the path!
        totalDistance = 0
        for index in range(1, len(value)):
            totalDistance += nodeDistance[nodeToIndex[value[index - 1]]][nodeToIndex[value[index]]]
        print(f"Distance: {totalDistance}")
    # Plot the routes via matplotlib!
    plotRoutes(depotID, depotLocation, customerLocation, vehicleRoute)
else:
    print("No optimal value was found! Current status:", model.Status)