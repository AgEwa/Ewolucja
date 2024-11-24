## grid ##

WIDTH = 100
HEIGHT = 100

## evolution ##

POPULATION_SIZE = 100
NUMBER_OF_GENERATIONS = 3
STEPS_PER_GENERATION = 100
GENOME_LENGTH = 4
MAX_NUMBER_OF_INNER_NEURONS = 5

## actions ##

LONG_PROBE_DISTANCE = None
KILL_ENABLED = False
RESPONSIVENESS_CURVE_K_FACTOR = 2
NEIGHBOURHOOD_RADIUS = 3

## Food & energy related const ##

FOOD_ADDED_ENERGY = 2
FOOD_INCREASED_MAX_LEVEL = 0.1
ENERGY_PER_ONE_UNIT_OF_MOVE = 0.2
ENTRY_MAX_ENERGY_LEVEL = 10  # = 5 food, = 50 units of movement
MAX_ENERGY_LEVEL_SUPREMUM = 50  # 400 times increased, allows for 25 food and 200 units of movement

## mutation ##

# mutation probability
MUTATION_PROBABILITY = 0.2

# select MUTATE_N_GENES from genome list to be mutated
# cannot be bigger than GENOME_LENGTH
MUTATE_N_GENES = 2

# in binary representation of gene negate MUTATE_N_BITS neighbouring bits
# cannot be bigger than number of bits in decoded gene, i.e. gene has 8 hexadecimal characters = 4 * 8 = 32 bits
MUTATE_N_BITS = 2

## selection ##

#
SELECT_N_SPECIMENS = int(0.1 * POPULATION_SIZE)

## animation ##
SAVE_ANIMATION = True