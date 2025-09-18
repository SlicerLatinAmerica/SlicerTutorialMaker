import logging
import os
import platform
import subprocess
import slicer
import importlib
import qt
import Lib.TutorialUtils
import Lib.TutorialPainter as AnnotationPainter
import Lib.GitTools as GitTools

from slicer.ScriptedLoadableModule import * # noqa: F403
from slicer.util import VTKObservationMixin
from slicer.i18n import tr as _
from slicer.i18n import translate
from Lib.TutorialEditor import TutorialEditor
import Lib.TutorialGUI
from Lib.CreateTutorial import CreateTutorial
from Lib.TutorialUtils import SelfTestTutorialLayer

#
# TutorialMaker
#

class TutorialMaker(ScriptedLoadableModule): # noqa: F405
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent) # noqa: F405
        self.parent.title = _("Tutorial Maker")
        self.parent.categories = [translate("qSlicerAbstractCoreModule", "Utilities")]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Douglas Gonçalves (Universidade de São Paulo)", "Enrique Hernández (Universidad Autónoma del Estado de México)",
                                    "João Januário (Universidade de São Paulo)", "Lucas Silva (Universidade de São Paulo)",
                                    "Paulo Pereira (Universidade de São Paulo)", "Lucas Miranda Mendonça Rezende (Universidade de São Paulo)"
                                    "Victor Montaño (Universidad Autónoma del Estado de México)", "Paulo Eduardo de Barros Veiga (Universidade de São Paulo)", 
                                    "Valeria Gomez-Valdes (Universidad Autónoma del Estado de México)", "Monserrat Rıos-Hernandez (Universidad Autónoma del Estado de México)", 
                                    "Fatou Bintou Ndiaye (University Cheikh Anta Diop)", "Mohamed Alalli Bilal (University Cheikh Anta Diop)", 
                                    "Steve Pieper (Isomics Inc.)", "Adriana Vilchis-Gonzalez (Universidad Autónoma del Estado de México)", 
                                    "Luiz Otavio Murta Junior (Universidade de São Paulo)", "Andras Lasso (Queen’s University)", 
                                    "Sonia Pujol (Brigham and Women’s Hospital, Harvard Medical School)"]
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """help text"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _("""
        The development of this module has been made possible in part by a grant from the Chan Zuckerberg Initiative
        """)

#
# TutorialMakerWidget
#

class TutorialMakerWidget(ScriptedLoadableModuleWidget, VTKObservationMixin): # noqa: F405
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent) # noqa: F405
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False
        self.__tableSize = 0
        self.__selectedTutorial = None
        self.isDebug = slicer.app.settings().value("Developer/DeveloperMode")

        print(_("Version Date: {}").format("2025/09/17-08:00AM"))

        #PROTOTYPE FOR PLAYBACK

        self.actionList = []

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        import importlib
        importlib.reload(Lib.TutorialGUI)
        importlib.reload(Lib.TutorialUtils)

        ScriptedLoadableModuleWidget.setup(self) # noqa: F405

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/TutorialMaker.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        #Verify if the folders to manipulate the tutorials are created
        Lib.TutorialUtils.Util.verifyOutputFolders()
        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = TutorialMakerLogic()

        # will only draw the circle at playback for now
        #self.widgetFinder.sinalManager.connect(self.widgetPainter.setTargetWidget)

        # Buttons

        #Dynamic Tutorial Prototype
        self.ui.pushButtonEdit.connect('clicked(bool)', self.logic.Edit)
        self.ui.pushButtonSave.connect('clicked(bool)', self.logic.Save)
        self.ui.pushButtonLoad.connect('clicked(bool)', self.logic.Load)
        self.ui.pushButtonExportScreenshots.connect('clicked(bool)', self.logic.ExportScreenshots)
        self.ui.pushButtonNewTutorial.connect('clicked(bool)', self.logic.CreateNewTutorial)
        self.ui.pushButtonOpenAnnotator.connect('clicked(bool)', self.logic.OpenAnnotator)
        self.ui.pushButtonFetchFromGithub.connect('clicked(bool)', self.getFromGithub)
        self.ui.listWidgetTutorials.itemSelectionChanged.connect(self.tutorialSelectionChanged)

        #Static Tutorial Handlers
        self.ui.pushButtonCapture.connect('clicked(bool)', self.captureButton)
        self.ui.pushButtonGenerate.connect('clicked(bool)', self.generateButton)
        if self.isDebug != True: # noqa: E712
            self.ui.CollapsibleButtonTutorialMaking.setVisible(0)
            self.ui.pushButtonNewTutorial.setVisible(0)
            self.logic.loadTutorialsFromRepos()

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

        #Update GUI
        self.populateTutorialList()

    def cleanup(self):
        # that will make an exception: AttributeError: 'NoneType' object has no attribute 'exitTutorialEditor'
        # self.logic.exitTutorialEditor()
        """
        Called when the application closes and the module widget is destroyed.
        """
        return

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        #self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        pass

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        return

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """
        return

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """
        return

    def generateButton(self):
        self.logic.Generate(self.__selectedTutorial)

    def CreateTutorialButton(self):
        self.logic.CreateNewTutorial()

    def captureButton(self):
        self.logic.Capture(self.__selectedTutorial)

    def tutorialSelectionChanged(self):
        self.__selectedTutorial = self.ui.listWidgetTutorials.selectedItems()[0].data(0)
        self.ui.pushButtonCapture.setEnabled(self.__selectedTutorial is not None)
        self.ui.pushButtonGenerate.setEnabled(self.__selectedTutorial is not None)

    def getFromGithub(self):
        self.logic.loadTutorialsFromRepos()
        self.populateTutorialList()
        pass

    def populateTutorialList(self):
        loadedTutorials = self.logic.loadTutorials()
        listWidget = self.ui.listWidgetTutorials
        listWidget.clear()
        listWidget.addItems(loadedTutorials)

#
# TutorialMakerLogic
#
class TutorialMakerLogic(ScriptedLoadableModuleLogic): # noqa: F405
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self) # noqa: F405
        self.tutorialEditor = TutorialEditor()
        self.TutorialRepos = [
            "SlicerLatinAmerica/SlicerTestTutorial"
        ]
        self.LanguageRepos = [
            "Slicer/SlicerLanguageTranslations"
        ]

    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        pass

    def exitTutorialEditor(self):
        self.tutorialEditor.exit()

    def Edit(self):
        self.tutorialEditor.Show()
        pass

    def Save(self):
        pass

    def Load(self):
        pass

    def ExportScreenshots(self):
        screenshot = Lib.TutorialUtils.ScreenshotTools()
        screenshot.saveScreenshotMetadata(0)
        pass

    def Capture(self, tutorialName):
        def FinishTutorial():
            slicer.util.mainWindow().moduleSelector().selectModule('TutorialMaker')
            slicer.util.infoDisplay(_("Tutorial Captured"), _("Captured Tutorial: {tutorialName}").format(tutorialName=tutorialName))
        
        with slicer.util.tryWithErrorDisplay("Failed to capture tutorial"):
            TutorialMakerLogic.runTutorialTestCases(tutorialName, FinishTutorial)

    def Generate(self, tutorialName):
        with slicer.util.tryWithErrorDisplay(_("Failed to generate tutorial")):
            AnnotationPainter.TutorialPainter().GenerateHTMLfromAnnotatedTutorial(Lib.TutorialUtils.get_module_basepath("TutorialMaker") + "/Outputs/Annotations/annotations.json")
            outputPath = Lib.TutorialUtils.get_module_basepath("TutorialMaker") + "/Outputs/"
            if platform.system() == "Windows":
                os.startfile(outputPath)
            else:
                import subprocess, sys
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, outputPath])
            qt.QMessageBox.information(slicer.util.mainWindow(), _("Tutorial Generated"), _("Generated Tutorial: {tutorialName}").format(tutorialName=tutorialName))
        pass

    def CreateNewTutorial(self):
        folderName = Lib.TutorialUtils.get_module_basepath("TutorialMaker") + "/Testing/"
        Tutorial_Win = CreateTutorial(folderName)
        Tutorial_Win.show()
        pass

    def OpenAnnotator(Self):
        Annotator = Lib.TutorialGUI.TutorialGUI()
        Annotator.open_json_file(Lib.TutorialUtils.get_module_basepath("TutorialMaker") + "/Outputs/Raw/Tutorial.json")
        Annotator.show()
        pass

    def loadTutorialsFromRepos(self):
        modulePath = Lib.TutorialUtils.get_module_basepath("TutorialMaker")
        
        os.makedirs(os.path.join(modulePath, "Testing"), exist_ok=True)
        os.makedirs(os.path.join(modulePath, "Languages"), exist_ok=True)
        
        # Tutorials
        for repo in self.TutorialRepos:
            files = GitTools.GitFile("", "")
            try:
                with slicer.util.tryWithErrorDisplay(_("Failed to fetch tutorials from {repo}").format(repo=repo)):
                    files = GitTools.GitTools.ParseRepo(repo)
            except:
                continue
            for TutorialRoot in files.dir("Tutorials"):
                for TutorialFile in files.dir(f"Tutorials/{TutorialRoot}"):
                    if TutorialFile.endswith(".py"):
                        try:
                            with slicer.util.tryWithErrorDisplay(_("Failed to fetch {TutorialFile} from {repo}".format(TutorialFile=TutorialFile, repo=repo))):
                                pyRaw = files.getRaw(f"Tutorials/{TutorialRoot}/{TutorialFile}")
                                fd = open(f"{modulePath}/Testing/{TutorialFile}", "w", encoding='utf-8')
                                fd.write(pyRaw)
                                fd.close()
                        except:
                            continue
                      
        # Language Packs  
        for repo in self.LanguageRepos:
            files = GitTools.GitFile("", "")
            try:
                with slicer.util.tryWithErrorDisplay(_("Failed to fetch language packs from {repo}").format(repo=repo)):
                    files = GitTools.GitTools.ParseRepo(repo)
            except:
                continue
            for langFile in files.dir("translations"):
                if not (langFile.endswith(".ts") or langFile.endswith(".qm")):
                    continue
                try:
                    with slicer.util.tryWithErrorDisplay(_("Failed to fetch {langFile} from {repo}").format(langFile=langFile, repo=repo)):
                        raw = files.getRaw(f"translations/{langFile}")
                        dest_path = os.path.join(modulePath, "Languages", langFile)
                       
                        # Save the file
                        if isinstance(raw, (bytes, bytearray)):
                            with open(dest_path, "wb") as fd:
                                fd.write(raw)
                        else:
                            with open(dest_path, "w", encoding='utf-8') as fd:
                                fd.write(raw)

                        # Compile .ts files to .qm files using lrelease
                        if langFile.endswith('.ts'):
                            try:
                                ts_full = dest_path
                                qm_full = os.path.splitext(ts_full)[0] + '.qm'
                                res = subprocess.run(["lrelease", ts_full], check=False, capture_output=True)
                                if res.returncode != 0:
                                    logging.warning(_("lrelease failed for {ts}: {err}").format(ts=ts_full, err=res.stderr.decode('utf-8', errors='ignore')))
                                else:
                                    if os.path.exists(qm_full):
                                        logging.info(_("Compiled {ts} -> {qm}").format(ts=ts_full, qm=qm_full))
                            except Exception as e:
                                logging.warning(_("Could not run lrelease to compile {ts}: {e}").format(ts=dest_path, e=e))
                except:
                    continue
        pass

    def loadTutorials(self):
        test_tutorials = []
        test_contents = os.listdir(Lib.TutorialUtils.get_module_basepath("TutorialMaker") + "/Testing/")
        for content in test_contents:
            if(".py" not in content):
                continue
            test_tutorials.append(content.replace(".py", ""))
        return test_tutorials

    @staticmethod
    def runTutorialTestCases(tutorial_name, callback=None):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """
        tPath = Lib.TutorialUtils.get_module_basepath("TutorialMaker") + f"/Testing/{tutorial_name}.py"
        SelfTestTutorialLayer.ParseTutorial(tPath)
        TutorialModule = importlib.import_module("Outputs.CurrentParsedTutorial")
        for className in TutorialModule.__dict__:
            if("Test" not in className or className == "ScriptedLoadableModuleTest"):
                continue
            testClass = getattr(TutorialModule, className)
            tutorial = testClass()
            SelfTestTutorialLayer.RunTutorial(tutorial, callback)
            return
        logging.error(_(f"No tests found in {tutorial_name}"))
        raise Exception(_("No Tests Found"))

