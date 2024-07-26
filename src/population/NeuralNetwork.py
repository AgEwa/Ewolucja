from src.population.SensorActionEnums import SensorType, ActionType, NeuronType
from src.utils.NumbersHelpers import bin_to_signed_int
from src.population.Sensor import Sensor

class Neuron:
    def __init__(self, neuron_type):
        self.type = neuron_type
        self.value = 0
        self.connections = [] # pairs, neuron and weight


    def receive_input(self, input_val):
        self.value += input_val

    def forward(self):
        # math operations if needed on value
        for neuron, weight in self.connections:
            neuron.receive_input(weight * self.value)




class NeuralNetwork:
    def __init__(self, genome, internal_max):
        self.neurons = {
            NeuronType.SENSOR: {},
            NeuronType.INTERNAL: {},
            NeuronType.OUTPUT: {}
        }
        self.__genome_to_neural_network(genome, internal_max)

    def __genome_to_neural_network(self, genome, internal_max):
        for hex_gene in genome:

            # decode
            bin_gene = bin(int(hex_gene, 16))[2:].zfill(32)
            source_type = NeuronType.SENSOR if int(bin_gene[:1]) == 0 else NeuronType.INTERNAL
            num_source = SensorType.NUM_SENSORS.value if source_type == NeuronType.SENSOR else internal_max
            source_id = bin_to_signed_int(bin_gene[1:8]) % num_source
            target_type = NeuronType.OUTPUT if int(bin_gene[8:9]) == 0 else NeuronType.INTERNAL
            num_target = ActionType.NUM_ACTIONS.value if target_type == NeuronType.OUTPUT else internal_max
            target_id = bin_to_signed_int(bin_gene[9:16]) % num_target
            weight = bin_to_signed_int(bin_gene[16:32]) / 8000  # make it a float from around (-4,4)
            print(source_type, weight, target_type)

            # add neurons to NN
            if source_id not in self.neurons.get(source_type):
                if source_type == NeuronType.SENSOR:
                    self.neurons.get(source_type)[source_id] = Sensor(SensorType(source_id))
                else:
                    self.neurons.get(source_type)[source_id] = Neuron(source_type)
            elif target_id not in self.neurons.get(target_type):
                self.neurons.get(target_type)[target_id] = Neuron(target_type)

            # add connection
            self.neurons.get(source_type).get(source_id).connections.append(
                (self.neurons.get(target_type).get(target_id), weight))


    def run(self):
        # after feeding sensors values from the world
        for _, sensor in self.neurons.get(NeuronType.SENSOR):
            sensor.sense()
            sensor.forward()

        for _, neuron in self.neurons.get(NeuronType.INTERNAL):
            neuron.forward()

        for action_type, neuron in self.neurons.get(NeuronType.OUTPUT):
            neuron.forward()
            # Action(action_type, neuron.value)

