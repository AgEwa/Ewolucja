from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QFrame


class HelpWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(QLabel('''This tab contains the complete user manual for the application. If you have any questions or doubts, you will find the necessary information here.'''))
        layout.addWidget(QLabel('''Options Tab:
In this tab, you can manage simulation parameters and select the data you want to be saved after the simulation run.
Edit Parameters: Change simulation parameters and select the data to save. After making changes, click Save.
Load Population: Load previously saved populations. Select the appropriate file.'''))
        layout.addWidget(QLabel('''Plane Tab:
Here you can create and edit templates of the simulation world.
Create New Plane: Draw a new plane template and save it.
Edit Plane: Open and edit existing plane template.
Load Plane: Load a saved plane template into the simulation.
Note: To pass a template into the simulation, after creating it, you must use the 'Load Plane' function.'''))
        layout.addWidget(QLabel('''Start Simulation Button:
Starts the simulation.
Note: Clicking multiple times will launch additional parallel simulations.'''))
        layout.addWidget(QLabel('''Animation:
The main application window contains three buttons for controlling the animation: Prev, Next, and Rep.
Prev: Go back to the previous generation.
Next: Go to the next generation.
Rep: Replay the current generation animation.
Note: If the animation is not ready, a "wait..." message will appear. The animation refreshes only after pressing one of the buttons.'''))
        layout.addWidget(QLabel('''Exit Button:
Closes the application, but the simulation process continues running.'''))
        layout.addWidget(QLabel('''Final Notes:
The simulation may take a long time depending on the chosen parameters. If you encounter difficulties or have suggestions, contact the application's authors.'''))
        layout.addWidget(QLabel('''Thank you for using our application!'''))

        container = QFrame()
        container.setLayout(layout)

        self.setWindowTitle('Help')

        self.setCentralWidget(container)

        return
