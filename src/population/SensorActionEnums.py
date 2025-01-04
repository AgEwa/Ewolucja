from enum import Enum


class AutoNumber(Enum):
    def __new__(cls):
        value = len(cls.__members__)  # note no + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


# I - data about individual specimen
# W - data about the world


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
    LONGPROBE_FOOD_FWD = ()  # W long look for food forward
    POPULATION = ()  # W population density in neighborhood
    POPULATION_FWD = ()  # W population density in the forward-reverse axis
    POPULATION_LR = ()  # W population density in the left-right axis
    FOOD = ()  # W food density in neighborhood
    FOOD_FWD = ()  # W food density in the forward-reverse axis
    FOOD_LR = ()  # W food density in the left-right axis
    FOOD_DIST_FWD = ()  # W neighborhood food distance in the forward-reverse axis
    FOOD_DIST_LR = ()  # W neighborhood food distance in the left-right axis
    OSC = ()  # I oscillator +-value
    AGE = ()  # I
    BARRIER_FWD = ()  # W neighborhood barrier distance forward-reverse axis
    BARRIER_LR = ()  # W neighborhood barrier distance left-right axis
    RANDOM = ()  # random sensor value = uniform distribution
    ENERGY = ()  # I
    PHEROMONE_FWD = ()  # W strength of pheromone in the forward-reverse axis
    PHEROMONE_L = ()  # W strength of pheromone to the left
    PHEROMONE_R = ()  # W strength of pheromone to the right


class ActionType(AutoNumber):
    SET_RESPONSIVENESS = ()  # I
    SET_OSCILLATOR_PERIOD = ()  # I
    SET_LONGPROBE_DIST = ()  # I
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
    EMIT_PHEROMONE = ()  # W


class NeuronType(Enum):
    SENSOR = SensorType
    INNER = 1
    ACTION = ActionType
