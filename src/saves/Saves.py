import os.path

import config
from src.saves.Settings import Settings


class Saves:
    @staticmethod
    def init() -> None:
        """ Initialises saves directory hierarchy """

        # if there is no root folder
        if not os.path.exists(config.ROOT_FOLDER_PATH):
            # create it
            os.mkdir(config.ROOT_FOLDER_PATH)

        # if there is no saves folder
        if not os.path.exists(config.SAVES_FOLDER_PATH):
            # create it
            os.mkdir(config.SAVES_FOLDER_PATH)

        # if there is no settings file
        if not os.path.exists(config.SETTINGS_PATH):
            # create new one with default values
            with open(config.SETTINGS_PATH, 'w') as f:
                f.write(Settings().to_json())
        # otherwise
        else:
            # try to parse the file
            try:
                # if it works, then settings file is OK
                with open(config.SETTINGS_PATH, 'r') as f:
                    Settings.from_json(f.read())
            # otherwise
            except Exception as e:
                # it is corrupted and recreate it with default values
                print(e)

                with open(config.SETTINGS_PATH, 'w') as f:
                    f.write(Settings().to_json())

        return

    @staticmethod
    def read_settings() -> Settings:
        with open(config.SETTINGS_PATH, 'r') as f:
            return Settings.from_json(f.read())
