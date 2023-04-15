# TSP, VRP, VRPTW Solver Service
The aim of this project is to provide a solution for the TSP, VRP, and VRPTW problem given the input data, and it has been developed using Python 3.10. The project employs RabbitMQ as the messaging broker to facilitate communication with other services.

## Used Technologies
    - Python 3
    - Pika (RabbitMQ python library)
    - Ortools (TSP optimizer engine)
    - Pydantic

## Deployment
### Docker container
The project includes a docker-compose file that specifies the necessary requirements for deploying the project using docker containers. To run the project with docker, navigate to the project directory and execute the following command:
```bash
docker-compose up
```

### Manual
If you prefer to manually run the project, execute the following commands in the project directory (Considering the RabbitMQ is running on localhost):
```bash 
virtualenve -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
export MESSAGE_BROKER="localhost"
python tsp_solver/service.py
```

## Packaging and Running
The **setup.py** file defined the necessary metadata such as the package name, version, description, author information, and required packages for packaging the project.

A bash file named **install.sh** provided in the project. This script is used to build, install, and run the TSP solver service. In order to use it, first change the MESSAGE_BROKER variable inside the install.sh based on the RabbitMQ address. Then run it according to follow:
```bash
chamod +x install.sh
./install.sh
```

## Message structure
To effectively leverage the tsp-solver service for solving TVP, TSP, or TVPTW problems, it is necessary to adhere to a specific message structure. This involves sending the message to the RabbitMQ on the designated topic, namely TSP_INPUT_QUEUE. Following the problem's processing, the optimized result will be published on the TSP_OUTPUT_QUEUE.

**NOTE:** In this project (since it is a test project), the distance matrix, and the time matrix calculate everytime a new message recieved. However, it's still more efficient to pre-compute all the distances between locations and store them in a matrix, rather than compute them at run time. 
Another alternative is to use the Google Maps Distance Matrix API to dynamically create a distance (or travel time) matrix for a routing problem.

### TSP message
The following code snippet represents a JSON object that contains information about a TSP task. It includes an identifier ('id') for the specific task, the type of problem ('message_type'), the depot location ('depot'), the number of vehicles required for the task ('num_vehicles'). For the TSP problem num_vehicles must be 1. And a list of locations to be visited by the vehicle ('locations').

