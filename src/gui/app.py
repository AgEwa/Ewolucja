from PyQt6.QtWidgets import QApplication

from src.gui.MainWindow import MainWindow


def main():
    """ Application entry point """

    # creating application object. you can pass sys.args as argument to it
    # if you want your application to support starting arguments
    # we don't need that (for now?) so pass empty list
    app = QApplication([])
    # create main window of application
    window = MainWindow()
    # show it most definitely
    window.show()
    # start application loop
    app.exec()

    return


if __name__ == '__main__':
    main()
