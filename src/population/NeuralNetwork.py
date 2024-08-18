import math

import config

from src.population.Neuron import Neuron
from src.population.Sensor import Sensor
from src.population.SensorActionEnums import SensorType, ActionType, NeuronType
from src.utils import bin_to_signed_int


class NeuralNetwork:
    def __init__(self, genome):
        # reminder for Michal: we don't use SensorType and ActionType as keys, 'cause INNER neurons don't have types
        self.neurons = {NeuronType.SENSOR: {}, NeuronType.INNER: {}, NeuronType.ACTION: {}}

        self.__genome_to_neural_network(genome)

        return

    def __genome_to_neural_network(self, genome):
        for hex_gene in genome:

            # decode
            bin_gene = bin(int(hex_gene, 16))[2:].zfill(32)

            source_type = NeuronType.SENSOR if int(bin_gene[0]) == 0 else NeuronType.INNER
            num_unique_sources = len(list(SensorType)) if source_type == NeuronType.SENSOR else config.MAX_NUMBER_OF_INNER_NEURONS
            source_id = bin_to_signed_int(bin_gene[1:8]) % num_unique_sources

            target_type = NeuronType.ACTION if int(bin_gene[8]) == 0 else NeuronType.INNER
            num_unique_targets = len(list(ActionType)) if target_type == NeuronType.ACTION else config.MAX_NUMBER_OF_INNER_NEURONS
            target_id = bin_to_signed_int(bin_gene[9:16]) % num_unique_targets

            weight = bin_to_signed_int(bin_gene[16:32]) / 8000  # make it a float from around (-4,4)

            # add neurons to NN
            if source_id not in self.neurons.get(source_type):
                if source_type == NeuronType.SENSOR:
                    self.neurons.get(source_type)[source_id] = Sensor(SensorType(source_id))
                else:
                    self.neurons.get(source_type)[source_id] = Neuron(source_type)

            if target_id not in self.neurons.get(target_type):
                self.neurons.get(target_type)[target_id] = Neuron(target_type)

            # add connection
            self.neurons.get(source_type).get(source_id).connections.append((self.neurons.get(target_type).get(target_id), weight))

    def run(self, step):
        # after feeding sensors values from the world
        for _, sensor in self.neurons.get(NeuronType.SENSOR).items():
            sensor.sense()
            sensor.forward()

        for _, neuron in self.neurons.get(NeuronType.INNER).items():
            neuron.forward()

        result = {}
        for action_type, neuron in self.neurons.get(NeuronType.ACTION).items():
            result[action_type] = math.tanh(neuron.value)

        return result
