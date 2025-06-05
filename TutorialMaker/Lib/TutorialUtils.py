import slicer
import qt
import os
import re
import copy

class Widget():
    def __init__(self, widgetData) -> None:
        self.__widgetData = widgetData
        self.name = widgetData.name
        self.className = widgetData.className()
        if not hasattr(self.__widgetData, 'toolTip'):
            self.toolTip = "None"
        else:
            self.toolTip = widgetData.toolTip
        if not hasattr(self.__widgetData, 'text'):
            self.text = "None"
        else:
            self.text = widgetData.text
        pass
        if not hasattr(self.__widgetData, "actions"):
            self.actions = []
        else:
            self.actions = self.__widgetData.actions()

    def __str__(self):
        string = "Widget:\n"
        string += "\tName:      " + self.name + "\n"
        string += "\tText:      " + self.text + "\n"
        string += "\tToolTip:   " + self.toolTip + "\n"
        string += "\tClassName: " + self.className + "\n"
        string += "\tID:        " + hex(id(self.__widgetData)) + "\n"
        string += "\tAction:    " + str(self.actions)+ "\n"
        string += "\tPath:      " + Util.uniqueWidgetPath(self)
        return string

    def __dict__(self):
        dict = {
            "name": self.name,
            "text": self.text,
            "toolTip": self.toolTip,
            "className": self.className,
            "id": hex(id(self.__widgetData))
        }
        return dict

    def inner(self):
        return self.__widgetData

    def parent(self):
        parent = self.__widgetData.parent()
        if not parent:
            return None
        return Widget(parent)

    def getNamedChild(self, childName):
        if not hasattr(self.__widgetData, 'children'):
            return None
        for child in self.__widgetData.children():
            if child.name == childName:
                return Widget(child)
        return None

    def getChildren(self):
        children = []
        if not hasattr(self.__widgetData, 'children'):
            return children
        for child in self.__widgetData.children():
            children.append(Widget(child))
        if self.className == "QListWidget":
            children.extend(self.__listWidgetAsChildren())
        elif self.className == "qMRMLSubjectHierarchyTreeView":
            children.extend(self.__MRMLTreeViewAsChildren())
        return children

    def childrenDetails(self):
        children = self.getChildren()
        for child in children:
            print(child)

    def click(self):
        result = self.__widgetData.click()
        self.__widgetData.update()
        #slicer.app.processEvents(qt.QEventLoop.AllEvents, 70)
        return result

    def getGlobalPos(self):
        mw = slicer.util.mainWindow()
        windowPos = mw.mapToGlobal(mw.rect.topLeft())

        globalPosTopLeft = self.__widgetData.mapToGlobal(self.__widgetData.rect.topLeft())
        return [(globalPosTopLeft.x() - windowPos.x())*slicer.app.desktop().devicePixelRatioF(), (globalPosTopLeft.y() - windowPos.y())*slicer.app.desktop().devicePixelRatioF()]

    def getSize(self):
        posTopLeft = self.__widgetData.rect.topLeft()
        posBotRight = self.__widgetData.rect.bottomRight()
        return [(posBotRight.x() - posTopLeft.x())*slicer.app.desktop().devicePixelRatioF(), (posBotRight.y() - posTopLeft.y())*slicer.app.desktop().devicePixelRatioF()]

    def __listWidgetAsChildren(self):
        from types import SimpleNamespace
        virtualChildren = []
        for ItemIndex in range(self.__widgetData.count):
            item = self.__widgetData.item(ItemIndex)
            __itemData = SimpleNamespace(name= f"XlistWidgetItem_{ItemIndex}",
            className= lambda:"XlistWidgetItem",
            text= item.text(),
            mapToGlobal= self.__widgetData.mapToGlobal,
            rect= self.__widgetData.visualItemRect(item),
            parent=lambda: self.__widgetData,
            isVisible= self.__widgetData.isVisible)
            virtualChildren.append(Widget(__itemData))
        return virtualChildren

    def __MRMLTreeViewAsChildren(self):
        from types import SimpleNamespace
        virtualChildren = []
        model = None
        if self.__widgetData.sortFilterProxyModel() is not None:
            model = self.__widgetData.sortFilterProxyModel()
        else:
            model = self.__widgetData.model()
        if model is None:
            return virtualChildren

        NodeIndex = 0
        def nodeTreeTraverser(_node):
            nonlocal NodeIndex
            if hasattr(_node, "child"):
                xIndex = 0
                while True:
                    yIndex = 0
                    if _node.child(xIndex, yIndex) is None or not _node.child(xIndex, yIndex).isValid():
                        break
                    while True:
                        if _node.child(xIndex, yIndex) is None or not _node.child(xIndex, yIndex).isValid():
                            break
                        nodeTreeTraverser(_node.child(xIndex, yIndex))
                        yIndex += 1
                    xIndex += 1

            #Create fake widgets to represent the nodes in the list
            _fRect = self.__widgetData.visualRect(_node)
            if (_fRect.size().height() == 0 or _fRect.size().width() == 0):
                return

            _fText = ""
            if _node.data(0) is not None:
                _fText = _node.data(0)

            __itemData = SimpleNamespace(name= f"XtreeViewWidget_{NodeIndex}",
            className= lambda:"XtreeViewWidget",
            text= _fText,
            mapToGlobal= self.__widgetData.viewport().mapToGlobal,
            rect= _fRect,
            parent=lambda: self.__widgetData,
            isVisible= self.__widgetData.isVisible)
            virtualChildren.append(Widget(__itemData))

            NodeIndex += 1

        nodeTreeTraverser(model.index(0,0))

        return virtualChildren

