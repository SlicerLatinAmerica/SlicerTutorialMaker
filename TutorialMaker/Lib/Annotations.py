import os
import qt
import copy
import math
from slicer.i18n import tr as _
from enum import Flag, auto
from Lib.utils import util

class AnnotationType(Flag):
    Nil = auto() # Not for saving
    Arrow = auto()
    Rectangle = auto()
    Circle = auto()
    TextBox = auto()
    Click = auto()
    Selecting = auto()
    Selected = auto()  # Not for saving


class Annotation:
    def __init__(self,
        TargetWidget : dict = None,
        OffsetX : float = 0,
        OffsetY : float = 0,
        OptX : float = 0, #Optional Helper Coordinates Used Differently in each Annotation Type
        OptY : float = 0,
        Text : str = "",
        Type : AnnotationType = None):

        if Type is None or TargetWidget is None :
            raise Exception(_("Annotation needs a widget reference and a valid type"))

        self.optX = OptX
        self.optY = OptY
        self.text = Text
        self.offsetX = OffsetX
        self.offsetY = OffsetY
        self.type = Type
        self.target = TargetWidget

        self.annotationOffset = [0,0]

        self.PERSISTENT = False
        self.drawBoundingBox = False

        self.boundingBoxTopLeft = [0,0]
        self.boundingBoxBottomRight = [0,0]
        self.__selectionSlideEffect = 0

        # Need to change this later, make it loaded through resources
        self.icon_click = qt.QImage(os.path.dirname(__file__) + '/../Resources/Icons/Painter/click_icon.png')
        self.icon_click = self.icon_click.scaled(20,30)

    def setSelectionBoundingBox(self, topLeftX, topLeftY, bottomRightX, bottomRightY):
        padding = 5
        if bottomRightX < topLeftX:
            tmp = topLeftX
            topLeftX = bottomRightX
            bottomRightX = tmp

        if bottomRightY < topLeftY:
            tmp = topLeftY
            topLeftY = bottomRightY
            bottomRightY = tmp

        self.boundingBoxTopLeft = [topLeftX - padding, topLeftY - padding]
        self.boundingBoxBottomRight = [bottomRightX + padding, bottomRightY + padding]

    def getSelectionBoundingBoxSize(self):
        return [self.boundingBoxBottomRight[0] - self.boundingBoxTopLeft[0], self.boundingBoxBottomRight[1] - self.boundingBoxTopLeft[1]]

    def wantsOptHelper(self):
        return self.type in AnnotationType.Arrow | AnnotationType.TextBox

    def wantsOffsetHelper(self):
        return self.type in AnnotationType.Click | AnnotationType.TextBox

    def toDict(self):
        annotationJSON = {"widgetPath": self.target["path"],
                          "type": self.type.name,
                          "offset": [self.offsetX, self.offsetY],
                          "optional": [self.optX, self.optY],
                          "custom": "",
                          "penSettings": {"color": self.color.name(),
                                          "thickness": self.thickness,
                                          "fontSize": self.fontSize},
                           "text": self.text}
        return annotationJSON

    def setOffset(self, Offset : list[int]):
        self.annotationOffset = Offset
        pass

    def setValuesOpt(self, x : float, y: float):
        self.optX = x
        self.optY = y
        pass

    def setValuesOffset(self, x: float, y:float):
        self.offsetX = x
        self.offsetY = y
        pass

    def penConfig(self, color, fontSize, thickness, brush = None, pen = None):
        self.color = color
        self.thickness = thickness
        self.brush = brush
        self.pen = pen
        self.fontSize = fontSize
        pass

    def draw(self, painter : qt.QPainter = None, pen : qt.QPen = None, brush :qt.QBrush = None):
        #Maybe we can organize this better
        targetPos = [self.target["position"][0] - self.annotationOffset[0] + self.offsetX,
                     self.target["position"][1] - self.annotationOffset[1] + self.offsetY]

        #Might as well do this then
        targetSize = self.target["size"]


        targetCenter = [targetPos[0] + targetSize[0]/2,
                        targetPos[1] + targetSize[1]/2]

        pen.setColor(self.color)
        pen.setWidth(self.thickness)
        pen.setStyle(qt.Qt.SolidLine)

        brush.setColor(self.color)
        brush.setStyle(qt.Qt.NoBrush)

        painter.setBrush(brush)
        painter.setPen(pen)

        highlightWidget = True

        if   self.type == AnnotationType.Arrow:
            # So the arrow will be filled
            brush.setStyle(qt.Qt.SolidPattern)
            painter.setBrush(brush)

            arrowRatio = 3 # defined as > 1 (bigger than one) and changes the arrow head angle
            arrowHeadSize = 40
            arrowSize = 90

            optX =  self.optX - targetCenter[0]
            optY = self.optY - targetCenter[1]

            # To better the user experience of moving the helper element
            optX = util.mapFromTo(optX, -targetSize[0], targetSize[0], -1, 1)
            optY = util.mapFromTo(optY, -targetSize[1], targetSize[1], -1, 1)

            # Clamp optional values between -1 and 1
            optX = min(max(-1, optX), 1)
            optY = min(max(-1, optY), 1)

            arrowHead = [targetCenter[0] + optX*targetSize[0]/2,
                         targetCenter[1] + optY*targetSize[1]/2]

            arrowTail = [arrowHead[0] + arrowSize*optX,
                         arrowHead[1] + arrowSize*optY]

            arrowLine = qt.QLineF(qt.QPointF(*arrowHead), qt.QPointF(*arrowTail))

            arrowAngle = math.atan2(-arrowLine.dy(), arrowLine.dx())

            arrowP1 = arrowLine.p1() + qt.QPointF(math.sin(arrowAngle + math.pi / arrowRatio) * arrowHeadSize,
                                                  math.cos(arrowAngle + math.pi / arrowRatio) * arrowHeadSize)

            arrowP2 = arrowLine.p1() + qt.QPointF(math.sin(arrowAngle + math.pi - math.pi / arrowRatio) * arrowHeadSize,
                                                  math.cos(arrowAngle + math.pi - math.pi / arrowRatio) * arrowHeadSize)

            arrowHeadPolygon = qt.QPolygonF()
            arrowHeadPolygon.clear()

            arrowHeadPolygon.append(arrowLine.p1())
            arrowHeadPolygon.append(arrowP1)
            arrowHeadPolygon.append(arrowP2)

            painter.drawLine(arrowLine)
            painter.drawPolygon(arrowHeadPolygon)

            self.setSelectionBoundingBox(*arrowTail, *arrowHead)
            pass
        elif self.type == AnnotationType.Rectangle:
            topLeft = qt.QPoint(targetPos[0], targetPos[1])
            bottomRight = qt.QPoint(targetPos[0] + targetSize[0],targetPos[1] + targetSize[1])
            rectToDraw = qt.QRect(topLeft,bottomRight)
            painter.drawRect(rectToDraw)

            highlightWidget = False
            self.setSelectionBoundingBox(targetPos[0], targetPos[1], targetPos[0] + targetSize[0],targetPos[1] + targetSize[1])
            pass
        elif self.type == AnnotationType.Circle:
            pass
        elif self.type == AnnotationType.TextBox:
            # So the box will be filled
            brush.setStyle(qt.Qt.SolidPattern)
            painter.setBrush(brush)

            # Padding

            yPadding = 6
            xPadding = 6
            lineSpacing = 2

            optX = self.optX - targetCenter[0]
            optY = self.optY - targetCenter[1]

            topLeft = qt.QPoint(targetPos[0], targetPos[1])
            bottomRight = qt.QPoint(targetPos[0] + optX, targetPos[1] + optY)
            rectToDraw = qt.QRect(topLeft,bottomRight)
            painter.drawRect(rectToDraw)

            # Calculate the text break and position
            font = qt.QFont("Arial", self.fontSize)
            painter.setFont(font)
            pen.setColor(qt.Qt.black)
            painter.setPen(pen)

            fontMetrics = qt.QFontMetrics(font)
            fHeight = fontMetrics.height()

            textBoxBottomRight = [targetPos[0] + optX, targetPos[1] + optY]
            textBoxTopLeft = [targetPos[0], targetPos[1]]

            if textBoxBottomRight[0] < textBoxTopLeft[0]:
                tmp = textBoxTopLeft[0]
                textBoxTopLeft[0] = textBoxBottomRight[0]
                textBoxBottomRight[0] = tmp

            if textBoxBottomRight[1] < textBoxTopLeft[1]:
                tmp = textBoxTopLeft[1]
                textBoxTopLeft[1] = textBoxBottomRight[1]
                textBoxBottomRight[1] = tmp

            textStart = [textBoxTopLeft[0] + xPadding,
                         textBoxTopLeft[1] + yPadding + fHeight]

            textToWrite = self.text
            if textToWrite == "":
                textToWrite = _("Write something here")

            textTokens = textToWrite.split()
            textLines = []
            line = ""
            for token in textTokens:
                if fontMetrics.width(line + token) > textBoxBottomRight[0] - textBoxTopLeft[0] - xPadding:
                    textLines.append(copy.deepcopy(line))
                    line = f"{token} "
                    continue
                line += f"{token} "
            textLines.append(line)

            for lineIndex, line in enumerate(textLines):
                painter.drawText(textStart[0], textStart[1] + lineSpacing + fHeight*lineIndex, line)

            self.setSelectionBoundingBox(targetPos[0], targetPos[1], targetPos[0] + optX, targetPos[1] + optY)
        elif self.type == AnnotationType.Click:
            bottomRight = [targetPos[0] + targetSize[0],
                           targetPos[1] + targetSize[1]]

            painter.drawImage(qt.QPoint(*bottomRight), self.icon_click)

            self.setSelectionBoundingBox(*bottomRight, bottomRight[0] + 20,bottomRight[1] + 30)
        pass
        if (self.drawBoundingBox or not self.PERSISTENT) and highlightWidget:
            #Draw bounding box for the widget
            pen.setColor(qt.QColor("white"))
            pen.setWidth(2)
            pen.setStyle(qt.Qt.SolidLine)
            brush.setStyle(qt.Qt.NoBrush)
            painter.setBrush(brush)
            painter.setPen(pen)
            topLeft = qt.QPoint(self.target["position"][0], self.target["position"][1])
            bottomRight = qt.QPoint(self.target["position"][0] + self.target["size"][0],self.target["position"][1] + self.target["size"][1])
            rectToDraw = qt.QRect(topLeft,bottomRight)
            painter.drawRect(rectToDraw)
        if self.drawBoundingBox:
            #Draw bounding box for the annotation
            pen.setColor(qt.QColor("green"))
            pen.setWidth(4)
            pen.setStyle(qt.Qt.DotLine)
            self.__selectionSlideEffect += 0.1
            pen.setDashOffset(self.__selectionSlideEffect)
            brush.setColor(qt.QColor("green"))
            brush.setStyle(qt.Qt.NoBrush)

            painter.setBrush(brush)
            painter.setPen(pen)

            topLeft = qt.QPoint(*self.boundingBoxTopLeft)
            bottomRight = qt.QPoint(*self.boundingBoxBottomRight)
            rectToDraw = qt.QRect(topLeft,bottomRight)
            painter.drawRect(rectToDraw)


