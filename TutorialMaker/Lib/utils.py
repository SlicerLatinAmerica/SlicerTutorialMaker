import slicer
import qt
import os


class util():

    def __init__(self) -> None:
        self.mainWindowWidget = Widget(slicer.util.mainWindow())

    __shortcutDict = {
        "Scene3D":
        "CentralWidget/CentralWidgetLayoutFrame/ThreeDWidget1",
        "SceneRed":
        "CentralWidget/CentralWidgetLayoutFrame/qMRMLSliceWidgetRed",
        "SceneYellow":
        "CentralWidget/CentralWidgetLayoutFrame/qMRMLSliceWidgetYellow",
        "SceneGreen":
        "CentralWidget/CentralWidgetLayoutFrame/qMRMLSliceWidgetGreen",
        "Module":
        "PanelDockWidget/dockWidgetContents/ModulePanel/ScrollArea/qt_scrollarea_viewport/scrollAreaWidgetContents",
    }

    def listOnScreenWidgets(self):
        print(self.mainWindowWidget.className, end=", ")
        print(self.mainWindowWidget.name)
        self.__listWidgetsRecursive(self.mainWindowWidget, 1)

    def __listWidgetsRecursive(self, widget, depth):
        children = widget.getChildren()
        for child in children:
            if child.name != "":
                print("\t" * depth, end="")
                print(child.className, end=", ")
                print(child.name)
                self.__listWidgetsRecursive(child, depth + 1)

    def getOnScreenWidgets(self, window=None):
        if window is None:
            window = self.mainWindowWidget
        window = Widget(window)
        widgets = self.__getWidgetsRecursive(window, 1)
        return widgets

    def __getWidgetsRecursive(self, widget, depth):
        widgets = []
        children = widget.getChildren()
        for child in children:
            widgets.append(child)
            widgets.extend(self.__getWidgetsRecursive(child, depth + 1))
        return widgets

    def getNamedWidget(self, path, widget=None):
        if path == "":
            return None
        if not widget:
            widget = self.mainWindowWidget
        widgetNames = path.split("/")
        fullPath = self.resolveWidgetShortcut(widgetNames[0])
        fullPath.extend(widgetNames[1:])
        for name in fullPath:
            currentWidget = widget.getNamedChild(name)
            if not currentWidget:
                temp = name.split(":", 1)
                if len(temp) < 2:
                    return None
                widgetList = self.getWidgetsByClassName(widget, temp[0])
                currentWidget = widgetList[int(temp[1])]
                if not currentWidget:
                    return None
            widget = currentWidget
        return widget

    def resolveWidgetShortcut(self, shortcut):
        if shortcut in self.__shortcutDict:
            return self.__shortcutDict[shortcut].split("/")
        return [shortcut]

    def getWidgetsByToolTip(self, parent, tooltip):
        widgets = []
        if not parent:
            parent = self.mainWindowWidget
        if tooltip == "":
            return widgets
        for child in parent.getChildren():
            if child.toolTip == tooltip:
                widgets.append(child)
        return widgets

    def getWidgetsByClassName(self, parent, className):
        widgets = []
        if not parent:
            parent = self.mainWindowWidget
        if className == "":
            return widgets
        for child in parent.getChildren():
            if child.className == className:
                widgets.append(child)
        return widgets

    def getUniqueWidgetPath(self, widget):
        path = widget.name
        currentWidget = widget
        if path == "":
            path = self.__generateClassName(widget)

        while True:
            currentWidget = currentWidget.parent()
            if not currentWidget:
                break
            if currentWidget.name != "":
                path = currentWidget.name + "/" + path
            else:
                className = self.__generateClassName(currentWidget)
                path = className + "/" + path
        return path

    def __generateClassName(self, widget):
        className = widget.className
        siblings = self.getWidgetsByClassName(widget.parent(), className)
        index = 0
        for sibling in siblings:
            if (id(widget.inner()) == id(sibling.inner())
                    and widget.text == sibling.text):
                break
            index += 1
        name = f"{className}:{index}"
        if index + 1 > len(siblings):
            name = "?"
        return name

    def verifyOutputFolders(self):
        basePath = (os.path.dirname(slicer.util.modulePath("TutorialMaker")) +
                    "/Outputs/")
        if not os.path.exists(basePath):
            os.mkdir(basePath)
            os.mkdir(basePath + "Raw")
            os.mkdir(basePath + "Annotations")
            os.mkdir(basePath + "Translation")

        testingFolder = (
            os.path.dirname(slicer.util.modulePath("TutorialMaker")) +
            "/Testing/")
        if not os.path.exists(testingFolder):
            os.mkdir(testingFolder)

    @staticmethod
    def mapValueRange(
        value: float,
        inputMin: float,
        inputMax: float,
        outputMin: float,
        outputMax: float,
    ) -> float:
        return (value - inputMin) / (inputMax - inputMin) * (
            outputMax - outputMin) + outputMin


