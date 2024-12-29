import json
import logging
import os
import pickle
import time
from enum import Enum, auto
from multiprocessing import Process, Queue

import numpy as np

import config
from config_src import to_split
from src.external import population, grid


class SaveType(Enum):
    STEP = auto()
    GEN = auto()
    SELECTION = auto()
    POP = auto()
    GRID = auto()
    CONFIG = auto()

    def is_enabled(self):
        return {
            SaveType.STEP: config.SAVE_EVOLUTION_STEP,
            SaveType.GEN: config.SAVE_GENERATION,
            SaveType.SELECTION: config.SAVE_SELECTION,
            SaveType.POP: False,  # config.SAVE_POPULATION,
            SaveType.GRID: False,  # config.SAVE_GRID,
            SaveType.CONFIG: False,  # config.SAVE_CONFIG,
        }[self]


def writer(dest_filename, data_queue):
    logging.debug(f"Process writer started for: {dest_filename}")
    started = False
    filepath = os.path.join(config.SAVE_FOLDER, dest_filename)
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
    to_write = {"gen": gen}

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


def pickle_pop(pop, filename):
    logging.info("Process pop started")
    filepath = os.path.join(config.SAVE_FOLDER, filename)
    with open(filepath, "wb") as file:
        for specimen in pop:
            if specimen:
                pickle.dump(pop, file)
    logging.debug(f"Process pop wrote.")
    return


def pickle_config(filename):
    logging.info("Process config started")
    filepath = os.path.join(config.SAVE_FOLDER, filename)
    config_dict = {key: value for key, value in vars(to_split).items() if not key.startswith('__')}
    with open(filepath, "wb") as file:
        pickle.dump(config_dict, file)
    logging.debug(f"Process config wrote.")
    return


def pickle_grid(barriers: list, food_sources: dict, filename):
    logging.info("Process grid started")
    filepath = os.path.join(config.SAVE_FOLDER, filename)
    with open(filepath, "wb") as file:
        pickle.dump(barriers, file)
        pickle.dump(food_sources, file)
    logging.debug(f"Process grid wrote.")
    return


class SavingHelper:
    def __init__(self, simulation_uid):
        self.queues = {member: Queue() for member in SaveType if member.is_enabled()}
        self.writing_processes = dict()
        self.writing_processes = {
            member: Process(target=writer,
                            args=(f"saved_{member.name}_{simulation_uid}.json", self.queues.get(member)))
            for member in SaveType if member.is_enabled()
        }
        self.processors = []
        self.uid = simulation_uid
        if not os.path.exists(config.SAVE_FOLDER):
            os.mkdir(config.SAVE_FOLDER)

    def start_writers(self):
        logging.debug("Started writers")
        for _, p in self.writing_processes.items():
            p.start()

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

    def save_step(self, gen, step, dead_count):
        line_to_write = {"gen": gen, "step": step, "dead count": dead_count}
        self.queues.get(SaveType.STEP).put(json.dumps(line_to_write))

    def save_selection(self, gen, selected_idx):
        p = Process(target=process_pop,
                    args=(gen, population.copy(), selected_idx, self.queues.get(SaveType.SELECTION)))
        p.start()
        self.processors.append(p)

    def save_gen(self, gen):
        p = Process(target=process_pop,
                    args=(gen, population.copy(), None, self.queues.get(SaveType.GEN)))
        p.start()
        self.processors.append(p)

    def save_pop(self):
        p = Process(target=pickle_pop, args=(population.copy(), f"saved_{SaveType.POP.name}_{self.uid}.pickle"))
        p.start()
        self.processors.append(p)

    def save_config(self):
        p = Process(target=pickle_config, args=(f"saved_{SaveType.CONFIG.name}_{self.uid}.pickle",))
        p.start()
        self.processors.append(p)

    def save_grid(self):
        p = Process(target=pickle_grid,
                    args=(grid.barriers.copy(), grid.food_data.copy(),
                          f"saved_{SaveType.GRID.name}_{self.uid}.pickle"))
        p.start()
        self.processors.append(p)