#
# TutorialMakerTest
#
class TutorialMakerTest(ScriptedLoadableModuleTest): # noqa: F405
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()
        TutorialMakerLogic().loadTutorialsFromRepos()

        Lib.TutorialUtils.Util.verifyOutputFolders()

        slicer.util.mainWindow().resize(1920, 1080)

        appFont = slicer.app.font()
        appFont.setPointSize(14)
        slicer.app.setFont(appFont)

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        languages = ["en", "fr", "es", "pt_BR"]
        
        self.setUp()
        
        tutorials_failed = 0
        error_message = ""
        
        testingFolder = Lib.TutorialUtils.get_module_basepath("TutorialMaker") + "/Testing/"
        languages_dir = Lib.TutorialUtils.get_module_basepath("TutorialMaker") + "/Languages/"
        
        test_tutorials = [f for f in os.listdir(testingFolder) if f.endswith(".py")]
    
        for lang in languages:
            translators = []
            
            if lang != "en":
                lang_files = [f for f in os.listdir(languages_dir) if (f.endswith(f"_{lang}.qm") or f.endswith(f"-{lang.replace('_', '-')}.qm"))]
                
                for file in lang_files:
                    qm_path = os.path.join(languages_dir, file)
                    translator = qt.QTranslator()
                    if os.path.exists(qm_path) and translator.load(qm_path):
                        slicer.app.installTranslator(translator)
                        translators.append(translator)
                        
            slicer.app.processEvents()
            slicer.util.mainWindow().update()
                
            for unit_tutorials in test_tutorials:
                tutorial_name = unit_tutorials.replace(".py", "")
                try:
                    # Generate Screenshots and widget metadata
                    TutorialMakerLogic.runTutorialTestCases(tutorial_name)
                    # Paint Screenshots with annotations
                    #AnnotationPainter.ImageDrawer.StartPaint(Lib.TutorialUtils.get_module_basepath("TutorialMaker") + "/Outputs/Annotations/" + unit_tutorials + ".json")
                except Exception as e:
                    error_message += _("Tutorial Execution Failed: {tutorial_name} in {lang} - Error: {e}. \n").format(tutorial_name=tutorial_name, lang=lang, e=e)
                    tutorials_failed += 1
                finally:
                    self.delayDisplay(_("Tutorial Tested in {lang}").format(lang=lang))
            
            for translator in translators:
                slicer.app.removeTranslator(translator)
            
            slicer.app.processEvents()
            slicer.util.mainWindow().update()
        
        if tutorials_failed > 0:
            raise Exception(_("{tutorials_failed} tutorials failed to execute. Errors: {error_message}").format(tutorials_failed=tutorials_failed, error_message=error_message))