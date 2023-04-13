# TSP Solver Service
The aim of this project is to provide a solution for the TSP and VRP problem given the input data, and it has been developed using Python 3.10. The project employs RabbitMQ as the messaging broker to facilitate communication with other services.

## Used Technologies
    - Python 3
    - Pika (RabbitMQ python library)
    - Ortools (TSP optimizer engine)

## Deployment
### Docker container
The project includes a docker-compose file that specifies the necessary requirements for deploying the project using docker containers. To run the project with docker, navigate to the project directory and execute the following command:
```bash
docker-compose up --build
```

### Manual
If you prefer to manually run the project, execute the following commands in the project directory:
```bash 
virtualenve -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Getting started

## Contributing
Contributions are welcome! If you want to contribute to this project, please fork the repository and submit a pull request.

## Licence
This project is licensed under the MIT License.
