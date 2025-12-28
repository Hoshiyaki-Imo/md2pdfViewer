from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWebEngineCore import QWebEnginePage

class PdfConverter(QObject):
    changed = Signal(bool)
    def convert(self, output_filename, tool, HTML_text):
        if tool == "ChromiumPrint":
            self.PrintChromium(HTML_text, output_filename)
        else:
            self.changeWorker = Worker_Change(tool, HTML_text, output_filename)
            self.changeWorker.finished.connect(self.Changed)
            self.changeWorker.start()

    def Changed(self, successChange):
        self.changed.emit(successChange)

    def PrintChromium(self, HTML_text, output_filename):
        self.page = QWebEnginePage(self)
        def on_load(ok):
            if not ok:
                self.page.deleteLater()
                self.Changed(False)
                return
            self.page.printToPdf(output_filename)
        def pdf_finished(path, ok):
            self.page.deleteLater()
            self.Changed(ok)
        self.page.loadFinished.connect(on_load)
        self.page.pdfPrintingFinished.connect(pdf_finished)
        self.page.setHtml(HTML_text)



class Worker_Change(QThread):
    finished = Signal(bool)

    def __init__(self, tool, HTML_text, output_filename):
        super().__init__()
        self.tool = tool
        self.HTML_text = HTML_text
        self.output_filename = output_filename


    def run(self):
        try:
            if(self.tool == "weasyprint"):
                from weasyprint import HTML
                HTML(string = self.HTML_text).write_pdf(self.output_filename)
            elif(self.tool == "xhtml2pdf"):
                from xhtml2pdf import pisa
                with open(self.output_filename, "w+b") as file:
                    pisa_status = pisa.CreatePDF(src=self.HTML_text, dest=file)
            self.finished.emit(True)
        except:
            self.finished.emit(False)
