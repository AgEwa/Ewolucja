from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QDialogButtonBox, QFrame, QHBoxLayout

import config


class SettingsEditor(QMainWindow):
    def __init__(self):
        """ constructor """

        # use derived constructor
        super().__init__()

        self._parameters = QFrame()
        self._container = QFrame(self)

        self.initialise()
        self.set_up_layout()

        self.setCentralWidget(self._container)

        return

    def initialise(self):
        self.setWindowTitle('Edit settings')
        self._container.setFixedSize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        return

    def set_up_parameters(self):
        parameters_layout = QHBoxLayout()

        return

    def set_up_layout(self):
        self.set_up_parameters()

        # what submission buttons to use - save and cancel
        buttons = QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        # automatically create container for submission buttons
        submission_block = QDialogButtonBox(buttons)
        # connect method that should be triggered
        submission_block.accepted.connect(self.accept)
        # connect method that should be triggered
        submission_block.rejected.connect(self.reject)

        # create layout
        root_layout = QVBoxLayout()
        # remove paddings
        root_layout.setContentsMargins(0, 0, 0, 0)
        # add submission buttons
        root_layout.addWidget(self._parameters)
        # add submission buttons
        root_layout.addWidget(submission_block)

        self._container.setLayout(root_layout)

        return

    def accept(self):
        print('accepted!')

        self.close()

        return

    def reject(self):
        print('rejected :(')

        self.close()

        return
