import unittest

from tsp_solver.solver import ortools_vrp_solver


class TestOrtoolsVRPSolver(unittest.TestCase):

    def test_optimal_solution(self):
        distance_matrix = [[0, 10, 15, 20],
                           [10, 0, 35, 25],
                           [15, 35, 0, 30],
                           [20, 25, 30, 0]]
        depot = 0
        num_vehicles = 1
        max_distance = 100
        cost_coefficient = 1

        expected_output = [
            {'route': [0, 1, 3, 2, 0], 'vehicle': 0, 'distance': 80}
        ]

        result = ortools_vrp_solver(distance_matrix, depot, num_vehicles, max_distance, cost_coefficient)

        self.assertEqual(result, expected_output)

    def test_small_input(self):
        distance_matrix = [[0, 10, 15, 20],
                           [10, 0, 35, 25],
                           [15, 35, 0, 30],
                           [20, 25, 30, 0]]
        depot = 0
        num_vehicles = 1
        max_distance = 100
        cost_coefficient = 1

        expected_output = [
            {'route': [0, 1, 3, 2, 0], 'vehicle': 0, 'distance': 80}
        ]

        result = ortools_vrp_solver(distance_matrix, depot, num_vehicles, max_distance, cost_coefficient)

        self.assertEqual(result, expected_output)

    def test_medium_input(self):
        distance_matrix = [[0, 20, 42, 35, 12, 25],
                           [20, 0, 30, 34, 21, 17],
                           [42, 30, 0, 12, 28, 43],
                           [35, 34, 12, 0, 31, 18],
                           [12, 21, 28, 31, 0, 24],
                           [25, 17, 43, 18, 24, 0]]
        depot = 0
        num_vehicles = 2
        max_distance = 100
        cost_coefficient = 1

        expected_output = [
            {'route': [0, 5, 3, 2, 4, 0], 'vehicle': 0, 'distance': 95},
            {'route': [0, 1, 0], 'vehicle': 1, 'distance': 40}
        ]

        result = ortools_vrp_solver(distance_matrix, depot, num_vehicles, max_distance, cost_coefficient)

        self.assertEqual(result, expected_output)

    def test_large_input(self):
        distance_matrix = [[0, 10, 20, 30, 40, 50, 60, 70],
                           [10, 0, 25, 35, 45, 55, 65, 75],
                           [20, 25, 0, 15, 30, 45, 60, 75],
                           [30, 35, 15, 0, 20, 40, 60, 80],
                           [40, 45, 30, 20, 0, 25, 50, 75],
                           [50, 55, 45, 40, 25, 0, 35, 60],
                           [60, 65, 60, 60, 50, 35, 0, 25],
                           [70, 75, 75, 80, 75, 60, 25, 0]]
        depot = 0
        num_vehicles = 3
        max_distance = 150
        cost_coefficient = 1

        expected_output = [
            {'route': [0, 7, 0], 'vehicle': 0, 'distance': 140},
            {'route': [0, 5, 6, 0], 'vehicle': 1, 'distance': 145},
            {'route': [0, 2, 3, 4, 1, 0], 'vehicle': 2, 'distance': 110}
        ]

        result = ortools_vrp_solver(distance_matrix, depot, num_vehicles, max_distance, cost_coefficient)

        self.assertEqual(result, expected_output)

    def test_not_square_distance_matrix(self):
        distance_matrix = [
            [10, 0, 25, 35, 45, 55, 65, 75],
            [20, 25, 0, 15, 30, 45, 60, 75],
            [30, 35, 15, 0, 20, 40, 60, 80],
            [40, 45, 30, 20, 0, 25, 50, 75],
            [50, 55, 45, 40, 25, 0, 35, 60],
            [60, 65, 60, 60, 50, 35, 0, 25]]
        depot = 0
        num_vehicles = 3
        max_distance = 150
        cost_coefficient = 1

        expected_output = "The distance matrix does not have equal rows and columns."

        try:
            result = ortools_vrp_solver(distance_matrix, depot, num_vehicles, max_distance, cost_coefficient)
        except Exception as e:
            self.assertEqual(str(e), expected_output)

    def test_negative_depot(self):
        distance_matrix = [[0, 10, 15, 20],
                           [10, 0, 35, 25],
                           [15, 35, 0, 30],
                           [20, 25, 30, 0]]
        depot = -1
        num_vehicles = 1
        max_distance = 100
        cost_coefficient = 1

        expected_output = "depot should be greater than or equal to zero."

        try:
            result = ortools_vrp_solver(distance_matrix, depot, num_vehicles, max_distance, cost_coefficient)
        except Exception as e:
            self.assertEqual(str(e), expected_output)

    def test_negative_num_vehicles(self):
        distance_matrix = [[0, 10, 15, 20],
                           [10, 0, 35, 25],
                           [15, 35, 0, 30],
                           [20, 25, 30, 0]]
        depot = 1
        num_vehicles = -1
        max_distance = 100
        cost_coefficient = 1

        expected_output = "Number of vehicles should be greater than or equal to zero."

        try:
            result = ortools_vrp_solver(distance_matrix, depot, num_vehicles, max_distance, cost_coefficient)
        except Exception as e:
            self.assertEqual(str(e), expected_output)

    def test_negative_max_distance(self):
        distance_matrix = [[0, 10, 15, 20],
                           [10, 0, 35, 25],
                           [15, 35, 0, 30],
                           [20, 25, 30, 0]]
        depot = 1
        num_vehicles = 1
        max_distance = -1
        cost_coefficient = 1

        expected_output = "Max distance should be greater than or equal to zero."

        try:
            result = ortools_vrp_solver(distance_matrix, depot, num_vehicles, max_distance, cost_coefficient)
        except Exception as e:
            self.assertEqual(str(e), expected_output)

    def test_negative_coefficient(self):
        distance_matrix = [[0, 10, 15, 20],
                           [10, 0, 35, 25],
                           [15, 35, 0, 30],
                           [20, 25, 30, 0]]
        depot = 1
        num_vehicles = 1
        max_distance = 1
        cost_coefficient = -1

        expected_output = "Cost coefficient should be greater than or equal to zero."

        try:
            result = ortools_vrp_solver(distance_matrix, depot, num_vehicles, max_distance, cost_coefficient)
        except Exception as e:
            self.assertEqual(str(e), expected_output)


if __name__ == '__main__':
    unittest.main()
