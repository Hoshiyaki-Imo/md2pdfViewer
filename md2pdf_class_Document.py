import chardet,os,markdown
from PySide6.QtCore import QObject


class Document(QObject):
    def __init__(self, filename = None):
        if not filename == None:
            self.filename = filename
            with open (self.filename,mode = "rb") as f:
                tmp = f.read()
                result = chardet.detect(tmp)["encoding"]
            if result == "SHIFT_JIS":
                self.encoding = "CP932"
            elif result == None:
                self.encoding = "utf-8"
            else:
                self.encoding = result
            with open(self.filename,"r", encoding = self.encoding, errors = "replace") as f:
                raw_text = f.read()
            extension = os.path.splitext(self.filename)[1]
            if extension == ".md":
                md = markdown.Markdown()
                self.HTML_text = md.convert(raw_text)
                self.md_text = raw_text
            elif extension == ".html" or extension == ".htm":
                import html2markdown
                self.HTML_text = raw_text
                self.md_text = html2markdown.convert(raw_text)
        else:
            self.HTML_text = ""
            self.md_text = ""
            self.filename = self.tr("新しいファイル.md")