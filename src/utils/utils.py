import random


def random_genome(length):
    return [generate_hex() for _ in range(length)]


def generate_hex():
    """
        Generates a random 8-digit hexadecimal number.

        Returns:
            str: An 8-char string representing a hexadecimal number.
        """
    return '{:08x}'.format(random.randint(0, 0xFFFFFFFF))


def bin_to_signed_int(binary):
    int_value = int(binary, 2)

    # Check the most significant bit to determine if the number is negative
    if binary[0] == '1':
        # If negative, compute the two's complement
        int_value -= (1 << 16)
    return int_value
