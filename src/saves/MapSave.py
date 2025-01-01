import json
from dataclasses import dataclass, field


@dataclass
# describes map save
class MapSave:
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
