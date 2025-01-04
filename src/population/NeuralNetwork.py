from math import tanh

import config
from src.population.Layer import Layer, LateralConnections, DirectConnections
from src.population.Sensor import Sensor
from src.population.SensorActionEnums import SensorType, ActionType, NeuronType
from src.utils.Oscilator import Oscillator
from src.utils.utils import bin_to_signed_int

sensors_num = len(list(SensorType)) if not config.DISABLE_PHEROMONES else len(list(SensorType)) - 3
action_num = len(list(ActionType)) if not config.DISABLE_PHEROMONES else len(list(ActionType)) - 1


def decode_connection(hex_gene: str) -> tuple[int, NeuronType, int, NeuronType, float]:
    bin_gene = bin(int(hex_gene, 16))[2:].zfill(32)

    source_type = NeuronType.SENSOR if int(bin_gene[0]) == 0 else NeuronType.INNER
    num_sources = sensors_num if source_type == NeuronType.SENSOR else config.MAX_NUMBER_OF_INNER_NEURONS
    source_id = bin_to_signed_int(bin_gene[1:8]) % num_sources

    target_type = NeuronType.ACTION if int(bin_gene[8]) == 0 else NeuronType.INNER
    num_targets = action_num if target_type == NeuronType.ACTION else config.MAX_NUMBER_OF_INNER_NEURONS
    target_id = bin_to_signed_int(bin_gene[9:16]) % num_targets

    weight = bin_to_signed_int(bin_gene[16:32]) / 8000  # make it a float from around (-4,4)

    return source_id, source_type, target_id, target_type, weight


class NeuralNetwork:
    def __init__(self, genome: list[str], specimen: 'Specimen'):
        self.sensors = None
        self.layers = None
        self.specimen = specimen
        self.__genome_to_neural_network(genome)

        return

    def __genome_to_neural_network(self, genome: list[str]):
        sensor_inner = {}
        inner_inner = {}
        inner_action = {}
        sensor_action = {}
        sensors_ids = set()
        for hex_gene in genome:
            assert len(hex_gene) == 8
            source_id, source_type, target_id, target_type, weight = decode_connection(hex_gene)

            match (source_type, target_type):
                case (NeuronType.SENSOR, NeuronType.INNER):
                    sensors_ids.add(source_id)
                    if target_id not in sensor_inner:
                        sensor_inner[target_id] = []
                    sensor_inner.get(target_id).append((source_id, weight))
                case (NeuronType.INNER, NeuronType.INNER):
                    if target_id not in inner_inner:
                        inner_inner[target_id] = []
                    inner_inner.get(target_id).append((source_id, weight))
                case (NeuronType.INNER, NeuronType.ACTION):
                    if target_id not in inner_action:
                        inner_action[target_id] = []
                    inner_action.get(target_id).append((source_id, weight))
                case (NeuronType.SENSOR, NeuronType.ACTION):
                    sensors_ids.add(source_id)
                    if target_id not in sensor_action:
                        sensor_action[target_id] = []
                    sensor_action.get(target_id).append((source_id, weight))

        self.layers = DirectConnections(sensor_action).add_activation_func(tanh)
        self.layers.next(
            Layer(sensor_inner)).next(
            LateralConnections(inner_inner)
            .add_activation_func(tanh)).next(
            Layer(inner_action))
        used_sensors = self.layers.optimize(sensors_ids)
        # visualize_neural_network(self.layers.get_network())
        self.sensors = Sensor(used_sensors, self.specimen)
        if SensorType.OSC.value in used_sensors:
            self.specimen.oscillator = Oscillator()
        return

    def run(self) -> dict[ActionType, float]:
        sensors_values = self.sensors.sense()
        action_results = self.layers.run(sensors_values)

        return {ActionType(idx): value for idx, value in action_results.items()}
