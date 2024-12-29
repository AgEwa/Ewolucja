from enum import Enum, auto

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QFrame, QFileDialog

import config
from src.gui.NewPlaneCreator import NewPlaneCreator
from src.saves.MapSave import MapSave


# this enum class describes available actions in 'Options' menu bar
class MainOptions(Enum):
    START_SIMULATION = auto()
    EDIT_SETTINGS = auto()
    EXIT = auto()


# this enum class describes available actions in 'Plane' menu bar
class PlaneOptions(Enum):
    CREATE_NEW_PLANE = auto()
    OPEN_PLANE = auto()


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

        # create action that corresponds to starting simulation
        self._actions[MainOptions.START_SIMULATION] = QAction('Start simulation', self)
        # connect method that should be triggered
        self._actions[MainOptions.START_SIMULATION].triggered.connect(self.start_simulation_action_triggered)

        # create action that corresponds to editing settings
        self._actions[MainOptions.EDIT_SETTINGS] = QAction('Edit settings', self)
        # connect method that should be triggered
        self._actions[MainOptions.EDIT_SETTINGS].triggered.connect(self.edit_settings_action_triggered)

        # create action that corresponds to exiting
        self._actions[MainOptions.EXIT] = QAction('Exit', self)
        # connect method that should be triggered
        self._actions[MainOptions.EXIT].triggered.connect(self.exit_action_triggered)

        # create action that corresponds to creating new plane
        self._actions[PlaneOptions.CREATE_NEW_PLANE] = QAction('Create new plane', self)
        # connect method that should be triggered
        self._actions[PlaneOptions.CREATE_NEW_PLANE].triggered.connect(self.create_new_plane_action_triggered)

        # create action that corresponds to opening plane
        self._actions[PlaneOptions.OPEN_PLANE] = QAction('Open plane', self)
        # connect method that should be triggered
        self._actions[PlaneOptions.OPEN_PLANE].triggered.connect(self.open_plane_action_triggered)

        return

    def set_up_menu_bar(self) -> None:
        """ sets up menu bar """

        # get menu bar
        menu = self.menuBar()

        # add 'Options' menu
        options_menu = menu.addMenu('Options')
        # add start simulation action
        options_menu.addAction(self._actions[MainOptions.START_SIMULATION])
        # add edit settings action
        options_menu.addAction(self._actions[MainOptions.EDIT_SETTINGS])
        # add separator
        options_menu.addSeparator()
        # add exit action
        options_menu.addAction(self._actions[MainOptions.EXIT])

        # add 'Plane' menu
        plane_menu = menu.addMenu('Plane')
        # add create new plane action
        plane_menu.addAction(self._actions[PlaneOptions.CREATE_NEW_PLANE])
        # add open plane action
        plane_menu.addAction(self._actions[PlaneOptions.OPEN_PLANE])

        return

    def start_simulation_action_triggered(self) -> None:
        """ happens when start simulation action is triggered """

        return

    def edit_settings_action_triggered(self) -> None:
        """ happens when edit settings action is triggered """

        return

    def exit_action_triggered(self) -> None:
        """ happens when exit action is triggered """

        # close main window, causes stopping application
        self.close()

        return

    def create_new_plane_action_triggered(self) -> None:
        """ happens when create new plane action is triggered """

        # create new NewPlaneCreator object and store it, so it isn't closed in an instant
        self._opened_new_plane_creators.append(NewPlaneCreator())
        # show the lastly appended window
        self._opened_new_plane_creators[-1].show()

        return

    def open_plane_action_triggered(self) -> None:
        """ happens when open plane action is triggered """

        try:
            # get path to saved plane user wants to open.
            # open dialog box in default spot (saves folder), take first element, since it is the path
            filepath = QFileDialog.getOpenFileName(directory=config.SAVES_FOLDER_PATH)[0]

            # if file selected
            if filepath != '':
                # open file for reading
                with open(filepath, 'r') as f:
                    # read contents and create MapSave object out of it
                    map_save = MapSave.from_json(f.read())

                # for further use
                print(map_save)

        except Exception as e:
            print(e)

        return

    def closeEvent(self, a0) -> None:
        """ executes when close event is triggered """

        # for every opened window
        for w in self._opened_new_plane_creators:
            # close it
            w.close()

        # then apply derived method
        super().closeEvent(a0)

        return
