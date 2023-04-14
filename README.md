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
docker-compose up --build
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

A bash file named **install.sh** provided in the project. This script is used to build, install, and run the TSP solver service. In order to use it, first change the MESSAGE_BROKER variable based on the RabbitMQ address. Then run it according to follow:
```bash
chamod +x install.sh
./install.sh
```

## About the project
This is a Python script that defines a service for solving the TSP (Traveling Salesman Problem), VRP (Vehicle Routing Problem), and  VRPTW (Vehicle Routing Problem with Time Windows) optimization problems using OR-Tools, a library for optimization problems developed by Google.

The project contains following modules:
1. `messaging.py`: This file contains necessary functions to handle incoming messages.
2. `service.py`: The entry point of the project which run the service.
3. `utils.py`: Contains necessary functions to generate distance and time matrices. 
4. `vrp_solver.py`: The TSP/VRP solver module.
5. `vrptw_solver.py`: The VRPTW solver module.

The script starts by importing necessary libraries like json, logging, os, pika, and BaseModel from the pydantic module. It also imports functions and classes from other modules of the _tsp_solver_ package such as _ortools_vrp_solver_, _ortools_vrptw_solver_, _generate_distance_matrix_, and _generate_time_matrix_.

The _VrpRequest_ and _VrptwRequest_ classes represent the format of incoming messages containing a request to solve the VRP or VRPTW optimization problem respectively, while the _VrpResponse_ class represents the format of outgoing messages containing the solution to the optimization problem.

The _dispatch_message_ function processes incoming messages based on their _message_type_ attribute, which can be either 'VRP', 'TSP' or 'VRPTW'. The function creates an instance of the appropriate request class based on the message type, then passes it to the appropriate processing function (_process_vrp_message_ or _process_vrptw_message_). If the message type is not supported, the function returns a response with error code 400 and message "Not supported message type." If there is a problem with the request data, the function returns a response with error code 400 and an error message.

The _process_vrp_message_ and _process_vrptw_message_ functions both take a request object and a channel object as arguments, and use the **OR-Tools** library to solve the corresponding optimization problem. They then create a _VrpResponse_ object with the solution and a success message if the optimization was successful, or an error message if there was a problem with the request or the optimization. The functions return the _VrpResponse_ object.

The _start_service_ function sets up a connection to a message broker specified by the **MESSAGE_BROKER** environment variable, creates input and output queues for TSP messages, and starts consuming messages from the input queue. When a message is received, the _dispatch_message_ function is called to handle it, and the resulting response is sent to the output queue with the same message ID as the incoming message.

# Contributing
Contributions are welcome! If you want to contribute to this project, please fork the repository and submit a pull request.

## Licence
This project is licensed under the MIT License.
