import os.path

PATH_TO_ROOT = os.path.join(os.path.expanduser('~'), 'Documents')

ROOT_FOLDER_NAME = 'evolution'

SAVES_FOLDER_NAME = 'saves'
SETTINGS_FILE_NAME = 'settings'

ROOT_FOLDER_PATH = os.path.join(PATH_TO_ROOT, ROOT_FOLDER_NAME)

SAVES_FOLDER_PATH = os.path.join(ROOT_FOLDER_PATH, SAVES_FOLDER_NAME)
SETTINGS_PATH = os.path.join(ROOT_FOLDER_PATH, SETTINGS_FILE_NAME)
