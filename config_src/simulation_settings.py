## grid ##

DIM = 50

## initialization const ##

BARRIERS_NUMBER = 100
FOOD_SOURCES_NUMBER = 50
FOOD_PER_SOURCE_MIN = 5
FOOD_PER_SOURCE_MAX = 10

## evolution ##

POPULATION_SIZE = 100
NUMBER_OF_GENERATIONS = 3
STEPS_PER_GENERATION = 10
GENOME_LENGTH = 16
MAX_NUMBER_OF_INNER_NEURONS = 3

## actions ##

LONG_PROBE_DISTANCE = 20
KILL_ENABLED = True
RESPONSIVENESS_CURVE_K_FACTOR = 2
NEIGHBOURHOOD_RADIUS = 3

## Food & energy related const ##

FOOD_ADDED_ENERGY = 2
FOOD_INCREASED_MAX_LEVEL = 0.1
ENERGY_PER_ONE_UNIT_OF_MOVE = 0.2
ENTRY_MAX_ENERGY_LEVEL = 10  # = 5 food, = 50 units of movement
MAX_ENERGY_LEVEL_SUPREMUM = 50  # 400 times increased, allows for 25 food and 200 units of movement
ENERGY_DECREASE_IN_TIME = ENTRY_MAX_ENERGY_LEVEL / STEPS_PER_GENERATION

## mutation ##

# mutation probability
MUTATION_PROBABILITY = 0.2

# select MUTATE_N_GENES from genome list to be mutated
# cannot be bigger than GENOME_LENGTH
MUTATE_N_GENES = 2

# in binary representation of gene negate MUTATE_N_BITS neighbouring bits
# cannot be bigger than number of bits in decoded gene, i.e. gene has 8 hexadecimal characters = 4 * 8 = 32 bits
MUTATE_N_BITS = 2

SELECT_N_SPECIMENS = max(int(0.1 * POPULATION_SIZE), 2)

## Pheromones ##
DISABLE_PHEROMONES = False
PHEROMONE_DIFFUSION_RATE = 0.01
PHEROMONE_DECAY_RATE = 0.05
FORCE_EMISSION_TEST = False
PHEROMONE_STRENGTH = 1.0

## saving simulation ##
SAVE_ANIMATION = True
SAVE_EVOLUTION_STEP = True
SAVE_GENERATION = True
SAVE_SELECTION = True
SAVE_POPULATION = True
SAVE_GRID = True
SAVE_CONFIG = True
SAVE = SAVE_EVOLUTION_STEP or SAVE_GENERATION or SAVE_SELECTION or SAVE_POPULATION or SAVE_GRID or SAVE_CONFIG

SAVE_FOLDER = "saved"
