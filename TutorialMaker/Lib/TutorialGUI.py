import slicer
import qt
import json
import os
import copy
from Lib.Annotations import Annotation, AnnotationType, AnnotatorSlide
from Lib.TutorialUtils import Tutorial, TutorialScreenshot
from slicer.i18n import tr as _

class DraggableLabel(qt.QLabel):
    def __init__(self, text="",parent=None):
        super().__init__(text, parent)

    def GetCenter(self):
        pos = self.pos
        x = pos.x()
        y = pos.y()
        size = self.size
        width = size.width()
        height = size.height()

        return [x + width/2, y + height/2]

    def SetCenter(self, x : int, y : int):
        size = self.size
        width = size.width()
        height = size.height()

        self.move(x - width/2, y - height/2)

    def SetActive(self, state : bool):
        #Did it explicit for clarity
        if state:
            self.show()
            self.setAttribute(qt.Qt.WA_TransparentForMouseEvents, False)
            pass
        else:
            self.hide()
            self.setAttribute(qt.Qt.WA_TransparentForMouseEvents)
            pass

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == qt.QEvent.MouseMove:
                if event.button() == 0: # Left Button pressed
                    sPos = event.screenPos().toPoint()
                    pos = self.parent().mapFromGlobal(sPos)
                    self.SetCenter(pos.x(), pos.y())

class tmLabel(qt.QLabel):
    clicked = qt.Signal()

    def __init__(self, text, index, parent=None):
        super().__init__(text, parent)
        self.index = index

    def mousePressEvent(self, event):
        self.clicked.emit()

