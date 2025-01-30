import slicer
import qt
import json
import math
import os
from Lib.tmLabel import tmLabel
from Lib.Anotations import Notes
from Lib.FileMDHTML import markdownHTMLCreator
import Lib.painter as AnnotationPainter
from slicer import qMRMLWidget
from slicer.i18n import tr as _

ListPositionWhite = []
List_totalImages = []

start = 0 #Indicates when all the images are load for the menu

class TutorialGUI(qt.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        self.rectangles = []
        self.selected_id = None
        self.select_annt = False

        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.start = None
        self.end = None

        self.drawing = False
        self.scree_prev = -1
        self.selected_color = qt.QColor(255, 128, 0)

        self.title = ""
        self.author = ""
        self.date = ""
        self.desc = ""

        self.output_name = "output"
        self.save_annotation = False

        self.metadata_image = None
        self.i_blank = 0

        # Load a UI file
        self.dir_path = os.path.dirname(__file__)
        self.uiWidget = slicer.util.loadUI(self.dir_path+'/../Resources/UI/ScreenshotAnnotator.ui')
        
        # Create a new accessible qt layout component
        self.newlayout = qt.QVBoxLayout()
        self.newlayout.setObjectName("uiWidget")

        # Create new toolbar
        self.addToolBar(self.create_toolbar_menu())
        self.addToolBar(self.create_toolbar_actions())
        self.addToolBar(self.create_toolbar_edit())

        # Add Widget from IU file to new layout
        self.newlayout.addWidget(self.uiWidget)

        # Set self layout with UI components 
        self.setCentralWidget(self.uiWidget)

        width = 1250
        height = 780

        self.setFixedSize(width, height)
        self.setWindowTitle("TutorialMaker - Annotator")

        self.scrollAreaWidgetContents = qt.QWidget()
        self.gridLayout = qt.QGridLayout(self.scrollAreaWidgetContents)
        
        # Add QWidget to QScrollArea
        self.uiWidget.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.imageslayout = qt.QVBoxLayout()

        self.scroll_area = self.uiWidget.findChild(qt.QScrollArea, "scrollArea")
        self.scroll_area.setFixedSize(315, 715) 

        label_width = 900  
        label_height = 530 
        self.label_image = self.uiWidget.findChild(qt.QLabel, "label_imagen")
        self.label_image.setFixedSize(label_width, label_height)

        self.label_image.installEventFilter(self)
        self.label_image.setMouseTracking(True)

        self.background_image = qt.QPixmap(label_width, label_height)
        self.background_image.fill(qt.QColor(255, 255, 255))
        
        self.line_edit = self.uiWidget.findChild(qt.QLineEdit, "lineEdit")
        self.line_edit.setMinimumWidth(label_width)
        self.line_edit.setMaximumWidth(label_width) 

        self.text_edit = self.uiWidget.findChild(qt.QTextEdit, "myTextEdit")
        self.text_edit.setFixedSize(label_width, 150)

        self.annotation_selected = False
        self.w_i = 0

        self.scroll_up_count = 0
        self.scroll_down_count = 0
        self.scroll_threshold = 5
        self.scroll_move = False

        self.widget_collection = []

        self.List_images_annotated =[]
        self.List_tutorial = []

    def eventFilter(self, obj, event):
        if obj == self.label_image:
            if event.type() == qt.QEvent.MouseButtonPress:
                self.mouse_press_event(event)
            elif event.type() == qt.QEvent.MouseMove:
                self.mouse_move_event(event)
            elif event.type() == qt.QEvent.MouseButtonRelease:
                self.mouse_release_event(event)
            elif event.type() == qt.QEvent.Wheel:
                self.wheel_event(event)

    def create_toolbar_menu(self):
        
        toolbar = qt.QToolBar("File", self)
        actionOpen = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/open.png'), _("Open"), self)
        actionSave = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/save.png'), _("Save"), self)
        actionBack = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/back.png'), _("Undo"), self)
        actionDelete = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/remove.png'), _("Delete"), self)
        actionCopy = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/copy.png'), _("Copy"), self)
        actionAdd = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/add.png'), _("Add"), self)
        add_menu = qt.QMenu(self)
       
        toolbar.addAction(actionOpen)
        toolbar.addAction(actionSave)
        toolbar.addAction(actionBack)
        toolbar.addAction(actionDelete)
        toolbar.addAction(actionAdd)
       
        toolbar.addAction(actionCopy)

        actionOpen.triggered.connect(self.open_json_file_dialog)
        actionSave.triggered.connect(self.save_json_file)
        actionBack.triggered.connect(self.delete_annotation)
        actionDelete.triggered.connect(self.delete_screen)
        actionAdd.triggered.connect(self.add_page)
        actionCopy.triggered.connect(self.copy_page)

        toolbar.setMovable(True)
        filepath = os.path.dirname(slicer.util.modulePath("TutorialMaker")) + "/Outputs/Raw/Tutorial.json"
        directory_path = os.path.dirname(filepath)
        with open(filepath, "r", encoding='utf-8') as file:
            data = json.load(file)
            file.close()
        #self.load_all_images(data, directory_path)
        
        self.load_images_tutorial(data,directory_path)
        return toolbar
    
    def create_image_action(image_path):
            widget_action = qt.QWidgetAction(self)
            widget = qt.QWidget()
            layout = qt.QHBoxLayout(widget)
            layout.setContentsMargins(5, 5, 5, 5)  # Espaciado interno

            label = qt.QLabel()
            pixmap = qt.QPixmap(image_path).scaled(icon_size, qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
            label.setPixmap(pixmap)

            layout.addWidget(label)
            widget_action.setDefaultWidget(widget)
            return widget_action

    def create_toolbar_actions(self):
        toolbar = qt.QToolBar("Actions", self)
        
        self.square = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act1.png'), _("Square"), self)
        self.square.setCheckable(True)
        toolbar.addAction(self.square)

        self.circle = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act2.png'), _("Circle"), self)
        self.circle.setCheckable(True)

        self.clck = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/pointer.png'), _("Click"), self)
        self.clck.setCheckable(True)
        toolbar.addAction(self.clck)

        self.arrow = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act3.png'), _("Arrow"), self)
        self.arrow.setCheckable(True)
        toolbar.addAction(self.arrow)

        self.icon_image = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act4.png'), _("Icon"), self)
        self.icon_image.setCheckable(True)

        self.in_text = qt.QAction(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act5.png'), _("Text"), self)
        self.in_text.setCheckable(True) 

        self.icons = {
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
                'active': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act3_p.png'),
                'inactive': qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/act3.png')
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

        self.toolbar_actions = [self.square, self.circle, self.clck, self.arrow, self.icon_image, self.in_text]
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
        self.action7.triggered.connect(self.change_color)

        self.valor = 4
        self.spin_box = qt.QSpinBox()
        self.spin_box.setSuffix(_(" thick."))
        self.spin_box.setMinimum(1)
        self.spin_box.setMaximum(15)
        self.spin_box.setSingleStep(1)
        self.spin_box.setValue(self.valor)
        toolbar.addWidget(self.spin_box)
        self.spin_box.valueChanged.connect(self.actualizar_valor)

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
        self.spin_box_txt.valueChanged.connect(self.actualizar_size)

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
    
    def open_json_file_dialog(self):
        file_dialog = qt.QFileDialog()
        file_dialog.setNameFilter(_("JSON Files (*.json)"))
        file_dialog.exec()

        # Check the result of the file dialog
        if file_dialog.result() == qt.QFileDialog.Accepted:
            # The user selected a file
            selected_file = file_dialog.selectedFiles()[0]
            self.open_json_file(
                
            )
        else:
            # The user canceled the file dialog
            print("The user canceled the file dialog")

    def open_json_file(self, filepath):
        directory_path = os.path.dirname(filepath)
        #print(filepath)
        # Read the data from the file
        with open(filepath, "r", encoding='utf-8') as file:
            data = json.load(file)
            file.close()
        self.add_first_page()
        self.load_all_images(data, directory_path)
        return data
        
    def delete_screen(self):
        pass
    def images_selector(self, images_showed):
        print(images_showed)
        images_tuto = []
        images_tuto= images_showed
        images_tuto.insert(-1, self.dir_path+'/../Resources/NewSlide/white.png')  
        self.dialog = qt.QDialog()
        self.dialog.setWindowTitle("Select an Image")
        self.dialog.setGeometry(100, 100, 800, 600) 
        
        #print("Hola")
        
        self.listWidget = qt.QListWidget()
        self.listWidget.setSelectionMode(qt.QAbstractItemView.MultiSelection) #Multiple selection
        self.listWidget.setIconSize(qt.QSize(300, 300))
        self.listWidget.setViewMode(qt.QListWidget.IconMode)  #Eliminate right bar (where the text is)
        self.listWidget.setResizeMode(qt.QListWidget.Adjust)  
        self.listWidget.setSpacing(10)
        
        self.selected_images_list = [] #Images to be added
        self.final_selected_images = []
        self.item_dict = {} 
        self.original_pixmaps = {}

        for image_path in images_tuto:
            item = qt.QListWidgetItem()
            pixmap = qt.QPixmap(image_path).scaled(300, 300, qt.Qt.KeepAspectRatio)
            icon = qt.QIcon(pixmap)
            item.setIcon(icon)
            item.setData(qt.Qt.UserRole, image_path)  
            self.listWidget.addItem(item)
            self.item_dict[image_path] = item 
            self.original_pixmaps[image_path] = pixmap

        self.listWidget.itemSelectionChanged.connect(self.update_selection_order)

        addButton = qt.QPushButton("Add images")
        addButton.clicked.connect(self.add_selected_to_final_list)  

        buttonBox = qt.QDialogButtonBox(qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.confirmSelection)  # Confirmar la selección
        buttonBox.rejected.connect(self.dialog.reject)  # Cancelar

        layout = qt.QVBoxLayout()
        layout.addWidget(self.listWidget)
        layout.addWidget(addButton)
        layout.addWidget(buttonBox)
        self.dialog.setLayout(layout)

        # Mostrar la ventana
        self.dialog.exec_()
    
        return self.final_selected_images

    def add_selected_to_final_list(self):
        self.final_selected_images = [image_path for _, image_path in self.selected_images_list]
        #print("Final selected images added:", self.final_selected_images)
        self.dialog.accept()
    
        
    def update_selection_order(self):
    
        selected_items = self.listWidget.selectedItems()
        self.selected_images_list = [(i + 1, item.data(qt.Qt.UserRole)) for i, item in enumerate(selected_items)]
        for image_path, item in self.item_dict.items():
            item.setIcon(qt.QIcon(self.original_pixmaps[image_path]))

        for index, (order, image_path) in enumerate(self.selected_images_list):
            item = self.item_dict.get(image_path)
            if item:
                new_pixmap = self.draw_order_on_image(image_path, order)
                item.setIcon(qt.QIcon(new_pixmap))  # Actualizar el ícono con el número

    def draw_order_on_image(self, image_path, order_number):
   
        pixmap = qt.QPixmap(image_path).scaled(300, 300, qt.Qt.KeepAspectRatio)     
        painter = qt.QPainter(pixmap)
        painter.setFont(qt.QFont("Arial", 40, qt.QFont.Bold)) 
        painter.setPen(qt.QColor(255, 0, 0))  
        
        
        painter.drawText(10, 50, str(order_number))  

        painter.end()  
        return pixmap  
    

    def confirmSelection(self):
        # Obtener los elementos seleccionados
        selected_items = self.listWidget.selectedItems()
        selected_images = [item.text() for item in selected_items]  # Extraer los textos (paths) de los ítems seleccionados

       # print("Selected images:", selected_images)
        self.dialog.accept()  # Cerrar el diálogo

    def add_page(self):
        newListImages = self.images_list
        images_showed = self.images_list

        new_images_annotated = self.images_selector(images_showed)
        self.labels = []
        new_annotation = []
        new_annotation_json = []
        cont = 0
        pos = self.scree_prev

        if pos in ListPositionWhite:
            for i, _ in enumerate(ListPositionWhite):
                if ListPositionWhite[i] >= pos:
                    ListPositionWhite[i] = ListPositionWhite[i] +1
            
        ListPositionWhite.append(pos)
        print(pos)
        
        k=0
        for image_path in new_images_annotated:
             self.images_annotated.insert(pos, new_images_annotated[k])
             #pos = pos+1
             k = k+1

       

        new_path = self.dir_path+'/../Resources/NewSlide/white.png'

       
        self.metadata_list.insert(pos, [])
        self.annotations.insert(pos, new_annotation)
        self.annotations_json.insert(pos, new_annotation_json)
        self.steps.insert(pos, "Title")
        self.widgets.insert(pos, "Description")
        

        while self.gridLayout.count():
            widget = self.gridLayout.itemAt(0).widget()
            self.gridLayout.removeWidget(widget)
            widget.deleteLater()

        for img in self.images_annotated:
            try:
                image = qt.QImage(img)
            except Exception as e:
                print(_("An unexpected error occurred while opening file '{image}': {error}".format(image=image, error=str(e))))
                break

            new_size = qt.QSize(280, 165)
            scaled_image = image.scaled(new_size)
            pixmap = qt.QPixmap.fromImage(scaled_image)

            label = tmLabel("QLabel_{}".format(cont), cont)
            label.setObjectName("QLabel_{}".format(cont))
            label.clicked.connect(lambda index=cont: self.label_clicked(index))
            label.setPixmap(pixmap)

            self.gridLayout.addWidget(label)
            self.labels.append(label)
            #self.images_list.append(img)
            
            cont += 1
        print(self.steps)
        self.label_clicked(self.scree_prev - 1 )

    
    def add_first_page(self):
        self.images_annotated = []
        #newListImages = self.images_annotated.copy()  # Create a copy to avoid modifying the original
        #print(newListImages)
        #newListImages2 = []
        self.labels = []
        new_annotation = []
        new_annotation_json = []
        cont = 0
        
        pos = 0
        #if pos in ListPositionWhite:
           # for i, _ in enumerate(ListPositionWhite):
                #if ListPositionWhite[i] >= pos:
                    #ListPositionWhite[i] = ListPositionWhite[i] + 1
        
        ListPositionWhite.append(pos)
        #List_totalImages.insert(pos, -1)
        self.List_images_annotated.insert(pos,-1)
        new_path = self.dir_path + '/../Resources/NewSlide/cover_page.png'
        # Insert new_path at position pos
        self.images_annotated.insert(pos, new_path)
        #newListImages.insert(pos,new_path)
        
        self.metadata_list.insert(pos, [])
        self.annotations.insert(pos, new_annotation)
        self.annotations_json.insert(pos, new_annotation_json)
        self.steps.insert(pos, (" - Add the author's name  and institution here"))
        self.widgets.insert(pos, ("Add a title here"))
        
        #Add the acknowledments page
        new_path = self.dir_path + '/../Resources/NewSlide/Acknowledgments.png'
        i = pos+1
        ListPositionWhite.append(i)
        self.List_images_annotated.insert(i,-1)
        self.images_annotated.insert(i, new_path)
       # List_totalImages.insert(i,-1)
        #newListImages.insert(i, new_path)
       # self.images_annotated.insert(i,new_path)
        self.metadata_list.insert(i, [])
        self.annotations.insert(i, new_annotation)
        self.annotations_json.insert(i, new_annotation_json)
        self.steps.insert(i, (" - Acknowledgments"))
        self.widgets.insert(i, ("Add the acknowledgments here"))
        self.steps.insert(i, (" - Acknowledgments"))
        self.widgets.insert(i, ("Add the acknowledgments here"))
        
        #self.List_images_anotated = [-1,-1]
        # Clear the existing grid layout
        while self.gridLayout.count():
            widget = self.gridLayout.itemAt(0).widget()
            self.gridLayout.removeWidget(widget)
            widget.deleteLater()

        # Repopulate the grid layout with the updated images
        for img in self.images_annotated:
            try:
                image = qt.QImage(img)
                new_size = qt.QSize(280, 165)
                scaled_image = image.scaled(new_size)
                pixmap = qt.QPixmap.fromImage(scaled_image)
                label = tmLabel("QLabel_{}".format(cont), cont)
                label.setObjectName("QLabel_{}".format(cont))
                label.clicked.connect(lambda index=cont: self.label_clicked(index))
                label.setPixmap(pixmap)
                self.gridLayout.addWidget(label)
                self.labels.append(label)
                cont += 1
            except Exception as e:
                print(f"An unexpected error occurred while opening file '{img}': {str(e)}")
                break

        print(self.List_images_annotated)
        print(self.images_annotated)
        #self.images_list = newListImages  # Update the original images_list
        self.label_clicked(0)

    def load_images_tutorial(self, data, directory_path):
        self.annotations = []
        self.annotations_json = []
        self.images_list = []
        self.images_annotated = [] #Just the images that are presented in tutorial
        self.metadata_list = []
        self.labels = []
        self.steps = []
        self.edit_screen = []
        self.widgets = []

        self.title = data["title"]
        self.author = data["author"]
        self.date = data["date"]
        self.desc = data["desc"]
    

        # Load all directories for images and metadata
        k = 0
       
        for step in data["steps"]:
            joinedImage = None
            joinedJson = None
            windowJson = None
            new_annotation = []
            new_annotation_json = []
            k = k+1
            #to obtain the images from the tutorial
            for m_data in step:
                exception_occurred = False
                path_image = directory_path+"/"+m_data["window"]
                List_totalImages.append(k) #Index of the images in the tutorial
                self.images_list.append(path_image) #Path of the images in the tutorial
        #self.add_first_page()


    def copy_page(self):
        newListImages = self.images_list
        self.labels = []
        new_annotation = []
        new_annotation_json = []
        cont = 0

        pos = self.scree_prev
            
        for i, _ in enumerate(ListPositionWhite):
            if ListPositionWhite[i] >= pos:
                ListPositionWhite[i] = ListPositionWhite[i] + 1
                
        List_totalImages.insert(pos,List_totalImages[pos])
        new_path = self.images_list[pos]

        # Insert new_path at position pos
        newListImages.insert(pos, new_path)
        self.metadata_list.insert(pos, self.metadata_list[self.scree_prev])
        self.annotations.insert(pos, new_annotation)
        self.annotations_json.insert(pos, new_annotation_json)
        self.steps.insert(pos, "")
        self.widgets.insert(pos, "")
        #self.images_list = []

        while self.gridLayout.count():
            widget = self.gridLayout.itemAt(0).widget()
            self.gridLayout.removeWidget(widget)
            widget.deleteLater()

        for img in newListImages:
            try:
                image = qt.QImage(img)
            except Exception as e:
                print(_("An unexpected error occurred while opening file '{image}': {error}".format(image=image, error=str(e))))
                break

            new_size = qt.QSize(280, 165)
            scaled_image = image.scaled(new_size)
            pixmap = qt.QPixmap.fromImage(scaled_image)

            label = tmLabel("QLabel_{}".format(cont), cont)
            label.setObjectName("QLabel_{}".format(cont))
            label.clicked.connect(lambda index=cont: self.label_clicked(index))
            label.setPixmap(pixmap)

            self.gridLayout.addWidget(label)
            self.labels.append(label)
            #self.images_list.append(img)
            
            cont += 1
        
        self.label_clicked(self.scree_prev)

    def create_blank_image(self, width, height, color=(255, 255, 255)):
        image = qt.QImage(width, height, qt.QImage.Format_RGB32)
        image.fill(qt.QColor("white"))
        return image

    def load_all_images(self, data, directory_path):
        #self.annotations = []
        #self.annotations_json = []
        #self.images_list = []
        #self.images_annotated = [] #Just the images that are presented in tutorial
        #self.metadata_list = []
        #self.labels = []
        #self.steps = []
        self.edit_screen = []
        #self.widgets = []

        self.title = data["title"]
        self.author = data["author"]
        self.date = data["date"]
        self.desc = data["desc"]
       

        while self.gridLayout.count():
            widget = self.gridLayout.itemAt(0).widget()
            self.gridLayout.removeWidget(widget)
            widget.deleteLater()

        exception_occurred = False
        # Load all directories for images and metadata
        k = 0
       
        for step in data["steps"]:
            joinedImage = None
            joinedJson = None
            windowJson = None
            new_annotation = []
            new_annotation_json = []
            k = k+1
            for m_data in step:
                exception_occurred = False
                path_image = directory_path+"/"+m_data["window"]
                path_meta = directory_path+"/"+m_data["metadata"]
                #List_totalImages.append(k) #Index of the images in the tutorial
                #print(List_totalImages)
                #self.List_tutorial.append(k)
                #self.images_list.append(path_image) #Path of the images in the tutorial
                #print(self.images_list)
                try:
                    if joinedImage == None:
                        with open(path_meta, 'r', encoding='utf-8') as fileT:
                            joinedJson = json.loads(fileT.read())
                            fileT.close()

                        joinedImage = qt.QImage(path_image).copy()
                        print(joinedImage)
                    else:
                        with open(path_meta, 'r', encoding='utf-8') as fileP:
                            fileOp = fileP.read()
                            windowJson = json.loads(fileOp)
                            joinedJson= {**joinedJson, **windowJson}
                            windowJson = windowJson[next(iter(windowJson))]
                            fileP.close()

                        painter = qt.QPainter(joinedImage)
                        windowImage = qt.QImage(path_image).copy()
                        painter.drawImage(qt.QRect(windowJson["position"][0], windowJson["position"][1], windowImage.width(), windowImage.height()), windowImage)
                        painter.end()
                except FileNotFoundError:
                    print(_("File '{path_meta}' was not found.".format(path_meta=path_meta)))
                    exception_occurred = True   
                    break
                except IOError:
                    print(_("Could not open file '{path_meta}'.".format(path_meta=path_meta)))
                    exception_occurred = True
                    break
                except Exception as e:
                    print(_("An unexpected error occurred while opening file '{path_meta}': {error}".format(path_meta=path_meta, error=str(e))))
                    exception_occurred = True
                    break
           
            new_size = qt.QSize(280, 165)
            scaled_image = joinedImage.scaled(new_size)
            pixmap = qt.QPixmap.fromImage(scaled_image)

            label = tmLabel("QLabel_{}".format(k), k)
            label.setObjectName("QLabel_{}".format(k))
            label.clicked.connect(lambda index=k: self.label_clicked(index))
            label.setPixmap(pixmap)
                
            last_wdg = self.find_bottom_right_widget(joinedJson)
            if not last_wdg:
                pass
            else:
                widget_x, widget_y = last_wdg['position']
                widget_width, widget_height = last_wdg['size']

                widget_end_x = widget_x + widget_width
                widget_end_y = widget_y + widget_height

                image = qt.QImage(joinedImage)
                image_width = image.width()
                image_height = image.height()
                print("Size image:",image_width,",",image_height)
                print("last wdg:",last_wdg)

                if widget_end_x == image_width:
                    pass
                else:
                    resized_image = image.scaled(widget_end_x, widget_end_y, qt.Qt.IgnoreAspectRatio, qt.Qt.SmoothTransformation)
                    resized_image.save(path_image)
                    joinedImage = qt.QImage(resized_image).copy()

            self.gridLayout.addWidget(label)
            self.labels.append(label)
            self.images_list.append(path_image)
           
            self.metadata_list.append(joinedJson)
            self.annotations.append(new_annotation)
            self.annotations_json.append(new_annotation_json)
            self.steps.append(_("Write a description here"))
            self.widgets.append(_("Add a title here"))
           
            
            if exception_occurred:
                break
        #self.create_toolbar_menu()
        List_images_tutorial = self.images_list
        #print(self.List_tutorial)
        #print(self.images_list)
        self.add_first_page()
        #self.firts_screen()

    def firts_screen(self):
        self.scree_prev = 0
        path = self.images_list[self.scree_prev]
        self.load_image(path)
        self.line_edit.setText(self.widgets[self.scree_prev])
        self.text_edit.append(self.steps[self.scree_prev])
        label = self.labels[self.scree_prev]
        label.setStyleSheet("border: 2px solid red;")

    def find_bottom_right_widget(self, content):
        max_x = 0
        max_y = 0
        bottom_right_widget = None

        for key, widget in content.items():
            if widget["name"] == "StatusBar":
                #print("StatusBar SI")
                bottom_right_widget = widget
            # pos_x, pos_y = widget["position"]
            # width, height = widget["size"]
            
            # # Calcular la esquina inferior derecha
            # bottom_right_x = pos_x + width
            # bottom_right_y = pos_y + height
            
            # # Comparar con el máximo actual
            # if bottom_right_x > max_x or (bottom_right_x == max_x and bottom_right_y > max_y):
            #     max_x = bottom_right_x
            #     max_y = bottom_right_y
            #     bottom_right_widget = widget


        return bottom_right_widget 

    def label_clicked(self, index):
        if str(self.scree_prev) != -1:
            label = self.labels[self.scree_prev]
            label.setStyleSheet("border: 0px")
            # Save text
            text = self.text_edit.toPlainText()
            self.steps[self.scree_prev] = text
            text = self.line_edit.text
            print(self.steps)
            self.widgets[self.scree_prev] = text
        
        self.text_edit.clear()

        # Load the image to viewer from qlabel selected
        label = self.labels[index]
        label.setStyleSheet("border: 2px solid red;")
        path = self.images_annotated[index]
        self.load_image(path)
        self.metadata_image = self.metadata_list[index]
        self.line_edit.setText(self.widgets[index])
        self.text_edit.append(self.steps[index])
        self.scree_prev = index
        self.draw_annotations()

    def load_image(self, path):
        image = qt.QImage(path)
        x = image.width()
        y = image.height()
        
        label_width = self.label_image.width

        a = x / label_width
        z = y / a

        self.label_image.setFixedSize(label_width, z)

        new_size = qt.QSize(label_width, z)
        scaled_image = image.scaled(new_size, qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
        pixmap = qt.QPixmap.fromImage(scaled_image)

        self.background_image = pixmap
        self.label_image.setPixmap(self.background_image)
        self.text_in.setPlaceholderText("Add text to accompany an arrow here.")

    def showEvent(self, event):
        pass

    def mouse_press_event(self, event):
        self.start = event.pos()
        self.save_annotation = True
        if self.square.isChecked():
            self.select_annt = "rect"
        elif self.circle.isChecked():
            self.select_annt = "crcls"
        elif self.arrow.isChecked():
            self.select_annt = "arwT"
        elif self.icon_image.isChecked():
            self.select_annt = "icon"
            self.end = event.pos()    
        elif self.in_text.isChecked():
            self.select_annt = "text"
            self.end = event.pos()   
        elif self.clck.isChecked():
            self.select_annt = "click"
            self.end = event.pos()

        if self.select_annt != False:
            if self.scroll_move == False:
                self.calculate_annotation()
            else :
                self.calculate_annotation_scroll()
    
    def mouse_move_event(self, event):
        self.start = event.pos()
        self.save_annotation = False
        self.scroll_move = False
        if self.square.isChecked():
            self.select_annt = "rect"
        elif self.circle.isChecked():
            self.select_annt = "crcls"
        elif self.arrow.isChecked():
            self.select_annt = "arwT"
        elif self.icon_image.isChecked():
            self.select_annt = "icon"
            self.end = event.pos()    
        elif self.in_text.isChecked():
            self.select_annt = "text"
            self.end = event.pos()   
        elif self.clck.isChecked():
            self.select_annt = "click"
            self.end = event.pos()   
        else:
            pass

        if self.select_annt != False:
            self.calculate_annotation()

    def mouse_release_event(self, event):
        pass

    def keyPressEvent(self, event):
        if event.key() == qt.Qt.Key_Escape:
            self.select_annt = False
            for action, icons in self.icons.items():
                action.setChecked(False)  
                action.setIcon(icons['inactive'])
            self.draw_annotations()
        elif event.key() == qt.Qt.Key_Z and (event.modifiers() & qt.Qt.ControlModifier or event.modifiers() & qt.Qt.MetaModifier):
            self.delete_annotation()

    def wheel_event(self, event):
        delta = event.angleDelta().y()
        self.scroll_move = True
        if self.annotation_selected == True:
            if delta > 0:
                self.scroll_up_count += 1
                self.scroll_down_count = 0
                if self.scroll_up_count >= self.scroll_threshold:
                    self.scroll_up_count = 0  # Reset the counter after confirmation
                    if self.w_i < len(self.widget_collection)-1:
                        self.w_i+=1
            else:
                self.scroll_down_count += 1
                self.scroll_up_count = 0
                if self.scroll_down_count >= self.scroll_threshold:
                    self.scroll_down_count = 0  # Reset the counter after confirmation
                    if self.w_i > 0:
                        self.w_i-=1
        self.calculate_annotation_scroll()

    def calculate_annotation(self):
        widgets = self.metadata_list[self.scree_prev]

        if not widgets:
            pass
        else :
            pnt_clk = self.map_point(self.start)
            self.widget_collection = self.find_widget(widgets, pnt_clk)
            try:
                wdgts_child = self.select_widget_child(self.widget_collection)
                
                star = None
                end = None

                anotation = None
                if wdgts_child is not None:
                    if self.select_annt == "rect":
                        x_i,y_i = wdgts_child["position"]
                        a,b = wdgts_child["size"]
                        x_f = x_i + a
                        y_f = y_i + b
                        star = self.remap_point(qt.QPoint(x_i, y_i))
                        end = self.remap_point(qt.QPoint(x_f, y_f))
                        anotation = Notes(self.select_annt, star, end, self.selected_color, self.valor, self.fill)
                    elif self.select_annt == "crcls":
                        x_i, y_i = wdgts_child["position"]
                        w, h = wdgts_child["size"]
                        c_x = x_i + w / 2
                        c_y = y_i + h / 2
                        wdgts_child['center'] = [c_x, c_y]
                        wdgts_child['radio'] = [x_i, y_i]
                        star = self.remap_point(qt.QPoint(c_x, c_y))
                        end = self.remap_point(qt.QPoint(x_i, y_i)) 
                        anotation = Notes(self.select_annt, star, end, self.selected_color, self.valor, self.fill)
                    elif self.select_annt == "click":
                        x_i, y_i = wdgts_child["position"]
                        w, h = wdgts_child["size"]
                        offset_x = 3 * w // 4
                        offset_y = 3 * h // 4
                        c_x = x_i + offset_x
                        c_y = y_i + offset_y
                        star = self.remap_point(qt.QPoint(c_x, c_y))
                        
                        anotation = Notes(self.select_annt, star, end, self.selected_color, self.t_px, self.fill, self.dir_icon)
                        wdgts_child['labelText'] = self.text_in.text
                    elif self.select_annt == "arwT":
                        x_i, y_i = wdgts_child["position"]
                        w, h = wdgts_child["size"]

                        td = int(w / 3)
                        bd = int(h / 3)
                        td_2 = int(td / 2)
                        bd_2 = int(bd / 2)

                        top_left = (x_i + td_2 * 1, y_i)
                        top_center = (x_i + td_2 * 3, y_i)
                        top_right = (x_i + td_2 * 5, y_i)

                        right_top = (x_i + w, y_i + bd_2 * 1)
                        right_center = (x_i + w, y_i + bd_2 * 3)
                        right_bottom = (x_i + w, y_i + bd_2 * 5)

                        bottom_left = (x_i + td_2 * 1, y_i + h)
                        bottom_center = (x_i + td_2 * 3, y_i + h)
                        bottom_right = (x_i + td_2 * 5, y_i + h)

                        right_top = (x_i + w,y_i + bd_2 * 1)
                        right_center = (x_i + w, y_i + bd_2 * 3)
                        right_bottom = (x_i + w, y_i + bd_2 * 5)

                        left_top = (x_i, y_i + bd_2 * 1)
                        left_center = (x_i, y_i + bd_2 * 3)
                        left_bottom = (x_i, y_i + bd_2 * 5)
                        
                        p1 = (x_i + td * 1, y_i)
                        p2 = (x_i + td * 2, y_i)                 
                        p3 = (x_i + w, y_i + bd * 1)
                        p4 = (x_i + w, y_i + bd * 2)                
                        p5 = (x_i + td * 2, y_i + h)
                        p6 = (x_i + td * 1, y_i + h)                   
                        p7 = (x_i, y_i + bd * 2)
                        p8 = (x_i, y_i + bd * 1)

                        p0 = (x_i, y_i)
                        p9 = (x_i + w, y_i)
                        p10 = (x_i + w, y_i + h)
                        p11 = (x_i, y_i + h)

                        click = self.map_point(self.start)
                        x = click.x()
                        y = click.y()

                        m1 = (p5[1] - p1[1]) / (p5[0] - p1[0])  # p1 to p5
                        m2 = (p6[1] - p2[1]) / (p6[0] - p2[0])  # p2 to p6
                        m3 = (p7[1] - p3[1]) / (p7[0] - p3[0])  # p7 to p3
                        m4 = (p8[1] - p4[1]) / (p8[0] - p4[0])  # p8 to p4  

                        m5 = (p10[1] - p0[1]) / (p10[0] - p0[0])  # p0 to p10 
                        m6 = (p11[1] - p9[1]) / (p11[0] - p9[0])  # p9 to p11 

                        b1 = p1[1] - m1 * p1[0]
                        b2 = p2[1] - m2 * p2[0]
                        b3 = p7[1] - m3 * p7[0]
                        b4 = p8[1] - m4 * p8[0]
                        b5 = p0[1] - m5 * p0[0]
                        b6 = p9[1] - m6 * p9[0]

                        distance = 80
                        cat = math.sqrt(distance ** 2 / 2)
                        
                        if y > m1 * x + b1 and y > m2 * x + b2:
                            wdgts_child['position_tail'] = [bottom_center[0], bottom_center[1]+distance]
                            star = self.remap_point(qt.QPoint(bottom_center[0], bottom_center[1]))
                            end = self.remap_point(qt.QPoint(bottom_center[0], bottom_center[1]+distance))
                            star_painter = qt.QPoint(bottom_center[0], bottom_center[1])
                            end_painter = qt.QPoint(bottom_center[0], bottom_center[1]+distance)
                        elif y < m2 * x + b2 and y > m6 * x + b6:
                            wdgts_child['position_tail'] = [bottom_left[0]-cat, bottom_left[1]+cat]
                            star = self.remap_point(qt.QPoint(bottom_left[0], bottom_left[1]))
                            end = self.remap_point(qt.QPoint(bottom_left[0]-cat, bottom_left[1]+cat))
                            star_painter = qt.QPoint(bottom_left[0], bottom_left[1])
                            end_painter = qt.QPoint(bottom_left[0]-cat, bottom_left[1]+cat)
                        elif y < m6 * x + b6 and y > m3 * x + b3:
                            wdgts_child['position_tail'] = [left_bottom[0]-cat, left_bottom[1]+cat]
                            star = self.remap_point(qt.QPoint(left_bottom[0], left_bottom[1]))
                            end = self.remap_point(qt.QPoint(left_bottom[0]-cat, left_bottom[1]+cat))
                            star_painter = qt.QPoint(left_bottom[0], left_bottom[1])
                            end_painter = qt.QPoint(left_bottom[0]-cat, left_bottom[1]+cat)
                        elif y > m4 * x + b4 and y < m3 * x + b3:
                            wdgts_child['position_tail'] = [left_center[0]-distance, left_center[1]]
                            star = self.remap_point(qt.QPoint(left_center[0], left_center[1]))
                            end = self.remap_point(qt.QPoint(left_center[0]-distance, left_center[1]))
                            star_painter = qt.QPoint(left_center[0], left_center[1])
                            end_painter = qt.QPoint(left_center[0]-distance, left_center[1])
                        elif y < m4 * x + b4 and y > m5 * x + b5:
                            wdgts_child['position_tail'] = [left_top[0]-cat, left_top[1]-cat]
                            star = self.remap_point(qt.QPoint(left_top[0], left_top[1]))
                            end = self.remap_point(qt.QPoint(left_top[0]-cat, left_top[1]-cat))
                            star_painter = qt.QPoint(left_top[0], left_top[1])
                            end_painter = qt.QPoint(left_top[0]-cat, left_top[1]-cat)
                        elif y < m5 * x + b5 and y > m1 * x + b1:
                            wdgts_child['position_tail'] = [top_left[0]-cat, top_left[1]-cat]
                            star = self.remap_point(qt.QPoint(top_left[0], top_left[1]))
                            end = self.remap_point(qt.QPoint(top_left[0]-cat, top_left[1]-cat))
                            star_painter = qt.QPoint(top_left[0], top_left[1])
                            end_painter = qt.QPoint(top_left[0]-cat, top_left[1]-cat)
                        elif y < m1 * x + b1 and y < m2 * x + b2:
                            wdgts_child['position_tail'] = [top_center[0], top_center[1]-distance]
                            star = self.remap_point(qt.QPoint(top_center[0], top_center[1]))
                            end = self.remap_point(qt.QPoint(top_center[0], top_center[1]-distance))
                            star_painter = qt.QPoint(top_center[0], top_center[1])
                            end_painter = qt.QPoint(top_center[0], top_center[1]-distance)
                        elif y > m2 * x + b2 and y < m6 * x + b6:
                            wdgts_child['position_tail'] = [top_right[0]+cat, top_right[1]-cat]
                            star = self.remap_point(qt.QPoint(top_right[0], top_right[1]))
                            end = self.remap_point(qt.QPoint(top_right[0]+cat, top_right[1]-cat))
                            star_painter = qt.QPoint(top_right[0], top_right[1])
                            end_painter = qt.QPoint(top_right[0]+cat, top_right[1]-cat)
                        elif y > m6 * x + b6 and y < m3 * x + b3:
                            wdgts_child['position_tail'] = [right_top[0]+cat, right_top[1]-cat]
                            star = self.remap_point(qt.QPoint(right_top[0], right_top[1]))
                            end = self.remap_point(qt.QPoint(right_top[0]+cat, right_top[1]-cat))
                            star_painter = qt.QPoint(right_top[0], right_top[1])
                            end_painter = qt.QPoint(right_top[0]+cat, right_top[1]-cat)
                        elif y < m4 * x + b4 and y > m3 * x + b3:
                            wdgts_child['position_tail'] = [right_center[0]+distance, right_center[1]]
                            star = self.remap_point(qt.QPoint(right_center[0], right_center[1]))
                            end = self.remap_point(qt.QPoint(right_center[0]+distance, right_center[1]))
                            star_painter = qt.QPoint(right_center[0], right_center[1])
                            end_painter = qt.QPoint(right_center[0]+distance, right_center[1])
                        elif y > m4 * x + b4 and y < m5 * x + b5:
                            wdgts_child['position_tail'] = [right_bottom[0]+cat, right_bottom[1]+cat]
                            star = self.remap_point(qt.QPoint(right_bottom[0], right_bottom[1]))
                            end = self.remap_point(qt.QPoint(right_bottom[0]+cat, right_bottom[1]+cat))
                            star_painter = qt.QPoint(right_bottom[0], right_bottom[1])
                            end_painter = qt.QPoint(right_bottom[0]+cat, right_bottom[1]+cat)
                        else:
                            wdgts_child['position_tail'] = [bottom_right[0]+cat, bottom_right[1]+cat]
                            star = self.remap_point(qt.QPoint(bottom_right[0], bottom_right[1]))
                            end = self.remap_point(qt.QPoint(bottom_right[0]+cat, bottom_right[1]+cat))
                            star_painter = qt.QPoint(bottom_right[0], bottom_right[1])
                            end_painter = qt.QPoint(bottom_right[0]+cat, bottom_right[1]+cat)

                        wdgts_child['labelPosition'] = [ float(star_painter.x()), float(star_painter.y()), float(end_painter.x()), float(end_painter.y())]
                        wdgts_child['labelText'] = self.text_in.text
                        anotation = Notes(self.select_annt, star, end, self.selected_color, self.valor, self.fill, self.text_in.text, self.t_px)

                    elif self.select_annt == "icon":
                        pass
                    elif self.select_annt == "text":
                        pass
                    else:
                        pass
                    
                    if self.save_annotation == True:
                        self.annotations[self.scree_prev].append(anotation)
                        self.annotations_json[self.scree_prev].append(wdgts_child)
                        self.draw_annotations()
                    else:
                        self.draw_annotations()
                        self.draw_preview(anotation)
            except:
                pass

    def calculate_annotation_scroll(self):
        widgets = self.metadata_list[self.scree_prev]

        if not widgets:
            pass
        else :
            try:
                wdgts_child = self.widget_collection[self.w_i]
                
                star = None
                end = None

                anotation = None
                if wdgts_child is not None:
                    if self.select_annt == "rect":
                        x_i,y_i = wdgts_child["position"]
                        a,b = wdgts_child["size"]
                        x_f = x_i + a
                        y_f = y_i + b
                        star = self.remap_point(qt.QPoint(x_i, y_i))
                        end = self.remap_point(qt.QPoint(x_f, y_f))
                        anotation = Notes(self.select_annt, star, end, self.selected_color, self.valor, self.fill)
                    elif self.select_annt == "crcls":
                        x_i, y_i = wdgts_child["position"]
                        w, h = wdgts_child["size"]
                        c_x = x_i + w / 2
                        c_y = y_i + h / 2
                        wdgts_child['center'] = [c_x, c_y]
                        wdgts_child['radio'] = [x_i, y_i]
                        star = self.remap_point(qt.QPoint(c_x, c_y))
                        end = self.remap_point(qt.QPoint(x_i, y_i)) 
                        anotation = Notes(self.select_annt, star, end, self.selected_color, self.valor, self.fill)
                    elif self.select_annt == "click":
                        x_i, y_i = wdgts_child["position"]
                        w, h = wdgts_child["size"]
                        offset_x = 3 * w // 4
                        offset_y = 3 * h // 4
                        c_x = x_i + offset_x
                        c_y = y_i + offset_y
                        star = self.remap_point(qt.QPoint(c_x, c_y))
                        
                        anotation = Notes(self.select_annt, star, end, self.selected_color, self.t_px, self.fill, self.dir_icon)
                        wdgts_child['labelText'] = self.text_in.text
                    elif self.select_annt == "arwT":
                        x_i, y_i = wdgts_child["position"]
                        w, h = wdgts_child["size"]

                        td = int(w / 3)
                        bd = int(h / 3)
                        td_2 = int(td / 2)
                        bd_2 = int(bd / 2)

                        top_left = (x_i + td_2 * 1, y_i)
                        top_center = (x_i + td_2 * 3, y_i)
                        top_right = (x_i + td_2 * 5, y_i)

                        right_top = (x_i + w, y_i + bd_2 * 1)
                        right_center = (x_i + w, y_i + bd_2 * 3)
                        right_bottom = (x_i + w, y_i + bd_2 * 5)

                        bottom_left = (x_i + td_2 * 1, y_i + h)
                        bottom_center = (x_i + td_2 * 3, y_i + h)
                        bottom_right = (x_i + td_2 * 5, y_i + h)

                        right_top = (x_i + w,y_i + bd_2 * 1)
                        right_center = (x_i + w, y_i + bd_2 * 3)
                        right_bottom = (x_i + w, y_i + bd_2 * 5)

                        left_top = (x_i, y_i + bd_2 * 1)
                        left_center = (x_i, y_i + bd_2 * 3)
                        left_bottom = (x_i, y_i + bd_2 * 5)
                        
                        p1 = (x_i + td * 1, y_i)
                        p2 = (x_i + td * 2, y_i)                 
                        p3 = (x_i + w, y_i + bd * 1)
                        p4 = (x_i + w, y_i + bd * 2)                
                        p5 = (x_i + td * 2, y_i + h)
                        p6 = (x_i + td * 1, y_i + h)                   
                        p7 = (x_i, y_i + bd * 2)
                        p8 = (x_i, y_i + bd * 1)

                        p0 = (x_i, y_i)
                        p9 = (x_i + w, y_i)
                        p10 = (x_i + w, y_i + h)
                        p11 = (x_i, y_i + h)

                        click = self.map_point(self.start)
                        x = click.x()
                        y = click.y()

                        m1 = (p5[1] - p1[1]) / (p5[0] - p1[0])  # p1 to p5
                        m2 = (p6[1] - p2[1]) / (p6[0] - p2[0])  # p2 to p6
                        m3 = (p7[1] - p3[1]) / (p7[0] - p3[0])  # p7 to p3
                        m4 = (p8[1] - p4[1]) / (p8[0] - p4[0])  # p8 to p4  

                        m5 = (p10[1] - p0[1]) / (p10[0] - p0[0])  # p0 to p10 
                        m6 = (p11[1] - p9[1]) / (p11[0] - p9[0])  # p9 to p11 

                        b1 = p1[1] - m1 * p1[0]
                        b2 = p2[1] - m2 * p2[0]
                        b3 = p7[1] - m3 * p7[0]
                        b4 = p8[1] - m4 * p8[0]
                        b5 = p0[1] - m5 * p0[0]
                        b6 = p9[1] - m6 * p9[0]

                        distance = 80
                        cat = math.sqrt(distance ** 2 / 2)
                        
                        if y > m1 * x + b1 and y > m2 * x + b2:
                            wdgts_child['position_tail'] = [bottom_center[0], bottom_center[1]+distance]
                            star = self.remap_point(qt.QPoint(bottom_center[0], bottom_center[1]))
                            end = self.remap_point(qt.QPoint(bottom_center[0], bottom_center[1]+distance))
                            star_painter = qt.QPoint(bottom_center[0], bottom_center[1])
                            end_painter = qt.QPoint(bottom_center[0], bottom_center[1]+distance)
                        elif y < m2 * x + b2 and y > m6 * x + b6:
                            wdgts_child['position_tail'] = [bottom_left[0]-cat, bottom_left[1]+cat]
                            star = self.remap_point(qt.QPoint(bottom_left[0], bottom_left[1]))
                            end = self.remap_point(qt.QPoint(bottom_left[0]-cat, bottom_left[1]+cat))
                            star_painter = qt.QPoint(bottom_left[0], bottom_left[1])
                            end_painter = qt.QPoint(bottom_left[0]-cat, bottom_left[1]+cat)
                        elif y < m6 * x + b6 and y > m3 * x + b3:
                            wdgts_child['position_tail'] = [left_bottom[0]-cat, left_bottom[1]+cat]
                            star = self.remap_point(qt.QPoint(left_bottom[0], left_bottom[1]))
                            end = self.remap_point(qt.QPoint(left_bottom[0]-cat, left_bottom[1]+cat))
                            star_painter = qt.QPoint(left_bottom[0], left_bottom[1])
                            end_painter = qt.QPoint(left_bottom[0]-cat, left_bottom[1]+cat)
                        elif y > m4 * x + b4 and y < m3 * x + b3:
                            wdgts_child['position_tail'] = [left_center[0]-distance, left_center[1]]
                            star = self.remap_point(qt.QPoint(left_center[0], left_center[1]))
                            end = self.remap_point(qt.QPoint(left_center[0]-distance, left_center[1]))
                            star_painter = qt.QPoint(left_center[0], left_center[1])
                            end_painter = qt.QPoint(left_center[0]-distance, left_center[1])
                        elif y < m4 * x + b4 and y > m5 * x + b5:
                            wdgts_child['position_tail'] = [left_top[0]-cat, left_top[1]-cat]
                            star = self.remap_point(qt.QPoint(left_top[0], left_top[1]))
                            end = self.remap_point(qt.QPoint(left_top[0]-cat, left_top[1]-cat))
                            star_painter = qt.QPoint(left_top[0], left_top[1])
                            end_painter = qt.QPoint(left_top[0]-cat, left_top[1]-cat)
                        elif y < m5 * x + b5 and y > m1 * x + b1:
                            wdgts_child['position_tail'] = [top_left[0]-cat, top_left[1]-cat]
                            star = self.remap_point(qt.QPoint(top_left[0], top_left[1]))
                            end = self.remap_point(qt.QPoint(top_left[0]-cat, top_left[1]-cat))
                            star_painter = qt.QPoint(top_left[0], top_left[1])
                            end_painter = qt.QPoint(top_left[0]-cat, top_left[1]-cat)
                        elif y < m1 * x + b1 and y < m2 * x + b2:
                            wdgts_child['position_tail'] = [top_center[0], top_center[1]-distance]
                            star = self.remap_point(qt.QPoint(top_center[0], top_center[1]))
                            end = self.remap_point(qt.QPoint(top_center[0], top_center[1]-distance))
                            star_painter = qt.QPoint(top_center[0], top_center[1])
                            end_painter = qt.QPoint(top_center[0], top_center[1]-distance)
                        elif y > m2 * x + b2 and y < m6 * x + b6:
                            wdgts_child['position_tail'] = [top_right[0]+cat, top_right[1]-cat]
                            star = self.remap_point(qt.QPoint(top_right[0], top_right[1]))
                            end = self.remap_point(qt.QPoint(top_right[0]+cat, top_right[1]-cat))
                            star_painter = qt.QPoint(top_right[0], top_right[1])
                            end_painter = qt.QPoint(top_right[0]+cat, top_right[1]-cat)
                        elif y > m6 * x + b6 and y < m3 * x + b3:
                            wdgts_child['position_tail'] = [right_top[0]+cat, right_top[1]-cat]
                            star = self.remap_point(qt.QPoint(right_top[0], right_top[1]))
                            end = self.remap_point(qt.QPoint(right_top[0]+cat, right_top[1]-cat))
                            star_painter = qt.QPoint(right_top[0], right_top[1])
                            end_painter = qt.QPoint(right_top[0]+cat, right_top[1]-cat)
                        elif y < m4 * x + b4 and y > m3 * x + b3:
                            wdgts_child['position_tail'] = [right_center[0]+distance, right_center[1]]
                            star = self.remap_point(qt.QPoint(right_center[0], right_center[1]))
                            end = self.remap_point(qt.QPoint(right_center[0]+distance, right_center[1]))
                            star_painter = qt.QPoint(right_center[0], right_center[1])
                            end_painter = qt.QPoint(right_center[0]+distance, right_center[1])
                        elif y > m4 * x + b4 and y < m5 * x + b5:
                            wdgts_child['position_tail'] = [right_bottom[0]+cat, right_bottom[1]+cat]
                            star = self.remap_point(qt.QPoint(right_bottom[0], right_bottom[1]))
                            end = self.remap_point(qt.QPoint(right_bottom[0]+cat, right_bottom[1]+cat))
                            star_painter = qt.QPoint(right_bottom[0], right_bottom[1])
                            end_painter = qt.QPoint(right_bottom[0]+cat, right_bottom[1]+cat)
                        else:
                            wdgts_child['position_tail'] = [bottom_right[0]+cat, bottom_right[1]+cat]
                            star = self.remap_point(qt.QPoint(bottom_right[0], bottom_right[1]))
                            end = self.remap_point(qt.QPoint(bottom_right[0]+cat, bottom_right[1]+cat))
                            star_painter = qt.QPoint(bottom_right[0], bottom_right[1])
                            end_painter = qt.QPoint(bottom_right[0]+cat, bottom_right[1]+cat)

                        wdgts_child['labelPosition'] = [ float(star_painter.x()), float(star_painter.y()), float(end_painter.x()), float(end_painter.y())]
                        wdgts_child['labelText'] = self.text_in.text
                        anotation = Notes(self.select_annt, star, end, self.selected_color, self.valor, self.fill, self.text_in.text, self.t_px)

                    elif self.select_annt == "icon":
                        pass
                    elif self.select_annt == "text":
                        pass
                    else:
                        pass
                    
                    if self.save_annotation == True:
                        self.annotations[self.scree_prev].append(anotation)
                        self.annotations_json[self.scree_prev].append(wdgts_child)
                        self.draw_annotations()
                    else:
                        self.draw_annotations()
                        self.draw_preview(anotation)
            except:
                pass

    def find_widget(self, widgets_json, pnt_clk):
        w_match = []
        x = pnt_clk.x()
        y = pnt_clk.y()
        
        widgets = widgets_json

        for id, info in widgets.items():
            rect_x, rect_y = info["position"]
            rect_width, rect_height = info["size"]
            if rect_x <= x <= rect_x + rect_width and rect_y <= y <= rect_y + rect_height:
                w_match.append(info)
        
        return w_match
    
    def select_widget_child(self, all_widgets):
        last_wdgt = None
        if len(all_widgets) > 0:
            self.w_i = len(all_widgets)-1
        else :
            self.w_i = len(all_widgets)
        last_wdgt  =  all_widgets[self.w_i]
        return last_wdgt
    
    def map_point(self, p):
        image = qt.QImage(self.images_annotated[self.scree_prev])
        x = image.width()
        y = image.height()
        
        label_width = self.label_image.width
        label_height = self.label_image.height

        x_ratio = p.x() / label_width
        y_ratio = p.y() / label_height
        
        new_x = int(x * x_ratio)
        new_y = int(y * y_ratio)

        new_point = qt.QPoint(new_x, new_y)
        
        return new_point

    def remap_point(self, p):
        image = qt.QImage(self.images_annotated[self.scree_prev])
        x = image.width()
        y = image.height()

        label_width = self.label_image.width
        label_height = self.label_image.height

        rel_x = p.x() / x
        rel_y = p.y() / y

        new_x = int(label_width * rel_x)
        new_y = int(label_height * rel_y)

        new_point = qt.QPoint(new_x, new_y)

        return new_point

    def draw_annotations(self):
        pixmap = self.label_image.pixmap
        painter = qt.QPainter(pixmap)
        painter.drawPixmap(self.label_image.rect, self.background_image)

        for antts in self.annotations[self.scree_prev]:
            pen = qt.QPen(antts.cl)
            pen.setWidth(antts.tk)
            painter.setPen(pen)
            painter.setBrush(qt.QBrush()) if antts.fl == False else painter.setBrush(qt.QBrush(qt.QColor(antts.cl)))
            if antts.tp == "rect":
                painter.drawRect(qt.QRect(antts.ip, antts.fp))
            elif antts.tp == "crcls":
                painter.drawEllipse(antts.ip, self.Mdistance(antts.ip, antts.fp), self.Mdistance(antts.ip, antts.fp))
            elif antts.tp == "click":
                painter.drawImage(antts.ip, self.new_image)
            elif antts.tp == "arwT":
                txt = self.split_string_to_dict(antts.tx)
                painter.drawPath(self.arrowPath(antts.tp, antts.ip, antts.fp))
                pen = qt.QPen(qt.QColor(255, 255, 255))
                painter.setPen(qt.Qt.NoPen)
                painter.setBrush(qt.QBrush(qt.QColor(antts.cl)))
                sbv = antts.sz
                font_small = qt.QFont("Arial", sbv)
                font_metrics = qt.QFontMetrics(font_small)
                texto=self.long_string(txt)
                l_box = font_metrics.horizontalAdvance(texto) + 10
                painter.setFont(font_small)
                if len(txt)  > 0:
                    bg_h = font_metrics.height() * len(txt) + 3
                    if antts.ip.y() > antts.fp.y():
                        tb_i = qt.QPoint(antts.fp.x()-100, antts.fp.y()-bg_h)
                        tb_f = qt.QPoint(tb_i.x()+l_box+sbv, tb_i.y()+bg_h)
                        painter.drawRect(qt.QRect(tb_i, tb_f))
                        pen = qt.QPen(qt.QColor(0, 0, 0))
                        painter.setPen(pen)
                        y_position = font_metrics.height()
                        for r in txt:
                            painter.drawText(tb_i.x()+5, tb_i.y()+y_position, r)
                            y_position+=font_metrics.height()
                    elif antts.ip.y() < antts.fp.y():
                        tb_i = qt.QPoint(antts.fp.x()-100, antts.fp.y())
                        tb_f = qt.QPoint(tb_i.x()+l_box+sbv, tb_i.y()+bg_h)
                        painter.drawRect(qt.QRect(tb_i, tb_f))
                        pen = qt.QPen(qt.QColor(0, 0, 0))
                        painter.setPen(pen)
                        y_position = font_metrics.height()
                        for r in txt:
                            painter.drawText(tb_i.x()+5, tb_i.y()+y_position, r)
                            y_position+=font_metrics.height()
                    elif antts.ip.x() > antts.fp.x():
                        tb_i = qt.QPoint(antts.fp.x()-l_box, antts.fp.y()-10)
                        tb_f = qt.QPoint(tb_i.x()+l_box+sbv, tb_i.y()+bg_h)
                        painter.drawRect(qt.QRect(tb_i, tb_f))
                        pen = qt.QPen(qt.QColor(0, 0, 0))
                        painter.setPen(pen)
                        y_position = font_metrics.height()
                        for r in txt:
                            painter.drawText(tb_i.x()+5, tb_i.y()+y_position, r)
                            y_position+=font_metrics.height()
                    elif antts.ip.x() < antts.fp.x():
                        tb_i = qt.QPoint(antts.fp.x(), antts.fp.y()-10)
                        tb_f = qt.QPoint(tb_i.x()+l_box+sbv, tb_i.y()+bg_h)
                        painter.drawRect(qt.QRect(tb_i, tb_f))
                        pen = qt.QPen(qt.QColor(0, 0, 0))
                        painter.setPen(pen)
                        y_position = font_metrics.height()
                        for r in txt:
                            painter.drawText(tb_i.x()+5, tb_i.y()+y_position, r)
                            y_position+=font_metrics.height()
            elif antts.tp == "icon":
                painter.drawImage(antts.ip, qt.QImage(antts.tx))
            elif antts.tp == "text":
                font_small = qt.QFont("Arial", antts.tk)
                painter.setFont(font_small)
                painter.drawText(antts.ip.x(), antts.ip.y(), antts.tx)
        
        painter.end()
        self.label_image.setPixmap(pixmap)

    def draw_preview(self, antt):
        pixmap = self.label_image.pixmap
        painter = qt.QPainter(pixmap)
        painter.drawPixmap(self.label_image.rect, self.background_image)

        for antts in self.annotations[self.scree_prev]:
            pen = qt.QPen(antts.cl)
            pen.setWidth(antts.tk)
            painter.setPen(pen)
            painter.setBrush(qt.QBrush()) if antts.fl == False else painter.setBrush(qt.QBrush(qt.QColor(antts.cl)))
            if antts.tp == "rect":
                painter.drawRect(qt.QRect(antts.ip, antts.fp))
            elif antts.tp == "crcls":
                painter.drawEllipse(antts.ip, self.Mdistance(antts.ip, antts.fp), self.Mdistance(antts.ip, antts.fp))
            elif antts.tp == "click":
                painter.drawImage(antts.ip, self.new_image)
            elif antts.tp == "arwT":
                txt = self.split_string_to_dict(antts.tx)
                painter.drawPath(self.arrowPath(antts.tp, antts.ip, antts.fp))
                pen = qt.QPen(qt.QColor(255, 255, 255))
                painter.setPen(qt.Qt.NoPen)
                painter.setBrush(qt.QBrush(qt.QColor(antts.cl)))
                sbv = antts.sz
                font_small = qt.QFont("Arial", sbv)
                font_metrics = qt.QFontMetrics(font_small)
                texto=self.long_string(txt)
                l_box = font_metrics.horizontalAdvance(texto) + 10
                painter.setFont(font_small)
                if len(txt) > 0:
                    bg_h = font_metrics.height() * len(txt) + 3
                    if antts.ip.y() > antts.fp.y():
                        tb_i = qt.QPoint(antts.fp.x()-100, antts.fp.y()-bg_h)
                        tb_f = qt.QPoint(tb_i.x()+l_box+sbv, tb_i.y()+bg_h)
                        painter.drawRect(qt.QRect(tb_i, tb_f))
                        pen = qt.QPen(qt.QColor(0, 0, 0))
                        painter.setPen(pen)
                        y_position = font_metrics.height()
                        for r in txt:
                            painter.drawText(tb_i.x()+5, tb_i.y()+y_position, r)
                            y_position+=font_metrics.height()
                    elif antts.ip.y() < antts.fp.y():
                        tb_i = qt.QPoint(antts.fp.x()-100, antts.fp.y())
                        tb_f = qt.QPoint(tb_i.x()+l_box+sbv, tb_i.y()+bg_h)
                        painter.drawRect(qt.QRect(tb_i, tb_f))
                        pen = qt.QPen(qt.QColor(0, 0, 0))
                        painter.setPen(pen)
                        y_position = font_metrics.height()
                        for r in txt:
                            painter.drawText(tb_i.x()+5, tb_i.y()+y_position, r)
                            y_position+=font_metrics.height()
                    elif antts.ip.x() > antts.fp.x():
                        tb_i = qt.QPoint(antts.fp.x()-l_box, antts.fp.y()-10)
                        tb_f = qt.QPoint(tb_i.x()+l_box+sbv, tb_i.y()+bg_h)
                        painter.drawRect(qt.QRect(tb_i, tb_f))
                        pen = qt.QPen(qt.QColor(0, 0, 0))
                        painter.setPen(pen)
                        y_position = font_metrics.height()
                        for r in txt:
                            painter.drawText(tb_i.x()+5, tb_i.y()+y_position, r)
                            y_position+=font_metrics.height()
                    elif antts.ip.x() < antts.fp.x():
                        tb_i = qt.QPoint(antts.fp.x(), antts.fp.y()-10)
                        tb_f = qt.QPoint(tb_i.x()+l_box+sbv, tb_i.y()+bg_h)
                        painter.drawRect(qt.QRect(tb_i, tb_f))
                        pen = qt.QPen(qt.QColor(0, 0, 0))
                        painter.setPen(pen)
                        y_position = font_metrics.height()
                        for r in txt:
                            painter.drawText(tb_i.x()+5, tb_i.y()+y_position, r)
                            y_position+=font_metrics.height()
            elif antts.tp == "icon":
                painter.drawImage(antts.ip, qt.QImage(antts.tx))
            elif antts.tp == "text":
                font_small = qt.QFont("Arial", antts.tk)
                painter.setFont(font_small)
                painter.drawText(antts.ip.x(), antts.ip.y(), antts.tx)

        pen = qt.QPen(antt.cl)
        pen.setWidth(antt.tk)
        painter.setPen(pen)

        painter.setBrush(qt.QBrush()) if antt.fl == False else painter.setBrush(qt.QBrush(qt.QColor(antt.cl)))
        if antt.tp == "rect":
            painter.drawRect(qt.QRect(antt.ip, antt.fp))
        elif antt.tp == "crcls":
            painter.drawEllipse(antt.ip, self.Mdistance(antt.ip, antt.fp), self.Mdistance(antt.ip, antt.fp))
        elif antt.tp == "click":
            painter.drawImage(antt.ip, self.new_image)
        elif antt.tp == "arwT":
            txt = self.split_string_to_dict(antt.tx)
            painter.drawPath(self.arrowPath(antt.tp, antt.ip, antt.fp))
            pen = qt.QPen(qt.QColor(255, 255, 255))
            painter.setPen(qt.Qt.NoPen)
            painter.setBrush(qt.QBrush(self.selected_color)) #self.selected_color
            sbv = self.t_px
            font_small = qt.QFont("Arial", sbv)
            font_metrics = qt.QFontMetrics(font_small)
            texto=self.long_string(txt)
            l_box = font_metrics.horizontalAdvance(texto) + 10
            painter.setFont(font_small)
            if len(txt) > 0 and antt.tx!="Add text to accompany an arrow here.":
                bg_h = font_metrics.height() * len(txt) + 3
                if antt.ip.y() > antt.fp.y():
                    tb_i = qt.QPoint(antt.fp.x()-100, antt.fp.y()-bg_h)
                    tb_f = qt.QPoint(tb_i.x()+l_box+sbv, tb_i.y()+bg_h)
                    painter.drawRect(qt.QRect(tb_i, tb_f))
                    pen = qt.QPen(qt.QColor(0, 0, 0))
                    painter.setPen(pen)
                    y_position = font_metrics.height()
                    for r in txt:
                        painter.drawText(tb_i.x()+5, tb_i.y()+y_position, r)
                        y_position+=font_metrics.height()
                elif antt.ip.y() < antt.fp.y():
                    tb_i = qt.QPoint(antt.fp.x()-100, antt.fp.y())
                    tb_f = qt.QPoint(tb_i.x()+l_box+sbv, tb_i.y()+bg_h)
                    painter.drawRect(qt.QRect(tb_i, tb_f))
                    pen = qt.QPen(qt.QColor(0, 0, 0))
                    painter.setPen(pen)
                    y_position = font_metrics.height()
                    for r in txt:
                        painter.drawText(tb_i.x()+5, tb_i.y()+y_position, r)
                        y_position+=font_metrics.height()               
                elif antt.ip.x() > antt.fp.x():
                    tb_i = qt.QPoint(antt.fp.x()-l_box, antt.fp.y()-10)
                    tb_f = qt.QPoint(tb_i.x()+l_box+sbv, tb_i.y()+bg_h)
                    painter.drawRect(qt.QRect(tb_i, tb_f))
                    pen = qt.QPen(qt.QColor(0, 0, 0))
                    painter.setPen(pen)
                    y_position = font_metrics.height()
                    for r in txt:
                        painter.drawText(tb_i.x()+5, tb_i.y()+y_position, r)
                        y_position+=font_metrics.height()
                elif antt.ip.x() < antt.fp.x():
                    tb_i = qt.QPoint(antt.fp.x(), antt.fp.y()-10)
                    tb_f = qt.QPoint(tb_i.x()+l_box+sbv, tb_i.y()+bg_h)
                    painter.drawRect(qt.QRect(tb_i, tb_f))
                    pen = qt.QPen(qt.QColor(0, 0, 0))
                    painter.setPen(pen)
                    y_position = font_metrics.height()
                    for r in txt:
                        painter.drawText(tb_i.x()+5, tb_i.y()+y_position, r)
                        y_position+=font_metrics.height()
        elif antt.tp == "icon":
            painter.drawImage(antt.ip, qt.QImage(antt.tx))
        elif antt.tp == "text":
            font_small = qt.QFont("Arial", antt.tk)
            painter.setFont(font_small)
            painter.drawText(antt.ip.x(), antt.ip.y(), antt.tx)
        
        painter.end()
        self.label_image.setPixmap(pixmap)
    
    def split_string_to_dict(self, input_string):
        words = input_string.split() 
        result_dict = []
        current_string = ""
        for word in words:
            if len(current_string) + len(word) + 1 < 30:
                if current_string:
                    current_string += " "
                current_string += word
            else:
                result_dict.append(current_string)
                current_string = word
        if current_string:
            result_dict.append(current_string)

        return result_dict
    
    def long_string(self, tex):
        longest_string = ""
        for r in tex:
            if len(r) > len(longest_string):
                longest_string = r

        return longest_string


    def figure_form(self, p_ini, p_fin):
        a1 = p_ini.x()
        a2 = p_ini.y()
        a3 = p_fin.x()
        a4 = p_fin.y()
        return qt.QRect(p_ini, p_fin)

    def Mdistance(self, p1, p2):
        if p2 == None:
            p2 = qt.QPoint(p1.x(), p1.y())
        d = abs(((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2) ** 0.5)
        return d
    
    def arrowPath(self, ty, p1, p2):
        path = qt.QPainterPath()
        tip = abs(int((((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2) ** 0.5)/4))
        tip = 10#tip if tip < 15 else 15
        x = p2.x() - p1.x()
        y = p2.y() - p1.y()
        if x >= 0 and y >= 0: # 4ro
            path.moveTo(qt.QPointF(p1)) 
            path.lineTo(qt.QPointF(p2))
            pa1_x, pa1y = self.rotate_point((p1.x()-tip, p1.y()+tip), p1, self.angle(x, y)-90)
            pa2_x, pa2y = self.rotate_point((p1.x()+tip, p1.y()+tip), p1, self.angle(x, y)-90)
            path.moveTo(pa1_x, pa1y)
            path.lineTo(qt.QPointF(p1))
            path.lineTo(pa2_x, pa2y)
        elif x < 0 and y >= 0: # 3ro
            path.moveTo(qt.QPointF(p1))  
            path.lineTo(qt.QPointF(p2))
            pa1_x, pa1y = self.rotate_point((p1.x()-tip, p1.y()+tip), p1, self.angle(x, y)+180)
            pa2_x, pa2y = self.rotate_point((p1.x()-tip, p1.y()-tip), p1, self.angle(x, y)+180)
            path.moveTo(pa1_x, pa1y)
            path.lineTo(qt.QPointF(p1))
            path.lineTo(pa2_x, pa2y)
        elif x < 0 and y < 0: # 3ro
            path.moveTo(qt.QPointF(p1)) 
            path.lineTo(qt.QPointF(p2))
            pa1_x, pa1y = self.rotate_point((p1.x()+tip, p1.y()-tip), p1, self.angle(x, y)+90)
            pa2_x, pa2y = self.rotate_point((p1.x()-tip, p1.y()-tip), p1, self.angle(x, y)+90)
            path.moveTo(pa1_x, pa1y)
            path.lineTo(qt.QPointF(p1))
            path.lineTo(pa2_x, pa2y)
        else: # 1ro
            path.moveTo(qt.QPointF(p1)) 
            path.lineTo(qt.QPointF(p2))
            pa1_x, pa1y = self.rotate_point((p1.x()+tip, p1.y()-tip), p1, self.angle(x, y))
            pa2_x, pa2y = self.rotate_point((p1.x()+tip, p1.y()+tip), p1, self.angle(x, y))
            path.moveTo(pa1_x, pa1y)
            path.lineTo(qt.QPointF(p1))
            path.lineTo(pa2_x, pa2y)
        return path
    
    def angle(self, dx, dy):
        rad = math.atan2(dy, dx)
        deg = math.degrees(rad)
        return deg
    
    def rotate_point(self, point, center, angle):
        angle_rad = math.radians(angle)
        
        x, y = point
        cx = center.x()
        cy = center.y()

        dx = x - cx
        dy = y - cy

        rotated_x = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        rotated_y = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)

        new_x = rotated_x + cx
        new_y = rotated_y + cy

        return int(new_x), int(new_y)

    def change_color(self):
        color_dialog = qt.QColorDialog()
        color_dialog.setCurrentColor(self.selected_color)
        if color_dialog.exec_():
            color = color_dialog.selectedColor()
            self.selected_color = color

    def createColorIcon(self, color):
        pixmap = qt.QPixmap(20, 20)
        pixmap.fill(color)

        return qt.QIcon(pixmap)
    
    def delete_annotation(self):
        if len(self.annotations[self.scree_prev]) != 0:
            self.annotations[self.scree_prev].pop()
            self.annotations_json[self.scree_prev].pop()
        self.draw_annotations()

    def fill_figures(self):
        if self.fill == True:
            self.fill_annot.setChecked(False)
            self.fill = False
            self.fill_annot.setIcon(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/fill_u.png'))
        else:
            self.fill_annot.setChecked(True)
            self.fill = True
            self.fill_annot.setIcon(qt.QIcon(self.dir_path+'/../Resources/Icons/ScreenshotAnnotator/fill_p.png'))

    def open_icon(self):
        selected_file = self.dir_path+'/../Resources/Icons/Painter/click_icon.png'
        self.new_image = qt.QImage(selected_file)
        self.new_image = self.new_image.scaled(20,30)  
        self.dir_icon = selected_file

    def actualizar_valor(self, valor):
        self.valor = valor
    
    def actualizar_size(self, valor):
        self.t_px = valor

    def on_action_triggered(self, sender):
        self.annotation_selected = True
        for action, icons in self.icons.items():
            if action is sender:
                action.setChecked(True)
                action.setIcon(icons['active'])
            else:
                action.setChecked(False)
                action.setIcon(icons['inactive'])
    
    def set_output_name(self, filename):
        self.output_name = filename

    def save_json_file(self):
        # Create json file 
        self.label_clicked(self.scree_prev) 
        json_out = []
        data = {}

        for i, image in enumerate(self.images_annotated, start=1):
            annotations = []
            for annts, wdg in zip(self.annotations[i-1], self.annotations_json[i-1]):
                color_rgb = f"{annts.cl.red()}, {annts.cl.green()}, {annts.cl.blue()}"
                if annts.tp == "rect":
                    annotation = { #Convert all to string
                        "path": wdg["path"],
                        "type": "rectangle",
                        "color": color_rgb, # (r,g,b)
                        "labelText":"", #text on annotation
                        "fontSize": "14", # size of text on annotions 14px 
                    }
                elif annts.tp == "click":
                    annotation = {
                        "path": wdg["path"],
                        "type": "clickMark",
                        "labelText":"", #text on annotation
                        "fontSize": "14", # size of text on annotions 14px 
                    }
                elif annts.tp == "arwT":
                    pos_off = wdg["position_tail"]
                    annotation = {
                        "path": wdg["path"],
                        "type": "arrow",
                        "color": color_rgb,
                        "labelText": wdg["labelText"],
                        "fontSize": annts.sz,
                        "direction_draw" : wdg["labelPosition"] #Enrique Line
                    }
                annotations.append(annotation)

            data[str(i)] = {
                "slide_title":self.widgets[i-1],
                "slide_text": self.steps[i-1],
                "annotations":annotations
            }

        output_file_path = os.path.join(self.dir_path, '..', 'Outputs/Annotations', self.output_name + '.json')
        with open(output_file_path, 'w', encoding='utf-8') as jsonFile:
            json.dump(data, jsonFile, indent=4)
            jsonFile.close()


        # Create MD and HTML file
        tutorialName = self.output_name
        AnnotationPainter.ImageDrawer.StartPaint(os.path.dirname(slicer.util.modulePath("TutorialMaker")) + "/Outputs/Annotations/"+tutorialName+".json",ListPositionWhite, List_totalImages)   
        markdown_creator = markdownHTMLCreator()  
        html_content = markdown_creator.markdown_to_html((os.path.dirname(slicer.util.modulePath("TutorialMaker")) + "/Outputs/Annotations/"+tutorialName), List_totalImages, tutorialName)
        