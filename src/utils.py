import random

import numpy as np


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

    return (np.tanh(p_x) + 1) / 2


def response_curve(p_x: float) -> float:
    pass


def bin_to_signed_int(binary):
    int_value = int(binary, 2)

    # Check the most significant bit to determine if the number is negative
    if binary[0] == '1':
        # If negative, compute the two's complement
        int_value -= (1 << 16)
    return int_value
