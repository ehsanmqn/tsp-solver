import sys
import time

from tsp_solver import messaging


def main():
    messaging.start_service()


if __name__ == '__main__':
    time.sleep(5)
    sys.exit(main())
