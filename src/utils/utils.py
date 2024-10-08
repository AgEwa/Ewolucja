import random
from math import tanh, sin, cos

import config
from src.external import grid
from src.typess import Conversions


def random_genome(length):
    return [generate_hex() for _ in range(length)]


def generate_hex():
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


def bin_to_signed_int(binary):
    int_value = int(binary, 2)

    # Check the most significant bit to determine if the number is negative
    if binary[0] == '1':
        # If negative, compute the two's complement
        int_value -= (1 << 16)
    return int_value


def drain_kill_queue(p_queue: list):
    pass


def drain_move_queue(p_queue: list):
    for record in p_queue:
        specimen = record[0]
        new_location = record[1]

        if specimen.alive and grid.is_empty_at(new_location):
            grid.data[specimen.location.x, specimen.location.y] = 0
            grid.data[new_location.x, new_location.y] = specimen.index
            specimen.last_movement = new_location - specimen.location
            specimen.location = new_location
            specimen.last_movement_direction = Conversions.coord_as_direction(new_location - specimen.location)

    p_queue.clear()

    return
