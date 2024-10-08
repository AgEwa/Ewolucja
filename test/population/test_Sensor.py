from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock

from config import NEIGHBOURHOOD_RADIUS
from src.population.Sensor import Sensor
from src.population.SensorActionEnums import SensorType
from src.typess import Direction


class TestSensor(TestCase):

    def setUp(self):
        # Mocking the Specimen object
        self.mock_specimen = Mock()

        # Setting up necessary attributes for the mock specimen
        self.mock_specimen.age = 5  # Example: setting age to 5
        self.mock_specimen.location = Mock()  # Mocking location attribute
        self.mock_specimen.location.x = 2
        self.mock_specimen.location.y = 3
        self.mock_specimen.osc_period = 100  # Example oscillation period
        self.mock_specimen.last_movement = Mock()
        self.mock_specimen.last_movement.x = 1
        self.mock_specimen.last_movement.y = 2
        self.mock_specimen.last_movement_direction = Mock(spec=Direction)
        self.mock_specimen.genome = ['deadbeef', 'cafebabe', '12345678']

        # Creating a Sensor instance using the mocked Specimen
        self.sensor = Sensor(sensor_type=SensorType.AGE, specimen=self.mock_specimen)

        # Mocking the grid object
        from src.external import grid
        self.grid_mock = grid
        self.grid_mock.width = 5
        self.grid_mock.height = 5
        self.grid_mock.in_bounds_xy = Mock(side_effect=lambda x, y: 0 <= x < 5 and 0 <= y < 5)
        self.grid_mock.is_occupied_at_xy = Mock(return_value=False)
        self.grid_mock.is_barrier_at_xy = Mock(return_value=False)

        # mock some other specimen in population
        self.mock_other_specimen = Mock()

        # Setting up necessary attributes for the mock specimen
        self.mock_other_specimen.genome = ['cafedead', 'babe1234', '87654321']

        # Create a mock for the population data
        self.mock_population = MagicMock()
        self.mock_population.__getitem__.side_effect = lambda idx: {
            1: self.mock_other_specimen
        }.get(idx, None)

        # Patch where `population` is being used in the `Sensor` class
        self.population_patch = patch('src.population.Sensor.population', self.mock_population)
        self.mock_population_patch = self.population_patch.start()

        # Patching NEIGHBOURHOOD_RADIUS from config
        self.neighbourhood_radius_patch = patch('config.NEIGHBOURHOOD_RADIUS', 1)
        self.neighbourhood_radius_patch.start()

        # Mocking Conversions for directions
        self.mock_mod = Mock()
        self.mock_mod.x = 1
        self.mock_mod.y = 0
        patch('src.typess.Conversions.direction_as_normalized_coord', return_value=self.mock_mod).start()

    def tearDown(self):
        self.population_patch.stop()
        self.neighbourhood_radius_patch.stop()

    def test_get_specimen_age(self):
        # Testing the `sense()` method for SensorType.AGE
        self.sensor.sense()

        # Since sensor type is AGE, the value should be the age of the mock specimen
        self.assertEqual(self.sensor.value, 5)

    def test_get_location_x(self):
        # Changing the sensor type to LOC_X
        self.sensor.sensor_type = SensorType.LOC_X
        self.sensor.sense()

        # The value should now reflect the x-coordinate of the location
        self.assertEqual(self.sensor.value, 2)

    def test_get_random_value(self):
        # Changing the sensor type to RANDOM
        self.sensor.sensor_type = SensorType.RANDOM
        self.sensor.sense()

        # The value should be between -1 and 1
        self.assertGreaterEqual(self.sensor.value, -1)
        self.assertLessEqual(self.sensor.value, 1)

    def test_get_boundary_distance_x(self):
        # Mocking the grid object and setting width
        from src.external import grid
        grid.width = 50

        # Changing the sensor type to BOUNDARY_DIST_X
        self.sensor.sensor_type = SensorType.BOUNDARY_DIST_X
        self.sensor.sense()

        # Since location.x is 2 and grid width is 5, the minimum distance to boundary is 2
        self.assertEqual(self.sensor.value, 2)

    def test_get_boundary_distance_y(self):
        # Changing the sensor type to BOUNDARY_DIST_Y
        self.sensor.sensor_type = SensorType.BOUNDARY_DIST_Y
        self.sensor.sense()

        # Since location.y is 3 and grid height is 5, the minimum distance to boundary is 2
        self.assertEqual(self.sensor.value, 2)

    def test_get_boundary_distance(self):
        # Changing the sensor type to BOUNDARY_DIST
        self.sensor.sensor_type = SensorType.BOUNDARY_DIST
        self.sensor.sense()

        # Since the boundary distances are 2 for x and 2 for y, the minimum distance should be 2
        self.assertEqual(self.sensor.value, 2)

    def test_get_last_move_dist_y(self):
        # Changing the sensor type to LAST_MOVE_DIST_Y
        self.sensor.sensor_type = SensorType.LAST_MOVE_DIST_Y
        self.sensor.sense()

        # The value should reflect the last movement in the y direction, which is 2
        self.assertEqual(self.sensor.value, 2)

    def test_get_last_move_dist_x(self):
        # Changing the sensor type to LAST_MOVE_DIST_X
        self.sensor.sensor_type = SensorType.LAST_MOVE_DIST_X
        self.sensor.sense()

        # The value should reflect the last movement in the x direction, which is 1
        self.assertEqual(self.sensor.value, 1)

    def test_get_population_density_in_neighbourhood(self):
        # Changing the sensor type to POPULATION
        self.sensor.sensor_type = SensorType.POPULATION

        # Mock the behavior of grid methods for population density
        # Mock that some cells in the neighborhood are occupied
        self.grid_mock.is_occupied_at_xy.side_effect = lambda x, y: (x, y) in [(1, 2), (2, 3), (3, 4)]
        # config.NEIGHBOURHOOD_RADIUS = 1  # Setting the neighborhood radius to 1 for this test

        self.sensor.sense()

        # There are 3 occupied cells in a neighborhood of 9 cells (3x3 grid)s
        expected_density = 3 / (4 * NEIGHBOURHOOD_RADIUS ** 2)  # 3 / (4 * 1^2) = 3 / 4 = 0.75
        self.assertAlmostEqual(self.sensor.value, expected_density)

        ############################################################# down from here doesn't work because of pop etc

    def test_get_population_density_forward_reverse(self):
        # Changing the sensor type to POPULATION_FWD
        self.sensor.sensor_type = SensorType.POPULATION_FWD

        # Mock the behavior of grid methods for population density
        self.grid_mock.is_occupied_at_xy.side_effect = lambda x, y: (x, y) in [(3, 3), (4, 3)]

        self.sensor.sense()

        # We expect 2 cells in the line of direction to be occupied
        expected_density = 2 / 5
        self.assertAlmostEqual(self.sensor.value, expected_density, places=2)

    def test_get_population_density_left_right(self):
        # Changing the sensor type to POPULATION_LR
        self.sensor.sensor_type = SensorType.POPULATION_LR

        # Mock rotation of direction by 90 degrees and grid method behavior
        self.grid_mock.is_occupied_at_xy.side_effect = lambda x, y: (x, y) in [(3, 3), (0, 3)]

        self.sensor.sense()

        # We expect 2 cells in the perpendicular direction to be occupied
        expected_density = 2 / 5
        self.assertAlmostEqual(self.sensor.value, expected_density, places=2)

    def test_get_barrier_dist_forward_reverse(self):
        # Changing the sensor type to BARRIER_FWD
        self.sensor.sensor_type = SensorType.BARRIER_FWD

        # Mocking barriers at specific distances
        self.grid_mock.is_barrier_at_xy.side_effect = lambda x, y: (x, y) in [(4, 3)]

        self.sensor.sense()

        # The barrier is at distance 2 in the forward direction, expect distance to be 2
        self.assertEqual(self.sensor.value, 2)

    def test_get_barrier_dist_left_right(self):
        # Changing the sensor type to BARRIER_LR
        self.sensor.sensor_type = SensorType.BARRIER_LR

        # Mock rotation of direction by 90 degrees and set barriers
        self.grid_mock.is_barrier_at_xy.side_effect = lambda x, y: (x, y) in [(3, 3)]

        self.sensor.sense()

        # The barrier is at distance 1 in the left-right direction, expect distance to be 1
        self.assertEqual(self.sensor.value, 1)

    def test_look_forward_pop_gen(self):
        # Changing the sensor type to GENETIC_SIM_FWD
        self.sensor.sensor_type = SensorType.GENETIC_SIM_FWD

        # Mock the grid to have an occupied cell with another specimen genome
        self.grid_mock.is_occupied_at_xy.return_value = True
        self.grid_mock.at_xy = Mock(return_value=1)  # index in pop to get specimen

        # Calculate genetic similarity
        self.sensor.sense()

        # Calculate expected similarity manually
        expected_similarity = self.sensor._genetic_similarity(['cafedead', 'babe1234', '87654321'])
        self.assertEqual(self.sensor.value, expected_similarity)

    def test_genetic_similarity(self):
        # Manually test genetic similarity calculation between two genomes
        genome1 = ['deadbeef', 'cafebabe']
        genome2 = ['deadbeef', 'cafebabe']
        self.mock_specimen.genome = genome1

        # Use the _genetic_similarity method
        similarity = self.sensor._genetic_similarity(genome2)

        # Expect 100% similarity (1.0)
        self.assertEqual(similarity, 1.0)

        # Test with a completely different genome
        genome3 = ['00000000', 'ffffffff']
        similarity = self.sensor._genetic_similarity(genome3)

        # The similarity should be computed as a fraction of matching bits
        self.assertTrue(0.0 <= similarity <= 1.0)
