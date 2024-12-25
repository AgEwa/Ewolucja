from PyQt6.QtWidgets import QApplication

from src.gui.MainWindow import MainWindow


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

    return


if __name__ == '__main__':
    main()