class AnnotatorStepWidget(qt.QWidget):
    thumbnailClicked = qt.Signal(int, int)
    swapRequest = qt.Signal(int, int)

    def __init__(self, stepIndex : int, thumbnailSize, parent = None):
        super().__init__(parent)

        self.stepIndex = stepIndex
        self.screenshotCount = 0

        self.UNDELETABLE = False

        self.showingMerged = False
        self.mergedSlideIndex = 0

        self.thumbnailSize = thumbnailSize

        self.buttonSize = [24, 24]

        self.Slides = []
        self.SlideWidgets = []

        self.SetupGUI()

    def SetupGUI(self):
        self.stepLayout = qt.QGridLayout()
        self.setLayout(self.stepLayout)
        self.setAttribute(qt.Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: #9e9493;')
        self.setObjectName(f"label_step_{self.stepIndex}")

        #This can be done in a UI file

        self.expandButton = qt.QPushButton()
        self.slideUpButton = qt.QPushButton()
        self.slideDownButton = qt.QPushButton()

        self.expandButton.setParent(self)
        self.expandButton.setFixedSize(*self.buttonSize)
        self.expandButton.move(10, 10)
        self.expandButton.setCheckable(True)
        self.expandButton.setIcon(self.parent().icon_chevron)

        self.slideUpButton.setParent(self)
        self.slideUpButton.setFixedSize(*self.buttonSize)
        self.slideUpButton.move(self.thumbnailSize[0] - 50, 10)
        self.slideUpButton.setIcon(self.parent().icon_arrowUp)

        self.slideDownButton.setParent(self)
        self.slideDownButton.setFixedSize(*self.buttonSize)
        self.slideDownButton.move(self.thumbnailSize[0] - 20, 10)
        self.slideDownButton.setIcon(self.parent().icon_arrowDown)

        self.expandButton.clicked.connect(self.ToggleExtended)
        self.slideUpButton.clicked.connect(self.swapUp)
        self.slideDownButton.clicked.connect(self.swapDown)

        pass

    def AddStepWindows(self, annotatorSlide : AnnotatorSlide):
        screenshotWidget = tmLabel(f"label_window_{self.screenshotCount}", self.screenshotCount)
        screenshotWidget.setObjectName(f"label_window_{self.screenshotCount}")
        self.stepLayout.addWidget(screenshotWidget)
        self.SlideWidgets.append(screenshotWidget)

        self.Slides.append(annotatorSlide)
        screenshotWidget.setPixmap(annotatorSlide.GetResized(*self.thumbnailSize))
        screenshotWidget.clicked.connect(lambda screen= self.screenshotCount: self.thumbnailClick(screen))

        self.screenshotCount = self.screenshotCount + 1

        screenshotWidget.stackUnder(self.expandButton)
        pass

    def swapUp(self, state):
        self.swapRequest.emit(self.stepIndex, self.stepIndex - 1)
        pass

    def swapDown(self, state):
        self.swapRequest.emit(self.stepIndex, self.stepIndex + 1)
        pass

    def thumbnailClick(self, screenshotIndex):
        self.thumbnailClicked.emit(self.stepIndex, screenshotIndex)
        pass

    def CreateMergedWindow(self):
        if(len(self.Slides) < 2):
            self.expandButton.hide()
            return
        finalImage = self.Slides[0].image.toImage()
        finalJson = copy.deepcopy(self.Slides[0].metadata)
        painter = qt.QPainter(finalImage)
        for slide in self.Slides[1:]:

            finalJson.extend(copy.deepcopy(slide.metadata))

            nextImage = slide.image.toImage()

            mainWidget = slide.metadata[0]
            painter.drawImage(qt.QRect(mainWidget["position"][0],
                                       mainWidget["position"][1],
                                       nextImage.width(),
                                       nextImage.height()),
                                       nextImage)
        painter.end()
        mergedSlide = AnnotatorSlide(qt.QPixmap().fromImage(finalImage), finalJson)

        self.mergedSlideIndex = self.screenshotCount
        self.AddStepWindows(mergedSlide)
        self.SlideWidgets[self.mergedSlideIndex].setVisible(False)
        pass

    def ToggleExtended(self):
        if(len(self.Slides) < 2):
            return
        self.showingMerged = not self.showingMerged
        if self.showingMerged:
            for wIndex, widget in enumerate(self.SlideWidgets):
                widget.setVisible(False)
                self.Slides[wIndex].Active = False
            self.SlideWidgets[self.mergedSlideIndex].setVisible(True)
            self.Slides[self.mergedSlideIndex].Active = True
        else:
            for wIndex, widget in enumerate(self.SlideWidgets):
                widget.setVisible(True)
                self.Slides[wIndex].Active = True
            self.SlideWidgets[self.mergedSlideIndex].setVisible(False)
            self.Slides[self.mergedSlideIndex].Active = False

    def mousePressEvent(self, event):
        #self.ToggleExtended()
        pass
    def mouseMoveEvent(self, event):
        if event.buttons() == qt.Qt.LeftButton:
            drag = qt.QDrag(self)
            mime = qt.QMimeData()
            mime.setText("AnnotatorStepWidget")
            drag.setMimeData(mime)
            drag.exec_(qt.Qt.MoveAction)
        pass

class TutorialGUI(qt.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        self.scrollAreaSize = [315, 715]
        self.selectedSlideSize = [900, 530]
        self.windowSize = [1250, 780]
        self.thumbnailSize = [280, 165]

        self.steps = []

        self.updateTimer = qt.QTimer()
        self.updateTimer.setTimerType(qt.Qt.PreciseTimer)
        self.updateTimer.setInterval(34) #34ms Interval = 30 ups
        self.updateTimer.timeout.connect(self.refreshViews)
        self.updateTimer.start()

        self.selectedIndexes = [0,0]
        self.selectedAnnotator = None
        self.selectedAnnotationType = AnnotationType.Nil
        self.selectedAnnotation = None

        _penSettings = {"color": qt.QColor(255, 128, 0),
                       "fontSize": 14,
                       "penThickness": 4}

        self.penSettings = _penSettings

        self.selectorParentCount = 0

        self.setupGUI()

        self.defaultHelperOffset = [60,60]

        # TODO: Get a better way to get the module position
        self.outputFolder = f"{os.path.dirname(__file__)}/../Outputs/Annotations"

        # Need to do a overhaul of the preview function so this isn't necessary
        self.lastAppPos = qt.QPoint()

        # This has to be handled somewhere, maybe when we sort the setupGUI to be more concise move it to there?

        # Offset positional helper
        self.OffsetHelperWidget = DraggableLabel()
        self.OffsetHelperWidget.setParent(self.selectedSlide)
        self.OffsetHelperWidget.setFixedSize(10,10)
        self.OffsetHelperWidget.setStyleSheet("background-color: #03fc0b;border-style: outset; border-width: 2px; border-color: #fc034e;")
        self.OffsetHelperWidget.SetCenter(250,250)
        self.OffsetHelperWidget.installEventFilter(self.OffsetHelperWidget)
        self.OffsetHelperWidget.SetActive(False)

        # Optional positional helper
        self.OptHelperWidget = DraggableLabel()
        self.OptHelperWidget.setParent(self.selectedSlide)
        self.OptHelperWidget.setFixedSize(10,10)
        self.OptHelperWidget.setStyleSheet("background-color: #fc034e;border-style: outset; border-width: 2px; border-color: #03fc0b;")
        self.OptHelperWidget.SetCenter(250,250)
        self.OptHelperWidget.installEventFilter(self.OptHelperWidget)
        self.OptHelperWidget.SetActive(False)

        # Tutorial Information
        self.tutorialInfo = {"name": "", "author" : "", "date": "", "desc": ""}
        self.outputName = ""

    def setupGUI(self):
        # TODO: A lot of the steps called from here could be remade in the qt designer to clean this up

        #UI File
        self.dir_path = os.path.dirname(__file__)
        self.uiWidget = slicer.util.loadUI(self.dir_path+'/../Resources/UI/ScreenshotAnnotator.ui')

        #Prepare the layout
        self.newlayout = qt.QVBoxLayout()
        self.newlayout.setObjectName("uiWidget")

        #Create the toolbar
        self.addToolBar(self.create_toolbar_menu())
        self.addToolBar(self.create_toolbar_actions())
        self.addToolBar(self.create_toolbar_edit())

        # Load UI File
        self.newlayout.addWidget(self.uiWidget)

        # Set self layout with UI components
        self.setCentralWidget(self.uiWidget)

        # Configure Main Window
        self.setFixedSize(*self.windowSize)
        self.setWindowTitle(_("TutorialMaker - Annotator"))

        # Left Scroll Area
        self.scrollAreaWidgetContents = qt.QWidget()
        self.gridLayout = qt.QGridLayout(self.scrollAreaWidgetContents)

        self.uiWidget.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.scroll_area = self.uiWidget.findChild(qt.QScrollArea, "scrollArea")
        self.scroll_area.setFixedSize(*self.scrollAreaSize)
        self.scroll_area.setAcceptDrops(True)
        self.scroll_area.installEventFilter(self)

        # Configure Main Slide Screen
        self.selectedSlide = self.uiWidget.findChild(qt.QLabel, "label_imagen")
        self.selectedSlide.setFixedSize(*self.selectedSlideSize)

        self.installEventFilter(self)
        self.selectedSlide.installEventFilter(self)
        self.selectedSlide.setMouseTracking(True)
        self.selectedSlide.setScaledContents(False)

        # Configure the Slide Title and Slide body text boxes
        self.slideTitleWidget = self.uiWidget.findChild(qt.QLineEdit, "lineEdit")
        self.slideTitleWidget.setMinimumWidth(self.selectedSlideSize[0])
        self.slideTitleWidget.setMaximumWidth(self.selectedSlideSize[0])
        self.slideTitleWidget.placeholderText = _("Title for the slide")

        self.slideBodyWidget = self.uiWidget.findChild(qt.QTextEdit, "myTextEdit")
        self.slideBodyWidget.setFixedSize(self.selectedSlideSize[0], 150)
        self.slideBodyWidget.placeholderText = _("Write a description for the slide")

        # Load Used Resources
        resourceFolder = os.path.dirname(__file__) + '/../Resources'
        self.image_ChevronUp = qt.QImage(f'{resourceFolder}/Icons/ScreenshotAnnotator/chevron_up.png').scaled(20,20, qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
        self.image_ChevronDown = qt.QImage(f'{resourceFolder}/Icons/ScreenshotAnnotator/chevron_down.png').scaled(20,20, qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
        self.image_ArrowUp = qt.QImage(f'{resourceFolder}/Icons/ScreenshotAnnotator/arrow_up.png').scaled(20,20, qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
        self.image_ArrowDown = qt.QImage(f'{resourceFolder}/Icons/ScreenshotAnnotator/arrow_down.png').scaled(20,20, qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)

        self.icon_chevron = qt.QIcon()
        self.icon_chevron.addPixmap(qt.QPixmap.fromImage(self.image_ChevronDown), qt.QIcon.Normal, qt.QIcon.Off)
        self.icon_chevron.addPixmap(qt.QPixmap.fromImage(self.image_ChevronUp), qt.QIcon.Normal, qt.QIcon.On)
        self.icon_arrowUp = qt.QIcon(qt.QPixmap.fromImage(self.image_ArrowUp))
        self.icon_arrowDown = qt.QIcon(qt.QPixmap.fromImage(self.image_ArrowDown))
        pass

    def open_json_file_dialog(self):
        pass

    def saveAnnotationsAsJSON(self):
        import re
        outputFileAnnotations = {**self.tutorialInfo}
        outputFileTextDict = {}
        outputFileOld = []

        outputFileAnnotations["slides"] = []

        for stepIndex, step in enumerate(self.steps):
            for slideIndex, slide in enumerate(step.Slides):
                if not slide.Active:
                    continue
                slideImage = slide.image

                cleanSlideTitle = slide.SlideTitle.replace(' ', '')
                cleanSlideTitle = re.sub(r'[^a-zA-Z0-9]', '', cleanSlideTitle)

                slidePrefix = f"{stepIndex}_{slideIndex}"
                slideTitle = f"{slidePrefix}_{cleanSlideTitle}"
                slideImagePath = f"{self.outputFolder}/{slideTitle}"
                if cleanSlideTitle == "":
                    slideTitle += "slide"
                    slideImagePath += "slide"
                slideImage.save(slideImagePath + ".png", "PNG")

                textDict = {f"{slideTitle}_title": slide.SlideTitle,
                            f"{slideTitle}_body": slide.SlideBody}

                slideInfo = {"ImagePath": f"{slideTitle}.png",
                             "SlideCode": f"{stepIndex}/{slideIndex}",
                             "SlideLayout": slide.SlideLayout,
                             "SlideTitle": f"{slideTitle}_title",
                             "SlideDesc": f"{slideTitle}_body",
                             "Annotations": []}

                for annIndex, annotation in enumerate(slide.annotations):
                    info = annotation.toDict()
                    textDict[f"{slidePrefix}_{info['type']}_{annIndex}"] = info["text"]
                    slideInfo["Annotations"].append({"widgetPath": info["widgetPath"],
                                                     "type": info["type"],
                                                     "offset": info["offset"],
                                                     "optional": info["optional"],
                                                     "custom": info["custom"],
                                                     "penSettings": info["penSettings"],
                                                      "text": f"{slidePrefix}_{info['type']}_{annIndex}"})
                    pass
                outputFileAnnotations["slides"].append(slideInfo)
                outputFileTextDict = {**outputFileTextDict, **textDict}
            pass

        with open(file= f"{self.outputFolder}/annotations.json", mode='w', encoding="utf-8") as fd:
            json.dump(outputFileAnnotations, fd, ensure_ascii=False, indent=4)

        with open(file= f"{self.outputFolder}/text_dict_default.json", mode='w', encoding="utf-8") as fd:
            json.dump(outputFileTextDict, fd, ensure_ascii=False, indent=4)



    def deleteSelectedAnnotation(self):
        self.selectedAnnotation = None
        if self.selectedAnnotationType == AnnotationType.Selected:
            self.selectedAnnotationType = AnnotationType.Selecting
        pass

    def delete_screen(self):
        pass

    def forceTutorialOutputName(self, name):
        self.outputName = name
        pass

    def loadImagesAndMetadata(self, tutorialData):
        for stepIndex, screenshots in enumerate(tutorialData.steps):
            stepWidget = AnnotatorStepWidget(stepIndex, self.thumbnailSize, parent=self)
            stepWidget.thumbnailClicked.connect(self.changeSelectedSlide)
            stepWidget.swapRequest.connect(self.swapStepPosition)

            #>>>>>> This assumes that the first window is always the SlicerAppMainWindow <<<<<<<

            #Main window
            try:
                annotatorSlide = AnnotatorSlide(screenshots[0].getImage(), screenshots[0].getWidgets())
                stepWidget.AddStepWindows(annotatorSlide)
            except Exception:
                print(f"ERROR: Annotator Failed to add top level window in step:{stepIndex}, loadImagesAndMetadata")
                del stepWidget
                continue

            for screenshot in screenshots[1:]:
                try:
                    annotatorSlide = AnnotatorSlide(screenshot.getImage(),
                                                    screenshot.getWidgets(),
                                                    WindowOffset=screenshot.getWidgets()[0]["position"])
                    stepWidget.AddStepWindows(annotatorSlide)  # noqa: F821
                except Exception:
                    print(f"ERROR: Annotator Failed to add window in step:{stepIndex}, loadImagesAndMetadata")

            self.steps.append(stepWidget)  # noqa: F821
            self.gridLayout.addWidget(stepWidget)  # noqa: F821
            stepWidget.UNDELETABLE = True # noqa: F821
            stepWidget.CreateMergedWindow() # noqa: F821
            stepWidget.ToggleExtended() # noqa: F821

        #TODO: use widget annotation infrastructure to make these pages more on the fly interactable
        # Insert Dummy Pages for Title, Acknowledgements
        #self.addBlankPage(False, 0, self.dir_path + '/../Resources/NewSlide/cover_page.png', type_="CoverPage")
        cover_pm = self.make_cover_pixmap(self.tutorialInfo, tuple(self.selectedSlideSize))
        self.addBlankPage(False, 0, "", type_="CoverPage", pixmap=cover_pm)
        acknowledgments_pm= self.make_acknowledments_pixmap(self.tutorialInfo, tuple(self.selectedSlideSize))
        if acknowledgments_pm is not None:
            self.addBlankPage(False, stepIndex + 2, type_="Acknowledgment", pixmap = acknowledgments_pm)

        pass

    def swapStepPosition(self, index, swapTo):
        if swapTo >= len(self.steps) or swapTo < 0:
            return
        tmp = self.steps[swapTo]
        self.steps[swapTo] = self.steps[index]
        self.steps[swapTo].stepIndex = swapTo
        self.gridLayout.addWidget(self.steps[swapTo], swapTo, 0)

        self.steps[index] = tmp
        self.steps[index].stepIndex = index
        self.gridLayout.addWidget(self.steps[index], index, 0)
        pass

    def changeSelectedSlide(self, stepId, screenshotId):
        self.cancelCurrentAnnotation()

        # Save text to slideAnnotator
        if self.selectedAnnotator is not None:
            self.selectedAnnotator.SlideTitle = self.slideTitleWidget.text
            self.selectedAnnotator.SlideBody = self.slideBodyWidget.toPlainText()

        # Change the slide variables
        self.selectedIndexes = [stepId, screenshotId]
        selectedStep = self.steps[stepId]
        selectedScreenshot = selectedStep.Slides[screenshotId]

        self.selectedSlide.setPixmap(selectedScreenshot.GetResized(*self.selectedSlideSize, keepAspectRatio=True))
        self.selectedAnnotator = selectedScreenshot

        # Load text from slideAnnotator
        self.slideTitleWidget.setText(self.selectedAnnotator.SlideTitle)
        self.slideBodyWidget.setText(self.selectedAnnotator.SlideBody)


    def cancelCurrentAnnotation(self):
        if self.selectedAnnotation is not None:
            self.selectedAnnotation.drawBoundingBox = False
            if not self.selectedAnnotation.PERSISTENT:
                self.selectedAnnotator.annotations.remove(self.selectedAnnotation)
            self.selectedAnnotation = None
            if self.selectedAnnotationType == AnnotationType.Selected:
                self.selectedAnnotationType = AnnotationType.Selecting

    def onActionTriggered():
        pass

    #TODO: Clean this up, there's a better way to keep track of the step.stepIndex value, with this we have to keep 2 copies redundant
    #This seems like a very expensive function
    # Cambia la firma:
    def addBlankPage(self, state, index:int=None, backgroundPath:str="", metadata:dict=None, type_:str="", pixmap:qt.QPixmap=None):
        stepWidget = AnnotatorStepWidget(len(self.steps), self.thumbnailSize, parent=self)
        stepWidget.thumbnailClicked.connect(self.changeSelectedSlide)
        stepWidget.swapRequest.connect(self.swapStepPosition)

        if metadata is None:
            metadata = {}

        if pixmap is not None:
            annotatorSlide = AnnotatorSlide(pixmap, metadata)
        elif backgroundPath:
            annotatorSlide = AnnotatorSlide(qt.QPixmap(backgroundPath), metadata)
        else:
            # comportamiento anterior (selector de imágenes)
            self.images_selector(self.tutorial2, index)
            return

        if type_:
            annotatorSlide.SlideLayout = type_
        stepWidget.AddStepWindows(annotatorSlide)
        stepWidget.CreateMergedWindow()

        def InsertWidget(_nWidget, _index):
            self.steps.append(_nWidget)
            self.gridLayout.addWidget(_nWidget)
            for stepIndex in range(len(self.steps) - 1, _index, -1):
                self.steps[stepIndex] = self.steps[stepIndex - 1]
                self.steps[stepIndex].stepIndex = stepIndex
                self.gridLayout.addWidget(self.steps[stepIndex], stepIndex, 0)
            self.steps[_index] = _nWidget
            _nWidget.stepIndex = _index
            self.gridLayout.addWidget(_nWidget, _index, 0)

        if index is not None:
            InsertWidget(stepWidget, index)
            return
        InsertWidget(stepWidget, self.selectedIndexes[0] + 1)

        
    def add_selected_image(self):
        insert_index = self.selectedIndexes[0]+1
        if self.selected_image:
            try:
                screenshot = self.selected_image[0]
                image_pixmap = screenshot.getImage()
                image_widgets = screenshot.getWidgets()
                annotatorSlide = AnnotatorSlide(image_pixmap, image_widgets)

            
                if not image_pixmap or image_pixmap.isNull():
                    print("Image pixmap is null")
                    return

                stepWidget = AnnotatorStepWidget(len(self.steps), self.thumbnailSize, parent=self)
                stepWidget.thumbnailClicked.connect(self.changeSelectedSlide)
                stepWidget.swapRequest.connect(self.swapStepPosition)            
                stepWidget.AddStepWindows(annotatorSlide) 

                self.steps.insert(insert_index, stepWidget) 
                while self.gridLayout.count():
                    item = self.gridLayout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.setParent(None)
                for idx, step in enumerate(self.steps):
                    step.stepIndex =idx
                    self.gridLayout.addWidget(step, idx, 0)  
               
                self.selected_image[1].setStyleSheet("border: 2px solid transparent;")
                self.selected_image = None
             
                    

            except Exception as e:
                print(f"Error: {str(e)}")
        
       



    def copy_page(self):
        pass

    def updateSelectedAnnotationSettings(self):
        if self.selectedAnnotation is not None:
            self.selectedAnnotation.penConfig(self.penSettings["color"], self.penSettings["fontSize"],self.penSettings["penThickness"], brush=True)

    def updateAnnotationThicknessValue(self):
        self.penSettings["penThickness"] = self.spin_box.value
        self.updateSelectedAnnotationSettings()
        pass

    def open_icon(self):
        pass

    def fill_figures(self):
        pass

    def actualizar_size(self):
        pass

    def updateTextFontSize(self):
        self.penSettings["fontSize"] = self.spin_box_txt.value
        self.updateSelectedAnnotationSettings()
        pass

    def changeColor(self):
        color_dialog = qt.QColorDialog()
        color_dialog.setCurrentColor(self.penSettings["color"])
        if color_dialog.exec_():
            color = color_dialog.selectedColor()
            self.penSettings["color"] = color
        pass
        self.updateSelectedAnnotationSettings()

    def mouse_press_event(self, event):
        self.setFocus()
        if self.selectedAnnotationType == AnnotationType.Nil:
            return
        if self.selectedAnnotationType == AnnotationType.Selecting:
            self.selectionHandler(event.pos())
            return
        self.annotationHandler(event.pos())

        pass #FindAnnotationsAtPos

    def selectionHandler(self, appPos):
        posInImage = self.selectedAnnotator.MapScreenToImage(appPos, self.selectedSlide)
        annotations = self.selectedAnnotator.FindAnnotationsAtPos(*posInImage)

        if len(annotations) < 1:
            return
        # Using the parent counter to go back a set amount from the widget parents
        if self.selectorParentCount > len(annotations) - 1:
            self.selectorParentCount = len(annotations) - 1
        elif self.selectorParentCount < 0:
            self.selectorParentCount = 0
        selectedAnnotation = annotations[len(annotations) - 1 - self.selectorParentCount]
        if selectedAnnotation is None:
            return
        optValuesInImage = self.selectedAnnotator.MapImageToScreen(qt.QPointF(selectedAnnotation.optX, selectedAnnotation.optY,), self.selectedSlide)
        self.OptHelperWidget.SetCenter(*optValuesInImage)
        _offsetPos = self.selectedAnnotator.MapImageToScreen(qt.QPointF(selectedAnnotation.target["position"][0] + selectedAnnotation.offsetX,
                                                                       selectedAnnotation.target["position"][1] + selectedAnnotation.offsetY), self.selectedSlide)

        self.OffsetHelperWidget.SetCenter(*_offsetPos)

        self.on_action_triggered(None) #TODO: This is needed because this affects the selectiontype every mouse movement event and makes the selection process very janky
        self.selectedAnnotation = selectedAnnotation
        self.selectedAnnotationType = AnnotationType.Selected
        self.selectedAnnotation.drawBoundingBox = True
        pass

    def annotationHandler(self, appPos):
        if self.selectedAnnotation is None:
            return
        self.selectedAnnotation.PERSISTENT = True
        selectedAnnotation = self.selectedAnnotation
        self.on_action_triggered(None)
        self.selectedAnnotation = selectedAnnotation
        self.selectedAnnotationType = AnnotationType.Selected
        self.selectedAnnotation.drawBoundingBox = True

    def previewAnnotation(self, appPos):
        self.lastAppPos = appPos
        posInImage = self.selectedAnnotator.MapScreenToImage(appPos, self.selectedSlide)
        widgets = self.selectedAnnotator.FindWidgetsAtPos(*posInImage)

        def ApplyHelper():
            optValuesInImage = self.selectedAnnotator.MapScreenToImage(qt.QPointF(*self.OptHelperWidget.GetCenter()), self.selectedSlide)
            self.selectedAnnotation.setValuesOpt(*optValuesInImage)


            _helperPos = self.selectedAnnotator.MapScreenToImage(qt.QPointF(*self.OffsetHelperWidget.GetCenter()), self.selectedSlide)
            offsetFromTargetWidget = [_helperPos[0] - self.selectedAnnotation.target["position"][0],
                                      _helperPos[1] - self.selectedAnnotation.target["position"][1]]

            self.selectedAnnotation.setValuesOffset(*offsetFromTargetWidget)

        if self.selectedAnnotationType == AnnotationType.Selected:
            self.OptHelperWidget.SetActive(self.selectedAnnotation.wantsOptHelper())
            self.OffsetHelperWidget.SetActive(self.selectedAnnotation.wantsOffsetHelper())
            ApplyHelper()
            return

        if len(widgets) < 1:
            return

        # Using the parent counter to go back a set amount from the widget parents
        if self.selectorParentCount > len(widgets) - 1:
            self.selectorParentCount = len(widgets) - 1
        elif self.selectorParentCount < 0:
            self.selectorParentCount = 0

        selectedWidget = widgets[len(widgets) - 1 - self.selectorParentCount]

        if selectedWidget is None:
            return

        if self.selectedAnnotation is None:
            self.selectedAnnotation = Annotation(TargetWidget=selectedWidget, Type=self.selectedAnnotationType)
            self.selectedAnnotator.AddAnnotation(self.selectedAnnotation)
            self.selectedAnnotation.penConfig(self.penSettings["color"], self.penSettings["fontSize"],self.penSettings["penThickness"], brush=True)
            self.OptHelperWidget.SetActive(self.selectedAnnotation.wantsOptHelper())
            self.OffsetHelperWidget.SetActive(self.selectedAnnotation.wantsOffsetHelper())

        self.selectedAnnotation.target = selectedWidget

        # Configure The Annotation Optional Helper so that its always towards the center

        helperPosition = copy.deepcopy(self.defaultHelperOffset)
        if appPos.x() > self.selectedSlideSize[0]/2:
            helperPosition[0] = -helperPosition[0]
        if appPos.y() > self.selectedSlideSize[1]/2:
            helperPosition[1] = -helperPosition[1]
        self.OptHelperWidget.SetCenter(appPos.x() + helperPosition[0], appPos.y() + helperPosition[1])

        # Configure The Annotation Offset Helper so it defaults to zero
        # Probably one the ugliest way to do this, maybe find someway better
        _reversePostion = self.selectedAnnotator.MapImageToScreen(qt.QPointF(*selectedWidget["position"]), self.selectedSlide)
        self.OffsetHelperWidget.SetCenter(*_reversePostion)

        ApplyHelper()
        pass

    def refreshViews(self):
        if self.selectedAnnotator is None:
            return
        self.selectedAnnotator.ReDraw()
        self.selectedSlide.setPixmap(self.selectedAnnotator.GetResized(*self.selectedSlideSize, keepAspectRatio=True))
        pass

    def mouse_move_event(self, event):
         #TODO: Clean this up as there has to be a less roundabout way to get these
        # Probably going to have to rewrite the whole action chain
        if self.select.isChecked():
            self.selectedAnnotationType = AnnotationType.Selecting
        if self.square.isChecked():
            self.selectedAnnotationType = AnnotationType.Rectangle
        elif self.circle.isChecked():
            self.selectedAnnotationType = AnnotationType.Circle
        elif self.arrow.isChecked():
            self.selectedAnnotationType = AnnotationType.Arrow
        elif self.arrowText.isChecked():
            self.selectedAnnotationType = AnnotationType.ArrowText
        elif self.textBox.isChecked():
            self.selectedAnnotationType = AnnotationType.TextBox
        elif self.icon_image.isChecked():
            self.selectedAnnotationType = AnnotationType.Nil # TODO: These needs to be implemented and "icon" is not a discriptive enough action chain name
        elif self.in_text.isChecked():
            self.selectedAnnotationType = AnnotationType.TextBox
        elif self.clck.isChecked():
            self.selectedAnnotationType = AnnotationType.Click
        pass

        if self.selectedAnnotationType is not AnnotationType.Nil and self.selectedAnnotationType is not AnnotationType.Selecting:
            self.previewAnnotation(event.pos())

    def mouse_release_event(self, event):
        pass

    def keyboardEvent(self, event):
        if event.key() == qt.Qt.Key_Escape:
            self.setFocus()
            return False

        if self.selectedAnnotationType == AnnotationType.Selected:
            if event.key() == qt.Qt.Key_Delete:
                self.selectedAnnotation.PERSISTENT = False
                self.cancelCurrentAnnotation()

            elif self.selectedAnnotation.type in [AnnotationType.TextBox, AnnotationType.ArrowText]:
                # Detect command Ctrl+C copy text
                if event.key() == qt.Qt.Key_C and event.modifiers() & qt.Qt.ControlModifier:
                    qt.QApplication.clipboard().setText(self.selectedAnnotation.text)
                
                # Detect command Ctl+v page text
                elif event.key() == qt.Qt.Key_V and event.modifiers() & qt.Qt.ControlModifier:
                    self.selectedAnnotation.text += qt.QApplication.clipboard().text()

                # Detect Enter to add a line break
                elif event.key() in [qt.Qt.Key_Return, qt.Qt.Key_Enter]:
                    self.selectedAnnotation.text += "\n"

                # Detect Backspace
                elif event.key() == qt.Qt.Key_Backspace:
                    self.selectedAnnotation.text = self.selectedAnnotation.text[:-1]

                else:
                    self.selectedAnnotation.text += event.text()

            return True

        elif self.selectedAnnotator is not None and self.selectedAnnotation is not None:
            if event.key() == qt.Qt.Key_Up:
                self.selectorParentDelta(-1)
                return True
            elif event.key() == qt.Qt.Key_Down:
                self.selectorParentDelta(1)
                return True

        return False


    def selectorParentDelta(self, delta : int):
        self.selectorParentCount += delta
        self.previewAnnotation(self.lastAppPos)


    def scrollEvent(self, event):
        threshold = 4 #scroll threshold

        delta = event.angleDelta().y()
        if delta > threshold:
            self.selectorParentDelta(-1)
        elif delta < threshold:
            self.selectorParentDelta(1)

    def open_json_file(self, filepath):
        directory_path = os.path.dirname(filepath)
        # Read the data from the file
        with open(filepath, encoding='utf-8') as file:
            rawTutorialData = json.load(file)
            file.close()


        tutorial = Tutorial(
            rawTutorialData["title"],
            rawTutorialData["author"],
            rawTutorialData["date"],
            rawTutorialData["desc"]
        )

        self.tutorialInfo = tutorial.metadata

        stepList = []
        tutorial.steps = stepList
        for step in rawTutorialData["steps"]:
            screenshotList = []
            for window in step:
                wScreenshot = TutorialScreenshot(
                    directory_path + "/" + window["window"],
                    directory_path + "/" + window["metadata"]
                )
                screenshotList.append(wScreenshot)
            tutorial.steps.append(screenshotList)
        self.loadImagesAndMetadata(tutorial)
        self.tutorial2 = tutorial
        
        new_image_path = self.dir_path+'/../Resources/NewSlide/white.png'
        new_screenshot = TutorialScreenshot(new_image_path, "")
        if self.tutorial2.steps:
            self.tutorial2.steps.append([new_screenshot])  #The white image is added
        else:
            self.tutorial2.steps.append([new_screenshot]) 


       



    def eventFilter(self, obj, event):
        if obj == self.selectedSlide:
            if event.type() == qt.QEvent.Leave:
                if self.selectedAnnotation is not None and not self.selectedAnnotation.PERSISTENT:
                    return self.cancelCurrentAnnotation()
            elif event.type() == qt.QEvent.MouseButtonPress:
                return self.mouse_press_event(event)
            elif event.type() == qt.QEvent.MouseMove:
                return self.mouse_move_event(event)
            elif event.type() == qt.QEvent.MouseButtonRelease:
                return self.mouse_release_event(event)
            elif event.type() == qt.QEvent.Wheel:
                return self.scrollEvent(event)
        else:
            if event.type() == qt.QEvent.KeyPress:
                return self.keyboardEvent(event)
            elif event.type() == qt.QEvent.DragEnter:
                return self.dragEnterEvent(event)
            elif event.type() == qt.QEvent.DragMove:
                return self.dragEnterEvent(event)
            elif event.type() == qt.QEvent.Drop:
                return self.dragDropEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            if event.mimeData().text() == "AnnotatorStepWidget":
                event.accept()
                return True
        event.ignore()
        return True

    def dragDropEvent(self, event):
        stepWidget = event.source()
        pos = event.pos()
        for step in self.steps:
            if pos.y() + self.scroll_area.verticalScrollBar().value < step.pos.y() + step.size.height():
                self.swapStepPosition(stepWidget.stepIndex, step.stepIndex)
                break
        event.accept()
        return True

    def create_toolbar_menu(self):
        toolbar = qt.QToolBar("File", self)

        actionOpen = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/open.png'), _("Open"), self)
        actionSave = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/save.png'), _("Save"), self)
        actionBack = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/back.png'), _("Undo"), self)
        actionDelete = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/remove.png'), _("Delete"), self)
        actionAdd = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/add.png'), _("Add"), self)
        actionCopy = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/copy.png'), _("Copy"), self)

        toolbar.addAction(actionOpen)
        toolbar.addAction(actionSave)
        toolbar.addAction(actionBack)
        # toolbar.addAction(actionDelete)
        toolbar.addAction(actionAdd)
        toolbar.addAction(actionCopy)

        actionOpen.triggered.connect(self.open_json_file_dialog)
        actionSave.triggered.connect(self.saveAnnotationsAsJSON)
        actionBack.triggered.connect(self.deleteSelectedAnnotation)
        actionDelete.triggered.connect(self.delete_screen)
        actionAdd.triggered.connect(self.addBlankPage)
        actionCopy.triggered.connect(self.copy_page)

        toolbar.setMovable(True)
        return toolbar

    def create_toolbar_actions(self):
        toolbar = qt.QToolBar("Actions", self)
        #TODO: Make icon for the selection action
        self.select = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/select.png'), _("Select"), self)
        self.select.setCheckable(True)
        toolbar.addAction(self.select)

        self.square = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act1.png'), _("Square"), self)
        self.square.setCheckable(True)
        toolbar.addAction(self.square)

        self.circle = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act2.png'), _("Circle"), self)
        self.circle.setCheckable(True)

        self.clck = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/pointer.png'), _("Click"), self)
        self.clck.setCheckable(True)
        toolbar.addAction(self.clck)

        #New Icon for textless arrows, if we add text back we change it back
        self.arrow = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/arrow_disabled.png'), _("Arrow"), self)
        self.arrow.setCheckable(True)
        toolbar.addAction(self.arrow)

        self.arrowText = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act3.png'), _("Arrow text"), self)
        self.arrowText.setCheckable(True)
        toolbar.addAction(self.arrowText)

        self.textBox = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/textBox_disabled.png'), _("Text Box"), self)
        self.textBox.setCheckable(True)
        toolbar.addAction(self.textBox)

        self.icon_image = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act4.png'), _("Icon"), self)
        self.icon_image.setCheckable(True)

        self.in_text = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act5.png'), _("Text"), self)
        self.in_text.setCheckable(True)

        self.icons = {
            #TODO:Create an icon for the select tool
            self.select: {
                'active': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/actselect.png'),
                'inactive': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/select.png')
            },

            self.square: {
                'active': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act1_p.png'),
                'inactive': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act1.png')
            },
            self.circle: {
                'active': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act2_p.png'),
                'inactive': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act2.png')
            },
            self.clck: {
                'active': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/pointer_p.png'),
                'inactive': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/pointer.png')
            },
            self.arrow: {
                'active': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/arrow_enabled.png'),
                'inactive': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/arrow_disabled.png')
            },
            self.arrowText:{
                'active': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act3_p.png'),
                'inactive': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act3.png')
            },
            self.textBox: {
                'active': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/textBox_enabled.png'),
                'inactive': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/textBox_disabled.png')
            },
            self.icon_image: {
                'active': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act4_p.png'),
                'inactive': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act4.png')
            },
            self.in_text: {
                'active': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act5_p.png'),
                'inactive': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act5.png')
            }
        }

        self.toolbar_actions = [self.select, self.square, self.circle, self.clck, self.arrow, self.arrowText ,self.icon_image, self.in_text, self.textBox]
        for a in self.toolbar_actions:
            a.triggered.connect(lambda checked, a=a: self.on_action_triggered(a))

        toolbar.setMovable(True)
        return toolbar

    def create_toolbar_edit(self):
        toolbar = qt.QToolBar("Edit", self)

        label_c = qt.QLabel("Color")
        toolbar.addWidget(label_c)

        self.action7 = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/color.png'), _("color"), self)
        toolbar.addAction(self.action7)
        self.action7.triggered.connect(self.changeColor)

        self.valor = 4
        self.spin_box = qt.QSpinBox()
        self.spin_box.setSuffix(_(" thick."))
        self.spin_box.setMinimum(1)
        self.spin_box.setMaximum(15)
        self.spin_box.setSingleStep(1)
        self.spin_box.setValue(self.valor)
        toolbar.addWidget(self.spin_box)
        self.spin_box.valueChanged.connect(self.updateAnnotationThicknessValue)

        label_t = qt.QLabel("Text: ")
        toolbar.addWidget(label_t)
        self.fill_annot = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/fill_u.png'), _("Fill"), self)
        self.fill_annot.setCheckable(True)
        self.fill = False
        #toolbar.addAction(self.fill_annot)

        self.t_px = 14
        self.spin_box_txt = qt.QSpinBox()
        self.spin_box_txt.setSuffix(" px")
        self.spin_box_txt.setMinimum(5)
        self.spin_box_txt.setMaximum(30)
        self.spin_box_txt.setSingleStep(1)
        self.spin_box_txt.setValue(self.t_px)
        toolbar.addWidget(self.spin_box_txt)
        self.spin_box_txt.valueChanged.connect(self.updateTextFontSize)

        self.text_in = qt.QLineEdit()
        self.text_in.setMaxLength(500)
        self.text_in.setMaximumWidth(590)
        self.widget_action = qt.QWidgetAction(self)
        self.widget_action.setDefaultWidget(self.text_in)
        toolbar.addAction(self.widget_action)
        self.text_in.setPlaceholderText("Add text to accompany an arrow here.")

        self.load_icon = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/image.png'), _("Load icon"), self)
        self.load_icon.setCheckable(True)
        self.new_image = qt.QPixmap(20, 20)
        self.dir_icon = None
        self.open_icon()

        self.fill_annot.triggered.connect(self.fill_figures)
        self.load_icon.triggered.connect(self.open_icon)

        toolbar.setMovable(True)

        return toolbar

    def on_action_triggered(self, sender):
        self.cancelCurrentAnnotation()
        for action, icons in self.icons.items():
            if action is sender:
                action.setChecked(True)
                action.setIcon(icons['active'])
            else:
                action.setChecked(False)
                action.setIcon(icons['inactive'])

    def images_selector(self, tutorialDara,index):
        self.dialog = qt.QDialog()
        self.dialog.setWindowTitle("Select the images")
        self.dialog.setGeometry(100, 100, 800, 600) 
        
        self.listWidget = qt.QListWidget()
        self.listWidget.setSelectionMode(qt.QAbstractItemView.NoSelection) 
        self.listWidget.setIconSize(qt.QSize(300, 300))
        self.listWidget.setViewMode(qt.QListWidget.IconMode) 
        self.listWidget.setResizeMode(qt.QListWidget.Adjust)  
        self.listWidget.setSpacing(10)
        
        self.final_selected_images = []
        self.selected_image = None
        self.image_buttons = {}
        grouped_steps = {}  #Groups for images in each step
        
        for stepIndex, screenshots in enumerate(self.tutorial2.steps):
            if stepIndex not in grouped_steps:
                grouped_steps[stepIndex] = []  
            for screenshotIndex, screenshot in enumerate(screenshots):
                try:
                    pixmap = screenshot.getImage()
                    if not pixmap or pixmap.isNull():
                        print(f"ERROR: pixmap Null")
                        continue

                    grouped_steps[stepIndex].append((pixmap, screenshot))  #Save the image in each group (step)

                except Exception as e:
                    print(f"ERROR")
        has_widgets = False
    
        for stepIndex, screenshots in grouped_steps.items():
            if not screenshots:
                continue 

            container_widget = qt.QWidget()
            layout = qt.QVBoxLayout(container_widget)

            main_pixmap, main_screenshot = screenshots[0]
            main_button = qt.QPushButton()
            main_button.setIcon(qt.QIcon(main_pixmap))
            main_button.setIconSize(qt.QSize(300, 200))
            main_button.setCheckable(True)
            if len(screenshots[1:])>0:
                main_button.setStyleSheet("border: 2px solid #FFFF00;")
            else:
                main_button.setStyleSheet("border: 2px solid transparent;")
            main_button.clicked.connect(lambda _, img=main_screenshot, btn=main_button: self.select_single_image(img, btn))
            if len(screenshots[1:])>0:
                toggle_button = qt.QPushButton()
                toggle_button.setIcon(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/chevron_down.png'))  
                toggle_button.setIconSize(qt.QSize(32, 32))
                toggle_button.setCheckable(True)

                secondary_container = qt.QWidget()
                secondary_layout = qt.QVBoxLayout(secondary_container)

                for pixmap, screenshot in screenshots[1:]:
                    if not pixmap:
                        continue 
                    sec_button = qt.QPushButton()
                    sec_button.setIcon(qt.QIcon(pixmap))
                    sec_button.setIconSize(qt.QSize(250, 150))
                    sec_button.setCheckable(True)
                    sec_button.setStyleSheet("border: 2px solid transparent;")  
                    
                    if hasattr(screenshot, 'widgets') and screenshot.widgets:
                        has_widgets = True

                    sec_button.clicked.connect(lambda _, img=screenshot, btn=sec_button: self.select_single_image(img, btn))
                    secondary_layout.addWidget(sec_button)

                secondary_container.setVisible(False)  

                def toggle_secondary_images(checked, container=secondary_container, button=toggle_button):
                    container.setVisible(checked)
                    if checked:
                        button.setIcon(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/chevron_up.png'))
                    else:
                        button.setIcon(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/chevron_down.png')) 

                toggle_button.toggled.connect(toggle_secondary_images)

            layout.addWidget(main_button)
            if len(screenshots[1:])>0:
                layout.addWidget(toggle_button)
                layout.addWidget(secondary_container)         

            
            item = qt.QListWidgetItem(self.listWidget)
            item.setSizeHint(qt.QSize(320, 220))  

            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, container_widget)  
            
        scroll_area = qt.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.listWidget)

        
        addButton = qt.QPushButton(_("Add Image"))
        addButton.clicked.connect(self.add_selected_image)

        button_layout = qt.QHBoxLayout()
        button_layout.addWidget(addButton)

        button_widget = qt.QWidget()
        button_widget.setLayout(button_layout)

        
        main_layout = qt.QVBoxLayout()
        main_layout.addWidget(scroll_area)  
        main_layout.addWidget(button_widget)  

        self.dialog.setLayout(main_layout)
        result = self.dialog.exec_()
        

    def select_single_image(self, screenshot, button):
        
        if self.selected_image:
            self.selected_image[1].setStyleSheet("border: 2px solid transparent;")

        self.selected_image = (screenshot, button)
        
        button.setStyleSheet("border: 2px solid blue;")

                
    def make_cover_pixmap(self, info: dict, size=(900, 530,)) -> qt.QPixmap: #Create an image with the tutorial information
        W, H = size
        pm = qt.QPixmap(W, H)
        pm.fill(qt.Qt.white)

        logo_path=self.dir_path + '/../Resources/Icons/3DSlicer.png' #Gets the logo of 3D Slicer
        logo_max_wh=(140, 80)
        line_color=(0, 102, 204)
        line_thickness=6

        title_bg_color = (0, 102, 204, 32)  
        title_text_color = (0, 0, 0)
        title_radius = 14

        marginX, marginTop = 10, 0
        logoSpaceH = logo_max_wh[1] if logo_path else 0
        titleTop = marginTop + logoSpaceH + 40

        p = qt.QPainter(pm)
        p.setRenderHint(qt.QPainter.Antialiasing, True)
        p.setRenderHint(qt.QPainter.TextAntialiasing, True)
        try:
            y_line = 20    
            pen = qt.QPen(qt.QColor(*line_color))
            pen.setWidth(line_thickness)
            pen.setCapStyle(qt.Qt.RoundCap)
            p.setPen(pen)
            p.drawLine(marginX, y_line, W - marginX, y_line)

            if logo_path:
                logo = qt.QPixmap(logo_path)
                if not logo.isNull():
                    maxW, maxH = logo_max_wh
                    logo = logo.scaled(maxW, maxH, qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
                    lx, ly = 20, 30
                    p.drawPixmap(lx, ly, logo)
            # title configuration
            title  = info.get("title", "")

            f_title = qt.QFont()
            f_title.setPointSize(28)
            f_title.setBold(True)
            p.setFont(f_title)
            top_margin = 40 + (logo_max_wh[1] if logo_path else 0)
            title_rect = qt.QRect(40, top_margin, W-80, 120)
            p.setPen(qt.QPen(qt.QColor(0, 0, 0)))
            #Background
            metrics = qt.QFontMetrics(f_title)
            wrapped_height = metrics.boundingRect(title_rect, qt.Qt.AlignCenter | qt.Qt.TextWordWrap, title).height()
            padY, padX = 35, 18
            bg_rect = qt.QRect(
                title_rect.left() - padX,
                title_rect.top() - padY,
                title_rect.width() + 2*padX,
                wrapped_height + 2*padY
            )

            r, g, b, *a = title_bg_color
            alpha = a[0] if a else 40
            brush = qt.QBrush(qt.QColor(r, g, b, alpha))
            p.setBrush(brush)
            p.setPen(qt.QPen(qt.Qt.NoPen))
            p.drawRoundedRect(bg_rect, title_radius, title_radius)

            # Title
            p.setPen(qt.QPen(qt.QColor(*title_text_color)))
            p.drawText(qt.QRect(50, 80, W-80, 120), 
                    qt.Qt.AlignCenter | qt.Qt.TextWordWrap, 
                    title)

            # authors
            f_auth = qt.QFont()
            f_auth.setPointSize(16)
            p.setFont(f_auth)
            p.drawText(qt.QRect(40, 200, W-80, 80),
                    qt.Qt.AlignCenter | qt.Qt.TextWordWrap, 
                    info.get("author", ""))

            # Date
            f_date = qt.QFont()
            f_date.setPointSize(12)
            p.setFont(f_date)
            p.drawText(qt.QRect(40, 280, W-80, 40),
                    qt.Qt.AlignCenter, 
                    info.get("date", ""))

            # Description)
            f_desc = qt.QFont()
            f_desc.setPointSize(12)
            p.setFont(f_desc)
            p.drawText(qt.QRect(80, 340, W-160, 150),
                    qt.Qt.AlignTop | qt.Qt.TextWordWrap, 
                    info.get("desc", ""))
        finally:
            p.end()
        return pm
    
    def make_acknowledments_pixmap(self, info: dict, size=(900, 530,)) -> qt.QPixmap: #Create an image with the tutorial information
        text = info.get("acknowledgments", "")
        if not text:
            return None

        W, H = size
        pm = qt.QPixmap(W, H)
        pm.fill(qt.Qt.white)

        p = qt.QPainter(pm)
        p.setRenderHint(qt.QPainter.Antialiasing, True)
        p.setRenderHint(qt.QPainter.TextAntialiasing, True)
        
        try:
            f_ack = qt.QFont()
            f_ack.setPointSize(16)
            p.setFont(f_ack)
            p.drawText(qt.QRect(40, 200, W-80, 80),
                    qt.Qt.AlignCenter | qt.Qt.TextWordWrap, 
                    info.get("acknowledgments", ""))

        finally:
            p.end()
        return pm