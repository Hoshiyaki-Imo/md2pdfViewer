from PySide6.QtWidgets import QWidget,QSplitter,QPlainTextEdit,QHBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt
from md2pdf_class_Document import Document

class DocumentView(QWidget):
    def __init__(self, doc : Document):
        self.viewdoc = doc
        super().__init__()
        self.Splitter = QSplitter()
        self.Preview = QWebEngineView()
        self.Preview.setHtml(doc.HTML_text)
        self.Editor = ZoomablePlainTextEdit()
        self.Editor.setPlainText(doc.md_text)
        self.Splitter.addWidget(self.Editor)
        self.Splitter.addWidget(self.Preview)
        splitter_width = self.Splitter.size().width()
        self.Splitter.setSizes([splitter_width * 0.5, splitter_width * 0.5])
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.Splitter)
        self.setLayout(self.layout)

class ZoomablePlainTextEdit(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.zoom_factor = 1.0  # 現在の倍率

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn(1) 
            else:
                self.zoomOut(1) 
        else:
            super().wheelEvent(event)