class AnnotatorSlide:
    def __init__(self, BackgroundImage : qt.QPixmap, Metadata : dict, Annotations : list[Annotation] = None, WindowOffset : list[int] = None):

        self.image = BackgroundImage
        self.outputImage = self.image.copy()
        self.metadata = Metadata
        if Annotations is None:
            Annotations = []
        if WindowOffset is None:
            WindowOffset = [0,0]
        self.windowOffset = WindowOffset
        self.annotations = Annotations
        self.Active = True

        self.SlideLayout = "Screenshot"
        self.SlideTitle = ""
        self.SlideBody = ""
        pass

    def AddAnnotation(self, annotation : Annotation):
        annotation.setOffset(self.windowOffset)
        self.annotations.append(annotation)
        pass

    def FindWidgetsAtPos(self, posX, posY):
        results = []

        posX += self.windowOffset[0]
        posY += self.windowOffset[1]

        for widget in self.metadata:
            rectX, rectY = widget["position"]
            rectWidth, rectHeight = widget["size"]
            if rectX <= posX <= rectX + rectWidth and rectY <= posY <= rectY + rectHeight:
                results.append(widget)
        return results

    def FindAnnotationsAtPos(self, posX, posY):
        results = []

        for annotation in self.annotations:
            rectX, rectY = annotation.boundingBoxTopLeft
            rectWidth, rectHeight = annotation.getSelectionBoundingBoxSize()
            if rectX <= posX <= rectX + rectWidth and rectY <= posY <= rectY + rectHeight:
                results.append(annotation)

        results.sort(reverse=True, key= lambda x: x.getSelectionBoundingBoxSize()[0]*x.getSelectionBoundingBoxSize()[1])
        return results


    def MapScreenToImage(self, qPos : qt.QPoint, qLabel : qt.QLabel):
        imageSizeX = self.image.width()
        imageSizeY = self.image.height()

        labelWidth = qLabel.width
        labelHeight = qLabel.height

        x = util.mapFromTo(qPos.x(), 0, labelWidth, 0, imageSizeX)
        y = util.mapFromTo(qPos.y(), 0, labelHeight, 0, imageSizeY)

        return [x,y]

    def MapImageToScreen(self, qPos : qt.QPoint, qLabel : qt.QLabel):
        imageSizeX = self.image.width()
        imageSizeY = self.image.height()

        labelWidth = qLabel.width
        labelHeight = qLabel.height

        x = util.mapFromTo(qPos.x(), 0, imageSizeX, 0, labelWidth)
        y = util.mapFromTo(qPos.y(), 0, imageSizeY, 0, labelHeight)

        return [x,y]

    def GetResized(self, resizeX : float = 0, resizeY : float = 0, keepAspectRatio=False) -> qt.QPixmap:
        if resizeX <= 0 or resizeY <= 0:
            return self.outputImage
        if keepAspectRatio:
            self.outputImage.scaled(resizeX, resizeY, qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
        return self.outputImage.scaled(resizeX, resizeY,qt.Qt.IgnoreAspectRatio, qt.Qt.SmoothTransformation)

    def ReDraw(self):
        del self.outputImage
        self.outputImage = self.image.copy()
        self.Draw()

    def Draw(self):
        painter = qt.QPainter(self.outputImage)
        painter.setRenderHint(qt.QPainter.Antialiasing, True)
        pen = qt.QPen()
        brush = qt.QBrush()
        for annotation in self.annotations:
            annotation.draw(painter, pen, brush)
        painter.end()