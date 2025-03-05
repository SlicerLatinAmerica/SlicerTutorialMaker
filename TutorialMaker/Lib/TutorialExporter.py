import qt

class CoverSlide():
    def __init__(self, title: str, author: str, date: str, description: str):
        self.Title = title
        self.Author = author
        self.Date = date
        self.Description = description
        pass
    
    def ToHtml(self):
        return  """
                <div class="cover">
                    <h1 class="coverTitle">{}</h1>
                    <h3 class="coverAuthor">{}</h3>
                    <h3 class="coverDescription">{}</h3>
                </div>
                """.format(self.Title, self.Author, self.Description)

class BackCoverSlide():
    def __init__(self, Title: str, Acknowledgements: dict[str, str]):
        self.Title = Title
        self.Acknowledgements = Acknowledgements
    
    def ToHtml(self):
        aknowledgements = ""
        for key, value in self.Acknowledgements.items():
            aknowledgements += "<li><h2><strong>{}</strong><br>{}</h2></li>".format(key, value)
        
        return  """
                <div class="backCover">
                    <h1 class="coverTitle">{}</h1>
                    <ul class="coverAcknowledgements">
                        {}
                    </ul>
                </div>
                """.format(self.Title, aknowledgements)  

class SimpleSlide():
    def __init__(self, Title: str, Description: str, ImagePath: str):
        self.Title = Title
        self.Description = Description
        self.ImagePath = ImagePath
        
    def ToHtml(self):
        return  """
                    <div class="slide">
                        <h1 class="slideTitle">{}</h1>
                        <div class="containerImage">
                            <img class="slideImage" src="{}">
                        </div>
                        <h3 class="slideDescription">{}</h3>
                    </div>
                """.format(self.Title, self.ImagePath, self.Description)

class SlideModel():
    Cover= CoverSlide
    SimpleSlide = SimpleSlide
    BackCover = BackCoverSlide

class SlidePage():
    def __init__(self, Model:SlideModel = SlideModel.SimpleSlide):
        self.Model = Model # Model will be used later to create more than one type of slide

class TutorialExporter():
    def __init__(self, Slides: list[SlidePage], Title: str):
        self.Slides = Slides
        self.Title = Title
        self.Html = """ <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>{}</title>
                        </head>
                        <body>
                            {}
                        </body>
                        <style>
                            {}
                        </style>
                        </html>
                    """
        self.Markdown = ""
        
    def ToHtml(self):
        body = "".join([slide.Model.ToHtml() for slide in self.Slides])
        return self.Html.format(self.Title, body, self.htmlStyle)
    
    def ToMarkdown():
        pass
    
    def ToPdf(self):
        printer = qt.QPrinter(qt.QPrinter.PrinterResolution)
        printer.setOutputFormat(qt.QPrinter.PdfFormat)
        printer.setPaperSize(qt.QPageSize.A4)
        printer.setOrientation(qt.QPrinter.Landscape)
        printer.setOutputFileName(self.Title + ".pdf")

        doc = qt.QTextDocument()
        doc.setHtml(self.ToHtml())
        doc.setPageSize(qt.QSizeF(printer.pageRect().size()))
        doc.print_(printer)
    
    # Slide, Cover and BackCover are divs that wrap the content of the slide
    # All the elements inside the divs have their own classes to style them
    htmlStyle = """               
                .slide, .cover, .backCover {
                    align-content: center;
                }
                
                .containerImage {
                    text-align: center;
                }

                .slideImage {
                    width: 95%;
                    height: auto;
                }

                .slideTitle, .coverTitle, .backCoverTitle,
                .coverAuthor, .coverDate {
                    text-align: center;
                    font-size: 2.5rem;
                }

                .slideDescription {
                    text-align: justify;    
                    font-size: 1.5rem;
                }

                .coverDescription {
                    font-size: 1.5rem;    
                }

                .coverAcknowledgements {
                    list-style: none;
                }

                @media print {
                    .slide,
                    .cover,
                    .backcover {
                        height: 99%;
                        align-content: center;
                        page-break-after: always;
                    }
                    body{
                        height: 21cm;
                        width: 29.7cm;
                    }
                }

                @page {
                    size: 29.7cm 21cm;
                }
                """