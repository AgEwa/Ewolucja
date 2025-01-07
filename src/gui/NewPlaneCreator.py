from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QFrame, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QRadioButton, QLabel, \
    QFileDialog

import config
from src.gui.Map import Map, MarkType
from src.saves.MapSave import MapSave
from src.saves.Settings import Settings


# new plane creator
class NewPlaneCreator(QMainWindow):
    def __init__(self, p_map_save: MapSave = None):
        """ constructor, takes optional parameter p_map_save which places default spaces on map """

        # use derived constructor
        super().__init__()

        # root widget in window, it is parent of everything else visible
        self._container = QFrame()
        # interactive map that you can click to edit it, init with p_map_save
        self._map = Map(p_map_save)
        # radio button to select what type of object to place on plane (barrier)
        self._barrier = QRadioButton('Barrier')
        # connect method that should be triggered
        self._barrier.clicked.connect(self.barrier_radio_clicked)
        # radio button to select what type of object to place on plane (food)
        self._food = QRadioButton('Food')
        # connect method that should be triggered
        self._food.clicked.connect(self.food_radio_clicked)
        # radio button to select what type of object to place on plane (remove barrier or food)
        self._empty = QRadioButton('Empty')
        # connect method that should be triggered
        self._empty.clicked.connect(self.empty_radio_clicked)
        # container for elements to be positioned as sidebar
        self._sidebar = QFrame()

        # initialise window
        self.initialise()
        # place all widgets
        self.set_up_layout()

        # place container at the center
        self.setCentralWidget(self._container)

        return

    def barrier_radio_clicked(self) -> None:
        """ happens when barrier corresponding radio button is clicked """

        # send info to interactive map to change currently placing object
        self._map.set_cur_mark(MarkType.BARRIER)

        return

    def food_radio_clicked(self) -> None:
        """ happens when food corresponding radio button is clicked """

        # send info to interactive map to change currently placing object
        self._map.set_cur_mark(MarkType.FOOD)

        return

    def empty_radio_clicked(self) -> None:
        """ happens when empty corresponding radio button is clicked """

        # send info to interactive map to change currently placing object
        self._map.set_cur_mark(MarkType.EMPTY)

        return

    def initialise(self):
        # set window title
        self.setWindowTitle('Create new plane')
        # set window size
        self._container.setFixedSize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        return

    def set_up_sidebar(self) -> None:
        """ place widgets in sidebar """

        # create container for radio buttons
        choose_block = QFrame()
        # create their layout
        choose_block_layout = QVBoxLayout()
        # change alignment to top
        choose_block_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # add descriptive label
        choose_block_layout.addWidget(QLabel('Place on plane:'))
        # add radio buttons
        choose_block_layout.addWidget(self._barrier)
        choose_block_layout.addWidget(self._food)
        choose_block_layout.addWidget(self._empty)
        # check default radio button
        self._barrier.setChecked(True)
        # apply created layout
        choose_block.setLayout(choose_block_layout)

        # what submission buttons to use - save and cancel
        buttons = QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        # automatically create container for submission buttons
        submission_block = QDialogButtonBox(buttons)
        # connect method that should be triggered
        submission_block.accepted.connect(self.accept)
        # connect method that should be triggered
        submission_block.rejected.connect(self.reject)

        # create sidebar layout
        sidebar_layout = QVBoxLayout()
        # remove paddings
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        # add radio buttons
        sidebar_layout.addWidget(choose_block)
        # add submission buttons
        sidebar_layout.addWidget(submission_block)

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

    def accept(self) -> None:
        """ tries to save created plane configuration """

        try:
            # create MapSave object out of data returned by interactive map
            map_save = self._map.get_marked_data()

            # get destination where user wants to store saved plane
            # default directory to saves directory, allow only .json endings, take first element, since it is the path
            filename = QFileDialog.getSaveFileName(self, 'Save file', config.PLANE_SAVES_FOLDER_PATH, 'Text files (*.json)')[
                0]

            # if file selected
            if filename != '':
                # open file either for creating or overwriting (was prompted)
                with open(filename, 'w') as f:
                    # write contents converting MapSave into json
                    f.write(map_save.to_json())

                # close NewPlaneCreator
                self.close()
        except Exception as e:
            print(e)

        return

    def reject(self) -> None:
        """ immediately close NewPlaneCreator window """

        # close NewPlaneCreator
        self.close()

        return
