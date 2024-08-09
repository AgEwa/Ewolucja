import config
from src.population.NeuralNetwork import NeuralNetwork
from src.types.Direction import Direction


class Specimen:
    def __init__(self, index, loc, genome):
        self.alive = True
        self.index = index
        self.location = loc  # [y,x]
        self.age = 0
        self.genome = genome
        self.brain = NeuralNetwork(genome)
        self.responsiveness = 0.5
        self.oscPeriod = 34
        self.longProbeDist = config.LONG_PROBE_DISTANCE
        self.last_movement = [Direction.random(), 0]
        # zakłada że jeśli kierunk jest typu N-W to przesuwa się w x i y o całą wartość ruchu(czyli niby o abs(2)movement)
        self.challengeBits = False

        return

    def __str__(self):
        return f'{self.location} {self.genome}'

    def __repr__(self):
        return f'{self.location} {self.genome}'
