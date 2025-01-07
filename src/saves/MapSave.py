import json
from dataclasses import dataclass, field

import config
from src.saves.Settings import Settings


def correct_positions(positions_list: list[list]):
    corrected = []
    for pos in positions_list:
        corrected.append((pos[0], Settings.settings.dim - pos[1] - 1))
    return corrected


@dataclass
# describes map save
class MapSave:
    dim: int = config.DIM
    barrier_positions: list = field(default_factory=list)
    food_positions: list = field(default_factory=list)

    def to_json(self) -> str:
        """ converts MapSave object to json representation """

        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(p_json: str) -> 'MapSave':
        """ based on json representation creates MapSave object """

        assert isinstance(p_json, str)

        return MapSave(**(json.loads(p_json)))

    def get_food_positions(self):
        return correct_positions(self.food_positions)

    def get_barrier_positions(self):
        return correct_positions(self.barrier_positions)