class Util():
    mw = Widget(slicer.util.mainWindow())

    __shortcutDict = {
        "Scene3D"     : "CentralWidget/CentralWidgetLayoutFrame/ThreeDWidget1",
        "SceneRed"    : "CentralWidget/CentralWidgetLayoutFrame/qMRMLSliceWidgetRed",
        "SceneYellow" : "CentralWidget/CentralWidgetLayoutFrame/qMRMLSliceWidgetYellow",
        "SceneGreen"  : "CentralWidget/CentralWidgetLayoutFrame/qMRMLSliceWidgetGreen",
        "Module"      : "PanelDockWidget/dockWidgetContents/ModulePanel/ScrollArea/qt_scrollarea_viewport/scrollAreaWidgetContents"
    }
    
    @staticmethod
    def listOnScreenWidgets():
        print(Util.mw.className, end=", ")
        print(Util.mw.name)
        Util.__listWidgetsRecursive(Util.mw, 1)

    @staticmethod
    def __listWidgetsRecursive(widget, depth):
        children = widget.getChildren()
        for child in children:
            if child.name != "":
                for i in range(depth):
                    print("\t", end="")
                print(child.className, end=", ")
                print(child.name)
                Util.__listWidgetsRecursive(child, depth + 1)

    @staticmethod
    def getOnScreenWidgets(window=None):
        if window is None:
            window = Util.mw
        window = Widget(window)
        return Util.__getWidgetsRecursive(window, 1)

    @staticmethod
    def __getWidgetsRecursive(widget, depth):
        widgets = []
        children = widget.getChildren()
        for child in children:
            widgets.append(child)
            widgets = widgets + Util.__getWidgetsRecursive(child, depth + 1)
        return widgets

    @staticmethod
    def getNamedWidget(path, widget=None):
        if path == "":
            return
        if not widget:
            widget = Util.mw
        wNames = path.split("/")
        extendedPath = Util.widgetShortcuts(wNames[0])
        extendedPath.extend(wNames[1:])
        for name in extendedPath:
            _widget = widget.getNamedChild(name)
            if not _widget:
                temp = name.split(":", 1)
                if len(temp) < 2:
                    return None
                wList = Util.getWidgetsByClassName(widget, temp[0])
                _widget = wList[int(temp[1])]
                if not _widget:
                    return None
            widget = _widget
        return widget

    @staticmethod
    def widgetShortcuts(shortcut):
        if shortcut in Util.__shortcutDict.keys():
            return Util.__shortcutDict[shortcut].split("/")
        else:
            return [shortcut]

    @staticmethod
    def getWidgetsByToolTip(parent, tooltip):
        widgets = []
        if not parent:
            parent = Util.mw
        if tooltip == "":
            return widgets
        for child in parent.getChildren():
            if child.toolTip == tooltip:
                widgets.append(child)
        return widgets

    @staticmethod
    def getWidgetsByClassName(parent, classname):
        widgets = []
        if not parent:
            parent = Util.mw
        if classname == "":
            return widgets
        for child in parent.getChildren():
            if child.className == classname:
                widgets.append(child)
        return widgets

    @staticmethod
    def uniqueWidgetPath(widgetToID):
        path = widgetToID.name
        parent = widgetToID
        if path == "":
            path = Util.__classtoname(widgetToID)
            pass
     
        while(True):
            parent = parent.parent()
            if not parent:
                break
            if parent.name != "":
                path = parent.name + "/" + path
            else:
                _name = Util.__classtoname(parent)
                path = _name + "/" + path
                pass
        return path

    @staticmethod
    def __classtoname(widget):
        classname = widget.className
        _widgets = Util.getWidgetsByClassName(widget.parent(), classname)
        index = 0
        for _w in _widgets:
            if id(widget.inner()) == id(_w.inner()) and widget.text == _w.text:
                break
            pass
            index += 1
        name = classname + ":" + str(index)
        if index + 1 > len(_widgets):
            name = "?"
        return name

    @staticmethod
    def verifyOutputFolders():
        basePath = os.path.dirname(slicer.util.modulePath("TutorialMaker")) + "/Outputs/"
        if not os.path.exists(basePath):
            os.mkdir(basePath)
            os.mkdir(basePath + "Raw")
            os.mkdir(basePath + "Annotations")
            os.mkdir(basePath + "Translation")

        # Verify if Testing folder exists
        testingFolder = os.path.dirname(slicer.util.modulePath("TutorialMaker")) + "/Testing/"
        # Check if testing folder exists
        if not os.path.exists(testingFolder):
            os.mkdir(testingFolder)

    @staticmethod
    def mapFromTo(value : float, inputMin : float, inputMax : float, outputMin : float, outputMax : float) -> float:
        result=(value-inputMin)/(inputMax-inputMin)*(outputMax-outputMin)+outputMin
        return result

