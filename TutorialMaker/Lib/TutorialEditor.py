import qt
import slicer
import os
import Lib.utils as utils
from slicer.i18n import tr as _

#
# Tutorial Editor Widget
#

class TutorialEditor(qt.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.logic = TutorialEditorLogic(self)
        self.setWindowTitle(_("Tutorial Editor"))
        self.setGeometry(0, 0, 300, 200)

        self.boxLayout = qt.QVBoxLayout()

        self.Setup()

        self.setLayout(self.boxLayout)

        self.currentCell = None
        self.annotator = Annotator(self)
        pass

    def Setup(self):

        # Load Ui file
        uiWidget = slicer.util.loadUI(resourcePath('UI/TutorialEditor.ui'))
        self.boxLayout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Table sentings
        self.ui.tableWidgetStates.horizontalHeader().setStretchLastSection(True)
        self.ui.tableWidgetStates.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)

        # Connections
        self.ui.pushButtonStartStopRecord.clicked.connect(self.logic.StopStartRecording)
        self.ui.pushButtonCapture.clicked.connect(self.OnClickedAnnotate)
        self.ui.tableWidgetStates.cellClicked.connect(self.onCellClicked)

        pass

    def Show(self):
        self.show()

    def OnClikedStartStopRecord(self):
        pass

    def OnClickedAnnotate(self):
        if self.currentCell is None:
            return
        self.hide()
        self.annotator.Show()
        pass

    def onCellClicked(self, row, collumn):
        self.currentCell = row

    #
    # Use this method for add itens on table
    #
    def TableAddItem(self, widget:str=''):
        item = qt.QTableWidgetItem(widget)
        table = self.ui.tableWidgetStates
        rowsCount = table.rowCount

        table.setRowCount(rowsCount + 1)
        table.setItem(rowsCount, 0, item)

        pass

    def exit(self):
        self.logic.StopRecording()
        self.annotator.close()
        self.close()

    pass

class TutorialEditorLogic():
    def __init__(self, gui=None):
        self.stateManager = StateManager()
        self.widgetFinder = utils.WidgetFinder(slicer.util.mainWindow())
        self.widgetFinder.sinalManager.connect(self.NextWidget)
        self.isRecording = False
        self.gui = gui
        pass

    def StopStartRecording(self):
        if not self.isRecording:
            self.StartRecording()
        else:
            self.StopRecording()
        self.isRecording = not self.isRecording
        pass

    def StartRecording(self):
        self.gui.showMinimized()
        self.gui.ui.pushButtonStartStopRecord.text = _("Stop Recording")
        self.widgetFinder.showFullSize()
        pass

    def StopRecording(self):
        self.gui.ui.pushButtonStartStopRecord.text = _("Start Recording")
        self.widgetFinder.hideOverlay()
        pass

    def NextWidget(self, widget):
        if self.isRecording:
            self.SaveState(widget)
            self.widgetFinder.showFullSize()
            self.gui.TableAddItem(widget)
        pass

    def SaveState(self, widget):
        _state = SlicerState(widget)

        self.stateManager.InsertState(_state)
        pass
class StateManager():
    def __init__(self):
        self.states = []
        pass

    def InsertState(self, state):
        self.states.append(state)
        pass


    def deleteState(self, index):
        self.states.pop(index)
        pass

    def annotateState(self, index):
        #
        pass


class SlicerState():
    def __init__(self, nextWidget):
        self.nextWidget = nextWidget

        self.annotations = []
        pass

class Annotator(qt.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.logic = TutorialEditorLogic(self)
        self.setWindowTitle(_("Widget Annotator"))
        self.setGeometry(0, 0, 600, 40)

        self.boxLayout = qt.QVBoxLayout()

        self.Setup()

        self.setLayout(self.boxLayout)

        self._parent = parent
        self.widgetFinder = utils.WidgetFinder(slicer.util.mainWindow())
        self.painter = utils.Shapes(slicer.util.mainWindow())
        self.widgetFinder.sinalManager.connect(self.AnnotateWidget)

        pass
    def Setup(self):
        # Load Ui file
        uiWidget = slicer.util.loadUI(resourcePath('UI/WidgetAnnotator.ui'))
        self.boxLayout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

    def Show(self):
        self.show()
        self.widgetFinder.showFullSize()
        pass

    def closeEvent(self, event):
        self._parent.Show()
        self.widgetFinder.hideOverlay()
        event.accept()
        pass

    def AnnotateWidget(self, widget):

        pass

    pass

# There should be a better way to expose the resource path to the underlying classes of a module but I couldn't think of a clean way.
def resourcePath(filename):
    """Return the absolute path of the module ``Resources`` directory."""
    scriptedModulesPath = os.path.dirname(slicer.util.modulePath("TutorialMaker"))
    return os.path.join(scriptedModulesPath, "Resources", filename)
