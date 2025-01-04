from unittest import TestCase
from unittest.mock import patch, MagicMock

from src.evolution.Operators import *
from src.utils.utils import initialize_genome
from src.world.LocationTypes import Coord


class TestOperators(TestCase):
    @patch('src.evolution.Operators.NeuralNetwork', autospec=True)
    def setUp(self, mock_neural_network):
        """Set up common test data for the test cases."""
        config.GENOME_LENGTH = 4
        config.MUTATE_N_GENES = 2
        config.MUTATE_N_BITS = 2
        config.SELECT_N_SPECIMENS = 2
        config.POPULATION_SIZE = 3

        # Create a mock specimen
        self.location = Coord(0, 0)
        self.mock_genome = initialize_genome(config.GENOME_LENGTH)
        self.other_genome = initialize_genome(config.GENOME_LENGTH)
        self.mock_brain = MagicMock()
        mock_neural_network.return_value = self.mock_brain
        self.mock_specimen = Specimen(1, self.location, self.mock_genome.copy())
        self.mock_specimen_2 = Specimen(2, self.location, self.other_genome.copy())
        self.mock_specimen_3 = Specimen(3, self.location, self.other_genome.copy())
        self.mock_specimen.max_energy += 1

        # Create a mock population
        self.mock_population = [None, self.mock_specimen, self.mock_specimen_2, self.mock_specimen_3]

    @patch("src.evolution.Operators.random.sample")
    @patch("src.evolution.Operators.random.randint")
    def test_mutate(self, mock_randint, mock_sample):
        # given
        mock_sample.return_value = [0, 1]  # select the first 2 genes
        mock_randint.side_effect = [2, 0]  # bit negation indices

        # when
        mutate(self.mock_specimen)

        # then
        self.assertEqual(len(self.mock_specimen.genome), config.GENOME_LENGTH)
        # unselected genes remain unchanged
        for gene in self.mock_genome[2:]:
            self.assertIn(gene, self.mock_specimen.genome)
        # right genes were mutated
        for gene in self.mock_genome[:2]:
            self.assertNotIn(gene, self.mock_specimen.genome)
        self.assertIsInstance(self.mock_specimen.brain, NeuralNetwork)

    def test_crossover_get_genomes(self):
        # given
        parent_a = self.mock_specimen
        parent_b = self.mock_specimen_2

        # when
        child_a, child_b = crossover_get_genomes(parent_a, parent_b)

        # then
        self.assertEqual(len(child_a), config.GENOME_LENGTH + 1)
        self.assertEqual(len(child_b), config.GENOME_LENGTH + 1)
        # check children's max energy
        self.assertTrue(child_a[0] == parent_a.max_energy or child_a[0] == parent_b.max_energy)
        self.assertTrue(child_b[0] == parent_a.max_energy or child_b[0] == parent_b.max_energy)
        # check if children are combinations of parents
        self.assertTrue(all(gene in parent_a.genome + parent_b.genome for gene in child_a[1:]))
        self.assertTrue(all(gene in parent_a.genome + parent_b.genome for gene in child_b[1:]))

    def test_reproduce(self):
        # given
        probabilities = [0.3, 0.7]
        selected_idx = [1, 2]

        # when
        with patch("src.evolution.Operators.population", self.mock_population):
            genomes = reproduce(probabilities, selected_idx)

        # then
        self.assertGreaterEqual(len(genomes), config.POPULATION_SIZE)
        self.assertLessEqual(len(genomes), config.POPULATION_SIZE + 1)
        for genome in genomes:
            self.assertEqual(len(genome), config.GENOME_LENGTH + 1)

    def test_evaluate_and_select(self):
        # when
        with patch("src.evolution.Operators.population", self.mock_population):
            probabilities, selected_idx = evaluate_and_select()

        # then
        self.assertAlmostEqual(np.sum(probabilities), 1.0)
        self.assertGreaterEqual(len(selected_idx), config.SELECT_N_SPECIMENS)

    def test_select_best(self):
        # given
        adaptation_values = [1, 5, 3, 8, 2, 6, 7, 4, 9, 10]
        energy = [1, 0, 3, 0, 2, 6, 0, 4, 9, 10]

        # when
        selected_idx = select_best(adaptation_values, energy)

        # then
        self.assertTrue(all(energy[idx] > 0 for idx in selected_idx))
        self.assertGreaterEqual(len(selected_idx), config.SELECT_N_SPECIMENS)

    def test_select_best_for_missing_nonzeros(self):
        # given
        adaptation_values = [1, 5, 3, 8, 2, 6, 7, 4, 9, 10]
        energy = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        # when
        selected_idx = select_best(adaptation_values, energy)

        # then
        self.assertListEqual([0, 9], selected_idx.tolist())

    def test_select_best_for_clear_lead(self):
        # given
        config.SELECT_N_SPECIMENS = 5
        adaptation_values = [1, 1, 1, 5, 5, 5, 5, 15, 15, 15]
        energy = [1, 0, 3, 0, 2, 6, 0, 4, 9, 10]

        # when
        selected_idx = select_best(adaptation_values, energy)

        # then
        self.assertListEqual([4, 5, 7, 8, 9], selected_idx.tolist())
