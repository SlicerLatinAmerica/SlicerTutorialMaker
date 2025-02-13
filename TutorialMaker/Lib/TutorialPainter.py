import qt
import slicer
import os
from slicer.i18n import tr as _
import math

class ImageDrawer:
    def __init__(self):
        self.image_path = None
        self.pixmap_item = None
        self.scene = None
        self.view = None

    def load_image(self, pixmap):
        """
        Load and display an image using QPixmap.

        Title: Load Image into QGraphicsView

        Inputs:
            - pixmap (QPixmap): A tutorial screenshoot as pixmap image to be displayed.

        Outputs:
            None

        Description:
            This method creates a QGraphicsPixmapItem from the provided QPixmap,
            adds it to a new QGraphicsScene, and sets the scene in a new QGraphicsView.
            The view is then displayed.
        """

        # Create a QGraphicsPixmapItem from the QPixmap
        self.pixmap_item = qt.QGraphicsPixmapItem(pixmap)

        # Create a QGraphicsScene and add the item to it
        self.scene = qt.QGraphicsScene()
        self.scene.addItem(self.pixmap_item)

        # Create a QGraphicsView and set the scene
        self.view = qt.QGraphicsView()
        self.view.setScene(self.scene)
        self.view.showFullScreen()


    def draw_rectangle(self, x, y, width, height, text, font_size, color, text_color=qt.Qt.black, pen_width=5, pen_style=qt.Qt.SolidLine):

        """
        Draw a rectangle with optional text below it on the QGraphicsView.

        Inputs:
            - x (int): The x-coordinate of the top-left corner of the rectangle.
            - y (int): The y-coordinate of the top-left corner of the rectangle.
            - width (int): The width of the widget.
            - height (int): The height of the widget.
            - text (str): The text to be displayed below the rectangle.
            - font_size (int): The font size of the text.
            - color (tuple): The color of the rectangle in RGB format (e.g., (255, 0, 0) for red).
            - text_color (QColor, optional): The color of the text. Default is black.
            - pen_width (int, optional): The width of the pen used to draw the rectangle. Default is 5.
            - pen_style (Qt.PenStyle, optional): The style of the pen used to draw the rectangle. Default is SolidLine.

        Outputs:
            - the path of the image with the drawn rectangle

        Description:
            This method draws a rectangle on the QGraphicsView at the specified coordinates
            with the given dimensions and color. It also adds optional text below the rectangle.
            If no image is loaded, it prints an error message.
        """

        if self.view is None:
            print(_("Error: Load an image first."))
            return

        # Create a QGraphicsRectItem (rectangle) and add it to the scene
        rectangle = qt.QGraphicsRectItem(x, y, width, height)
        pen = qt.QPen(qt.QColor.fromRgb(*color))
        pen.setWidth(pen_width)
        pen.setStyle(pen_style)
        rectangle.setPen(pen)
        self.scene.addItem(rectangle)

        # Add text below the rectangle
        if text and text != "Add text to accompany an arrow here.":
            # Create a background rectangle for the text
            text_item = qt.QGraphicsTextItem(self.wrap_text(text))
            text_item.setDefaultTextColor(text_color)
            font = qt.QFont("Arial")
            font.setPixelSize(font_size)
            text_item.setFont(font)

            # Calculate the background size based on the text size
            text_rect = text_item.boundingRect()
            text_background = qt.QGraphicsRectItem(x + width / 2 - text_rect.width() / 2, y + height + 5, text_rect.width(), text_rect.height() + 5)

            text_background.setBrush(qt.QBrush(qt.Qt.white))
            self.scene.addItem(text_background)

            # Set the position of the text on top of the background rectangle
            text_item.setPos(x + width / 2 - text_rect.width() / 2, y + height + 5)
            self.scene.addItem(text_item)

    def arrowPath(self, p1, p2):

        """
            Create a QPainterPath representing an arrow from point p1 to point p2.

            Title: Create Arrow Path

            Inputs:
                - p1 (QPointF): The starting point of the arrow.
                - p2 (QPointF): The ending point of the arrow.

            Outputs:
                QPainterPath: The path representing the arrow.

            Description:
                This method creates a QPainterPath that represents an arrow starting at p1 and ending at p2.
                The arrow's head is created based on the direction and distance between p1 and p2.
        """
        # Initialize a new QPainterPath
        path = qt.QPainterPath()
        
        tip_length = 15
        tip_width = 12
        
        # Calcular diferencias en x e y
        x = p2.x() - p1.x()
        y = p2.y() - p1.y()

        # Determine the quadrant and create the arrow accordingly
        if x >= 0 and y >= 0:  # 4th quadrant
            path.moveTo(qt.QPointF(p1))  # Start point
            path.lineTo(qt.QPointF(p2))
            # Calculate points for the arrowhead
            pa1_x, pa1y = self.rotate_point((p1.x() - tip, p1.y() + tip), p1, self.angle(x, y) - 90)
            pa2_x, pa2y = self.rotate_point((p1.x() + tip, p1.y() + tip), p1, self.angle(x, y) - 90)
            # Draw the arrowhead
            path.moveTo(pa1_x, pa1y)
            path.lineTo(qt.QPointF(p1))
            path.lineTo(pa2_x, pa2y)
        elif x < 0 and y >= 0:  # 3rd quadrant
            path.moveTo(qt.QPointF(p1))  # Start point
            path.lineTo(qt.QPointF(p2))
            # Calculate points for the arrowhead
            pa1_x, pa1y = self.rotate_point((p1.x() - tip, p1.y() + tip), p1, self.angle(x, y) + 180)
            pa2_x, pa2y = self.rotate_point((p1.x() - tip, p1.y() - tip), p1, self.angle(x, y) + 180)
            # Draw the arrowhead
            path.moveTo(pa1_x, pa1y)
            path.lineTo(qt.QPointF(p1))
            path.lineTo(pa2_x, pa2y)
        elif x < 0 and y < 0:  # 2nd quadrant
            path.moveTo(qt.QPointF(p1))  # Start point
            path.lineTo(qt.QPointF(p2))
            # Calculate points for the arrowhead
            pa1_x, pa1y = self.rotate_point((p1.x() + tip, p1.y() - tip), p1, self.angle(x, y) + 90)
            pa2_x, pa2y = self.rotate_point((p1.x() - tip, p1.y() - tip), p1, self.angle(x, y) + 90)
            # Draw the arrowhead
            path.moveTo(pa1_x, pa1y)
            path.lineTo(qt.QPointF(p1))
            path.lineTo(pa2_x, pa2y)
        else:  # 1st quadrant
            path.moveTo(qt.QPointF(p1))  # Start point
            path.lineTo(qt.QPointF(p2))
            # Calculate points for the arrowhead
            pa1_x, pa1y = self.rotate_point((p1.x() + tip, p1.y() - tip), p1, self.angle(x, y))
            pa2_x, pa2y = self.rotate_point((p1.x() + tip, p1.y() + tip), p1, self.angle(x, y))
            # Draw the arrowhead
            path.moveTo(pa1_x, pa1y)
            path.lineTo(qt.QPointF(p1))
            path.lineTo(pa2_x, pa2y)

        return path

    def rotate_point(self, point, center, angle):

        """
        Rotate a point around a center point by a given angle.

        Inputs:
            - point (tuple): The coordinates of the point to be rotated (x, y).
            - center (QPointF): The center point around which the rotation is performed.
            - angle (float): The angle of rotation in degrees.

        Outputs:
            - (int, int): The new coordinates of the rotated point.

        Description:
            This method rotates a given point around a specified center point by a certain angle.
            The angle is given in degrees and is converted to radians for the rotation calculation.
            The method then applies the rotation matrix to compute the new coordinates of the point.
        """

        # Convert the angle to radians
        angle_rad = math.radians(angle)

        # Decompose the point coordinates
        x, y = point
        cx = center.x()
        cy = center.y()

        # Calculate the differences
        dx = x - cx
        dy = y - cy

        # Apply the rotation
        rotated_x = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        rotated_y = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)

        # Calculate the new coordinates
        new_x = rotated_x + cx
        new_y = rotated_y + cy

        # Return the new coordinates as integers
        return int(new_x), int(new_y)

    def angle(self, dx, dy):
        """
        Calculate the angle in degrees between the positive x-axis and the point (dx, dy).

        Title: Calculate Angle

        Inputs:
            - dx (float): The difference in the x-coordinate.
            - dy (float): The difference in the y-coordinate.

        Outputs:
            - deg (float): The angle in degrees between the positive x-axis and the point (dx, dy).

        Description:
            This method calculates the angle in degrees between the positive x-axis and the point (dx, dy).
            It uses the atan2 function to compute the angle in radians and then converts it to degrees.
        """

        # Calculate the angle in radians using atan2, which considers the sign of both dx and dy
        rad = math.atan2(dy, dx)

        # Convert the angle from radians to degrees
        deg = math.degrees(rad)

        # Return the angle in degrees
        return deg

    def add_text_with_background(self, text, end_x, end_y, font_size, back_color ,text_color=qt.Qt.black):
        """
        Add text with a background rectangle to the scene.

        Inputs:
            - text (str): The text to display.
            - end_x (int): The x-coordinate where the text should be positioned.
            - end_y (int): The y-coordinate where the text should be positioned.
            - font_size (int): The font size of the text.
            - text_color (Qt.Color, optional): The color of the text. Default is Qt.black.
            - type (str): type of draw (ej. 'rectangle','arrow','clickMark')

        Outputs:
            None

        Description:
            This method creates a QGraphicsTextItem with the specified text, font size, and color,
            and positions it at (end_x, end_y). It also creates a background rectangle for the text
            and adds both the text item and the background rectangle to the scene.
        """
        # Create the QGraphicsTextItem for the text
        text_item = qt.QGraphicsTextItem(text)
        text_item.setDefaultTextColor(text_color)

        # Set the font to Arial with the specified font size
        font = qt.QFont("Arial")
        font.setPixelSize(font_size)
        text_item.setFont(font)

        # Calculate the bounding rectangle of the text
        text_rect = text_item.boundingRect()

        # Create the background rectangle for the text
        text_background = qt.QGraphicsRectItem(
            (end_x - text_rect.width() / 2) - 8,
            (end_y - text_rect.height() / 2) - 8,
            text_rect.width() + 16 ,
            text_rect.height() + 16
        )
        text_background.setBrush(qt.QBrush(back_color))

        # Add the background rectangle and the text item to the scene
        self.scene.addItem(text_background)
        text_item.setPos(end_x - text_rect.width() / 2 ,end_y - text_rect.height() / 2)
        self.scene.addItem(text_item)


    def draw_arrow(self, start_x, start_y, end_x, end_y, color, text, font_size, pen_width=4, text_color=qt.Qt.black):
        """
        Draw an arrow on the image with optional text positioned based on arrow direction.

        Inputs:
            - start_x (int): The x-coordinate of the starting point of the arrow.
            - start_y (int): The y-coordinate of the starting point of the arrow.
            - end_x (int): The x-coordinate of the ending point of the arrow.
            - end_y (int): The y-coordinate of the ending point of the arrow.
            - color (tuple): The color of the arrow in RGB format.
            - text (str): The text to be displayed near the arrow.
            - font_size (int): The font size of the text.
            - pen_width (int, optional): The width of the arrow's pen. Default is 4.
            - text_color (Qt.Color, optional): The color of the text. Default is Qt.black.

        Outputs:
            None
        """

        if self.view is None:
            print(_("Error: Load an image first."))
            return

        if text and text != "Add text to accompany an arrow here.":
            # Wrap and justify the text before calculating its size
            wrapped_text = self.wrap_text(text)

            # Create a temporary QGraphicsTextItem with the wrapped text to calculate the bounding rectangle size
            temp_text_item = qt.QGraphicsTextItem(wrapped_text)
            font = qt.QFont("Arial")
            font.setPixelSize(font_size + 31)
            temp_text_item.setFont(font)
            text_rect = temp_text_item.boundingRect()

            # Calculate offset dynamically based on text rectangle dimensions
            offset_x, offset_y = 0, 0
            text_width = text_rect.width()
            text_height = text_rect.height()

            # Check if arrow direction is straight (horizontal or vertical)
            if end_x == start_x:  # Vertical arrow
                if end_y > start_y:  # Arrow pointing down
                    offset_y = text_height / 2  # Place below the arrow tip
                else:  # Arrow pointing up
                    offset_y = -text_height / 2   # Place above the arrow tip
            elif end_y == start_y:  # Horizontal arrow
                if end_x > start_x:  # Arrow pointing right
                    offset_x = text_width / 2   # Place to the right of the arrow tip
                else:  # Arrow pointing left
                    offset_x = -text_width / 2  # Place to the left of the arrow tip
            else:  # Diagonal arrow
                if end_x > start_x and end_y > start_y:  # Arrow down-right
                    offset_x, offset_y = text_width / 2, text_height / 2
                elif end_x < start_x and end_y < start_y:  # Arrow up-left
                    offset_x, offset_y = -text_width / 2 , -text_height / 2
                elif end_x > start_x and end_y < start_y:  # Arrow up-right
                    offset_x, offset_y = text_width / 2 , -text_height / 2
                elif end_x < start_x and end_y > start_y:  # Arrow down-left
                    offset_x, offset_y = -text_width / 2 , text_height / 2

            # Add text with calculated dynamic offset
            self.add_text_with_background(
                wrapped_text,
                end_x + offset_x,
                end_y + offset_y,
                font_size + 10,
                qt.QColor.fromRgb(*color),
                qt.Qt.black
            )
            
            # Obtener los límites de la imagen en la escena
            pixmap_rect = self.view.rect  # Obtiene el rectángulo de la imagen en la escena

            print(pixmap_rect)
            if not pixmap_rect.contains(text_bounding_rect):
                print("Fuera")
                print(text_bounding_rect)
                # If the text is outside, reposition it within visible bounds
                screen_height = self.view.height
                screen_width = self.view.width

                if text_position_y < screen_height / 2:  # Top half of the screen
                    new_text_position_y = screen_height - text_height -16
                    end_y = new_text_position_y 
                else:  # Bottom half of the screen
                    new_text_position_y = 16
                    end_y = new_text_position_y + text_height
                
                if end_x < start_x:  # Left side
                    new_text_position_x = 8
                else:  # Right side
                    new_text_position_x = screen_width - text_width -16
                
                end_x = new_text_position_x + text_width / 2
                
                # Recalculate the text rectangle with new coordinates
                #new_text_bounding_rect = qt.QRect(
                 #   new_text_position_x - 8, new_text_position_y - 8,
                 #   text_width + 16, text_height + 16)

                p1 = qt.QPointF(start_x, start_y)
                p2 = qt.QPointF(end_x, end_y)
                arrow_path = self.arrowPath(p1, p2)
                path_item = qt.QGraphicsPathItem(arrow_path)
                pen = qt.QPen(qt.QColor.fromRgb(*color))
                pen.setWidth(3.5)
                brush = qt.QBrush(qt.QColor.fromRgb(*color))  # Mismo color que el borde
                path_item.setPen(pen)
                path_item.setBrush(brush)  # Establece el relleno
                self.scene.addItem(path_item)
        

                # Add text with calculated dynamic offset
                self.add_text_with_background(
                    wrapped_text, 
                    end_x, 
                    end_y, 
                    font_size + 31, 
                    qt.QColor.fromRgb(*color), 
                    qt.Qt.black
                )
            else:
                print("Dentro")
                print(text_bounding_rect)

                p1 = qt.QPointF(start_x, start_y)
                p2 = qt.QPointF(end_x, end_y)
                arrow_path = self.arrowPath(p1, p2)
                path_item = qt.QGraphicsPathItem(arrow_path)
                pen = qt.QPen(qt.QColor.fromRgb(*color))
                pen.setWidth(3.5)
                brush = qt.QBrush(qt.QColor.fromRgb(*color))  # Mismo color que el borde
                path_item.setPen(pen)
                path_item.setBrush(brush)  # Establece el relleno
                self.scene.addItem(path_item)
                                        # Add text with calculated dynamic offset
                self.add_text_with_background(
                    wrapped_text, 
                    end_x + offset_x, 
                    end_y + offset_y, 
                    font_size + 31, 
                    qt.QColor.fromRgb(*color), 
                    qt.Qt.black
                )
                # Create the arrow path and add it to the scene



    def draw_click(self, x, y, text, font_size, text_color=qt.Qt.black):

        """
        Draw a click icon at a specified position on the image with optional text.

        Title: Draw Click Icon

        Inputs:
            - x (int): The x-coordinate of the click icon.
            - y (int): The y-coordinate of the click icon.
            - text (str): The text to be displayed near the click icon.
            - font_size (int): The font size of the text.
            - text_color (Qt.Color, optional): The color of the text. Default is Qt.black.

        Outputs:
            None

        Description:
            This method draws a click icon at a specified position on the image.
            If provided, it also displays text near the click icon. The text is
            displayed with a specified font size and color.
        """

        if self.view is None:
            print(_("Error: Load an image first."))
            return
        path = os.path.dirname(slicer.util.modulePath("TutorialMaker")) + '/Resources/Icons/Painter/click_icon.png'
        icon_pixmap = qt.QPixmap(path).scaledToWidth(30)
        icon_item = qt.QGraphicsPixmapItem(icon_pixmap)
        icon_item.setPos(x, y)
        self.scene.addItem(icon_item)
        bounding_box = icon_item.boundingRect()

        # Add text below the rectangle
        if text and text != "Add text to accompany an arrow here.":
            # Create a background rectangle for the text
            text_item = qt.QGraphicsTextItem(text)
            text_item.setDefaultTextColor(text_color)
            font = qt.QFont("Arial")
            font.setPixelSize(font_size)
            text_item.setFont(font)

            # Calculate the background size based on the text size
            text_rect = text_item.boundingRect()
            text_background = qt.QGraphicsRectItem(x + bounding_box.width(), y + bounding_box.height(), text_rect.width(), text_rect.height() + 5)

            text_background.setBrush(qt.QBrush(qt.Qt.white))
            self.scene.addItem(text_background)

            # Set the position of the text on top of the background rectangle
            text_item.setPos(x + bounding_box.width(), y + bounding_box.height())
            self.scene.addItem(text_item)

    def save_to_png(self, filename):
        """
        Save the contents of the QGraphicsView to a PNG file.

        Title: Save to PNG

        Inputs:
            - filename (str): The name of the file to save.

        Outputs:
            None

        Description:
            This method saves the contents of the QGraphicsView to a PNG file.
            If the view is available, it grabs its contents, saves it to the specified
            filename using a dynamic path, and then closes the view. If the view is not
            available, it prints an error message.
        """

        if self.view is not None:
            dynamic_path = os.path.join(os.getcwd(), filename)
            image = self.view.showFullScreen()
            image = self.view.grab()
            image.save(dynamic_path, "PNG")
            self.view.close()
        else:
            print("Error: No view to save.")

    # TODO: In that moment we will remove the translation and only show in English
    # after define the infrastructre with Weblate or GitHub we will use community translation
    def painter(self, metadata, screenshotData, language):

        """
        Paint annotations on the image based on metadata and screenshot data.

        Inputs:
            - metadata (dict): Metadata containing annotations information.
            - screenshotData (list): List of dictionaries containing widget information.
            - language (str): Language used for annotations (not used in the method).

        Outputs:
            None

        Description:
            This method iterates over annotations in the metadata and draws rectangles,
            arrows, or click marks on the image based on the annotation type. It uses
            screenshot data to determine positions and sizes of widgets. The annotations
            are drawn with specified colors, text, font sizes, and pen widths.
        """

         # Find corresponding widget data in screenshotData
        for item in metadata['annotations']:
            text_ann = ""
            widgetPosX = 0
            widgetPosY = 0
            widgetSizeX = 0
            widgetSizeY = 0

            for widget in screenshotData:
                if widget["path"] == item["path"]:
                    widgetPosX = widget["position"][0]
                    widgetPosY = widget["position"][1]
                    widgetSizeX = widget["size"][0]
                    widgetSizeY = widget["size"][1]
                    text_ann = item["labelText"]

            if item['type'] == 'rectangle':
                self.draw_rectangle(x=widgetPosX,
                                    y=widgetPosY,
                                    width=widgetSizeX ,
                                    height=widgetSizeY,
                                    text=text_ann,
                                    font_size=int(item['fontSize']),
                                    text_color=qt.Qt.black,
                                    color=tuple(map(int, item["color"].split(', '))),
                                    pen_width=5,
                                    pen_style=qt.Qt.SolidLine)

            elif item['type'] == 'arrow':
                self.draw_arrow(start_x= item["direction_draw"][0],
                                start_y= item["direction_draw"][1],
                                end_x= item["direction_draw"][2],
                                end_y= item["direction_draw"][3],
                                color=tuple(map(int, item["color"].split(', '))),
                                pen_width=6,
                                text=text_ann,
                                font_size=int(item['fontSize']),
                                text_color=qt.Qt.black)

            elif item['type'] == 'clickMark':
                self.draw_click(x=widgetPosX + (widgetSizeX / 2),
                                y=widgetPosY + (widgetSizeY / 2),
                                text=text_ann,
                                font_size=int(item['fontSize']),
                                text_color=qt.Qt.black)

    def StartPaint(path,ListPositionWhite, ListoTotalImages):
        """
        Start painting annotations on images and saving them as PNG files.

        Inputs:
            - path (str): Path to the JSON file containing annotation data.
            - ListPositionWhite (list): List of positions to add white images (not used in the current implementation).
            - ListoTotalImages (list): List of indices indicating which images to process.

        Outputs:
            None

        Description:
            This function loads images and corresponding annotation data from a JSON file,
            paints annotations on the images using ImageDrawer methods, and saves each
            annotated image as a PNG file. It handles cases where images are not to be
            annotated (marked by -1 in ListoTotalImages) by skipping them.
        """

        # Initialize ImageDrawer and JSONHandler instances
        import Lib.utils as utils
        image_drawer = ImageDrawer()
        jsonHandler = utils.JSONHandler()
        tutorial = jsonHandler.parseTutorial(True)
        OutputAnnotator = utils.JSONHandler.parseJSON(path)

        cont = 0
        imgSS = 0
        ListPositionWhite.sort()
        for i, annotateSteps in enumerate(OutputAnnotator):
            if(ListoTotalImages[i] == -1):
                if(cont < len(ListPositionWhite)-1):
                    cont = cont + 1
            else:
                screenshot = tutorial.steps[ListoTotalImages[i]].getImage()
                screenshotData = tutorial.steps[ListoTotalImages[i]].getWidgets()
                # Load the image
                image_drawer.load_image(screenshot)
                image_drawer.painter(OutputAnnotator[annotateSteps], screenshotData, 'es')

                # Save the view to a PNG file with a dynamic path
                image_drawer.save_to_png(
                    os.path.dirname(slicer.util.modulePath("TutorialMaker")) + '/Outputs/Translation/output_image_' + str(i) + '.png')

                imgSS = imgSS + 1
            pass

    def wrap_text(self, text, line_length=30):
        """
        Wraps and justifies a given text into multiple lines, ensuring that each line
        does not exceed a specified character limit, and attempting to justify
        the text (even spacing between words).

        Parameters:
        text (str): The input text to be wrapped and justified.
        line_length (int, optional): The maximum number of characters allowed
                                    per line. Default is 30.

        Returns:
        str: The input text split into justified lines, where each line is at most
            `line_length` characters long.
        """
        # List to store the formatted lines
        lines = []

        # Current line being constructed
        current_line = ''

        # Split the text into words
        words = text.split()

        # Iterate through each word in the text
        for word in words:
            # Check if adding the word to the current line will exceed the character limit
            if len(current_line) + len(word) + 1 <= line_length:
                # If it fits, add the word to the current line with a space
                current_line += word + ' '
            else:
                # Justify the current line (if it's not the last line)
                justified_line = self.justify_line(current_line.strip(), line_length)
                lines.append(justified_line)
                # Start a new line with the current word
                current_line = word + ' '

        # Add any remaining text in the current line to the list of lines (without justification)
        if current_line:
            lines.append(current_line.strip())

        # Join the lines with new line characters and return the result
        return '\n'.join(lines)

    def justify_line(self, line, line_length):
        """
        Justifies a single line by adding extra spaces between words
        so that the line length matches `line_length`.

        Parameters:
        line (str): The line of text to be justified.
        line_length (int): The desired length of the line.

        Returns:
        str: The justified line of text.
        """
        words = line.split()

        # If the line contains only one word, return it as is
        if len(words) == 1:
            return line

        # Calculate the number of spaces needed to justify the line
        total_spaces = line_length - len(line) + (len(words) - 1)

        # Calculate how many spaces to add between each word
        space_between_words = total_spaces // (len(words) - 1)
        extra_spaces = total_spaces % (len(words) - 1)

        # Create the justified line by adding spaces between words
        justified_line = ''
        for i, word in enumerate(words[:-1]):
            justified_line += word + ' ' * (space_between_words + (1 if i < extra_spaces else 0))

        # Add the last word without extra spaces
        justified_line += words[-1]

        return justified_line

class Paiter:
    