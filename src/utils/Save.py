import json
import logging
import os
import pickle
import time
from enum import Enum, auto
from multiprocessing import Process, Queue

import numpy as np

import config
from config_src import simulation_settings
from src.external import population, grid
from src.saves.Settings import Settings


class SaveType(Enum):
    STEP = auto()
    GEN = auto()
    SELECTION = auto()
    POP = auto()
    GRID = auto()
    CONFIG = auto()

    def is_enabled(self):
        return {
            SaveType.STEP: Settings.settings.SAVE_EVOLUTION_STEP,
            SaveType.GEN: Settings.settings.SAVE_GENERATION,
            SaveType.SELECTION: Settings.settings.SAVE_SELECTION,
            SaveType.POP: Settings.settings.SAVE_POPULATION,
            SaveType.GRID: Settings.settings.SAVE_GRID,
            SaveType.CONFIG: Settings.settings.SAVE_CONFIG,
        }[self]


def writer(dest_filename, data_queue, uid):
    logging.debug(f"Process writer started for: {dest_filename}")
    started = False

    # path to saves for current simulation
    sim_folder_path = os.path.join(config.SIMULATION_SAVES_FOLDER_PATH, f'{uid}')
    # create saves directory for current simulation
    if not os.path.exists(sim_folder_path):
        os.mkdir(sim_folder_path)

    filepath = os.path.join(sim_folder_path, dest_filename)

    while True:
        line = data_queue.get()
        with open(filepath, "a") as file:
            if line is None:
                logging.debug("closing writer...")
                file.write("]")
                return
            logging.debug(f"Process tries writing item: {line}")
            if not started:
                file.write("[" + line)
                started = True
            else:
                file.write("," + line)


def process_pop(gen, pop, selected, queue):
    logging.debug("Process pop started")

    if selected is not None:
        pop = np.array(pop)[selected]
    to_write = {
        "gen": gen
    }

    for specimen in pop:
        if specimen:
            to_write[specimen.index] = {
                "energy": specimen.energy,
                "max_energy": specimen.max_energy,
                "adaptation_value": specimen.energy * 0.25 + specimen.max_energy * 0.75,
                "genome": specimen.genome,
                "alive": specimen.alive
            }

    logging.debug(f"Process pop wrote: {to_write}")
    queue.put(json.dumps(to_write))

    return


def pickle_pop(pop, filename, uid):
    logging.info("Process pop started")

    # path to saves for current simulation
    sim_folder_path = os.path.join(config.SIMULATION_SAVES_FOLDER_PATH, f'{uid}')
    # create saves directory for current simulation
    if not os.path.exists(sim_folder_path):
        os.mkdir(sim_folder_path)

    filepath = os.path.join(sim_folder_path, filename)

    with open(filepath, "wb") as file:
        for specimen in pop:
            if specimen:
                pickle.dump(pop, file)

    logging.debug(f"Process pop wrote.")

    return


def pickle_config(config_dict, filename, uid):
    logging.info("Process config started")

    # path to saves for current simulation
    sim_folder_path = os.path.join(config.SIMULATION_SAVES_FOLDER_PATH, f'{uid}')
    # create saves directory for current simulation
    if not os.path.exists(sim_folder_path):
        os.mkdir(sim_folder_path)

    filepath = os.path.join(sim_folder_path, filename)

    with open(filepath, "wb") as file:
        pickle.dump(config_dict, file)

    logging.debug(f"Process config wrote.")

    return


def pickle_grid(barriers: list, food_sources: dict, filename, uid):
    logging.info("Process grid started")

    # path to saves for current simulation
    sim_folder_path = os.path.join(config.SIMULATION_SAVES_FOLDER_PATH, f'{uid}')
    # create saves directory for current simulation
    if not os.path.exists(sim_folder_path):
        os.mkdir(sim_folder_path)

    filepath = os.path.join(sim_folder_path, filename)

    with open(filepath, "wb") as file:
        pickle.dump(barriers, file)
        pickle.dump(food_sources, file)

    logging.debug(f"Process grid wrote.")

    return


class SavingHelper:
    def __init__(self, simulation_uid):
        self.queues = {member: Queue() for member in SaveType if member.is_enabled()}
        self.writing_processes = dict()
        self.writing_processes = {member: Process(target=writer, args=(
            f"saved_{member.name}.json", self.queues.get(member), simulation_uid)) for member in
                                  SaveType if member.is_enabled()}
        self.processors = []
        self.uid = simulation_uid

        return

    def start_writers(self):
        logging.debug("Started writers")

        for _, p in self.writing_processes.items():
            p.start()

        return

    def close_writers(self):
        logging.debug("Started closing saver")

        start = time.time()
        for p in self.processors:
            p.join()
        for _, q in self.queues.items():
            q.put(None)
        for _, p in self.writing_processes.items():
            p.join()

        logging.debug(f"Closed writers, waited: {time.time() - start}s.")

        return

    def save_step(self, gen, step, dead_count):
        line_to_write = {
            "gen": gen,
            "step": step,
            "dead count": dead_count
        }
        self.queues.get(SaveType.STEP).put(json.dumps(line_to_write))

        return

    def save_selection(self, gen, selected_idx):
        p = Process(target=process_pop, args=(
            gen, population.copy(), selected_idx, self.queues.get(SaveType.SELECTION)))
        p.start()
        self.processors.append(p)

        return

    def save_gen(self, gen):
        p = Process(target=process_pop, args=(gen, population.copy(), None, self.queues.get(SaveType.GEN)))
        p.start()
        self.processors.append(p)

        return

    def save_pop(self):
        p = Process(target=pickle_pop, args=(population.copy(), f"saved_{SaveType.POP.name}.pickle", self.uid))
        p.start()
        self.processors.append(p)

        return

    def save_config(self):
        config_dict = {key: value for key, value in vars(simulation_settings).items() if not key.startswith('__')}
        p = Process(target=pickle_config, args=(config_dict.copy(), f"saved_{SaveType.CONFIG.name}.pickle", self.uid))
        p.start()
        self.processors.append(p)

        return

    def save_grid(self):
        p = Process(target=pickle_grid, args=(
            grid.barriers.copy(), grid.food_data.copy(), f"saved_{SaveType.GRID.name}.pickle", self.uid))
        p.start()
        self.processors.append(p)

        return
