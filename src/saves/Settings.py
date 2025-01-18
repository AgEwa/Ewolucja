import json
from dataclasses import dataclass
from math import ceil
from typing import ClassVar

import config


@dataclass
# describes settings file
class Settings:
    population_size: int = config.POPULATION_SIZE
    number_of_generations: int = config.NUMBER_OF_GENERATIONS
    steps_per_generation: int = config.STEPS_PER_GENERATION

    mutation_probability: float = config.MUTATION_PROBABILITY
    mutate_n_genes: int = config.MUTATE_N_GENES
    mutate_n_bits: int = config.MUTATE_N_BITS

    genome_length: int = config.GENOME_LENGTH
    max_number_of_inner_neurons: int = config.MAX_NUMBER_OF_INNER_NEURONS
    disable_pheromones: bool = config.DISABLE_PHEROMONES
    enable_kill: bool = config.KILL_ENABLED

    entry_max_energy_level: int = config.ENTRY_MAX_ENERGY_LEVEL
    max_energy_level_supremum: int = config.MAX_ENERGY_LEVEL_SUPREMUM
    dim: int = config.DIM

    SAVE_ANIMATION: bool = config.SAVE_ANIMATION
    SAVE_EVOLUTION_STEP: bool = config.SAVE_EVOLUTION_STEP
    SAVE_GENERATION: bool = config.SAVE_GENERATION

    SAVE_SELECTION: bool = config.SAVE_SELECTION
    SAVE_POPULATION: bool = config.SAVE_POPULATION

    SAVE_CONFIG: bool = config.SAVE_CONFIG

    min_food_per_source: int = config.FOOD_PER_SOURCE_MIN
    max_food_per_source: int = config.FOOD_PER_SOURCE_MAX

    food_added_energy: int = config.FOOD_ADDED_ENERGY
    energy_per_move: int = config.ENERGY_PER_ONE_UNIT_OF_MOVE

    settings: ClassVar['Settings'] = None

    @property
    def ENERGY_DECREASE_IN_TIME(self):
        return self.entry_max_energy_level / self.steps_per_generation

    @property
    def SELECT_N_SPECIMENS(self):
        return max(int(0.1 * self.population_size), 2)

    @property
    def SAVE(self):
        return self.SAVE_EVOLUTION_STEP or self.SAVE_GENERATION or self.SAVE_SELECTION or self.SAVE_POPULATION or self.SAVE_CONFIG

    @property
    def FOOD_INCREASED_MAX_LEVEL(self):
        return self.food_added_energy / 10

    @property
    def BARRIERS_NUMBER(self):
        return ceil((self.dim ^ 2) * 0.05)

    @property
    def FOOD_SOURCES_NUMBER(self):
        return ceil((self.dim ^ 2) * 0.1)

    @staticmethod
    def SPACE_DIM(dim):
        return config.MAP_DIM / dim

    def to_json(self) -> str:
        """ converts Settings object to json representation """

        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(p_json: str) -> 'Settings':
        """ based on json representation creates Settings object """

        assert isinstance(p_json, str)

        return Settings(**(json.loads(p_json)))

    @staticmethod
    def read() -> None:
        """ reads current value of Settings and stores as static class field """

        try:
            with open(config.SETTINGS_PATH, 'r') as f:
                Settings.settings = Settings.from_json(f.read())
        except Exception as e:
            print(e)

        return

    @staticmethod
    def write() -> None:
        """  """

        with open(config.SETTINGS_PATH, 'w') as f:
            f.write(Settings.settings.to_json())

        return
