from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QFrame, QLabel, QScrollArea


class HelpWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        try:
            text = """This tab contains the <b>complete user manual</b> for the application. If you have any <b>questions</b> or <b>doubts</b>, you will find the necessary information below.
<br><br>
<span style="font-size: 15px;"><b>Options Tab:</b></span>
<ul>
    <li><u>Edit Parameters:</u> Change simulation parameters and select the data you want to be saved. After making changes, click <b>Save</b>.</li>
    <li><u>Load Population:</u> Load previously saved populations by selecting the appropriate file.</li>
</ul>
<b>Note:</b> To view the animation of evolution, ensure that the "<i>Save Animation</i>" option is <b>checked</b>.<br><br>

<span style="font-size: 15px;"><b>Plane Tab:</b></span>
<ul>
    <li><u>Create New Plane:</u> Draw a new plane template and save it.</li>
    <li><u>Edit Plane:</u> Open and edit existing plane templates. You can save it as a new one.</li>
    <li><u>Load Plane:</u> Load a saved plane template into the simulation.</li>
</ul>
<b>Note:</b> To pass a template into the simulation, after creating it, you must use the <b>'Load Plane'</b> function. The chosen template will appear in the main window.<br><br>

<span style="font-size: 15px;"><b>Start Simulation Button:</b></span>
<ul>
    <li>Starts the simulation.</li>
</ul>
<b>Note:</b> Clicking multiple times will launch <b>additional parallel simulations</b>.<br><br>

<span style="font-size: 15px;"><b>Animation:</b></span>
<ul>
    <li><u>Prev:</u> Go back to the previous generation.</li>
    <li><u>Next:</u> Go to the next generation.</li>
    <li><u>Repeat:</u> Replay the current generation animation.</li>
</ul>
<b>Note:</b> If the animation is not ready, a "<i>Trying to find animation...</i>" message will appear. The animation refreshes only after pressing one of the buttons.<br><br>

<span style="font-size: 15px;"><b>Exit Button:</b></span>
<ul>
    <li>Closes the application, but the simulation process continues running.</li>
</ul>

<span style="font-size: 15px;"><b>Final Notes:</b></span>
<ul>
    <li>The simulation may take a <b>long time</b> depending on the chosen parameters.</li>
    <li>If you encounter <b>difficulties</b> or have <b>suggestions</b>, contact the application's authors.</li>
</ul>

Thank you for using our application!
"""
            label = QLabel(text)
            label.setWordWrap(True)

            scroll_area = QScrollArea()
            scroll_area.setWidget(label)
            scroll_area.setWidgetResizable(True)

            layout.addWidget(scroll_area)

        except Exception as e:
            print(e)

        container = QFrame()
        container.setLayout(layout)

        self.setWindowTitle('Help')

        self.setCentralWidget(container)

        return
