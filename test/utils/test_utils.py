from unittest import TestCase

from utils.utils import *


class TestUtils(TestCase):
    def test_initialize_genome(self):
        genome = initialize_genome(4)
        self.assertEqual(len(genome), 5)

    def test_generate_hex(self):
        gene = generate_hex()
        self.assertEqual(len(gene), 8)

    def test_bin_to_signed_int(self):
        positive_int = bin_to_signed_int('0111111111111111')
        negative_int = bin_to_signed_int('1111111111111111')
        self.assertEqual(positive_int, 32767)
        self.assertEqual(negative_int, -1)

