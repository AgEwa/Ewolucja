from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock

from config import NEIGHBOURHOOD_RADIUS
from src.LocationTypes import Direction, Compass
from src.external import grid
from src.population.Sensor import Sensor
from src.population.SensorActionEnums import SensorType
from src.utils.utils import squeeze


class TestSensor(TestCase):

    def setUp(self):
        # mock the Specimen object with its attributes
        self.mock_specimen = Mock()
        self.mock_specimen.age = 5
        self.mock_specimen.location = Mock()
        self.mock_specimen.location.x = 2
        self.mock_specimen.location.y = 3
        self.mock_specimen.last_movement = Mock()
        self.mock_specimen.last_movement.x = 1
        self.mock_specimen.last_movement.y = 2
        self.mock_specimen.last_movement_direction = Mock(spec=Direction)
        self.mock_specimen.long_probe_dist = 6
        self.mock_specimen.genome = ['deadbeef', 'cafebabe', '12345678']

        # create Sensor instance using the mocked Specimen
        self.sensor = Sensor(types=set(), specimen=self.mock_specimen)

        # mock the Grid
        self.grid_mock = grid
        self.grid_mock.width = 5
        self.grid_mock.height = 5
        self.grid_mock.in_bounds_xy = Mock(side_effect=lambda x, y: 0 <= x < 5 and 0 <= y < 5)
        self.grid_mock.is_occupied_at_xy = Mock(return_value=False)
        self.grid_mock.is_food_at_xy = Mock(return_value=False)
        self.grid_mock.is_barrier_at_xy = Mock(return_value=False)

        # mock some other Specimen in population and their needed attributes
        self.mock_other_specimen = Mock()
        self.mock_other_specimen.genome = ['cafedead', 'babe1234', '87654321']

        # mock population and its get method
        self.mock_population = MagicMock()
        self.mock_population.__getitem__.side_effect = lambda idx: {1: self.mock_other_specimen}.get(idx, None)

        # patch population usage in the Sensor class
        self.population_patch = patch('src.population.Sensor.population', self.mock_population)
        self.mock_population_patch = self.population_patch.start()

        # patch NEIGHBOURHOOD_RADIUS from config
        self.neighbourhood_radius_patch = patch('config.NEIGHBOURHOOD_RADIUS', 1)
        self.neighbourhood_radius_patch.start()

        # mock Conversions for directions
        self.mock_mod = Mock()
        self.mock_mod.x = 1
        self.mock_mod.y = 0
        self.direction_as_normalized_coord_patch = patch('src.LocationTypes.Conversions.direction_as_normalized_coord',
                                                         return_value=self.mock_mod)  # returns east direction
        self.direction_as_normalized_coord_patch.start()

    def tearDown(self):
        self.population_patch.stop()
        self.neighbourhood_radius_patch.stop()
        self.direction_as_normalized_coord_patch.stop()

    def test_get_oscillating_value(self):
        # given
        value = 0.3
        mock_oscillator = Mock()  # Create a mock for the oscillator
        self.mock_specimen.oscillator = mock_oscillator  # Attach the oscillator mock to the specimen
        mock_oscillator.get_value.return_value = value

        sensor_type = SensorType.OSC.value
        self.sensor.types.add(sensor_type)

        # when
        result = self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(value)), result.get(sensor_type))

    def test_get_specimen_age(self):
        # given
        sensor_type = SensorType.AGE.value
        self.sensor.types.add(sensor_type)
        # when
        result = self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(self.mock_specimen.age)), result.get(sensor_type))

    def test_get_location_x(self):
        # given
        sensor_type = SensorType.LOC_X.value
        self.sensor.types.add(sensor_type)
        # when
        result = self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(self.mock_specimen.location.x)), result.get(sensor_type))

    def test_get_random_value(self):
        # given
        sensor_type = SensorType.RANDOM.value
        self.sensor.types.add(sensor_type)
        # when
        result = self.sensor.sense()
        # then
        self.assertGreaterEqual(result.get(sensor_type), -1)
        self.assertLessEqual(result.get(sensor_type), 1)

    def test_get_boundary_distance_x(self):
        # given
        sensor_type = SensorType.BOUNDARY_DIST_X.value
        self.sensor.types.add(sensor_type)
        # when
        result = self.sensor.sense()
        # then
        # location.x is 2 and grid width is 5 so the minimum distance x to boundary is 2
        self.assertEqual(squeeze(float(2)), result.get(sensor_type))

    def test_get_boundary_distance_y(self):
        # given
        sensor_type = SensorType.BOUNDARY_DIST_Y.value
        self.sensor.types.add(sensor_type)
        # when
        result = self.sensor.sense()
        # then
        # location.y is 3 and grid height is 5 so the minimum distance y to boundary is 2
        self.assertEqual(squeeze(float(2)), result.get(sensor_type))

    def test_get_boundary_distance(self):
        # given
        sensor_type = SensorType.BOUNDARY_DIST.value
        self.sensor.types.add(sensor_type)
        # when
        result = self.sensor.sense()
        # then
        # boundary distances are 2 for x and 2 for y so the minimum distance should be 2
        self.assertEqual(squeeze(float(2)), result.get(sensor_type))

    def test_get_last_move_dist_y(self):
        # given
        sensor_type = SensorType.LAST_MOVE_DIST_Y.value
        self.sensor.types.add(sensor_type)
        # when
        result = self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(self.mock_specimen.last_movement.y)), result.get(sensor_type))

    def test_get_last_move_dist_x(self):
        # given
        sensor_type = SensorType.LAST_MOVE_DIST_X.value
        self.sensor.types.add(sensor_type)
        # when
        result = self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(self.mock_specimen.last_movement.x)), result.get(sensor_type))

    def test_get_population_density_in_neighbourhood(self):
        # given
        sensor_type = SensorType.POPULATION.value
        self.sensor.types.add(sensor_type)
        # mock that some cells in the neighborhood are occupied
        self.grid_mock.is_occupied_at_xy.side_effect = lambda x, y: (x, y) in [(1, 2), (2, 3), (3, 4)]
        # when
        result = self.sensor.sense()
        # then
        # 3 occupied cells in the neighborhood
        expected_density = 3 / (4 * NEIGHBOURHOOD_RADIUS ** 2)
        self.assertEqual(squeeze(float(expected_density)), result.get(sensor_type))

    def test_get_population_density_forward_reverse(self):
        # given
        sensor_type = SensorType.POPULATION_FWD.value
        self.sensor.types.add(sensor_type)
        # mock that some cells in the line are occupied
        self.grid_mock.is_occupied_at_xy.side_effect = lambda x, y: (x, y) in [(3, 3), (4, 3)]
        # when
        result = self.sensor.sense()
        # then
        # 2 occupied cells in the line of 5 (grid is 5x5 and specimen last direction was east)
        expected_density = 2 / 5
        self.assertEqual(squeeze(float(expected_density)), result.get(sensor_type))

    def test_get_population_density_left_right(self):
        # given
        sensor_type = SensorType.POPULATION_LR.value
        self.sensor.types.add(sensor_type)
        # mock that some cells in the line are occupied
        self.grid_mock.is_occupied_at_xy.side_effect = lambda x, y: (x, y) in [(3, 3), (0, 3)]
        # when
        result = self.sensor.sense()
        # then
        # 2 occupied cells in the line of 5 (grid is 5x5 and specimen last direction was east)
        expected_density = 2 / 5
        self.assertEqual(squeeze(float(expected_density)), result.get(sensor_type))

    def test_get_barrier_dist_forward_reverse(self):
        # given
        sensor_type = SensorType.BARRIER_FWD.value
        self.sensor.types.add(sensor_type)
        self.grid_mock.is_barrier_at_xy.side_effect = lambda x, y: (x, y) in [(4, 3)]
        # when
        result = self.sensor.sense()
        # then
        # barrier is at (4,3), specimen is at (2, 3) so distance is 2
        self.assertEqual(squeeze(float(2)), result.get(sensor_type))

    def test_get_barrier_dist_left_right(self):
        # given
        sensor_type = SensorType.BARRIER_LR.value
        self.sensor.types.add(sensor_type)
        self.grid_mock.is_barrier_at_xy.side_effect = lambda x, y: (x, y) in [(3, 3)]
        # when
        result = self.sensor.sense()
        # then
        # barrier is at (3,3), specimen is at (2, 3) so distance is 1
        self.assertEqual(squeeze(float(1)), result.get(sensor_type))

    def test_look_forward_pop_gen(self):
        # given
        sensor_type = SensorType.GENETIC_SIM_FWD.value
        self.sensor.types.add(sensor_type)
        # mock the grid to have an occupied cell with another specimen
        self.grid_mock.is_occupied_at_xy.return_value = True
        self.grid_mock.at_xy = Mock(return_value=1)  # index in pop to get another specimen
        # when
        result = self.sensor.sense()
        # then
        expected_similarity = self.sensor._genetic_similarity(['cafedead', 'babe1234', '87654321'])
        self.assertEqual(squeeze(float(expected_similarity)), result.get(sensor_type))

    def test_look_forward_pop(self):
        # given
        sensor_type = SensorType.LONGPROBE_POP_FWD.value
        self.sensor.types.add(sensor_type)
        # mock the grid to have an occupied cell at first check
        self.grid_mock.is_occupied_at_xy.return_value = True
        # when
        result = self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(1)), result.get(sensor_type))

    def test_look_forward_bar(self):
        # given
        sensor_type = SensorType.LONGPROBE_BAR_FWD.value
        self.sensor.types.add(sensor_type)
        # mock the grid to have a barrier at first check
        self.grid_mock.is_barrier_at_xy.return_value = True
        # when
        result = self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(1)), result.get(sensor_type))

    def test_look_forward_within_dist(self):
        # given
        sensor_type = SensorType.LONGPROBE_BAR_FWD.value
        self.sensor.types.add(sensor_type)
        # mock the grid to have a barrier at first check
        self.mock_specimen.long_probe_dist = 2
        # when
        result = self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(2)), result.get(sensor_type))

    def test_get_food_density_in_neighbourhood(self):
        # given
        sensor_type = SensorType.FOOD.value
        self.sensor.types.add(sensor_type)
        # mock that some cells in the neighborhood are occupied
        self.grid_mock.is_food_at_xy.side_effect = lambda x, y: (x, y) in [(1, 2), (2, 3), (3, 4)]
        self.grid_mock.food_data = {(1, 2): 1, (2, 3): 2, (3, 4): 3}
        # when
        result = self.sensor.sense()
        # then
        # 3 food sources with 6 foods total in the neighborhood
        expected_density = 6 / (4 * NEIGHBOURHOOD_RADIUS ** 2)
        self.assertEqual(squeeze(float(expected_density)), result.get(sensor_type))

    def test_get_food_density_forward_reverse(self):
        # given
        sensor_type = SensorType.FOOD_FWD.value
        self.sensor.types.add(sensor_type)
        # mock that some cells in the line are occupied
        self.grid_mock.is_food_at_xy.side_effect = lambda x, y: (x, y) in [(3, 3), (4, 3)]
        self.grid_mock.food_data = {(3, 3): 2, (4, 3): 0}
        # when
        result = self.sensor.sense()
        # then
        # 2 food sources with 2 foods total in the line of 5 (grid is 5x5 and specimen last direction was east)
        expected_density = 2 / 5
        self.assertEqual(squeeze(float(expected_density)), result.get(sensor_type))

    def test_get_food_density_left_right(self):
        # given
        sensor_type = SensorType.FOOD_LR.value
        self.sensor.types.add(sensor_type)
        # mock that some cells in the line are occupied
        self.grid_mock.is_food_at_xy.side_effect = lambda x, y: (x, y) in [(3, 3), (0, 3)]
        self.grid_mock.food_data = {(3, 3): 2, (0, 3): 1}
        # when
        result = self.sensor.sense()
        # then
        # 2 food sources with 3 foods total in the line of 5 (grid is 5x5 and specimen last direction was east)
        expected_density = 3 / 5
        self.assertEqual(squeeze(float(expected_density)), result.get(sensor_type))

    def test_get_food_dist_forward_reverse(self):
        # given
        sensor_type = SensorType.FOOD_DIST_FWD.value
        self.sensor.types.add(sensor_type)
        self.grid_mock.is_food_at_xy.side_effect = lambda x, y: (x, y) in [(4, 3)]
        # when
        result = self.sensor.sense()
        # then
        # food source is at (4,3), specimen is at (2, 3) so distance is 2
        self.assertEqual(squeeze(float(2)), result.get(sensor_type))

    def test_get_food_dist_left_right(self):
        # given
        sensor_type = SensorType.FOOD_DIST_LR.value
        self.sensor.types.add(sensor_type)
        self.grid_mock.is_food_at_xy.side_effect = lambda x, y: (x, y) in [(3, 3)]
        # when
        result = self.sensor.sense()
        # then
        # food source is at (3,3), specimen is at (2, 3) so distance is 1
        self.assertEqual(squeeze(float(1)), result.get(sensor_type))

    def test_genetic_similarity(self):
        # given identical genomes
        genome1 = ['deadbeef', 'cafebabe']
        genome2 = ['deadbeef', 'cafebabe']
        self.mock_specimen.genome = genome1
        # when
        similarity = self.sensor._genetic_similarity(genome2)
        # then
        self.assertEqual(similarity, 1.0)

        # given different genomes
        genome3 = ['00000000', 'ffffffff']
        # when
        similarity = self.sensor._genetic_similarity(genome3)
        # then
        self.assertTrue(0.0 <= similarity <= 1.0)

    def test_get_pheromone_fwd(self):
        self.grid_mock.pheromones.grid[3, 3] = 0.5
        self.grid_mock.pheromones.grid[4, 3] = 0.7
        self.mock_specimen.last_movement_direction = Direction(Compass.SOUTH)

        sensor_type = SensorType.PHEROMONE_FWD.value
        self.sensor.types.add(sensor_type)
        # when
        result = self.sensor.sense()
        # then
        expected_density = (0.5 + 0.7 + 0) / 3  # Average of pheromone values in the "forward" direction
        self.assertAlmostEqual(squeeze(float(expected_density)), result.get(sensor_type))


    def test_get_pheromone_l(self):
        # Mock pheromone values on the grid
        self.grid_mock.pheromones.grid[2, 1] = 0.5
        self.grid_mock.pheromones.grid[2, 2] = 0.7
        self.mock_specimen.last_movement_direction = Direction(Compass.NORTH)

        # given
        sensor_type = SensorType.PHEROMONE_L.value
        self.sensor.types.add(sensor_type)
        # when
        result = self.sensor.sense()
        # then
        expected_density = (0.5 + 0.7 + 0 ) / 2
        self.assertEqual(squeeze(float(expected_density)), result.get(sensor_type))

    def test_get_pheromone_r(self):
        # Mock pheromone values on the grid
        self.grid_mock.pheromones.grid[2, 4] = 0.5
        self.grid_mock.pheromones.grid[2, 9] = 0.7
        self.mock_specimen.last_movement_direction = Direction(Compass.NORTH)

        # given
        sensor_type = SensorType.PHEROMONE_R.value
        self.sensor.types.add(sensor_type)
        # when
        result = self.sensor.sense()
        # then
        expected_density = (0.5 + 0 + 0) / 3
        self.assertEqual(squeeze(float(expected_density)), result.get(sensor_type))
