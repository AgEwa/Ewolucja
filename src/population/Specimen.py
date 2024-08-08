import config

from src.types.Direction import Direction
from src.population.NeuralNetwork import NeuralNetwork


class Specimen:
    def __init__(self, index, loc, genome):
        self.alive = True
        self.index = index
        self.location = loc
        self.birth_location = loc
        self.age = 0
        self.genome = genome
        self.brain = NeuralNetwork(genome)
        self.responsiveness = 0.5
        self.oscPeriod = 34
        self.longProbeDist = config.LONG_PROBE_DISTANCE
        self.last_movement_direction = Direction.random()
        self.challengeBits = False

        return

    def __str__(self):
        return f'{self.location} {self.genome}'

    def __repr__(self):
        return f'{self.location} {self.genome}'
