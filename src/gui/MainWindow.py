from enum import Enum, auto

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QFrame

import config
from src.gui.NewPlaneCreator import NewPlaneCreator


class OPTIONS(Enum):
    START_SIMULATION = auto()
    CREATE_NEW_PLANE = auto()
    EDIT_SETTINGS = auto()
    EXIT = auto()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._opened_new_plane_creators = []
        self._actions = {}
        self._container = QFrame(self)

        self.initialise()
        self.set_up_actions()
        self.set_up_menu_bar()

        self.setCentralWidget(self._container)

        return

    def initialise(self):
        self.setWindowTitle('Evolution')
        self._container.setFixedSize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self._container.setStyleSheet('background-color: teal;')

        return

    def set_up_actions(self):
        self._actions[OPTIONS.START_SIMULATION] = QAction('Start simulation', self)
        self._actions[OPTIONS.START_SIMULATION].triggered.connect(self.start_simulation_action_triggered)

        self._actions[OPTIONS.CREATE_NEW_PLANE] = QAction('Create new plane', self)
        self._actions[OPTIONS.CREATE_NEW_PLANE].triggered.connect(self.create_new_plane_action_triggered)

        self._actions[OPTIONS.EDIT_SETTINGS] = QAction('Edit settings', self)
        self._actions[OPTIONS.EDIT_SETTINGS].triggered.connect(self.edit_settings_action_triggered)

        self._actions[OPTIONS.EXIT] = QAction('Exit', self)
        self._actions[OPTIONS.EXIT].triggered.connect(self.exit_action_triggered)

        return

    def set_up_menu_bar(self):
        menu = self.menuBar()

        options_menu = menu.addMenu('Options')
        options_menu.addAction(self._actions[OPTIONS.START_SIMULATION])
        options_menu.addAction(self._actions[OPTIONS.CREATE_NEW_PLANE])
        options_menu.addAction(self._actions[OPTIONS.EDIT_SETTINGS])
        options_menu.addSeparator()
        options_menu.addAction(self._actions[OPTIONS.EXIT])

        return

    def start_simulation_action_triggered(self):
        return

    def create_new_plane_action_triggered(self):
        self._opened_new_plane_creators.append(NewPlaneCreator())
        self._opened_new_plane_creators[-1].show()

        return

    def edit_settings_action_triggered(self):
        return

    def exit_action_triggered(self):
        self.close()

        return

    def closeEvent(self, a0):
        for w in self._opened_new_plane_creators:
            w.close()

        super().closeEvent(a0)

        return