To facilitate the task, the user is required to provide two additional parameters, namely the maximum distance and cost coefficient, to the VRP optimizer while solving a problem.
According to the [Or-tools documentation](https://developers.google.com/optimization/routing/vrp), _cost_coefficient_ defines the difference between the largest value of route end cumul variables and the smallest value of route start cumul variables.
Respectively, _max_distance_ defines vehicle maximum travel distance.
```json
{
    "id": 1,
    "message_type": "TSP",
    "depot": 0,
    "num_vehicles": 1,
    "locations": [
      {"latitude": 40.7128, "longitude": -74.0060},
      {"latitude": 34.0522, "longitude": -118.2437},
      {"latitude": 41.8781, "longitude": -87.6298},
      {"latitude": 29.7604, "longitude": -95.3698},
      {"latitude": 39.9526, "longitude": -75.1652},
      {"latitude": 33.4484, "longitude": -112.0740},
      {"latitude": 29.4241, "longitude": -98.4936},
      {"latitude": 32.7157, "longitude": -117.1611},
      {"latitude": 32.7767, "longitude": -96.7970},
      {"latitude": 37.3382, "longitude": -121.8863}
    ],
    "max_distance": 100000,
    "cost_coefficient": 100
}
```

### VRP message
The following code snippet represents a JSON object that contains information about a VRP (Vehicle Routing Problem) task. It includes an identifier ('id') for the specific task, the type of problem ('message_type'), the depot location ('depot'), the number of vehicles required for the task ('num_vehicles'), and a list of locations to be visited by the vehicles ('locations').

Each location is specified using its latitude and longitude coordinates. This information can be leveraged as input data for a routing optimization algorithm to determine the most efficient routes for vehicles to visit all the specified locations.

To facilitate the task, the user is required to provide two additional parameters, namely the maximum distance and cost coefficient, to the VRP optimizer while solving a problem.
According to the [Or-tools documentation](https://developers.google.com/optimization/routing/vrp), _cost_coefficient_ defines the difference between the largest value of route end cumul variables and the smallest value of route start cumul variables.
Respectively, _max_distance_ defines vehicle maximum travel distance.

```json
{
    "id": 1,
    "message_type": "VRP",
    "depot": 0,
    "num_vehicles": 2,
    "locations": [
      {"latitude": 40.7128, "longitude": -74.0060},
      {"latitude": 34.0522, "longitude": -118.2437},
      {"latitude": 41.8781, "longitude": -87.6298},
      {"latitude": 29.7604, "longitude": -95.3698},
      {"latitude": 39.9526, "longitude": -75.1652},
      {"latitude": 33.4484, "longitude": -112.0740},
      {"latitude": 29.4241, "longitude": -98.4936},
      {"latitude": 32.7157, "longitude": -117.1611},
      {"latitude": 32.7767, "longitude": -96.7970},
      {"latitude": 37.3382, "longitude": -121.8863}
    ],
    "max_distance": 100000,
    "cost_coefficient": 100
}
```

### VRPTW message
This is a JSON object representing a vehicle routing problem with time windows (VRPTW). It specifies the details of the problem, including:

**NOTE:** To simplify the calculation of the time matrix for the VRPTW problem, I have used the formula `time = Velocity / distance`, where V represents velocity. It's worth noting that although a constant velocity of 80 is considered in this formula, it doesn't affect the final solution. In other words, if all vehicles travel at the same speed, you will get the same solution if you use a distance matrix or a time matrix, since travel distances are a constant multiple of travel times.

* message_type: The type of message, which is VRPTW.
* id: The ID of the request.
* depot: The index of the depot location.
* num_vehicles: The number of vehicles available for the problem.
* locations: A list of dictionary objects containing the latitude and longitude coordinates of each location to be visited by the vehicles.
* time_windows: A list of tuples specifying the time window for each location.
* wait_time: An upper bound for slack (the wait times at the locations).
* max_time_vehicle: An upper bound for the total time over each vehicle's route.

```json
{
    "message_type": "VRPTW",
    "id": 1,
    "depot": 0,
    "num_vehicles": 2,
    "locations": [
        {"latitude": 40.7128, "longitude": -74.0060},
            {"latitude": 34.0522, "longitude": -118.2437},
            {"latitude": 41.8781, "longitude": -87.6298},
            {"latitude": 29.7604, "longitude": -95.3698},
            {"latitude": 39.9526, "longitude": -75.1652},
            {"latitude": 33.4484, "longitude": -112.0740},
            {"latitude": 29.4241, "longitude": -98.4936},
            {"latitude": 32.7157, "longitude": -117.1611},
            {"latitude": 32.7767, "longitude": -96.7970},
            {"latitude": 37.3382, "longitude": -121.8863}
    ],
    "time_windows": [
        [0, 5],  
        [7, 12],
        [10, 15],
        [16, 18],  
        [10, 13],  
        [0, 5],  
        [5, 10],  
        [0, 4],  
        [5, 10],  
        [0, 3]  
    ],
    "wait_time": 30,
    "max_time_vehicle": 30
}
```
## Project structure
This is a Python script that defines a service for solving the TSP (Traveling Salesman Problem), VRP (Vehicle Routing Problem), and  VRPTW (Vehicle Routing Problem with Time Windows) optimization problems using OR-Tools, a library for optimization problems developed by Google.

The project contains following modules:
1. **messaging.py**: This file contains necessary functions to handle incoming messages.
2. **service.py**: The entry point of the project which run the service.
3. **utils.py**: Contains necessary functions to generate distance and time matrices. 
4. **vrp_solver.py**: The TSP/VRP solver module.
5. **vrptw_solver.py**: The VRPTW solver module.

```
tsp-solver/
    tests/
        __init__.py
        test_solver.py
    tsp_solver/
        __init__.py
        messaging.py
        service.py
        utils.py
        vrp_solver.py
        vrptw_solver.py
    setup.py
    main.py
    README.md
```
The script starts by importing necessary libraries like _json_, _logging_, _os_, _pika_, and _BaseModel_ from the _pydantic_ module. It also imports functions and classes from other modules of the **tsp_solver** package such as **_ortools_vrp_solver_**, **_ortools_vrptw_solver_**, **_generate_distance_matrix_**, and **_generate_time_matrix_**.

The **_VrpRequest_** and **_VrptwRequest_** classes represent the format of incoming messages containing a request to solve the VRP or VRPTW optimization problem respectively, while the _**VrpResponse**_ class represents the format of outgoing messages containing the solution to the optimization problem.
```python
class VrpRequest(BaseModel):
    id: str
    locations: List
    depot: int
    num_vehicles: int
    message_type: str
    max_distance: int
    cost_coefficient: int

class VrptwRequest(BaseModel):
    id: str
    locations: List
    depot: int
    num_vehicles: int
    message_type: str
    time_windows: List
    wait_time: int
    max_time_vehicle: int

class VrpResponse:
    def __init__(self, id, solution, code, message):
        self.id = id
        self.solution = solution
        self.code = code
        self.message = message
```
The _**dispatch_message**_ function processes incoming messages based on their _**message_type**_ attribute, which can be either 'VRP', 'TSP' or 'VRPTW'. The function creates an instance of the appropriate request class based on the message type, then passes it to the appropriate processing function (_**process_vrp_message**_ or _**process_vrptw_message**_). If the message type is not supported, the function returns a response with error code 400 and message "Not supported message type." If there is a problem with the request data, the function returns a response with error code 400 and an error message.
```python
def dispatch_message(channel, method, properties, body):
    """
    Process incoming message regarding the message type
    """
    ...
```
The _**process_vrp_message**_ and _**process_vrptw_message**_ functions both take a request object and a channel object as arguments, and use the OR-Tools library to solve the corresponding optimization problem. They then create a _**VrpResponse**_ object with the solution and a success message if the optimization was successful, or an error message if there was a problem with the request or the optimization. The functions return the _**VrpResponse**_ object.
```python
def process_vrp_message(request, channel):
    """
    Process incoming message regarding the VRP/TSP optimization engine, then publish result on output queue
    """
    ...

def process_vrptw_message(request, channel):
    """
    Process incoming message regarding the TSP optimization engine, then publish result on output queue
    """
    ...
```
The _**start_service**_ function sets up a connection to a message broker specified by the **MESSAGE_BROKER** environment variable, creates input and output queues for TSP messages, and starts consuming messages from the input queue. When a message is received, the _**dispatch_message**_ function is called to handle it, and the resulting response is sent to the output queue with the same message ID as the incoming message.
```python
def start_service():
    ...
```

## Tests
To conduct tests against the VRP solver (_ortools_vrp_solver_), there are 9 tests that have been implemented. Please run the following command to execute these tests:

```bash
python -m unittest
```

## Improvement
Here are a few suggestions for improving this code:

1. Add error handling: Although there is some basic error handling in place, it could be improved to handle more edge cases and provide more informative error messages. For example, if the input message is malformed, the service should return an appropriate error response. In addition, errors that occur during processing, such as network errors or solver failures, should be handled more gracefully.

2. Add support for more problem types: Currently, the service only supports three problem types: VRP, TSP, and VRPTW. It would be useful to add support for other types of optimization problems, such as vehicle routing with pickups and deliveries (VRPD), or capacitated vehicle routing problem (CVRP).

3. Improve performance: The current implementation uses a simple round-robin approach for message distribution, which may not be optimal for large volumes of traffic. To improve performance, the service could use load balancing techniques, such as using multiple workers or implementing a more sophisticated message distribution algorithm.

4. Add authentication and authorization: Currently, anyone can send messages to the input queue and receive responses from the output queue, which could pose security risks. It would be useful to add authentication and authorization mechanisms to restrict access to authorized users only.

5. Use a more robust messaging system: While RabbitMQ is a popular and reliable messaging system, it may not be the best choice for all use cases. Depending on the specific requirements of the service, a different messaging system or architecture, such as Apache Kafka or event-driven microservices, may be more suitable.

## Contributing
Contributions are welcome! If you want to contribute to this project, please fork the repository and submit a pull request.

## Licence
This project is licensed under the MIT License.
