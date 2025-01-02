from enum import Enum, auto
from multiprocessing import Process

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QFrame, QFileDialog

import config
from src.evolution import Simulation
from src.gui.NewPlaneCreator import NewPlaneCreator
from src.saves.MapSave import MapSave


# this enum class describes available actions menus
class MenuBarOptions(Enum):
    EDIT_SETTINGS = auto()
    INFO = auto()
    CREATE_NEW_PLANE = auto()
    EDIT_PLANE = auto()
    OPEN_PLANE = auto()
    EXIT = auto()


# this enum class describes available actions in window
class Buttons(Enum):
    SAVE_SETTINGS = auto()
    REVERT_SETTINGS = auto()
    START_SIMULATION = auto()


# main window of application
class MainWindow(QMainWindow):
    def __init__(self):
        """ constructor """

        # use derived constructor
        super().__init__()

        # every opened window with new plane creator is stored here
        # if not stored, it is immediately closed automatically and if stored in a single variable
        # it overwrites if you try to open the next one, so list it is
        self._opened_new_plane_creators = []
        # dict of actions, for easier access
        self._actions = {}
        # root widget in window, it is parent of everything else visible
        self._container = QFrame(self)

        # initialise window
        self.initialise()
        # fill in actions dictionary
        self.set_up_actions()
        # create menu bar
        self.set_up_menu_bar()

        # place container at the center
        self.setCentralWidget(self._container)

        # create process for main program with simulation
        self.simulation_process = Process(target=Simulation.main)

        return

    def initialise(self) -> None:
        """ initialises main window (size, color, title) """

        # set title
        self.setWindowTitle('Evolution')
        # set size
        # this is why container was used, cause if size was set on window itself, menu bar would take that space a bit
        self._container.setFixedSize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        # set background color (for ui developing purposes)
        self._container.setStyleSheet('background-color: teal;')

        return

    def set_up_actions(self) -> None:
        """ fills in actions dictionary """

        # create action that corresponds to editing settings
        self._actions[MenuBarOptions.EDIT_SETTINGS] = QAction('Edit settings', self)
        # connect method that should be triggered
        self._actions[MenuBarOptions.EDIT_SETTINGS].triggered.connect(self.edit_settings_action_triggered)

        # create action that corresponds to accessing information and instructions on how to use application
        self._actions[MenuBarOptions.INFO] = QAction('Info', self)
        # connect method that should be triggered
        self._actions[MenuBarOptions.INFO].triggered.connect(self.info_action_triggered)

        # create action that corresponds to creating new plane
        self._actions[MenuBarOptions.CREATE_NEW_PLANE] = QAction('Create new plane', self)
        # connect method that should be triggered
        self._actions[MenuBarOptions.CREATE_NEW_PLANE].triggered.connect(self.create_new_plane_action_triggered)

        # create action that corresponds to editing plane
        self._actions[MenuBarOptions.EDIT_PLANE] = QAction('Edit plane', self)
        # connect method that should be triggered
        self._actions[MenuBarOptions.EDIT_PLANE].triggered.connect(self.edit_plane_action_triggered)

        # create action that corresponds to opening plane
        self._actions[MenuBarOptions.OPEN_PLANE] = QAction('Open plane', self)
        # connect method that should be triggered
        self._actions[MenuBarOptions.OPEN_PLANE].triggered.connect(self.open_plane_action_triggered)

        # create action that corresponds to exiting
        self._actions[MenuBarOptions.EXIT] = QAction('Exit', self)
        # connect method that should be triggered
        self._actions[MenuBarOptions.EXIT].triggered.connect(self.exit_action_triggered)

        # create action that corresponds to saving settings
        self._actions[Buttons.SAVE_SETTINGS] = QAction('Save settings', self)
        # connect method that should be triggered
        self._actions[Buttons.SAVE_SETTINGS].triggered.connect(self.save_settings_action_triggered)

        # create action that corresponds to reverting changes in settings
        self._actions[Buttons.REVERT_SETTINGS] = QAction('Revert settings', self)
        # connect method that should be triggered
        self._actions[Buttons.REVERT_SETTINGS].triggered.connect(self.revert_settings_action_triggered)

        # create action that corresponds to starting simulation
        self._actions[Buttons.START_SIMULATION] = QAction('Start simulation', self)
        # connect method that should be triggered
        self._actions[Buttons.START_SIMULATION].triggered.connect(self.start_simulation_action_triggered)

        return

    def set_up_menu_bar(self) -> None:
        """ sets up menu bar """

        # get menu bar
        menu = self.menuBar()

        # depending on mode use different layouts
        if config.MODE == config.SETTINGS_MODES['new']:
            # create menu 'Options'
            options = menu.addMenu('Options')
            # add edit settings action
            options.addAction(self._actions[MenuBarOptions.EDIT_SETTINGS])
            # add separator
            options.addSeparator()
            # add exit action
            options.addAction(self._actions[MenuBarOptions.EXIT])

            # create menu 'Plane'
            plane_menu = menu.addMenu('Plane')
            # add create new plane action
            plane_menu.addAction(self._actions[MenuBarOptions.CREATE_NEW_PLANE])
            # add edit new plane action
            plane_menu.addAction(self._actions[MenuBarOptions.EDIT_PLANE])
            # add open plane action
            plane_menu.addAction(self._actions[MenuBarOptions.OPEN_PLANE])

            # create menu action info
            menu.addAction(self._actions[MenuBarOptions.INFO])
        elif config.MODE == config.SETTINGS_MODES['main']:
            # create menu action info
            menu.addAction(self._actions[MenuBarOptions.INFO])

            # create menu 'Plane'
            plane_menu = menu.addMenu('Plane')
            # add create new plane action
            plane_menu.addAction(self._actions[MenuBarOptions.CREATE_NEW_PLANE])
            # add edit plane action
            plane_menu.addAction(self._actions[MenuBarOptions.EDIT_PLANE])
            # add open plane actiona
            plane_menu.addAction(self._actions[MenuBarOptions.OPEN_PLANE])

            # create menu action exit
            menu.addAction(self._actions[MenuBarOptions.EXIT])

            pass
        else:
            raise Exception('Invalid mode')

        return

    def edit_settings_action_triggered(self):
        """ happens when edit settings action is triggered """

        # settings_new_window mode only

        return

    def info_action_triggered(self):
        """ happens when info action is triggered """

        return

    def create_new_plane_action_triggered(self) -> None:
        """ happens when create new plane action is triggered """

        # create new NewPlaneCreator object and store it, so it isn't closed in an instant
        self._opened_new_plane_creators.append(NewPlaneCreator())
        # show the lastly appended window
        self._opened_new_plane_creators[-1].show()

        return

    @staticmethod
    def get_map_save():
        try:
            # get path to saved plane user wants to open.
            # open dialog box in default spot (saves folder), take first element, since it is the path
            filepath = QFileDialog.getOpenFileName(directory=config.SAVES_FOLDER_PATH)[0]

            # if file selected
            if filepath != '':
                # open file for reading
                with open(filepath, 'r') as f:
                    # read contents and create MapSave object out of it
                    return MapSave.from_json(f.read())

        except Exception as e:
            print(e)

        return

    def open_plane_action_triggered(self) -> None:
        """ happens when open plane action is triggered """

        # read selected map save file
        map_save = MainWindow.get_map_save()

        # example visualisation
        print(map_save)

        return

    def edit_plane_action_triggered(self) -> None:
        """ happens when edit plane action is triggered """

        # read selected map save file
        map_save = MainWindow.get_map_save()

        # create new NewPlaneCreator object and store it, so it isn't closed in an instant
        # pass map_save object to load its data
        self._opened_new_plane_creators.append(NewPlaneCreator(map_save))
        # show the lastly appended window
        self._opened_new_plane_creators[-1].show()

        pass

    def exit_action_triggered(self) -> None:
        """ happens when exit action is triggered """

        # close main window, causes stopping application
        self.close()

        return

    def save_settings_action_triggered(self):
        """ happens when save settings action is triggered """

        # settings_main_window mode only

        return

    def revert_settings_action_triggered(self):
        """ happens when revert settings action is triggered """

        # settings_main_window mode only

        return

    def start_simulation_action_triggered(self) -> None:
        """ happens when start simulation action is triggered """
        self.simulation_process.start()

        return

    def closeEvent(self, event) -> None:
        """ executes when close event is triggered """

        # for every opened window
        for w in self._opened_new_plane_creators:
            # close it
            w.close()

        # then apply derived method
        super().closeEvent(event)

        return

    def shut(self):
        if self.simulation_process.is_alive():
            self.simulation_process.join()