class WidgetFinder(qt.QWidget):

    def __init__(self, parent=None):
        super().__init__(None)
        self.setAttribute(qt.Qt.WA_StyledBackground)
        self.setStyleSheet(
            "QWidget { background-color: rgba(153, 51, 153, 50)}")
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
            self.shortcut.connect("activated()", self.showFullSize)

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
        # we need to work on this
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
        pen.setColor(qt.QColor(255, 0, 0))

        pos = widget.mapToGlobal(qt.QPoint())
        pos = self.parent().mapFromGlobal(pos)
        painter = qt.QPainter(self)
        painter.setPen(pen)
        painter.drawEllipse(
            pos.x() - (200 / 2) + widget.rect.width() / 2,
            pos.y() - (200 / 2) + widget.rect.height() / 2,
            200,
            200,
        )


class Widget:

    def __init__(self, widgetData) -> None:
        self.__widgetData = widgetData
        self.name = widgetData.name
        self.className = widgetData.className()
        if not hasattr(self.__widgetData, "toolTip"):
            self.toolTip = "None"
        else:
            self.toolTip = widgetData.toolTip
        if not hasattr(self.__widgetData, "text"):
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
        string += "\tAction:    " + str(self.actions) + "\n"
        string += "\tPath:      " + util().uniqueWidgetPath(self)
        return string

    def __dict__(self):
        dict = {
            "name": self.name,
            "text": self.text,
            "toolTip": self.toolTip,
            "className": self.className,
            "id": hex(id(self.__widgetData)),
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
        if not hasattr(self.__widgetData, "children"):
            return None
        for child in self.__widgetData.children():
            if child.name == childName:
                return Widget(child)
        return None

    def getChildren(self):
        children = []
        if not hasattr(self.__widgetData, "children"):
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
        slicer.app.processEvents(qt.QEventLoop.AllEvents, 70)
        return result

    def getGlobalPos(self):
        mw = slicer.util.mainWindow()
        windowPos = mw.mapToGlobal(mw.rect.topLeft())

        globalPosTopLeft = self.__widgetData.mapToGlobal(
            self.__widgetData.rect.topLeft())
        return [
            globalPosTopLeft.x() - windowPos.x(),
            globalPosTopLeft.y() - windowPos.y(),
        ]

    def getSize(self):
        posTopLeft = self.__widgetData.rect.topLeft()
        posBotRight = self.__widgetData.rect.bottomRight()
        return [
            posBotRight.x() - posTopLeft.x(),
            posBotRight.y() - posTopLeft.y()
        ]

    def __listWidgetAsChildren(self):
        from types import SimpleNamespace

        virtualChildren = []
        for ItemIndex in range(self.__widgetData.count):
            item = self.__widgetData.item(ItemIndex)
            __itemData = SimpleNamespace(
                name=f"XlistWidgetItem_{ItemIndex}",
                className=lambda: "XlistWidgetItem",
                text=item.text(),
                mapToGlobal=self.__widgetData.mapToGlobal,
                rect=self.__widgetData.visualItemRect(item),
                parent=lambda: self.__widgetData,
                isVisible=self.__widgetData.isVisible,
            )
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
                    if (_node.child(xIndex, yIndex) is None
                            or not _node.child(xIndex, yIndex).isValid()):
                        break
                    while True:
                        if (_node.child(xIndex, yIndex) is None
                                or not _node.child(xIndex, yIndex).isValid()):
                            break
                        nodeTreeTraverser(_node.child(xIndex, yIndex))
                        yIndex += 1
                    xIndex += 1

            # Create fake widgets to represent the nodes in the list
            _fRect = self.__widgetData.visualRect(_node)
            if _fRect.size().height() == 0 or _fRect.size().width() == 0:
                return

            _fText = ""
            if _node.data(0) is not None:
                _fText = _node.data(0)

            __itemData = SimpleNamespace(
                name=f"XtreeViewWidget_{NodeIndex}",
                className=lambda: "XtreeViewWidget",
                text=_fText,
                mapToGlobal=self.__widgetData.viewport().mapToGlobal,
                rect=_fRect,
                parent=lambda: self.__widgetData,
                isVisible=self.__widgetData.isVisible,
            )
            virtualChildren.append(Widget(__itemData))

            NodeIndex += 1

        nodeTreeTraverser(model.index(0, 0))

        return virtualChildren


class SignalManager(qt.QObject):
    received = qt.Signal(object)

    def __init__(self):
        super().__init__(None)

    def connect(self, func):
        self.received.connect(func)

    def emit(self, msg):
        self.received.emit(msg)


class ScreenshotTools:

    def __init__(self) -> None:
        self.handler = JSONHandler()
        pass

    def saveScreenshotMetadata(self, index):
        path = (os.path.dirname(slicer.util.modulePath("TutorialMaker")) +
                "/Outputs/Raw/")

        openWindows = []
        for w in slicer.app.topLevelWidgets():
            if hasattr(w, "isVisible") and not w.isVisible():
                continue
            if w.objectName == "qSlicerMainWindow":
                openWindows.insert(0, w)
            else:
                openWindows.append(w)
            pass

        windows = []
        for wIndex in range(len(openWindows)):
            if not os.path.exists(path + str(index)):
                os.mkdir(path + str(index))
                pass

            screenshotData = TutorialScreenshot()
            screenshotData.screenshot = path + str(index) + "/" + str(
                wIndex) + ".png"
            screenshotData.metadata = path + str(index) + "/" + str(
                wIndex) + ".json"

            self.saveScreenshot(screenshotData.screenshot, openWindows[wIndex])
            self.saveAllWidgetsData(screenshotData.metadata,
                                    openWindows[wIndex])

            windows.append(screenshotData)
            pass
        pass
        return windows

    def getPixmap(self, window):
        slicer.app.processEvents(qt.QEventLoop.AllEvents, 69)
        pixmap = window.grab()
        return pixmap

    def saveScreenshot(self, filename, window):
        self.getPixmap(window).save(filename, "PNG")
        pass

    def saveAllWidgetsData(self, filename, window):
        tool = util()
        data = {}
        widgets = tool.getOnScreenWidgets(window)
        for index in range(len(widgets)):
            try:
                if (hasattr(widgets[index].inner(), "isVisible")
                        and not widgets[index].inner().isVisible()):
                    continue
                data[index] = {
                    "name": widgets[index].name,
                    "path": tool.uniqueWidgetPath(widgets[index]),
                    "text": widgets[index].text,
                    "position": widgets[index].getGlobalPos(),
                    "size": widgets[index].getSize(),
                }
                pass
            except AttributeError:
                # Working as expected, so to not save QObjects that are not QWidgets
                pass
            except Exception as e:
                print(e)
                pass
        self.handler.saveScreenshotMetadata(data, filename)


class Tutorial:

    def __init__(self, title, author, date, description):
        self.metadata = {}
        self.metadata["title"] = title
        self.metadata["author"] = author
        self.metadata["date"] = date
        self.metadata["desc"] = description

        self.steps = []

    def beginTutorial(self):
        screenshotTools = ScreenshotTools()
        # Screenshot counter
        self.nSteps = 0
        self.screenshottools = screenshotTools

    # TODO:Unsafe, there should be a better method to do this, at least add some conditions
    def clearTutorial(self):
        outputPath = (
            os.path.dirname(slicer.util.modulePath("TutorialMaker")) +
            "/Outputs/Raw/")
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
            self.steps.append(
                self.screenshottools.saveScreenshotMetadata(overwriteName))
            self.nSteps = self.nSteps + 1
            return
        self.steps.append(
            self.screenshottools.saveScreenshotMetadata(self.nSteps))
        self.nSteps = self.nSteps + 1

    pass

    def endTutorial(self):
        handler = JSONHandler()
        handler.saveTutorial(self.metadata, self.steps)


class TutorialScreenshot:

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


class JSONHandler:

    def __init__(self):
        self.path = (os.path.dirname(slicer.util.modulePath("TutorialMaker")) +
                     "/Outputs/Raw/")
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        import json

        self.json = json
        pass

    def parseTutorial(self, inline=False):
        with open(self.path + "Tutorial.json", encoding="utf-8") as f:
            tutorialData = self.json.load(f)
        tutorial = Tutorial(
            tutorialData["title"],
            tutorialData["author"],
            tutorialData["date"],
            tutorialData["desc"],
        )
        if inline:
            stepList = []
            tutorial.steps = stepList
            for step in tutorialData["steps"]:
                for window in step:
                    wScreenshot = TutorialScreenshot(
                        self.path + window["window"],
                        self.path + window["metadata"])
                    tutorial.steps.append(wScreenshot)
            return tutorial
        # TODO: Non inline parser
        return tutorial

    def parseJSON(path):
        import json

        with open(path, encoding="utf-8") as file:
            data = json.load(file)
        return data

    def saveTutorial(self, metadata, stepsList):
        metadata["steps"] = []
        for step in stepsList:
            windows = []
            for screenshot in step:
                datapair = {}
                datapair["window"] = screenshot.screenshot.replace(
                    self.path, "")
                datapair["metadata"] = screenshot.metadata.replace(
                    self.path, "")
                windows.append(datapair)
            pass
            metadata["steps"].append(windows)
        with open(self.path + "Tutorial.json", "w", encoding="utf-8") as f:
            self.json.dump(metadata, f, ensure_ascii=False, indent=4)
        pass

    def saveScreenshotMetadata(self, data, path):
        with open(path, "w", encoding="utf-8") as f:
            self.json.dump(data, f, ensure_ascii=False, indent=4)
        pass
