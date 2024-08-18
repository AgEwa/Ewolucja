from enum import Enum, auto


# copy paste z gita z YT
# I - data about individual specimen
# W - data about the world
class NeuronType(Enum):
    SENSOR = 0
    NEURON = 1
    ACTION = 2


class SensorType(Enum):
    LOC_X = 0  # I distance from left edge
    LOC_Y = 1  # I distance from bottom
    BOUNDARY_DIST_X = 2  # I X distance to nearest edge of world
    BOUNDARY_DIST = 3  # I distance to nearest edge of world
    BOUNDARY_DIST_Y = 4  # I Y distance to nearest edge of world
    GENETIC_SIM_FWD = 5  # I genetic similarity to forward neighbour
    LAST_MOVE_DIR_X = 6  # I +- amount of X movement in last movement
    LAST_MOVE_DIR_Y = 7  # I +- amount of Y movement in last movement
    LONGPROBE_POP_FWD = 8  # W long look for population forward
    LONGPROBE_BAR_FWD = 9  # W long look for barriers forward
    POPULATION = 10  # W population density in neighborhood
    POPULATION_FWD = 11  # W population density in the forward-reverse axis
    POPULATION_LR = 12  # W population density in the left-right axis
    OSC1 = 13  # I oscillator +-value
    AGE = 14  # I
    BARRIER_FWD = 15  # W neighborhood barrier distance forward-reverse axis
    BARRIER_LR = 16  # W neighborhood barrier distance left-right axis
    RANDOM = 17  # random sensor value = uniform distribution
    PHEROMONE = 18  # W strength of pheromone in neighborhood
    PHEROMONE_FWD = 19  # W strength of pheromone in the forward-reverse axis
    PHEROMONE_LR = 20  # W strength of pheromone in the left-right axis


class ActionType(Enum):
    SET_RESPONSIVENESS = auto()  # I
    SET_OSCILLATOR_PERIOD = auto()  # I
    SET_LONGPROBE_DIST = auto()  # I
    EMIT_PHEROMONE = auto()  # W
    KILL = auto()
    MOVE_X = auto()  # W +- X component of movement
    MOVE_Y = auto()  # W +- Y component of movement
    MOVE_EAST = auto()  # W
    MOVE_WEST = auto()  # W
    MOVE_NORTH = auto()  # W
    MOVE_SOUTH = auto()  # W
    MOVE_FORWARD = auto()  # W continue last direction
    MOVE_REVERSE = auto()  # W
    MOVE_LEFT = auto()  # W
    MOVE_RIGHT = auto()  # W
    MOVE_RANDOM = auto()  # W
