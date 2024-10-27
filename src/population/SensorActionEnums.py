from enum import Enum


class AutoNumber(Enum):
    def __new__(cls):
        value = len(cls.__members__)  # note no + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


# copy paste z gita z YT
# I - data about individual specimen
# W - data about the world
class NeuronType(Enum):
    SENSOR = 0
    INNER = 1
    ACTION = 2


class SensorType(AutoNumber):
    LOC_X = ()  # I distance from left edge
    LOC_Y = ()  # I distance from bottom
    BOUNDARY_DIST_X = ()  # I X distance to nearest edge of world
    BOUNDARY_DIST = ()  # I distance to nearest edge of world
    BOUNDARY_DIST_Y = ()  # I Y distance to nearest edge of world
    GENETIC_SIM_FWD = ()  # I genetic similarity to forward neighbour
    LAST_MOVE_DIST_X = ()  # I +- amount of X movement in last movement
    LAST_MOVE_DIST_Y = ()  # I +- amount of Y movement in last movement
    LONGPROBE_POP_FWD = ()  # W long look for population forward
    LONGPROBE_BAR_FWD = ()  # W long look for barriers forward
    POPULATION = ()  # W population density in neighborhood
    POPULATION_FWD = ()  # W population density in the forward-reverse axis
    POPULATION_LR = ()  # W population density in the left-right axis
    OSC1 = ()  # I oscillator +-value
    AGE = ()  # I
    BARRIER_FWD = ()  # W neighborhood barrier distance forward-reverse axis
    BARRIER_LR = ()  # W neighborhood barrier distance left-right axis
    RANDOM = ()  # random sensor value = uniform distribution
    PHEROMONE = ()  # W strength of pheromone in neighborhood
    PHEROMONE_FWD = ()  # W strength of pheromone in the forward-reverse axis
    PHEROMONE_LR = ()  # W strength of pheromone in the left-right axis


class ActionType(AutoNumber):
    SET_RESPONSIVENESS = ()  # I
    SET_OSCILLATOR_PERIOD = ()  # I
    SET_LONGPROBE_DIST = ()  # I
    EMIT_PHEROMONE = ()  # W
    KILL = ()
    MOVE_X = ()  # W +- X component of movement
    MOVE_Y = ()  # W +- Y component of movement
    MOVE_EAST = ()  # W
    MOVE_WEST = ()  # W
    MOVE_NORTH = ()  # W
    MOVE_SOUTH = ()  # W
    MOVE_FORWARD = ()  # W continue last direction
    MOVE_REVERSE = ()  # W
    MOVE_LEFT = ()  # W
    MOVE_RIGHT = ()  # W
    MOVE_RANDOM = ()  # W
