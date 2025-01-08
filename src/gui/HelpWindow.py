from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QFrame


class HelpWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._label = QLabel("""        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam lobortis eleifend risus, quis finibus mi commodo ut. Ut quis rutrum nisl. Ut tellus orci, egestas non ligula sit amet, suscipit pretium est. Aenean sollicitudin, nisl ac fringilla volutpat, dui justo pharetra orci, sit amet accumsan ex orci ac eros. Donec venenatis sapien massa, sit amet ultrices diam efficitur sed. Interdum et malesuada fames ac ante ipsum primis in faucibus. Duis eget varius dui. Duis fermentum varius erat quis malesuada.
        
        Mauris sit amet odio eu risus placerat tincidunt. Quisque dignissim enim eget viverra aliquam. Phasellus non lacus in libero scelerisque posuere. Morbi gravida tristique vulputate. Proin sit amet tortor ac libero congue maximus. Etiam justo arcu, molestie at tincidunt nec, consectetur et nulla. Phasellus mattis velit sit amet urna condimentum euismod. Proin eu ultricies arcu. Aliquam iaculis tempus porta. Morbi non dapibus risus. Aliquam pulvinar risus eu condimentum dapibus. In hac habitasse platea dictumst.""")
        self._label.setFixedWidth(300)
        self._label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self._label)

        container = QFrame()
        container.setLayout(layout)

        self.setWindowTitle('Help')

        self.setCentralWidget(container)

        return
