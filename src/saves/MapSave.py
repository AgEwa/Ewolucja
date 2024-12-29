import json


# describes map save
class MapSave:
    def __init__(self, barrier_positions, food_positions):
        """ constructor """

        # crucial for parameters and corresponding fields to have identical names

        # assign barrier positions
        self.barrier_positions = barrier_positions
        # assign food positions
        self.food_positions = food_positions

        return

    def to_json(self) -> str:
        """ converts MapSave object to json representation """

        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(p_json: str) -> 'MapSave':
        """ based on json representation creates MapSave object """

        assert isinstance(p_json, str)

        return MapSave(**(json.loads(p_json)))
