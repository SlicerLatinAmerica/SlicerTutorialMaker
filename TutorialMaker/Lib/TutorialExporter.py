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
    
    def ToMarkdown(self):
        return f"# {self.Title}\n**Autor:** {self.Author}\n\n{self.Description}\n"

class BackCoverSlide():
    def __init__(self, title: str, Acknowledgments: str):
        self.Title = title
        self.Acknowledgments = Acknowledgments 
    
    def ToHtml(self):
        if isinstance(self.Acknowledgments, dict):
            items = "".join(
                f"<li><h2><strong>{k}</strong><br>{v}</h2></li>"
                for k, v in self.Acknowledgments.items()
            )
        else:
            text = (self.Acknowledgments or "").strip()
            items = f"<li><h2>{text}</h2></li>" if text else ""

        return f"""
            <div class="backCover">
                <h1 class="coverTitle">{self.Title}</h1>
                <ul class="coverAcknowledgments">
                    {items}
                </ul>
            </div>
        """

    
    def ToMarkdown(self):
        if isinstance(self.Acknowledgments, dict):
            lines = "\n".join(f"- **{k}**\n  {v}" for k, v in self.Acknowledgments.items())
        else:
            text = (self.Acknowledgments or "").strip()
            lines = f"- {text}" if text else ""
        return f"# {self.Title}\n{lines}\n"

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
    
    def ToMarkdown(self):
        title_html = f"""<div style="background-color:#003366; color:white; padding:10px; text-align:center; font-size:24px; font-weight:bold;">{self.Title}</div>"""
        return f"{title_html}\n\n![Imagen]({self.ImagePath})\n\n{self.Description}\n"

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
    
    def ToMarkdown(self):
        md = f"# {self.Title}\n\n"
        md += "\n".join([slide.Model.ToMarkdown() for slide in self.Slides])
        self.Markdown = md
        return md
    
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
                    display: block;
                    max-width: 100%;
                    height: auto;
                    margin: 10px auto;
                    border-radius: 3px;
                    box-shadow: 0 4px 4px rgba(0,0,0,0.2);
                }
                
                .containerImage {
                    text-align: center;
                }

                .slideImage {
                    width: 85%;
                    height: auto;
                }

                .slideTitle, .coverTitle, .backCoverTitle {
                    text-align: center;
                    font-size: 2.5rem;
                    background: #003366;
                    color: white;
                }
                
                .coverAuthor, .coverDate {
                    text-align: center;
                    font-size: 2.0rem;
                   
                }

                .slideDescription {
                    text-align: justify;    
                    font-size: 1.5rem;
                }

                .coverDescription {
                    font-size: 1.5rem;    
                }

                .coverAcknowledgments {
                    list-style: none;
                }

                @media print {
                    .slide,
                    .cover,
                    .backCover {
                        height: 99%;
                        align-content: center;
                        page-break-after: always;
                    }
                    body{
                        height: 19cm;
                        width: 28.7cm;
                    }
                }

                @page {
                    size: 28.7cm 20cm;
                }
                """