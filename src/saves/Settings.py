import json


# describes settings file
class Settings:
    def __init__(self, grid_dim: int = 50):
        """ constructor """

        # crucial for parameters and corresponding fields to have identical names

        self.grid_dim = grid_dim

        return

    def to_json(self) -> str:
        """ converts Settings object to json representation """

        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(p_json: str) -> 'Settings':
        """ based on json representation creates Settings object """

        assert isinstance(p_json, str)

        return Settings(**(json.loads(p_json)))
