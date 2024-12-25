from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QFrame, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QRadioButton, QLabel, \
    QLineEdit

import config
from src.gui.Map import Map, MarkType


class NewPlaneCreator(QMainWindow):
    def __init__(self):
        super().__init__()

        self._container = QFrame()
        self._map = Map()
        self._barrier = QRadioButton('Barrier')
        self._barrier.clicked.connect(self.barrier_radio_clicked)
        self._food = QRadioButton('Food')
        self._food.clicked.connect(self.food_radio_clicked)
        self._sidebar = QFrame()

        self.initialise()
        self.set_up_layout()

        self.setCentralWidget(self._container)

        return

    def barrier_radio_clicked(self, s):
        self._map.set_cur_mark(MarkType.BARRIER)

        return

    def food_radio_clicked(self, s):
        self._map.set_cur_mark(MarkType.FOOD)

        return

    def initialise(self):
        self.setWindowTitle('Create new plane')
        self._container.setFixedSize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        return

    def set_up_sidebar(self):
        # barriers or food
        choose_block = QFrame()
        choose_block_layout = QVBoxLayout()
        choose_block_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        choose_block_layout.addWidget(QLabel('Create name:'))
        choose_block_layout.addWidget(QLineEdit())
        choose_block_layout.addWidget(QLabel('Place on plane:'))
        choose_block_layout.addWidget(self._barrier)
        choose_block_layout.addWidget(self._food)
        self._barrier.setChecked(True)
        choose_block.setLayout(choose_block_layout)

        # save or discard
        buttons = QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        submission_block = QDialogButtonBox(buttons)
        submission_block.accepted.connect(self.accept)
        submission_block.rejected.connect(self.reject)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.addWidget(choose_block)
        sidebar_layout.addWidget(submission_block)

        self._sidebar.setLayout(sidebar_layout)

        return

    def accept(self):
        barrier_positions, food_positions = self._map.get_marked_data()

        self.close()

        return

    def reject(self):
        self.close()

        return

    def set_up_layout(self):
        self.set_up_sidebar()

        root_layout = QHBoxLayout()
        root_layout.setSpacing(config.EMPTY_SPACE_WIDTH)
        m = config.WINDOW_PADDINGS
        root_layout.setContentsMargins(m, m, m, m)
        root_layout.addWidget(self._map)
        root_layout.addWidget(self._sidebar)

        self._container.setLayout(root_layout)

        return
