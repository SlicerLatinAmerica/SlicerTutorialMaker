import slicer
import os
import webbrowser
import qt
from slicer.i18n import tr as _


class markdownHTMLCreator:
    def __init__(self) -> None:
        pass
            
    def show_installing_message(self, message):
        msgBox = qt.QMessageBox()
        msgBox.setIcon(qt.QMessageBox.Information)
        msgBox.setText(message)
        msgBox.setStandardButtons(qt.QMessageBox.NoButton)
        msgBox.show()
        
        # Allow the interface to process events to keep the message box responsive
        slicer.app.processEvents()
        return msgBox
    
    def tutorial_to_markdown(self,path,ListotalImages):
        tutorialName = "fourMin_tutorial"
        metadata = self.getMetadata(path)
        i = len(ListotalImages) -1
        
        with open(path + ".md", 'w', encoding='utf-8') as md_file:
            #Create pages of the tutorial with annotations
            for num,item in enumerate(metadata):            
                numString = str(num)
                if (ListotalImages[num] == -1):
                    if (num == 0 or num ==i):
                        md_file.write('<meta charset="UTF-8">\n')
                        md_file.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
                        md_file.write(f'</style>\n')
                        md_file.write(f'<div class="page">\n')
                        md_file.write(f'    <div class="header-container">\n')
                        md_file.write(f'        <img class="lineImage" src="{os.path.dirname(slicer.util.modulePath("TutorialMaker"))}/Resources/Icons/Painter/line_top.png" alt="Top Line">\n')
                        md_file.write(f'        <img class="logo" src="{os.path.dirname(slicer.util.modulePath("TutorialMaker"))}/Resources/Icons/Painter/slicer.png" alt="Logo">\n')
                        md_file.write(f'    </div>\n')
                        md_file.write(f'    <div class="header">{metadata[item]["slide_title"]}</div>\n')
                        authors = metadata[item]["slide_text"].replace('\n', '<br>')
                        if authors.endswith('<br>'):
                            authors = authors[:-4]
                        md_file.write(f'    <div class="subheader">{authors}</div>\n')       
                        md_file.write('    <div class="footer">\n')
                        md_file.write(f'        <img src="{os.path.dirname(slicer.util.modulePath("TutorialMaker"))}/Resources/Icons/Painter/line_down.png" alt="Bottom Line">\n')
                        md_file.write('    </div>\n')
                        md_file.write('</div>\n')
                        md_file.write('<!-- page break -->\n')
                                            
                        
                    else:
                        md_file.write(f'</style>\n')
                        md_file.write(f'<div class="page">\n')
                        md_file.write(f'    <div class="header-container">\n')
                        md_file.write(f'        <img class="lineImage" src="{os.path.dirname(slicer.util.modulePath("TutorialMaker"))}/Resources/Icons/Painter/line_top.png" alt="Top Line">\n')
                        md_file.write(f'        <img class="logo" src="{os.path.dirname(slicer.util.modulePath("TutorialMaker"))}/Resources/Icons/Painter/slicer.png" alt="Logo">\n')
                        md_file.write(f'    </div>\n')
                        md_file.write(f'    <div class="titulo">{metadata[item]["slide_title"]}</div>\n')
                        #md_file.write(f'    <div class="subheader">{metadata[item]["slide_text"]}</div>\n')       
                        md_file.write(f'    <div class="containerWhite" style="background-color: #ffffff; padding: 20px; margin: 20px auto; max-width: 90%;">')
                        md_file.write(f'        <img class="marginImage" src="{os.path.dirname(slicer.util.modulePath("TutorialMaker"))}/Resources/NewSlide/white.png" style="width: 100%; max-width: 500px;">\n')
                        md_file.write(f'        <div class="textWhite" style="font-size: 18px;">{metadata[item]["slide_text"]}</div>')
                        md_file.write(f'    </div>\n')
                        md_file.write(f'    <div class="footer">\n')
                        md_file.write(f'        <img src="{os.path.dirname(slicer.util.modulePath("TutorialMaker"))}/Resources/Icons/Painter/line_down.png" alt="Bottom Line">')
                        numString = str(num + 1)
                        totalSteps = str(len(metadata) + 1)
                        md_file.write(f'        <div class="footerText"><small><small>Tutorial page {numString}/{totalSteps}</small></small></div>')
                        md_file.write(f'    </div>\n')
                        md_file.write(f'</div>\n')
                        md_file.write(f'<!-- page break -->\n')
                                

                else: 
                    md_file.write(f'</style>\n')
                    md_file.write(f'<div class="page">\n')
                    md_file.write(f'    <div class="header-container">\n')
                    md_file.write(f'        <img class="lineImage" src="{os.path.dirname(slicer.util.modulePath("TutorialMaker"))}/Resources/Icons/Painter/line_top.png" alt="Top Line">')
                    md_file.write(f'        <img class="logo" src="{os.path.dirname(slicer.util.modulePath("TutorialMaker"))}/Resources/Icons/Painter/slicer.png" alt="Logo">')
                    md_file.write(f'    </div>\n')
                    md_file.write(f'    <div class="titulo">{metadata[item]["slide_title"]}</div>\n')
                    #md_file.write(f'    <div class="subheader">{metadata[item]["slide_text"]}</div>\n')       
                    md_file.write(f'    <div class="containerWhite" style="background-color: #ffffff; padding: 20px; margin: 20px auto; max-width: 90%;">\n')
                    md_file.write(f'        <img class="marginImage" src="{os.path.dirname(slicer.util.modulePath("TutorialMaker"))}/Outputs/Translation/output_image_{num}.png" style="max-width: 100px;max-width: 600px;"><br>')
                    md_file.write(f'        <div class="textWhite" style="font-size: 18px;">{metadata[item]["slide_text"]}</div>')
                    md_file.write(f'    </div>\n')
                    md_file.write(f'    <div class="footer">\n')
                    md_file.write(f'        <img src="{os.path.dirname(slicer.util.modulePath("TutorialMaker"))}/Resources/Icons/Painter/line_down.png" alt="Bottom Line">')
                    numString = str(num + 1)
                    totalSteps = str(len(metadata) + 1)
                    md_file.write(f'        <div class="footerText"><small><small>Tutorial page {numString}/{totalSteps}</small></small></div>')
                    md_file.write(f'    </div>')
                    md_file.write(f'</div>')
                    md_file.write(f'<!-- page break -->\n')

            message = _("Markdown file '{tutorialName}' has been generated. Would you like to open it?".format(tutorialName=tutorialName))
            confirm = qt.QMessageBox.question(slicer.util.mainWindow(), _("Markdown Generated"), message,
                                            qt.QMessageBox.Yes | qt.QMessageBox.No)
            if confirm == qt.QMessageBox.Yes:
                webbrowser.open("file://" + path + ".md")



    def markdown_to_html(self,path, ListTotalImages,tutorialName):
        self.tutorial_to_markdown(os.path.dirname(slicer.util.modulePath("TutorialMaker")) + "/Outputs/Annotations/" + tutorialName, ListTotalImages)   
        # Define CSS styles
        styles = """
        <style> 
            @page{
                size: A4 landscape; 
                margin: 10mm; 
            }
             body {
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
            }
            .page {
                width: 100%; "
                max-width: 297mm;
                height: auto;
                display: flex;
                flex-direction: column; 
                justify-content: space-between; 
                align-items: center;
                text-align: center; 
                box-sizing: border-box;
                padding: 10mm; 
          
            }
            .header-container {
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: flex-start; 
                margin-bottom: 20px;
            }
            .lineImage {
                width: 100%; 
            }

            .logo {
                transform: scale(0.4); 
                transform-origin: top left;
            }

            .header {
                background-color: #a8d0e6;
                color: white;
                font-size: 40px;
                font-weight: bold;
                padding: 10px;
                width: 100%;
                box-sizing: border-box;
                text-align: center;
            }

            .subheader {
                font-size: 30px;
                color: gray;
                margin: 10px 0;
                width: 200mm; 
                height: 140mm;
            }

            .footer {
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-top: auto;
            }

            .footer img {
                width: 100%; 
                margin-bottom: 5px;
            }

            .footer-text {
                font-size: 15px;
                color: #666;
            }
            .containerWhite {
                position: relative;
                display: inline-block;
                width: 90%;
                display: block;
                margin-left: auto;
                margin-right: auto;
                margin-bottom:1in;
            }
            .textWhite {
                font-size: 28px;
                text-align:center;
                position: absolute;  
            }
            
            .marginImage {
                width: 500%;
                display: block;
                margin-left: auto;
                margin-right: auto;
            }
            .titulo {
                font-size: 30px;
                font-weight: bold;
                text-align:center;
                align-items: center;
            }
                    
        </style>
        """

        # Read the Markdown file
        with open(path + ".md", 'r', encoding='utf-8') as file:
            md_file = file.read()
            # Combine styleswith the Markdown file
    
        html_content = f"{styles}\n{md_file}"

        # Define the path of the HTML file
        path = path.replace('_WithoutStyle', '')
        output_html_file = path + ".html"
        # Write the Markdown content with the styles in a HTML file
        with open(output_html_file, 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)

        message = _("HTML file '{tutorialName}' has been generated. Would you like to open it?".format(tutorialName=tutorialName))
        confirm = qt.QMessageBox.question(slicer.util.mainWindow(), _("HTML Generated"), message,
                                           qt.QMessageBox.Yes | qt.QMessageBox.No)
        if confirm == qt.QMessageBox.Yes:
            webbrowser.open("file://" + output_html_file)
        #self.onCreatePDFReportButton(output_html_file, path, tutorialName)   
        self.create_pdf(path, ListTotalImages) 
        #self.html_to_pdf(path, output_html_file, tutorialName)

    def getMetadata(self,path):
        import Lib.utils as utils
        path = path + ".json"
        OutputAnnotator = utils.JSONHandler.parseJSON(path)
        return OutputAnnotator
    
    def onCreatePDFReportButton(self, html_file_path, path, tutorialName):
        
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)

        
        printer = qt.QPrinter(qt.QPrinter.PrinterResolution)
        printer.setOutputFormat(qt.QPrinter.PdfFormat)
        printer.setPaperSize(qt.QPrinter.A4)  # A4 size
        printer.setOrientation(qt.QPrinter.Landscape)
        printer.setPageMargins(10, 10, 10, 10, qt.QPrinter.Millimeter)

        output_pdf_file = path + ".pdf"
        printer.setOutputFileName(output_pdf_file)

        with open(html_file_path, "r", encoding="utf-8") as file:
            out_html = file.read()
        pages = out_html.split('<!-- page break -->')
        

     
        doc = qt.QTextDocument()
        cursor = qt.QTextCursor(doc)

        doc.setHtml(out_html)
        page_width = printer.pageRect().width()
        page_height = printer.pageRect().height()
        doc.setPageSize(qt.QSizeF(page_width, page_height))

        doc.setPageSize(qt.QSizeF(printer.paperRect().size()))

        for index, page in enumerate(pages):
            cursor.insertHtml(page)  
        if index < len(pages) - 1:
            cursor.insertText("\f")  

        doc.print(printer)
    
    def create_pdf(self, path, ListotalImages):
        output_pdf_file = path + ".pdf"
        metadata = self.getMetadata(path)
        i = len(ListotalImages) -1

        printer = qt.QPrinter(qt.QPrinter.PrinterResolution)
        printer.setOutputFormat(qt.QPrinter.PdfFormat)
        printer.setPaperSize(qt.QPrinter.A4)  # Tamaño A4
        printer.setOrientation(qt.QPrinter.Landscape)
        printer.setPageMargins(10, 0, 10, 0, qt.QPrinter.Millimeter)
        printer.setOutputFileName(output_pdf_file)

        page_rect = printer.pageRect()
        width = page_rect.width()   
        height = page_rect.height() 

        doc = qt.QTextDocument()
        cursor = qt.QTextCursor(doc)

        for num,item in enumerate(metadata):            
            numString = str(num)
            if (ListotalImages[num] == -1):
                if (num == 0 or num ==i):
                    numString = str(num + 1)
                    totalSteps = str(len(metadata) )
                    self.add_page_divided(cursor,
                            title=metadata[item]["slide_title"],
                            image_path=None,  # No imagen en la portada
                            text=metadata[item]["slide_text"],
                            footer=f"{str(numString)}/{str(totalSteps)}",
                            page_height = height,
                            num_page = num,
                            is_first_title=True,
                            is_white_page=False
                    ) 
                    printer.newPage()
                    
                            
                else:
                    numString = str(num + 1)
                    totalSteps = str(len(metadata) )
                    cursor.insertBlock()
                    cursor.insertText("\f") 
                    self.add_page_divided(cursor,
                            title=metadata[item]["slide_title"],
                            image_path=None,
                            text=metadata[item]["slide_text"],
                            footer = f"{str(numString)}/{str(totalSteps)}",
                            page_height = height,
                            num_page = num,
                            is_first_title= False,
                            is_white_page=True)
                        
            else:
                numString = str(num + 1)
                totalSteps = str(len(metadata) )
                cursor.insertBlock()
                cursor.insertText("\f") 
                self.add_page_divided(cursor,
                        title=metadata[item]["slide_title"],
                        image_path = os.path.join(os.path.dirname(slicer.util.modulePath("TutorialMaker")),"Outputs","Translation",f"output_image_{num}.png"),
                        text=metadata[item]["slide_text"],
                        footer = f"{str(numString)}/{str(totalSteps)}",
                        page_height = height,
                        num_page = num,
                        is_SS_page = True)
                
        doc.setPageSize(qt.QSizeF(printer.pageRect().size()))
        doc.print_(printer)



    def add_page_divided(self, cursor, title, image_path,text,footer, page_height, num_page, is_first_title=False,is_white_page=False, is_SS_page=False):
        section_heights_SS = [0.05, 0.05, 0.2, 0.2, 0.2, 0.1, 0.1] 
        calculated_heights = [int(h * page_height) for h in section_heights_SS]
        center_format = qt.QTextBlockFormat()
        center_format.setAlignment(qt.Qt.AlignCenter)
        left_format = qt.QTextBlockFormat()
        left_format.setAlignment(qt.Qt.AlignLeft)
        right_format = qt.QTextBlockFormat()
        right_format.setAlignment(qt.Qt.AlignRight)

        header_image_path = os.path.join(os.path.dirname(slicer.util.modulePath("TutorialMaker")),"Resources", "Icons","Painter", "line_top.png")
        icon_image_path = os.path.join(os.path.dirname(slicer.util.modulePath("TutorialMaker")),"Resources", "Icons","Painter", "slicer.png")
        footer_image_path = os.path.join(os.path.dirname(slicer.util.modulePath("TutorialMaker")),"Resources", "Icons","Painter", "line_down.png")
        black_image_path = os.path.join(os.path.dirname(slicer.util.modulePath("TutorialMaker")),"Resources", "NewSlide","white.png")

        if is_first_title:
            section_heights_white = [0.06, 0.15, 0.3, 0.1] 
            calculated_heights_white = [int(h * page_height) for h in section_heights_white]
            
            if header_image_path:
                header_image_format = qt.QTextImageFormat()
                header_image_format.setName(header_image_path)
                header_image_format.setWidth(800)  
                header_image_format.setHeight(10)  
                cursor.insertBlock(center_format) 
                cursor.insertImage(header_image_format)
                cursor.insertBlock()  

            if icon_image_path:
                icon_image_format = qt.QTextImageFormat()
                icon_image_format.setName(icon_image_path)
                icon_image_format.setWidth(600)  
                icon_image_format.setHeight(20)  
                cursor.insertBlock(left_format)  
                cursor.insertImage(icon_image_format)
                cursor.insertText("\n\n") 
            current_block = cursor.block()
            doc = cursor.document()
            layout = doc.documentLayout()
            current_pos = layout.blockBoundingRect(current_block).bottom()

            cursor.insertBlock()
            for _ in range(int(calculated_heights_white[0] / 20)):
                cursor.insertText("\n")
            #title
            title_format = qt.QTextCharFormat()
            title_format.setFont(qt.QFont("Times", 16, qt.QFont.Bold))
            if is_white_page == False:
                title_format.setBackground(qt.QColor("#a8d0e6"))
                title_format.setForeground(qt.QColor("#FFFFFF"))
            cursor.insertBlock(center_format) 
            cursor.insertText(title + "\n\n", title_format)

           
            cursor.insertBlock()
            for _ in range(int(calculated_heights_white[1] / 20)):
                cursor.insertText("\n")

            # Text
            authors_format = qt.QTextCharFormat()
            authors_format.setFont(qt.QFont("Times", 12))
            cursor.insertBlock(center_format)  
            cursor.insertText(text + "\n\n", authors_format)

            current_block = cursor.block()    
            doc = cursor.document()
            layout = doc.documentLayout()
            current_pos2 = layout.blockBoundingRect(current_block).bottom()
           
            remaining_space = page_height - current_pos2
            cursor.insertBlock()
            for _ in range(int(calculated_heights_white[2] / 20)):
                cursor.insertText("\n")
            current_block = cursor.block()
            doc = cursor.document()
            layout = doc.documentLayout()
            current_pos2 = layout.blockBoundingRect(current_block).bottom()
           
            if footer_image_path:
                if is_white_page == True:
                    footer_y = current_pos + 400
                else:
                    footer_y = 545
                footer_block_format = qt.QTextBlockFormat()
                footer_block_format.setAlignment(qt.Qt.AlignCenter)

                cursor.movePosition(qt.QTextCursor.Start)
                while cursor.block().layout().position().y() < footer_y:
                    cursor.movePosition(qt.QTextCursor.NextBlock)

                
                footer_image_format = qt.QTextImageFormat()
                footer_image_format.setName(footer_image_path)
                footer_image_format.setWidth(800)  
                footer_image_format.setHeight(10) 
                
                
                cursor.insertBlock(footer_block_format)
                cursor.insertImage(footer_image_format)
                if is_white_page == True:
                    footer_format = qt.QTextCharFormat()
                    footer_format.setFont(qt.QFont("Times", 7))
                    cursor.insertBlock(right_format)
                    cursor.insertText(footer + "\n", footer_format)
            current_block = cursor.block()
            doc = cursor.document()
            
    
            layout = doc.documentLayout()
            current_pos = layout.blockBoundingRect(current_block).bottom()
            
         
            remaining_space = page_height - current_pos
            lines_needed = int(remaining_space / 20)  
            
    
            cursor.insertBlock()
            for _ in range(max(0, lines_needed)):
                cursor.insertText("\n")

        if is_white_page:
            section_heights_white = [0.05, 0.07, 0.29, 0.05] 
            calculated_heights_white = [int(h * page_height-10) for h in section_heights_white]
            
            if header_image_path:
                header_image_format = qt.QTextImageFormat()
                header_image_format.setName(header_image_path)
                header_image_format.setWidth(800)  
                header_image_format.setHeight(10)  
                cursor.insertBlock(center_format) 
                cursor.insertImage(header_image_format)
                cursor.insertBlock()  

            if icon_image_path:
                icon_image_format = qt.QTextImageFormat()
                icon_image_format.setName(icon_image_path)
                icon_image_format.setWidth(600)  
                icon_image_format.setHeight(20)  
                cursor.insertBlock(left_format)  
                cursor.insertImage(icon_image_format)
                cursor.insertText("\n\n") 
            current_block = cursor.block()
            doc = cursor.document()
            layout = doc.documentLayout()
            current_pos = layout.blockBoundingRect(current_block).bottom()

            cursor.insertBlock()
            for _ in range(int(calculated_heights_white[0] / 20)):
                cursor.insertText("\n")
            #title
            title_format = qt.QTextCharFormat()
            title_format.setFont(qt.QFont("Times", 16, qt.QFont.Bold))
            
            cursor.insertBlock(center_format) 
            cursor.insertText(title + "\n\n\n", title_format)

           
            cursor.insertBlock()
            for _ in range(int(calculated_heights_white[1] / 20)):
                cursor.insertText("\n")

            # Text
            authors_format = qt.QTextCharFormat()
            authors_format.setFont(qt.QFont("Times", 12))
            cursor.insertBlock(center_format)  
            cursor.insertText(text + "\n\n", authors_format)

            current_block = cursor.block()    
            doc = cursor.document()
            layout = doc.documentLayout()
            current_pos2 = layout.blockBoundingRect(current_block).bottom()
           
            remaining_space = page_height - current_pos2
            cursor.insertBlock()
            for _ in range(int(calculated_heights_white[2] / 20)):
                cursor.insertText("\n")
            current_block = cursor.block()
            doc = cursor.document()
            layout = doc.documentLayout()
            current_pos2 = layout.blockBoundingRect(current_block).bottom()
            if footer_image_path:
                
                footer_block_format = qt.QTextBlockFormat()
                footer_block_format.setAlignment(qt.Qt.AlignCenter)

                #cursor.movePosition(qt.QTextCursor.Start)
                #while cursor.block().layout().position().y() < footer_y:
                #    cursor.movePosition(qt.QTextCursor.NextBlock)

                
                footer_image_format = qt.QTextImageFormat()
                footer_image_format.setName(footer_image_path)
                footer_image_format.setWidth(800)  
                footer_image_format.setHeight(10) 
                
                
                cursor.insertBlock(footer_block_format)
                cursor.insertImage(footer_image_format)
            
                footer_format = qt.QTextCharFormat()
                footer_format.setFont(qt.QFont("Times", 7))
                cursor.insertBlock(right_format)
                cursor.insertText(footer + "\n", footer_format)
            current_block = cursor.block()
            doc = cursor.document()
            
    
            layout = doc.documentLayout()
            current_pos = layout.blockBoundingRect(current_block).bottom()
            
         
            remaining_space = page_height - current_pos
            lines_needed = int(remaining_space / 20)  
            
    
            cursor.insertBlock()
            current_height = current_pos
            while current_height < 590:
                cursor.insertText("\n")
                current_height += 20  

        if is_SS_page:
            #Header
            if header_image_path:
                header_image_format = qt.QTextImageFormat()
                header_image_format.setName(header_image_path)
                header_image_format.setWidth(800)  
                header_image_format.setHeight(10)  
                cursor.insertBlock(center_format)  
                cursor.insertImage(header_image_format)

            if icon_image_path:
                icon_image_format = qt.QTextImageFormat()
                icon_image_format.setName(icon_image_path)
                icon_image_format.setWidth(600)  
                icon_image_format.setHeight(20)  
                cursor.insertBlock(left_format)  
                cursor.insertImage(icon_image_format)
            cursor.insertText("\n")

            title_format = qt.QTextCharFormat()
            title_format.setFont(qt.QFont("Times", 16, qt.QFont.Bold))
            cursor.insertBlock(center_format)
            cursor.insertText(title + "\n", title_format)

            # Secciones 3-6: Imagen
            if image_path:
            
                image_format = qt.QTextImageFormat()
                image_format.setName(image_path)
                image_format.setWidth(600) 
                image_format.setHeight(600 / 1.72)
              
                cursor.insertBlock(center_format)
                cursor.insertImage(image_format)
                cursor.insertText("\n\n")
            current_block = cursor.block()
            doc = cursor.document()
            layout = doc.documentLayout()
            current_pos = layout.blockBoundingRect(current_block).bottom()

            # Sección 7: Texto Principal
            text_format = qt.QTextCharFormat()
            text_format.setFont(qt.QFont("Times", 12))
            cursor.insertBlock(left_format)
            cursor.insertText(text + "\n\n", text_format)

           
            if footer_image_path:
                footer_y = current_pos + 60
                current_block = cursor.block()
                doc = cursor.document()
                        
                layout = doc.documentLayout()
                current_pos = layout.blockBoundingRect(current_block).bottom()

                footer_block_format = qt.QTextBlockFormat()
                footer_block_format.setAlignment(qt.Qt.AlignCenter)

                
                footer_image_format = qt.QTextImageFormat()
                footer_image_format.setName(footer_image_path)
                footer_image_format.setWidth(800)  
                footer_image_format.setHeight(10) 
                
                cursor.insertBlock(footer_block_format)
                cursor.insertImage(footer_image_format)
                footer_format = qt.QTextCharFormat()
                footer_format.setFont(qt.QFont("Times", 7))

                cursor.insertBlock(right_format)
                cursor.insertText(footer + "\n", footer_format)
        
            current_block = cursor.block()
            doc = cursor.document()
            
    
            layout = doc.documentLayout()
            current_pos = layout.blockBoundingRect(current_block).bottom()
           

