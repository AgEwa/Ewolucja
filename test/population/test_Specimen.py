from unittest import TestCase

import config
from population.Specimen import get_max_energy_level_from_genome


class TestSpecimen(TestCase):
    def test_get_max_energy_level_from_genome(self):
        level = get_max_energy_level_from_genome(f"{config.ENTRY_MAX_ENERGY_LEVEL:02X}")
        self.assertEqual(level, config.ENTRY_MAX_ENERGY_LEVEL)
