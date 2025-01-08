import json
import os
import pickle
from multiprocessing import Queue, Process
from unittest import TestCase
from unittest.mock import Mock, patch

import config
from config_src import simulation_settings
from src.population.Specimen import Specimen
from src.utils.Save import pickle_pop, write_json_config, process_pop, writer
from src.utils.utils import initialize_genome
from src.world.LocationTypes import Coord


def eq_specimen(first, second, msg=None):
    if isinstance(first, Specimen) and isinstance(second, Specimen):
        first_attr = first.__dict__
        second_attr = second.__dict__
        for atrr in first_attr:
            if atrr not in second_attr:
                return False
            if atrr == "brain":
                continue
            if first_attr.get(atrr) != second_attr.get(atrr):
                return False
        return True
    return False


class TestPickleSaving(TestCase):

    def setUp(self):
        if not os.path.exists(config.SIMULATION_SAVES_FOLDER_PATH):
            os.mkdir(config.SIMULATION_SAVES_FOLDER_PATH)
        self.test_filepath = ''

    def tearDown(self):
        os.remove(self.test_filepath)

    def test_pickle_pop(self):
        # given
        self.addTypeEqualityFunc(Specimen, eq_specimen)
        mock_settings = Mock()
        mock_settings.genome_length = 4
        mock_settings.disable_pheromones = False
        mock_settings.max_number_of_inner_neurons = 2
        mock_settings.entry_max_energy_level = 10
        mock_settings.max_energy_level_supremum = 12
        mock_settings.population_size = 3
        settings_patch = patch('src.population.Specimen.Settings.settings', mock_settings)
        settings_patch.start()
        genome_1 = initialize_genome(mock_settings.genome_length)
        genome_2 = initialize_genome(mock_settings.genome_length)
        specimen_1 = Specimen(1, Coord(1, 1), genome_1)
        specimen_2 = Specimen(2, Coord(2, 2), genome_2)
        pop = [None, specimen_1, specimen_2]
        test_file = "test_pop.pickle"
        uid = "test"
        # when
        pickle_pop(pop, test_file, uid)
        # then
        self.test_filepath = os.path.join(config.SIMULATION_SAVES_FOLDER_PATH, f'{uid}', test_file)
        with open(self.test_filepath, "rb") as file:
            data = pickle.load(file)
        self.assertIsNotNone(data)
        self.assertEqual(len(pop), len(data))
        for i in range(len(data)):
            self.assertEqual(pop[i], data[i])

    def test_write_json_config(self):
        # given
        test_file = "test_config.json"
        uid = "test"
        original_config_dict = {key: value for key, value in vars(simulation_settings).items() if not key.startswith('__')}
        mock_settings_dict = {"genome_length": 10, "population_size": 5}
        # when
        write_json_config(original_config_dict.copy(), mock_settings_dict.copy(), test_file, uid)
        # then
        self.test_filepath = os.path.join(config.SIMULATION_SAVES_FOLDER_PATH, f'{uid}', test_file)
        with open(self.test_filepath, "rb") as file:
            data = json.load(file)
        self.assertDictEqual(original_config_dict, data.get("config"))
        self.assertDictEqual(mock_settings_dict, data.get("parameters"))


class TestWriterSaving(TestCase):
    def setUp(self):
        if not os.path.exists(config.SIMULATION_SAVES_FOLDER_PATH):
            os.mkdir(config.SIMULATION_SAVES_FOLDER_PATH)
        self.test_file = "test_pop.json"
        self.uid = "test"
        self.test_filepath = os.path.join(config.SIMULATION_SAVES_FOLDER_PATH, f'{self.uid}', self.test_file)

        self.mock_settings = Mock()
        self.mock_settings.genome_length = 4
        self.mock_settings.disable_pheromones = False
        self.mock_settings.max_number_of_inner_neurons = 2
        self.mock_settings.entry_max_energy_level = 10
        self.mock_settings.max_energy_level_supremum = 12
        settings_patch = patch('src.population.Specimen.Settings.settings', self.mock_settings)
        settings_patch.start()

    def tearDown(self):
        os.remove(self.test_filepath)

    def test_saving_pop_for_selected(self):
        # given
        pop = [None]
        pop.extend([Specimen(i, Coord(i, i), initialize_genome(self.mock_settings.genome_length)) for i in range(1, 11)])
        gen = 0
        selected = [2, 4, 6, 8, 10]
        queue = Queue()
        writer_process = Process(target=writer, args=(self.test_file, queue, self.uid))
        # when
        writer_process.start()
        process_pop(gen, pop.copy(), selected, queue)
        queue.put(None)
        writer_process.join()
        # then

        with open(self.test_filepath, "r") as file:
            data = json.load(file)
        # one pop processed
        self.assertEqual(1, len(data))
        data = data[0]
        self.assertIn("gen", data)
        self.assertEqual(gen, data.get("gen"))
        self.assertEqual(len(selected), len(data) - 1)
        for idx in selected:
            self.assertIn(str(idx), data)
            self.assertEqual(pop[idx].energy, data[str(idx)].get("energy"))
            self.assertEqual(pop[idx].max_energy, data[str(idx)].get("max_energy"))
            self.assertEqual(pop[idx].alive, data[str(idx)].get("alive"))
            self.assertListEqual(pop[idx].genome, data[str(idx)].get("genome"))

    def test_saving_pop_for_all(self):
        # given
        pop = [None]
        pop.extend([Specimen(i, Coord(i, i), initialize_genome(self.mock_settings.genome_length)) for i in range(1, 11)])
        gen = 0
        queue = Queue()
        writer_process = Process(target=writer, args=(self.test_file, queue, self.uid))
        # when
        writer_process.start()
        process_pop(gen, pop.copy(), None, queue)
        queue.put(None)
        writer_process.join()
        # then
        with open(self.test_filepath, "r") as file:
            data = json.load(file)
        # one pop processed
        self.assertEqual(1, len(data))
        data = data[0]
        self.assertIn("gen", data)
        self.assertEqual(gen, data.get("gen"))
        self.assertEqual(len(pop), len(data))
        for idx in range(1, len(pop)):
            self.assertIn(str(idx), data)
            self.assertEqual(pop[idx].energy, data[str(idx)].get("energy"))
            self.assertEqual(pop[idx].max_energy, data[str(idx)].get("max_energy"))
            self.assertEqual(pop[idx].alive, data[str(idx)].get("alive"))
            self.assertListEqual(pop[idx].genome, data[str(idx)].get("genome"))
