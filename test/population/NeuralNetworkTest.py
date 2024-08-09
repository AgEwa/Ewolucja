from src.population.NeuralNetwork import NeuralNetwork
from utils.utils import generate_hex


def test_genome_to_NN():
    genome = [generate_hex() for _ in range(10)]
    net = NeuralNetwork(genome)
    print(net.neurons)


def test():
    test_genome_to_NN()


test()
