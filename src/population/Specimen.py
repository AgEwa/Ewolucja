
from src.utils.NumbersHelpers import generate_hex
from NeuralNetwork import NeuralNetwork
class Specimen:
    def __init__(self, gene_num, birth_loc, ):
        self.genome = [generate_hex() for _ in range(gene_num)]  # list of genes (8 digit hex number)
        self.brain = NeuralNetwork(self.genome)
        self.age = 0
        self.location = birth_loc
        self.responsiveness = 1
        self.last_movement = None
