import logging
import random
from math import tanh, sin, cos

import config
from src.external import grid, population
from world.LocationTypes import Conversions, Coord, Direction


def initialize_genome(neuron_link_amount: int) -> list:
    """
    Initializes a list of genes.
    Genes are generated as 8-digit hex describing links in neural network of a Specimen
    :param neuron_link_amount: amount of links in Specimen's brain (neural network)
    :return: list of genes specifying specimen's neural network
    """

    return [generate_hex() for _ in range(neuron_link_amount)]


def generate_hex() -> str:
    """
    Generates a random 8-digit hexadecimal number.
    Returns:
        str: An 8-char string representing a hexadecimal number.
    """
    return '{:08x}'.format(random.randint(0, 0xFFFFFFFF))


def probability(p_prob: float) -> bool:
    """ returns true with probability p_prob """

    assert isinstance(p_prob, float)
    assert 0 <= p_prob <= 1

    return random.random() < p_prob


def squeeze(p_x: float) -> float:
    """ squeezes output into [0; 1] interval """

    assert isinstance(p_x, float)

    return (tanh(p_x) + 1) / 2


def response_curve(p_r: float) -> float:
    k = config.RESPONSIVENESS_CURVE_K_FACTOR
    return (p_r - 2) ** (-2 * k) - 2 ** (-2 * k) * (1 - p_r)


# for fun
def rotate(p_a, p_alpha, p_c=(0, 0)):
    """ rotates p_a around p_c by p_alpha radians """

    assert isinstance(p_a, tuple) and len(p_a) == 2
    x = p_a[0]
    y = p_a[1]
    assert isinstance(x, (int, float)) and isinstance(y, (int, float))
    assert isinstance(p_alpha, (int, float))
    assert isinstance(p_c, tuple) and len(p_c) == 2
    a = p_c[0]
    b = p_c[1]
    assert isinstance(a, (int, float)) and isinstance(b, (int, float))

    return (x - a) * cos(p_alpha) - (y - b) * sin(p_alpha) + a, (x - a) * sin(p_alpha) + (y - b) * cos(p_alpha) + b


def bin_to_signed_int(binary: bin) -> int:
    int_value = int(binary, 2)

    # Check the most significant bit to determine if the number is negative
    if binary[0] == '1':
        # If negative, compute the two's complement
        int_value -= (1 << 16)
    return int_value


def drain_kill_set(p_set: set):
    for idx in p_set:
        specimen = population[idx]
        specimen.alive = False
        specimen.energy = 0
        logging.info("killed")
    p_set.clear()


def drain_move_queue(p_queue: list[tuple]):
    """
    Processes and executes movements for a queue of specimens.
    Args:
        p_queue: List of tuples, where each tuple consists of:
            - Specimen: The specimen object to move.
            - list[Coord]: A path of coordinates representing movement steps.

    Method iterates through each specimen and its path in the queue.
    If the specimen is alive:
        - Attempts to move the specimen along the path, step by step.
        - Checks if each step leads to an empty grid cell; if so, moves there.
        - If the new location contains food, the specimen eats it, and the food is removed from the grid.
        - Updates the specimen's last movement, location, and movement direction.
    The queue is being cleared after processing movements for all specimens.

    Side Effects:
        - Modifies the `grid` to reflect the specimen's movement and food consumption.
        - Updates the specimen's state (location, energy, etc.).
        - Clears the input queue.
    """
    for record in p_queue:
        specimen = record[0]
        path = record[1]
        assert isinstance(path, list)
        new_location = specimen.location

        if specimen.alive:

            for step in path:
                assert isinstance(step, Coord)
                if grid.in_bounds(new_location + step) and grid.is_empty_at(new_location + step):
                    if not specimen.can_move():
                        break
                    new_location += step
                    if grid.is_food_at(new_location):
                        specimen.eat()
                        grid.food_eaten_at(new_location)  # decreases amount of food at food source
                    specimen.use_energy(config.ENERGY_PER_ONE_UNIT_OF_MOVE)

            grid.data[specimen.location.x, specimen.location.y] = 0
            grid.data[new_location.x, new_location.y] = specimen.index
            specimen.last_movement = new_location - specimen.location
            if new_location == specimen.location:
                specimen.last_movement_direction = Direction.random()
            else:
                specimen.last_movement_direction = Conversions.coord_as_direction(new_location - specimen.location)
            specimen.location = new_location

    p_queue.clear()

    return
