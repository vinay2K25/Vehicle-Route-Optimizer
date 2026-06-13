import matplotlib.pyplot as plt

def plotRoutes(depotID, depotLocation, customerLocation, vehicleRoute):
    # To achieve a cleaner-look!
    plt.figure(figsize=(10, 8))
    plt.axis('equal')

    # Storing all node co-ordinates in a single dictionary!
    nodeLocation = {depotID:depotLocation}
    nodeLocation.update(customerLocation)

    # Plotting the depot!
    plt.scatter(depotLocation[0], depotLocation[1], s=150, marker='s', label='Depot')

    # Plotting the customers!
    for customer, location in customerLocation.items():
        plt.scatter(location[0], location[1], s=150)
        plt.text(location[0], location[1], str(customer), fontsize=18)

    # Different color for every vehicle!
    # Red for vehicle 1, green for 2 and blue for 3!
    colors = ['red', 'green', 'blue']

    # Drawing the routes!
    for index, (vehicle, edges) in enumerate(vehicleRoute.items()):
        color = colors[index % len(colors)]
        for source, destination in edges:
            startX, startY = nodeLocation[source]
            endX, endY = nodeLocation[destination]

            plt.arrow(startX, startY, endX - startX, endY - startY, length_includes_head=True, head_width=0.10, color=color, linewidth=2)

    # Adding the necessary labels!
    plt.title('Vehicle Routes')
    plt.xlabel('X Co-ordinate')
    plt.ylabel('Y Co-ordinate')
    plt.grid(True)
    plt.legend()
    plt.show()