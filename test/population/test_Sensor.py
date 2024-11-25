from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock

from config import NEIGHBOURHOOD_RADIUS
from src.LocationTypes import Direction
from src.external import grid
from src.population.Sensor import Sensor
from src.population.SensorActionEnums import SensorType
from src.utils.utils import squeeze


class TestSensor(TestCase):

    # TODO: add tests for food type sensors

    def setUp(self):
        # mock the Specimen object with its attributes
        self.mock_specimen = Mock()
        self.mock_specimen.age = 5
        self.mock_specimen.location = Mock()
        self.mock_specimen.location.x = 2
        self.mock_specimen.location.y = 3
        self.mock_specimen.osc_period = 100
        self.mock_specimen.last_movement = Mock()
        self.mock_specimen.last_movement.x = 1
        self.mock_specimen.last_movement.y = 2
        self.mock_specimen.last_movement_direction = Mock(spec=Direction)
        self.mock_specimen.genome = ['deadbeef', 'cafebabe', '12345678']

        # create Sensor instance using the mocked Specimen
        self.sensor = Sensor(sensor_type=SensorType.AGE, specimen=self.mock_specimen)

        # mock the Grid
        self.grid_mock = grid
        self.grid_mock.width = 5
        self.grid_mock.height = 5
        self.grid_mock.in_bounds_xy = Mock(side_effect=lambda x, y: 0 <= x < 5 and 0 <= y < 5)
        self.grid_mock.is_occupied_at_xy = Mock(return_value=False)
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

    def test_get_specimen_age(self):
        # given SensorType.AGE set up earlier
        # when
        self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(self.mock_specimen.age)), self.sensor.value)

    def test_get_location_x(self):
        # given
        self.sensor.sensor_type = SensorType.LOC_X
        # when
        self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(self.mock_specimen.location.x)), self.sensor.value)

    def test_get_random_value(self):
        # given
        self.sensor.sensor_type = SensorType.RANDOM
        # when
        self.sensor.sense()
        # then
        self.assertGreaterEqual(self.sensor.value, -1)
        self.assertLessEqual(self.sensor.value, 1)

    def test_get_boundary_distance_x(self):
        # given
        self.sensor.sensor_type = SensorType.BOUNDARY_DIST_X
        # when
        self.sensor.sense()
        # then
        # location.x is 2 and grid width is 5 so the minimum distance x to boundary is 2
        self.assertEqual(squeeze(float(2)), self.sensor.value)

    def test_get_boundary_distance_y(self):
        # given
        self.sensor.sensor_type = SensorType.BOUNDARY_DIST_Y
        # when
        self.sensor.sense()
        # then
        # location.y is 3 and grid height is 5 so the minimum distance y to boundary is 2
        self.assertEqual(squeeze(float(2)), self.sensor.value)

    def test_get_boundary_distance(self):
        # given
        self.sensor.sensor_type = SensorType.BOUNDARY_DIST
        # when
        self.sensor.sense()
        # then
        # boundary distances are 2 for x and 2 for y so the minimum distance should be 2
        self.assertEqual(squeeze(float(2)), self.sensor.value)

    def test_get_last_move_dist_y(self):
        # given
        self.sensor.sensor_type = SensorType.LAST_MOVE_DIST_Y
        # when
        self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(self.mock_specimen.last_movement.y)), self.sensor.value)

    def test_get_last_move_dist_x(self):
        # given
        self.sensor.sensor_type = SensorType.LAST_MOVE_DIST_X
        # when
        self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(self.mock_specimen.last_movement.x)), self.sensor.value)

    def test_get_population_density_in_neighbourhood(self):
        # given
        self.sensor.sensor_type = SensorType.POPULATION
        # mock that some cells in the neighborhood are occupied
        self.grid_mock.is_occupied_at_xy.side_effect = lambda x, y: (x, y) in [(1, 2), (2, 3), (3, 4)]
        # when
        self.sensor.sense()
        # then
        # 3 occupied cells in the neighborhood
        expected_density = 3 / (4 * NEIGHBOURHOOD_RADIUS ** 2)
        self.assertEqual(squeeze(float(expected_density)), self.sensor.value)

    def test_get_population_density_forward_reverse(self):
        # given
        self.sensor.sensor_type = SensorType.POPULATION_FWD
        # mock that some cells in the line are occupied
        self.grid_mock.is_occupied_at_xy.side_effect = lambda x, y: (x, y) in [(3, 3), (4, 3)]
        # when
        self.sensor.sense()
        # then
        # 2 occupied cells in the line of 5 (grid is 5x5 and specimen last direction was east)
        expected_density = 2 / 5
        self.assertEqual(squeeze(float(expected_density)), self.sensor.value)

    def test_get_population_density_left_right(self):
        # given
        self.sensor.sensor_type = SensorType.POPULATION_LR
        # mock that some cells in the line are occupied
        self.grid_mock.is_occupied_at_xy.side_effect = lambda x, y: (x, y) in [(3, 3), (0, 3)]
        # when
        self.sensor.sense()
        # then
        # 2 occupied cells in the line of 5 (grid is 5x5 and specimen last direction was east)
        expected_density = 2 / 5
        self.assertEqual(squeeze(float(expected_density)), self.sensor.value)

    def test_get_barrier_dist_forward_reverse(self):
        # given
        self.sensor.sensor_type = SensorType.BARRIER_FWD
        self.grid_mock.is_barrier_at_xy.side_effect = lambda x, y: (x, y) in [(4, 3)]
        # when
        self.sensor.sense()
        # then
        # barrier is at (4,3), specimen is at (2, 3) so distance is 2
        self.assertEqual(squeeze(float(2)), self.sensor.value)

    def test_get_barrier_dist_left_right(self):
        # given
        self.sensor.sensor_type = SensorType.BARRIER_LR
        self.grid_mock.is_barrier_at_xy.side_effect = lambda x, y: (x, y) in [(3, 3)]
        # when
        self.sensor.sense()
        # then
        # barrier is at (3,3), specimen is at (2, 3) so distance is 1
        self.assertEqual(squeeze(float(1)), self.sensor.value)

    def test_look_forward_pop_gen(self):
        # given
        self.sensor.sensor_type = SensorType.GENETIC_SIM_FWD
        # mock the grid to have an occupied cell with another specimen
        self.grid_mock.is_occupied_at_xy.return_value = True
        self.grid_mock.at_xy = Mock(return_value=1)  # index in pop to get another specimen
        # when
        self.sensor.sense()
        # then
        expected_similarity = self.sensor._genetic_similarity(['cafedead', 'babe1234', '87654321'])
        self.assertEqual(squeeze(float(expected_similarity)), self.sensor.value)

    def test_look_forward_pop(self):
        # given
        self.sensor.sensor_type = SensorType.LONGPROBE_POP_FWD
        # mock the grid to have an occupied cell at first check
        self.grid_mock.is_occupied_at_xy.return_value = True
        # when
        self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(1)), self.sensor.value)

    def test_look_forward_bar(self):
        # given
        self.sensor.sensor_type = SensorType.LONGPROBE_BAR_FWD
        # mock the grid to have a barrier at first check
        self.grid_mock.is_barrier_at_xy.return_value = True
        # when
        self.sensor.sense()
        # then
        self.assertEqual(squeeze(float(1)), self.sensor.value)

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