class WidgetFinder(qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(None)
        self.setAttribute(qt.Qt.WA_StyledBackground)
        self.setStyleSheet("QWidget { background-color: rgba(153, 51, 153, 50)}")
        self.focusPolicy = qt.Qt.StrongFocus
        self.LanguageToolsLogic = None
        self.shortcutKeySequence = qt.QKeySequence("Ctrl+6")
        self.shortcut = None
        self.logic = None
        self.cursorOverridden = False
        self.currentWidget = None
        self.sinalManager = SignalManager()
        self.aux = parent

    def __del__(self):
        self.showPointCursor(False)

    def enableShortcut(self, enable):
        if (self.shortcut is not None) == enable:
            return
        if self.shortcut:
            self.shortcut.disconnect("activated()")
            self.shortcut.setParent(None)
            self.shortcut.deleteLater()
            self.shortcut = None
            self.hideOverlay()
        else:
            self.shortcut = qt.QShortcut(self.parent())
            self.shortcut.setKey(self.shortcutKeySequence)
            self.shortcut.connect( "activated()", self.showFullSize)

    def showPointCursor(self, enable):
        if enable == self.cursorOverridden:
            return
        if enable:
            slicer.app.setOverrideCursor(qt.Qt.PointingHandCursor)
        else:
            slicer.app.restoreOverrideCursor()
        self.cursorOverridden = enable

    def showFullSize(self):
        self.pos = qt.QPoint()
        self.setFixedSize(self.aux.size)
        self.setWindowOpacity(0.2)
        self.show()
        self.setFocus(qt.Qt.ActiveWindowFocusReason)
        self.showPointCursor(True)

    def overlayOnWidget(self, widget):
        pos = widget.mapToGlobal(qt.QPoint())
        pos = self.aux.mapFromGlobal(pos)
        self.pos = pos
        self.setFixedSize(widget.size)

    def hideOverlay(self):
        self.hide()
        self.showPointCursor(False)

    def widgetAtPos(self, pos):
        self.setAttribute(qt.Qt.WA_TransparentForMouseEvents)
        widget = qt.QApplication.widgetAt(pos)
        self.setAttribute(qt.Qt.WA_TransparentForMouseEvents, False)
        return widget

    def keyPressEvent(self, event):
        self.hideOverlay()

    def mousePressEvent(self, event):
        pos = qt.QCursor().pos()
        widget = self.widgetAtPos(pos)
        self.overlayOnWidget(widget)
        self.hideOverlay()
        self.showPointCursor(False)
        self.sinalManager.emit(Widget(widget))

        self.currentWidget = widget

    def paintEvent(self, event):
        #we need to work on this
        self.setFixedSize(self.aux.size)
        self.pos = self.aux.pos

class Shapes(qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.focusPolicy = qt.Qt.StrongFocus
        self.setAttribute(qt.Qt.WA_TransparentForMouseEvents)
        self.widget = None

    def setTargetWidget(self, widget):
        if widget is None:
            return

        self.widget = widget
        self.setFixedSize(widget.size)
        self.showFullSize()

    def showFullSize(self):
        self.pos = qt.QPoint()
        self.setFixedSize(self.parent().size)
        self.show()
        self.setFocus(qt.Qt.ActiveWindowFocusReason)

    def hideOverlay(self):
        self.hide()

    def paintEvent(self, event):
        if self.widget is None:
            return

        self.setFixedSize(self.parent().size)
        widget = self.widget

        pen = qt.QPen()
        pen.setWidth(20)
        pen.setColor(qt.QColor(255,0,0))

        pos = widget.mapToGlobal(qt.QPoint())
        pos = self.parent().mapFromGlobal(pos)
        painter = qt.QPainter(self)
        painter.setPen(pen)
        painter.drawEllipse(pos.x() - (200/2) + widget.rect.width()/2, pos.y() - (200/2) + widget.rect.height()/2, 200, 200)

class SelfTestTutorialLayer():

    directives = {
        "id" : "TUTORIALMAKER",
        "begin" : "BEGIN",
        "end" : "END",
        "metadata" : "INFO",
        "metadata_title" : "TITLE",
        "metadata_author" : "AUTHOR",
        "metadata_date" : "DATE",
        "metadata_desc" : "DESC",
        "takeScreenshot" : "SCREENSHOT",
    }

    @staticmethod
    def ParseTutorial(path):
        if path == "" or path == None:
            raise Exception()

        counter = NextCounter()

        code_contents = ""
        with open(path) as fd:
            code_contents = fd.read()

        # GENERATE FUNCTIONS FOR EACH TUTORIAL DIRECTIVE
        _tutorialBeginString = f"# {SelfTestTutorialLayer.directives['id']} {SelfTestTutorialLayer.directives['begin']}"
        _tutorialEndString = f"# {SelfTestTutorialLayer.directives['id']} {SelfTestTutorialLayer.directives['end']}"
        _tutorialTakeScreenshot = f"# {SelfTestTutorialLayer.directives['id']} {SelfTestTutorialLayer.directives['takeScreenshot']}"

        tutorialMatcher = rf"(?s)(?<={_tutorialBeginString}).*?(?={_tutorialEndString})"
        functionMatcher = rf"(?s).+?(?={_tutorialTakeScreenshot})"
        infoMatcher = rf"(?m)(?<=# {SelfTestTutorialLayer.directives['id']} {SelfTestTutorialLayer.directives['metadata']} )([A-z]+)( )(.*)\n"

        tutorial_tests = []
        for test_module in re.findall(tutorialMatcher, code_contents):
            tutorial_title = ""
            tutorial_author = ""
            tutorial_date = ""
            tutorial_desc = ""

            for info in re.findall(infoMatcher, test_module):
                if info[0] == SelfTestTutorialLayer.directives['metadata_title']:
                    tutorial_title = info[2]
                    pass
                elif info[0] == SelfTestTutorialLayer.directives['metadata_author']:
                    tutorial_author = info[2]
                    pass
                elif info[0] == SelfTestTutorialLayer.directives['metadata_date']:
                    tutorial_date = info[2]
                    pass
                elif info[0] == SelfTestTutorialLayer.directives['metadata_desc']:
                    tutorial_desc = info[2]
                    pass
            
            info_func = (
                "\n"
                f"{' '*8}def TUTORIAL_GETINFO():\n"
                f"{' '*12}return ['{tutorial_title}','{tutorial_author}', '{tutorial_date}', '{tutorial_desc}']\n"
            )
            
            tutorial_functions = []
            for idx, test_function in enumerate(re.findall(functionMatcher, test_module)):
                _functionSignature = f"def TUTORIAL_SCREENSHOT_{idx}(_locals):\n"
                lines = test_function.split("\n")
                _indentation = lines[0].count(" ") # THIS DOESN'T WORK
                _indentation = 8 #TODO: NEED TO FIND A FAST WAY TO GET THIS DINAMICALLY
                lines[0] = ""
                _newFunction = "\n" + " "*_indentation + _functionSignature
                _newFunction += " "*(_indentation + 4) + "globals().update(_locals)\n"

                for line in lines:
                    _newFunction += " "*4 + line + "\n"
                
                _newFunction += " "*(_indentation + 4) + "_locals.update(locals())\n"

                tutorial_functions.append(_newFunction)
                pass
            tutorial_functions[0] = info_func + tutorial_functions[0]
            tutorial_functions[len(tutorial_functions) - 1] = tutorial_functions[len(tutorial_functions) - 1] + f"{' '*8}return locals()\n"
            counter.count = 0
            tutorial_tests.append(re.sub(functionMatcher, lambda match : tutorial_functions[counter.next()], test_module))
        counter.count = 0
        finalFile = re.sub(tutorialMatcher, lambda match : tutorial_tests[counter.next()], code_contents)

        path = os.path.dirname(slicer.util.modulePath("TutorialMaker")) + "/Outputs/"

        with open(path + "CurrentParsedTutorial.py", "w") as fd:
            fd .write(finalFile)
        pass

    @staticmethod
    def ScreenshotCallable(tutorial, callback, _locals):
        callback(_locals)
        tutorial.nextScreenshot()
        

    @staticmethod
    def RunTutorial(tutorialClass, callback = None):
        import inspect
        import functools

        tutorialSource = inspect.getsource(tutorialClass.runTest)
        funcMatcher = rf"(?m)(?<=self\.).+(?=\()"
        functionIndex = 0
        for funcName in re.findall(funcMatcher, tutorialSource):
            func = getattr(tutorialClass, funcName)
            _locals = func()
            if _locals is None:
                continue
            if not type(_locals) == dict:
                continue
            if _locals["TUTORIAL_GETINFO"] is not None:
                info = _locals["TUTORIAL_GETINFO"]()
                tutorial = Tutorial(*info)
                tutorial.clearTutorial()
                tutorial.beginTutorial()
                while True:
                    try:
                        timerCallback = functools.partial(SelfTestTutorialLayer.ScreenshotCallable, tutorial, _locals[f"TUTORIAL_SCREENSHOT_{functionIndex}"], _locals)
                        qt.QTimer.singleShot(2000*functionIndex, timerCallback)
                        functionIndex += 1
                    except Exception as e:
                        break
                qt.QTimer.singleShot(2000*functionIndex, tutorial.endTutorial)
        # This needs to happen only after every possible tutorial is ran
        if callback is not None:
            qt.QTimer.singleShot(2000*(functionIndex + 1), callback)

class NextCounter():
    def __init__(self, count=0):
        self.count = count
    def next(self):
        self.count += 1
        return self.count - 1

class SignalManager(qt.QObject):
    received = qt.Signal(object)
    def __init__(self):
        super().__init__(None)

    def connect(self,func):
        self.received.connect(func)

    def emit(self, msg):
        self.received.emit(msg)

class ScreenshotTools():
    def __init__(self) -> None:
        self.handler = JSONHandler()
        pass

    def saveScreenshotMetadata(self, index):
        path = os.path.dirname(slicer.util.modulePath("TutorialMaker")) + "/Outputs/Raw/"

        openWindows = []
        for w in slicer.app.topLevelWidgets():
            if hasattr(w, "isVisible") and not w.isVisible():
                continue
            if w.objectName == "qSlicerMainWindow":
                openWindows.insert(0,w)
            else:
                openWindows.append(w)
            pass

        windows = []
        for wIndex in range(len(openWindows)):
            if not os.path.exists(path + str(index)):
                os.mkdir(path + str(index))
                pass

            screenshotData = TutorialScreenshot()
            screenshotData.screenshot = path + str(index) + "/" + str(wIndex) + ".png"
            screenshotData.metadata = path + str(index) + "/" + str(wIndex) + ".json"

            self.saveScreenshot(screenshotData.screenshot, openWindows[wIndex])
            self.saveAllWidgetsData(screenshotData.metadata, openWindows[wIndex])

            windows.append(screenshotData)
            pass
        pass
        return windows

    def getPixmap(self, window):
        #slicer.app.processEvents(qt.QEventLoop.AllEvents, 70)
        pixmap = window.grab()
        return pixmap

    def saveScreenshot(self, filename, window):
        self.getPixmap(window).save(filename, "PNG")
        pass

    def saveAllWidgetsData(self, filename, window):
        data = {}
        widgets = Util.getOnScreenWidgets(window)
        for index in range(len(widgets)):
            try:
                if hasattr(widgets[index].inner(), "isVisible") and not widgets[index].inner().isVisible():
                    continue
                data[index] = {"name": widgets[index].name, "path": tool.uniqueWidgetPath(widgets[index]), "text": widgets[index].text, "position": widgets[index].getGlobalPos(), "size": widgets[index].getSize()}
                pass
            except AttributeError:
                #Working as expected, so to not save QObjects that are not QWidgets
                pass
            except Exception as e:
                print(e)
                pass
        self.handler.saveScreenshotMetadata(data, filename)

class Tutorial():
    def __init__(self,
            title,
            author,
            date,
            description
    ):
        self.metadata = {}
        self.metadata["title"] = title
        self.metadata["author"] = author
        self.metadata["date"] = date
        self.metadata["desc"] = description

        self.steps = []

    def beginTutorial(self):
        screenshotTools = ScreenshotTools()
        #Screenshot counter
        self.nSteps = 0
        self.screenshottools = screenshotTools

    #TODO:Unsafe, there should be a better method to do this, at least add some conditions
    def clearTutorial(self):
        outputPath = os.path.dirname(slicer.util.modulePath("TutorialMaker")) + "/Outputs/Raw/"
        if not os.path.exists(outputPath):
            return
        dirs = os.listdir(outputPath)
        for dir in dirs:
            if os.path.isdir(outputPath + dir):
                for sdir in os.listdir(outputPath + dir):
                    os.remove(outputPath + "/" + dir + "/" + sdir)
                os.rmdir(outputPath + dir)
            else:
                os.remove(outputPath + dir)
        pass

    def nextScreenshot(self, overwriteName=None):
        if type(overwriteName) is str:
            self.steps.append(self.screenshottools.saveScreenshotMetadata(overwriteName))
            self.nSteps = self.nSteps + 1
            return
        self.steps.append(self.screenshottools.saveScreenshotMetadata(self.nSteps))
        self.nSteps = self.nSteps + 1
    pass

    def endTutorial(self):
        handler = JSONHandler()
        handler.saveTutorial(self.metadata, self.steps)

class TutorialScreenshot():
    def __init__(self, screenshot="", metadata=""):
        self.screenshot = screenshot
        self.metadata = metadata
        pass

    def getImage(self):
        image = qt.QImage(self.screenshot)
        return qt.QPixmap.fromImage(image)
    def getWidgets(self):
        widgets = []
        nWidgets = JSONHandler.parseJSON(self.metadata)
        for keys in nWidgets:
            widgets.append(nWidgets[keys])
        return widgets

# TODO: REMOVE THIS, DEPRECATED
class JSONHandler:
    def __init__(self):
        self.path = os.path.dirname(slicer.util.modulePath("TutorialMaker")) + "/Outputs/Raw/"
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        import json
        self.json = json
        pass

    def parseTutorial(self, inline=False):
        with open(self.path + "Tutorial.json", encoding='utf-8') as f:
            tutorialData = self.json.load(f)
        tutorial = Tutorial(
            tutorialData["title"],
            tutorialData["author"],
            tutorialData["date"],
            tutorialData["desc"]
        )
        if inline:
            stepList = []
            tutorial.steps = stepList
            for step in tutorialData["steps"]:
                for window in step:
                    wScreenshot = TutorialScreenshot(
                        self.path + window["window"],
                        self.path + window["metadata"]
                    )
                    tutorial.steps.append(wScreenshot)
            return tutorial
        #TODO: Non inline parser
        return tutorial

    def parseJSON(path):
        import json
        with open(path, encoding='utf-8') as file:
            data = json.load(file)
        return data


    def saveTutorial(self, metadata, stepsList):
        metadata["steps"] = []
        for step in stepsList:
            windows = []
            for screenshot in step:
                datapair = {}
                datapair["window"] = screenshot.screenshot.replace(self.path, "")
                datapair["metadata"] = screenshot.metadata.replace(self.path, "")
                windows.append(datapair)
            pass
            metadata["steps"].append(windows)
        with open(self.path + "Tutorial.json", 'w', encoding='utf-8') as f:
            self.json.dump(metadata, f, ensure_ascii=False, indent=4)
        pass

    def saveScreenshotMetadata(self, data, path):
        with open(path, 'w', encoding='utf-8') as f:
            self.json.dump(data, f, ensure_ascii=False, indent=4)
        pass
