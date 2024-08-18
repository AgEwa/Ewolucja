import config

from src.population.Neuron import Neuron
from src.population.Sensor import Sensor
from src.population.SensorActionEnums import SensorType, ActionType, NeuronType
from src.utils import bin_to_signed_int


class NeuralNetwork:
    def __init__(self, genome):
        self.neurons = {NeuronType.SENSOR: {}, NeuronType.NEURON: {}, NeuronType.ACTION: {}}

        self.__genome_to_neural_network(genome)

        return

    def __genome_to_neural_network(self, genome):
        for hex_gene in genome:

            # decode
            bin_gene = bin(int(hex_gene, 16))[2:].zfill(32)
            source_type = NeuronType.SENSOR if int(bin_gene[:1]) == 0 else NeuronType.NEURON
            num_source = len(list(SensorType)) if source_type == NeuronType.SENSOR else config.MAX_NUMBER_OF_INNER_NEURONS
            source_id = bin_to_signed_int(bin_gene[1:8]) % num_source
            target_type = NeuronType.ACTION if int(bin_gene[8:9]) == 0 else NeuronType.NEURON
            num_target = len(list(ActionType)) if target_type == NeuronType.ACTION else config.MAX_NUMBER_OF_INNER_NEURONS
            target_id = bin_to_signed_int(bin_gene[9:16]) % num_target
            weight = bin_to_signed_int(bin_gene[16:32]) / 8000  # make it a float from around (-4,4)

            # add neurons to NN
            if source_id not in self.neurons.get(source_type):
                if source_type == NeuronType.SENSOR:
                    self.neurons.get(source_type)[source_id] = Sensor(SensorType(source_id))
                else:
                    self.neurons.get(source_type)[source_id] = Neuron(source_type)
            elif target_id not in self.neurons.get(target_type):
                self.neurons.get(target_type)[target_id] = Neuron(target_type)

            # add connection
            self.neurons.get(source_type).get(source_id).connections.append((self.neurons.get(target_type).get(target_id), weight))

    def run(self):
        # after feeding sensors values from the world
        for _, sensor in self.neurons.get(NeuronType.SENSOR):
            sensor.sense()
            sensor.forward()

        for _, neuron in self.neurons.get(NeuronType.NEURON):
            neuron.forward()

        for action_type, neuron in self.neurons.get(NeuronType.ACTION):
            neuron.forward()  # Action(action_type, neuron.value)
