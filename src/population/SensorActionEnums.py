from enum import Enum

# copy paste z gita z YT
# I - data about individual specimen
# W - data about the world
class NeuronType(Enum):
    SENSOR = 0
    INTERNAL = 1
    OUTPUT = 2
class SensorType(Enum):
    LOC_X = 0 # I distance from left edge
    LOC_Y = 1 # I distance from bottom
    BOUNDARY_DIST_X = 2 # I X distance to nearest edge of world
    BOUNDARY_DIST = 3 # I distance to nearest edge of world
    BOUNDARY_DIST_Y = 4 # I Y distance to nearest edge of world
    GENETIC_SIM_FWD = 5 # I genetic similarity to forward neighbour
    LAST_MOVE_DIR_X = 6 # I +- amount of X movement in last movement
    LAST_MOVE_DIR_Y = 7 # I +- amount of Y movement in last movement
    LONGPROBE_POP_FWD = 8 # W long look for population forward
    LONGPROBE_BAR_FWD = 9 # W long look for barriers forward
    POPULATION = 10 # W population density in neighborhood
    POPULATION_FWD = 11 # W population density in the forward-reverse axis
    POPULATION_LR = 12 # W population density in the left-right axis
    OSC1 = 13 # I oscillator +-value
    AGE = 14 # I
    BARRIER_FWD = 15 # W neighborhood barrier distance forward-reverse axis
    BARRIER_LR = 16 # W neighborhood barrier distance left-right axis
    RANDOM = 17 # random sensor value = uniform distribution
    PHEROMONE = 18 # W strength of pheromone in neighborhood
    PHEROMONE_FWD = 19 # W strength of pheromone in the forward-reverse axis
    PHEROMONE_LR = 20 # W strength of pheromone in the left-right axis
    NUM_SENSORS = 21
class ActionType(Enum):
    MOVE_X = 0 # W +- X component of movement
    MOVE_Y = 1 # W +- Y component of movement
    MOVE_FORWARD = 2 # W continue last direction
    MOVE_RL = 3 # W +- component of movement
    MOVE_RANDOM = 4 # W
    SET_OSCILLATOR_PERIOD = 5 # I
    SET_LONGPROBE_DIST = 6 # I
    SET_RESPONSIVENESS = 7 # I
    EMIT_PHEROMONE = 8 # W
    MOVE_EAST = 9 # W
    MOVE_WEST = 10 # W
    MOVE_NORTH = 11 # W
    MOVE_SOUTH = 12 # W
    MOVE_LEFT = 13 # W
    MOVE_RIGHT = 14 # W
    MOVE_REVERSE = 15  # W
    NUM_ACTIONS = 16


def main():
    print(SensorType(0))

main()