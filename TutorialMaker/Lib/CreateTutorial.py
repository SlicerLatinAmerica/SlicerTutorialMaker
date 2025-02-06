import os
import qt
import slicer
from datetime import datetime

class CreateTutorial(qt.QMainWindow):
    def __init__(self, foldername, parent=None):
        if not parent:
            parent = slicer.util.mainWindow()
        super().__init__(parent)

        self.foldername = foldername  # Store the folder name

        # Set the directory where the .ui file is located
        self.dir_path = os.path.dirname(__file__)

        # Load the UI file
        self.uiWidget = slicer.util.loadUI(os.path.join(self.dir_path, '../Resources/UI/CreateNewTutorial.ui'))

        # Create a central widget and set the layout
        self.setMinimumSize(500, 370)
        central_widget = qt.QWidget()
        self.setCentralWidget(central_widget)

        # Create and configure the grid layout
        layout = qt.QGridLayout(central_widget)

        # Add the UI widget to the grid layout
        layout.addWidget(self.uiWidget)

        # Connect widgets to signals
        self.pushButton = self.uiWidget.findChild(qt.QPushButton, "pushButton_save")
        self.lineEdit_title = self.uiWidget.findChild(qt.QLineEdit, "lineEdit_title")
        self.lineEdit_autor = self.uiWidget.findChild(qt.QLineEdit, "lineEdit_autor")
        self.lineEdit_affiliation = self.uiWidget.findChild(qt.QLineEdit, "lineEdit_affiliation")

        # Connect the button to the save_tutorial function
        self.pushButton.clicked.connect(self.save_tutorial)
        self.setWindowTitle("TutorialMaker - Create Tutorial")

        # Show the window
        self.show()

    def save_tutorial(self):
        try:
            now = datetime.now()

            # Get and process the text values from the QLineEdit fields
            title_text = self.lineEdit_title.text.lower().strip().replace(" ", "_")
            author_text = self.lineEdit_autor.text
            file_name = title_text + ".py"

            # Format the date as mm/dd/yyyy
            formatted_date = now.strftime("%m/%d/%Y")

            # Define a simple or empty description
            description = " "

            # Define the full path of the file
            file_path = os.path.join(self.foldername, file_name)

            # Define the content of the file as a string
            content = f"""import Lib.utils as utils

    Tutorial = utils.Tutorial("{title_text}", "{author_text}", "{formatted_date}", "{description}")

    # Tutorial Name: {title_text}
    # Author Name: {author_text}

    # Start tutorial
    Tutorial.clearTutorial()
    Tutorial.beginTutorial()

    # Here code the first step of the tutorial
    Tutorial.nextScreenshot()

    # Here code the second step of the tutorial
    Tutorial.nextScreenshot()

    # Here code the umpteenth step of the tutorial
    Tutorial.nextScreenshot()

    # End tutorial
    Tutorial.endTutorial()
            """

            # Ensure the directory exists
            if not os.path.exists(self.foldername):
                os.makedirs(self.foldername)

            # Write the content to the .py file
            with open(file_path, 'w') as file:
                file.write(content)
                file.close()

            # Print the full path of the saved file
            print(f"File saved at: {file_path}")

            # Open the folder where the file was saved
            qt.QDesktopServices().openUrl(qt.QUrl("file:///" + self.foldername))

            self.close()
        except Exception as e:
            print(e)
        pass
