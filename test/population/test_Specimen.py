import math
from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock

import config
from src.LocationTypes import Coord, Direction, Compass
from src.population.SensorActionEnums import ActionType
from src.population.Specimen import Specimen
from src.utils.utils import squeeze, response_curve


class TestSpecimen(TestCase):

    @patch('src.population.Specimen.NeuralNetwork', autospec=True)
    def setUp(self, mock_neural_network):
        self.index = 1
        self.location = Coord(0, 0)
        self.genome = ["a3f", "b2e", "c1d"]
        self.mock_brain = MagicMock()
        mock_neural_network.return_value = self.mock_brain
        self.specimen = Specimen(self.index, self.location, self.genome.copy())

    def test_initialization(self):
        self.assertTrue(self.specimen.alive)
        self.assertEqual(self.specimen.index, self.index)
        self.assertEqual(self.specimen.location, self.location)
        self.assertEqual(self.specimen.birth_location, self.location)
        self.assertEqual(self.specimen.age, 0)
        self.assertEqual(self.specimen.energy, self.specimen.max_energy)

    def test_eat(self):
        # given
        initial_energy = self.specimen.energy
        initial_max_energy = self.specimen.max_energy
        # when
        self.specimen.eat()
        # then
        if initial_max_energy < config.MAX_ENERGY_LEVEL_SUPREMUM:
            self.assertEqual(self.specimen.max_energy, initial_max_energy + config.FOOD_INCREASED_MAX_LEVEL)
        self.assertLessEqual(self.specimen.energy, self.specimen.max_energy)
        if initial_energy + config.FOOD_ADDED_ENERGY > initial_max_energy + config.FOOD_INCREASED_MAX_LEVEL:
            self.assertEqual(self.specimen.energy, initial_max_energy + config.FOOD_INCREASED_MAX_LEVEL)
        else:
            self.assertEqual(self.specimen.energy, initial_energy + config.FOOD_ADDED_ENERGY)

    def test_act_for_non_move_actions(self):
        # given
        value = 0.6
        p_actions = {
            ActionType.SET_RESPONSIVENESS: value,
            ActionType.SET_OSCILLATOR_PERIOD: value,
            ActionType.SET_LONGPROBE_DIST: value
        }
        expected_responsiveness = squeeze(value)
        expected_period = 1 + int(1.5 + math.exp(7 * squeeze(value)))
        expected_dist = 1 + squeeze(value) * 32
        mock_oscillator = Mock()  # Create a mock for the oscillator
        self.specimen.oscillator = mock_oscillator  # Attach the oscillator mock to the specimen
        mock_oscillator.set_frequency = Mock()
        # when
        self.specimen.act(p_actions)
        # then
        self.assertEqual(expected_responsiveness, self.specimen.responsiveness)
        self.assertEqual(response_curve(expected_responsiveness), self.specimen.responsiveness_adj)
        mock_oscillator.set_frequency.assert_called_once_with(1/expected_period)
        self.assertEqual(int(expected_dist), self.specimen.long_probe_dist)

    def test_act_for_phermone(self):
        # given
        value = 0.5
        p_actions = {ActionType.EMIT_PHEROMONE: value}
        # when
        self.specimen.act(p_actions)
        # then
        pass

    @patch('src.LocationTypes.Conversions.direction_as_normalized_coord')
    @patch('src.population.Specimen.random.choice')
    @patch('src.population.Specimen.probability')
    @patch('src.LocationTypes.Conversions.coord_as_direction')
    @patch('src.population.Specimen.move_queue')
    def test_act_for_move(self, mock_move_queue, mock_coord_as_direction, mock_probability, mock_choice,
                          mock_direction_as_coord):
        # given
        mock_coord_as_direction.return_value = Direction(Compass.CENTER)
        mock_probability.return_value = True
        mock_choice.return_value = -1
        mock_direction_as_coord.return_value = Coord(1, 0)
        self.specimen.energy = config.ENERGY_PER_ONE_UNIT_OF_MOVE + 1
        value = 0.6
        p_actions = {
            ActionType.MOVE_X: value,
            ActionType.MOVE_Y: value,
            ActionType.MOVE_EAST: value,
            ActionType.MOVE_WEST: value,
            ActionType.MOVE_NORTH: value,
            ActionType.MOVE_SOUTH: value,
            ActionType.MOVE_FORWARD: value,
            ActionType.MOVE_REVERSE: value,
            ActionType.MOVE_LEFT: value,
            ActionType.MOVE_RIGHT: value,
            ActionType.MOVE_RANDOM: value
        }
        # when
        self.specimen.act(p_actions)
        # then
        mock_probability.asser_calleed()
        mock_move_queue.append.assert_called_once()
        # check if every move happened, was added to path as a step, and got appended to move_queue
        self.assertEqual(11, len(mock_move_queue.append.mock_calls[0].args[0][1]))
