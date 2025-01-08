from unittest import TestCase
from unittest.mock import patch, Mock

from src.population.Layer import Layer
from src.population.NeuralNetwork import decode_connection, NeuralNetwork
from src.population.SensorActionEnums import NeuronType, SensorType, ActionType


class TestDecodeConnection(TestCase):
    def test_decode_connection(self):
        # given
        mock_settings = Mock()
        mock_settings.disable_pheromones = False
        mock_settings.max_number_of_inner_neurons = 8
        settings_patch = patch('src.population.Specimen.Settings.settings', mock_settings)
        settings_patch.start()
        hex_gene = "F0F0F0F0"
        sensors_num = len(list(SensorType))
        action_num = len(list(ActionType))
        # when
        source_id, source_type, target_id, target_type, weight = decode_connection(hex_gene)

        # then
        self.assertIn(source_type, [NeuronType.SENSOR, NeuronType.INNER])
        self.assertIn(target_type, [NeuronType.ACTION, NeuronType.INNER])
        self.assertGreaterEqual(source_id, 0)
        self.assertLess(source_id, sensors_num if source_type == NeuronType.SENSOR else 8)
        self.assertGreaterEqual(target_id, 0)
        self.assertLess(target_id, action_num if target_type == NeuronType.ACTION else 8)
        self.assertTrue(-4 <= weight <= 4)


class TestNeuralNetwork(TestCase):

    def setUp(self):
        mock_settings = Mock()
        mock_settings.disable_pheromones = False
        mock_settings.max_number_of_inner_neurons = 2
        settings_patch = patch('src.population.Specimen.Settings.settings', mock_settings)
        settings_patch.start()
        self.mock_specimen = Mock()
        self.mock_specimen.oscillator = None
        self.mock_genome = ["00000001", "80000002", "C0000003"]
        self.network = NeuralNetwork(self.mock_genome, self.mock_specimen)

    def test_initialization(self):
        # check initialization
        self.assertIsNotNone(self.network.layers)
        self.assertIsNotNone(self.network.sensors)
        self.assertTrue(isinstance(self.network.layers, Layer))

    def test_run_method(self):
        # given
        self.network.sensors.sense = Mock(return_value={0: 1.0})
        self.network.layers.run = Mock(return_value={1: 0.5, 2: 0.7})
        # when
        result = self.network.run()
        # then
        self.assertIsInstance(result, dict)
        self.assertIn(ActionType(1), result)
        self.assertEqual(0.5, result.get(ActionType(1)))
        self.assertIn(ActionType(2), result)
        self.assertEqual(0.7, result.get(ActionType(2)))
