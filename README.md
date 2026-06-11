# Vehicle-Route-Optimizer
A Vehicle Routing Problem (V-R-P) solver implemented using GurobiPy and Mixed Integer Programming (M-I-P).

The project models a fleet of vehicles serving customer demands from a central depot which minimizing total travel distance.

## Features
- Distance matrix generation from customer co-ordinates
- Binary routing decision variables
- Travel distance minimization
- Customer visit constraints
- Depot entry and exit constraints
- Flow conservation constraints
- Miller-Tucker-Zemlin (M-T-Z) sub-tour elimination
- Vehicle capacity constraints
- Route visualization using Matplotlib

## Technologies Used
- Python 3
- GurobiPy
- NumPy
- Matplotlib

## Current Test Instance
1. Depot
| ID | Location |
| --- | --- |
| 0 | (0, 0) |

2. Customers
| ID | Location | Demand |
| --- | --- | --- |
| 1 | (-6, 2) | 3 |
| 2 | (0, 6) | 4 |
| 3 | (6, 2) | 5 |
| 4 | (4, -5) | 6 |
| 5 | (-4, -5) | 7 |

3. Vehicles
| ID | Capacity |
| --- | --- |
| 1 | 8 |
| 2 | 9 |
| 3 | 10 |

## Files
1. main.py
Builds and solves the Capacitated Vehicle Routing Problem (C-V-R-P) using Gurobi.

2. visualise.py
Plots customer locations, depot location, and optimized vehicle routes using Matplotlib.

## Future Improvements
- Read problem instances from external files
- Automatic route extraction for visualization
- Larger benchmark instances
- Time window constraints
- Multiple depots
- Interactive route visualization