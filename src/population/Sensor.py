from src.population.NeuralNetwork import Neuron
from src.population.SensorActionEnums import NeuronType

class Sensor(Neuron):
    # let's make sensor-children for every type and make them be able to get values on their own instead of feeding them
    def __init__(self, sensor_type):
        Neuron.__init__(NeuronType.SENSOR)
        # mach case from python 3.10, upgrade!!
        # per sensor type make different sensors that have the same method
        # sense() or sth overwritten and 'senses' sth different
        self.sensor_type = sensor_type
        pass

    def sense(self):
        pass
    #or just based of sensor_type match case which method to use as sense()