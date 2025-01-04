import json
import os
import pickle
from multiprocessing import Queue, Process
from unittest import TestCase

import config
from config_src import simulation_settings
from src.population.Specimen import Specimen
from src.utils.Save import pickle_pop, pickle_config, pickle_grid, process_pop, writer
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
        if not os.path.exists(config.SAVE_FOLDER):
            os.mkdir(config.SAVE_FOLDER)
        self.test_filepath = ''

    def tearDown(self):
        os.remove(self.test_filepath)

    def test_pickle_pop(self):
        # given
        self.addTypeEqualityFunc(Specimen, eq_specimen)
        genome_1 = initialize_genome(config.GENOME_LENGTH)
        genome_2 = initialize_genome(config.GENOME_LENGTH)
        specimen_1 = Specimen(1, Coord(1, 1), genome_1)
        specimen_2 = Specimen(2, Coord(2, 2), genome_2)
        pop = [None, specimen_1, specimen_2]
        test_file = "test_pop.pickle"
        # when
        pickle_pop(pop, test_file)
        # then
        self.test_filepath = os.path.join(config.SAVE_FOLDER, test_file)
        with open(self.test_filepath, "rb") as file:
            data = pickle.load(file)
        self.assertIsNotNone(data)
        self.assertEqual(len(pop), len(data))
        for i in range(len(data)):
            self.assertEqual(pop[i], data[i])

    def test_pickle_config(self):
        # given
        test_file = "test_config.pickle"
        original_config_dict = {key: value for key, value in vars(simulation_settings).items() if not key.startswith('__')}
        # when
        pickle_config(original_config_dict.copy(),test_file)
        # then
        self.test_filepath = os.path.join(config.SAVE_FOLDER, test_file)
        with open(self.test_filepath, "rb") as file:
            data = pickle.load(file)
        self.assertDictEqual(original_config_dict, data)

    def test_pickle_grid(self):
        # given
        test_file = "test_grid.pickle"
        barriers = [(0, 0), (1, 1), (2, 2)]
        food_data = {(0, 0): 2, (1, 1): 3, (2, 2): 0}
        # when
        pickle_grid(barriers, food_data, test_file)
        # then
        self.test_filepath = os.path.join(config.SAVE_FOLDER, test_file)
        with open(self.test_filepath, "rb") as file:
            data_1 = pickle.load(file)
            data_2 = pickle.load(file)
        self.assertListEqual(barriers, data_1)
        self.assertDictEqual(food_data, data_2)


class TestWriterSaving(TestCase):
    def setUp(self):
        if not os.path.exists(config.SAVE_FOLDER):
            os.mkdir(config.SAVE_FOLDER)
        self.test_file = "test_pop.json"
        self.test_filepath = os.path.join(config.SAVE_FOLDER, self.test_file)

    def tearDown(self):
        os.remove(self.test_filepath)

    def test_saving_pop_for_selected(self):
        # given
        pop = [None]
        pop.extend([Specimen(i, Coord(i, i), initialize_genome(config.GENOME_LENGTH)) for i in range(1, 11)])
        gen = 0
        selected = [2, 4, 6, 8, 10]
        queue = Queue()
        writer_process = Process(target=writer, args=(self.test_file, queue))
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
        pop.extend([Specimen(i, Coord(i, i), initialize_genome(config.GENOME_LENGTH)) for i in range(1, 11)])
        gen = 0
        queue = Queue()
        writer_process = Process(target=writer, args=(self.test_file, queue))
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
