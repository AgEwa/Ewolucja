import json
import os
import uuid
from enum import Enum, auto
from multiprocessing import Process
from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QMovie, QImage, QPixmap
from PyQt6.QtWidgets import QMainWindow, QFrame, QFileDialog, QHBoxLayout, QVBoxLayout, QPushButton, QLabel

import config
from src.evolution.Initialization import initialize_simulation
from src.gui.HelpWindow import HelpWindow
from src.gui.NewPlaneCreator import NewPlaneCreator
from src.gui.ParametersEditor import ParametersEditor
from src.saves.PlaneSave import PlaneSave
from src.saves.Settings import Settings
from src.utils.Plot import plot_plane


# this enum class describes available actions menus
class MenuBarOptions(Enum):
    LOAD_POPULATION = auto()
    EDIT_PARAMETERS = auto()
    HELP = auto()
    CREATE_NEW_PLANE = auto()
    EDIT_PLANE = auto()
    LOAD_PLANE = auto()
    EXIT = auto()


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
        # field to store parameters editor window object ref
        self._parameters_editor = None
        # field to store help window object ref
        self._help_window = None

        # dict of actions, for easier access
        self._actions = {}

        #
        self._uid = None
        # indicator of current simulation id
        self._simulation_id = QLabel(f'Simulation ID: Simulation not run')
        # field to store which generation's animation is being played
        self._cur_generation_animation = 0
        # indicator of progress
        self._progress_indicator = QLabel(f'Generation: 1/{Settings.settings.number_of_generations}')
        #
        self._this_gen_spec_survived = QLabel('data was not found yet.')
        self._this_gen_spec_selected = QLabel()
        self._this_gen_spec_killers = QLabel()
        #
        self._start_simulation_btn_blocked = False

        # loaded population
        self._population_file = None
        #
        self._plane_save: PlaneSave = None
        #
        self.simulation_process: Process = None

        # where to place animations
        self._map = QLabel()
        self._map.setStyleSheet('background-color: white')
        self._map.setFixedSize(config.MAP_DIM, config.MAP_DIM)
        # space with buttons
        self._sidebar = QFrame()
        # root widget in window, it is parent of everything else visible
        self._container = QFrame(self)

        # initialise window
        self.initialise()
        # fill in actions dictionary
        self.set_up_actions()
        # create menu bar
        self.set_up_menu_bar()
        # initiate layout
        self.set_up_layout()

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

        return

    def set_up_actions(self) -> None:
        """ fills in actions dictionary """

        # create action that corresponds to loading population
        self._actions[MenuBarOptions.LOAD_POPULATION] = QAction('Load population', self)
        # connect method that should be triggered
        self._actions[MenuBarOptions.LOAD_POPULATION].triggered.connect(self.load_population_action_triggered)

        # create action that corresponds to editing settings
        self._actions[MenuBarOptions.EDIT_PARAMETERS] = QAction('Edit parameters', self)
        # connect method that should be triggered
        self._actions[MenuBarOptions.EDIT_PARAMETERS].triggered.connect(self.edit_parameters_action_triggered)

        # create action that corresponds to exiting
        self._actions[MenuBarOptions.EXIT] = QAction('Exit', self)
        # connect method that should be triggered
        self._actions[MenuBarOptions.EXIT].triggered.connect(self.exit_action_triggered)

        # create action that corresponds to creating new plane
        self._actions[MenuBarOptions.CREATE_NEW_PLANE] = QAction('Create new plane', self)
        # connect method that should be triggered
        self._actions[MenuBarOptions.CREATE_NEW_PLANE].triggered.connect(self.create_new_plane_action_triggered)

        # create action that corresponds to editing plane
        self._actions[MenuBarOptions.EDIT_PLANE] = QAction('Edit plane', self)
        # connect method that should be triggered
        self._actions[MenuBarOptions.EDIT_PLANE].triggered.connect(self.edit_plane_action_triggered)

        # create action that corresponds to loading plane
        self._actions[MenuBarOptions.LOAD_PLANE] = QAction('Load plane', self)
        # connect method that should be triggered
        self._actions[MenuBarOptions.LOAD_PLANE].triggered.connect(self.load_plane_action_triggered)

        # create action that corresponds to accessing information and instructions on how to use application
        self._actions[MenuBarOptions.HELP] = QAction('Help', self)
        # connect method that should be triggered
        self._actions[MenuBarOptions.HELP].triggered.connect(self.help_action_triggered)

        return

    def set_up_menu_bar(self) -> None:
        """ sets up menu bar """

        # get menu bar
        menu = self.menuBar()

        # create menu 'Options'
        options = menu.addMenu('Options')
        # add load population action
        options.addAction(self._actions[MenuBarOptions.LOAD_POPULATION])
        # add edit settings action
        options.addAction(self._actions[MenuBarOptions.EDIT_PARAMETERS])
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
        # add load plane action
        plane_menu.addAction(self._actions[MenuBarOptions.LOAD_PLANE])

        # create menu action help
        menu.addAction(self._actions[MenuBarOptions.HELP])

        return

    def set_up_sidebar(self):
        # switch to previous generation's animation
        switch_prev_gif_btn = QPushButton('Prev')
        # connect method that should be triggered
        switch_prev_gif_btn.clicked.connect(self.prev_gif_btn_clicked)

        # repeat current generation's animation
        repeat_gif_btn = QPushButton('Repeat')
        # connect method that should be triggered
        repeat_gif_btn.clicked.connect(self.repeat_gif_btn_clicked)

        # switch to next generation's animation
        switch_next_gif_btn = QPushButton('Next')
        # connect method that should be triggered
        switch_next_gif_btn.clicked.connect(self.next_gif_btn_clicked)

        mini_layout = QHBoxLayout()
        mini_layout.addWidget(switch_prev_gif_btn)
        mini_layout.addWidget(repeat_gif_btn)
        mini_layout.addWidget(switch_next_gif_btn)

        # what submission buttons to use - save and cancel
        start_simulation_btn = QPushButton('Start simulation')
        # connect method that should be triggered
        start_simulation_btn.clicked.connect(self.start_simulation_action_triggered)

        # create sidebar layout
        sidebar_layout = QVBoxLayout()
        # remove paddings
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        #
        sidebar_layout.addWidget(self._simulation_id)
        #
        sidebar_layout.addWidget(self._progress_indicator)
        #
        sidebar_layout.addWidget(QLabel('This generation:'))
        sidebar_layout.addWidget(self._this_gen_spec_survived)
        sidebar_layout.addWidget(self._this_gen_spec_selected)
        sidebar_layout.addWidget(self._this_gen_spec_killers)
        #
        sidebar_layout.addLayout(mini_layout)
        # add submission buttons
        sidebar_layout.addWidget(start_simulation_btn)

        # apply sidebar layout to sidebar object
        self._sidebar.setLayout(sidebar_layout)

        return

    def set_up_layout(self) -> None:
        """ place widgets in window """

        # assemble sidebar
        self.set_up_sidebar()

        # create layout
        root_layout = QHBoxLayout()
        # set space between widgets to be added
        root_layout.setSpacing(config.EMPTY_SPACE_WIDTH)
        # shortcut
        m = config.WINDOW_PADDINGS
        # set window paddings
        root_layout.setContentsMargins(m, m, m, m)
        # add interactive map
        root_layout.addWidget(self._map)
        # add sidebar
        root_layout.addWidget(self._sidebar)

        # apply created layout
        self._container.setLayout(root_layout)

        return

    def load_population_action_triggered(self):
        """ happens when load population action is triggered """
        try:
            # save selected population save file
            self._population_file = QFileDialog.getOpenFileName(directory=config.SIMULATION_SAVES_FOLDER_PATH)[0]
        except Exception as e:
            print(e)

        return

    def edit_parameters_action_triggered(self):
        """ happens when edit settings action is triggered """

        # settings_new_window mode only
        self._parameters_editor = ParametersEditor()
        self._parameters_editor.show()

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

    @staticmethod
    def get_plane_save():
        try:
            # get path to saved plane user wants to open.
            # open dialog box in default spot (saves folder), take first element, since it is the path
            filepath = QFileDialog.getOpenFileName(directory=config.PLANE_SAVES_FOLDER_PATH)[0]

            # if file selected
            if filepath != '':
                # open file for reading
                with open(filepath, 'r') as f:
                    # read contents and create MapSave object out of it
                    return PlaneSave.from_json(f.read())

        except Exception as e:
            print(e)

        return

    def edit_plane_action_triggered(self) -> None:
        """ happens when edit plane action is triggered """

        # read selected map save file
        plane_save = MainWindow.get_plane_save()

        if plane_save is not None:
            # create new NewPlaneCreator object and store it, so it isn't closed in an instant
            # pass plane_save object to load its data
            self._opened_new_plane_creators.append(NewPlaneCreator(plane_save))
            # show the lastly appended window
            self._opened_new_plane_creators[-1].show()

        pass

    def load_plane_action_triggered(self) -> None:
        """ happens when load plane action is triggered """

        # read selected map save file
        self._plane_save = MainWindow.get_plane_save()

        # example visualisation
        print(self._plane_save)

        path = os.path.join(config.PLANE_SAVES_FOLDER_PATH, 'currently_loaded_plane')

        try:
            if self._plane_save.dim != Settings.settings.dim:
                self._plane_save.dim = None

            if self._plane_save.dim is not None:
                plot_plane(self._plane_save.get_barrier_positions(), self._plane_save.get_food_positions(), path)
            else:
                plot_plane([], [], path)
        except Exception as e:
            print(e, 1)

        try:
            image = QImage(path)
            image = image.scaled(config.MAP_DIM, config.MAP_DIM)

            self._map.setPixmap(QPixmap.fromImage(image))
        except Exception as e:
            print(e, 2)

        return

    def help_action_triggered(self):
        """ happens when help action is triggered """

        self._help_window = HelpWindow()
        self._help_window.show()

        return

    def update_(self):
        self._progress_indicator.setText(f'Generation: {self._cur_generation_animation + 1}/{Settings.settings.number_of_generations}')

        ## ANIMATION

        # path to desired generation animation of current simulation
        path = os.path.join(config.SIMULATION_SAVES_FOLDER_PATH, f'{self._uid}', 'animation', f'generation_{self._cur_generation_animation}.gif')

        if os.path.exists(path):
            # if current generation is the last one AND animation for this generation exists
            if self._cur_generation_animation + 1 == Settings.settings.number_of_generations:
                # then animation completed! we can unblock starting next simulations
                self._start_simulation_btn_blocked = False
        else:
            path = os.path.join(Path(os.path.realpath(__file__)).parent.parent.absolute().__str__(), 'trying_to_load_animation.png')

        animation = QMovie(path)
        animation.setScaledSize(QSize(config.MAP_DIM, config.MAP_DIM))
        self._map.setMovie(animation)
        animation.start()

        ## STATISTICS

        path = os.path.join(config.SIMULATION_SAVES_FOLDER_PATH, f'{self._uid}', 'stats', f'gen_{self._cur_generation_animation}.json')
        if os.path.exists(path):
            with open(path, 'r') as f:
                x = json.loads(f.read())

            self._this_gen_spec_survived.setText(f'{x['survived']} specimens survived.')
            self._this_gen_spec_selected.setText(f'{x['selected']} specimens were selected.')
            self._this_gen_spec_killers.setText(f'{x['killers count']} specimens had killer gene.')
        else:
            self._this_gen_spec_survived.setText(f'data was not found yet.')
            self._this_gen_spec_selected.setText(f'')
            self._this_gen_spec_killers.setText(f'')

        return

    def prev_gif_btn_clicked(self):
        """"""

        self._cur_generation_animation -= 1

        if self._cur_generation_animation < 0:
            self._cur_generation_animation = 0

        self.update_()

        return

    def repeat_gif_btn_clicked(self):
        self.update_()

        return

    def next_gif_btn_clicked(self):
        """"""

        self._cur_generation_animation += 1

        if self._cur_generation_animation > Settings.settings.number_of_generations - 1:
            self._cur_generation_animation = Settings.settings.number_of_generations - 1

        self.update_()

        return

    def start_simulation_action_triggered(self) -> None:
        """ happens when start simulation action is triggered """

        if not self._start_simulation_btn_blocked:
            self._start_simulation_btn_blocked = True

            self._uid = uuid.uuid4()

            self._simulation_id.setText(f'Simulation ID: \n{self._uid}')

            self.simulation_process = Process(target=initialize_simulation, args=(
                self._plane_save, self._uid, self._population_file))
            self.simulation_process.start()
            self._cur_generation_animation = 0

            self.update_()

        return

    def closeEvent(self, event) -> None:
        """ executes when close event is triggered """

        if self._help_window is not None:
            self._help_window.close()

        if self._parameters_editor is not None:
            self._parameters_editor.close()

        # for every opened window
        for w in self._opened_new_plane_creators:
            # close it
            w.close()

        # then apply derived method
        super().closeEvent(event)

        return

    def shut(self):
        if self.simulation_process and self.simulation_process.is_alive():
            self.simulation_process.join()
