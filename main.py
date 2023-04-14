import sys
import logging

from tsp_solver import messaging

# Configure logging settings
logging.basicConfig(filename='tsp_solver.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')


def main():
    logging.info('TSP solver service is going to be started.')
    messaging.start_service()


if __name__ == '__main__':
    sys.exit(main())

# Shutdown the logger when done
logging.shutdown()
