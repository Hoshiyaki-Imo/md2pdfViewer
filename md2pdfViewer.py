import PySide6
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWebEngineCore import *
import os
import sys
import markdown
import chardet

# PySide6のアプリ本体（ユーザがコーディングしていく部分）
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        # 親クラスの初期化
        super().__init__(parent)
        self.settings = QSettings("HoshiYakiImo", "md2pdfViewer")
        self.loadSetting(self.settings)

        self.MAKEWINDOW()
        self.restart()


    def loadSetting(self,settings):
        self.ConfirmedSetting = {"Main__DisplayStatusBar" : settings.value("Main/DisplayStatusBar", True, type = bool),
                           "Change__ChangeTool" : settings.value("Change/ChangeTool", "ChromiumPrint"),
                           "Change__ChangeCompletedDialog" : settings.value("Change/ChangeCompletedDialog", True, type = bool),
                           "Display__ChangeButton" : settings.value("Display/ChangeButton", True, type = bool),
                           "Display__TabCloseButton" : settings.value("Display/TabCloseButton", False, type = bool)}
        self.BeingEditedList = {}
        for key, value in self.ConfirmedSetting.items():
                self.BeingEditedList[key.replace("/","__")] = value


    def MAKEWINDOW(self):
        self.setWindowTitle(self.tr("md2pdfViewer"))
        self.resize(800,600)
        self.makeMenuBar()
        self.MainWinMainLayout = QVBoxLayout()

        self.tab = QTabWidget()
        self.tab.setMovable(True)
        self.tab.setTabsClosable(True)
        self.tab.tabCloseRequested.connect(self.file_close)
        self.newdocview = DocumentView(Document(None))
        self.tab.addTab(self.newdocview, "NewFile")
        self.MainWinMainLayout.addWidget(self.tab)
        centralWidget = QWidget()
        centralWidget.setLayout(self.MainWinMainLayout)
        self.setCentralWidget(centralWidget)
        self.StatusBar = self.statusBar()
        self.setStatusBar(self.StatusBar)

        self.MainDisplaySomethings()


    def restart(self):
        self.ChangeButton.setDisabled(True)
        self.acChange.setDisabled(True)
        self.acCloseFile.setDisabled(True)


    def makeMenuBar(self):
        #メニューバーの作成
        MenuBar = self.menuBar()
        mFile = MenuBar.addMenu(self.tr("ファイル"))
        mEdit = MenuBar.addMenu(self.tr("編集"))
        mDisplay = MenuBar.addMenu(self.tr("表示"))
        mHelp = MenuBar.addMenu(self.tr("ヘルプ"))

        acOpenFile = QAction(self.tr("ファイルを開く"), self)
        acOpenFile.triggered.connect(self.file_choose)
        self.acChange = QAction(self.tr("現在のファイルを変換"), self)
        self.acChange.triggered.connect(self.Change)
        self.acCloseFile = QAction(self.tr("ファイルを閉じる"), self)
        self.acCloseFile.triggered.connect(self.file_close)
        self.acCloseApp = QAction(self.tr("ソフトを終了"), self)
        self.acCloseApp.triggered.connect(lambda _ : sys.exit(app.exec()))

        acSetting = QAction(self.tr("設定"),self)
        acSetting.triggered.connect(self.SettingDialog)

        self.acDisplayStatusBar = QAction(self.tr("ステータスバー"),self)
        self.acDisplayStatusBar.triggered.connect(self.DisplayChangeStatusBar)
        self.acDisplayStatusBar.setCheckable(True)

        acVersion = QAction(self.tr("バージョン情報"),self)
        acVersion.triggered.connect(self.versionInfo)
        acIcon = QAction(self.tr("アイコンを見る"), self)
        acIcon.triggered.connect(self.showIcon)

        #メニューバーにアクションを追加
        mFile.addAction(acOpenFile)
        mFile.addAction(self.acChange)
        mFile.addAction(self.acCloseFile)
        mFile.addAction(self.acCloseApp)
        mEdit.addAction(acSetting)
        mDisplay.addAction(self.acDisplayStatusBar)
        mHelp.addAction(acVersion)
        mHelp.addAction(acIcon)


    def file_choose(self):
        try:
            Filenames, tmp = QFileDialog.getOpenFileNames(self,self.tr("ファイルを開く"),"","Text File (*.html *.htm *.md)")
        except FileNotFoundError:
            self.StatusBar.showMessage(self.tr("ファイルが選択されませんでした"))
            return
        if Filenames == []:
            return
        self.StatusBar.showMessage(self.tr("ファイルを開きました"))
        for iFilename in Filenames:
            doc = Document(iFilename)
            docview = DocumentView(doc)
            self.tab.addTab(docview, os.path.basename(doc.filename))
            self.tab.setCurrentWidget(docview)
        self.ChangeButton.setDisabled(False)
        self.acCloseFile.setDisabled(False)
        self.acChange.setDisabled(False)


    def Change(self):
        output_filename = os.path.splitext(self.tab.currentWidget().filename)[0] + ".pdf"
        tool = self.ConfirmedSetting["Change__ChangeTool"]
        HTML_text = self.tab.currentWidget().HTML_text

        if os.path.isfile(output_filename):
            reply = QMessageBox.question(self, self.tr("上書き確認"), self.tr("pdfファイルは既に存在しています。\n上書きしますか？"), QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
        self.wait = InformationDialog(self.tr("変換中"), self.tr("変換中です"))
        self.wait.OffCloseButton()
        self.wait.setModal(True)
        self.wait.show()
        self.conv = PdfConverter()
        self.conv.changed.connect(self.ChangedDialog)
        self.conv.convert(output_filename, tool, HTML_text)


    def SettingDialog(self):
        import md2pdf_Setting as s
        sd = s.SettingDialog(self)
        sd.exec()


    def versionInfo(self):
        from version import __version__
        dig = InformationDialog(self.tr("バージョン情報"), "md2pdfViewer\nVersion : "+ __version__)
        dig.exec()


    def DisplayChangeStatusBar(self):
        self.BeingEditedList["Main__DisplayStatusBar"] = False if self.ConfirmedSetting["Main__DisplayStatusBar"] else True
        self.ChangeSetting()


    #First once
    def MainDisplaySomethings(self):
        self.ChangeButton = QPushButton(self.tr("このファイルを変換"))
        self.ChangeButton.clicked.connect(self.Change)
        self.MainWinMainLayout.addWidget(self.ChangeButton)
        self.ChangeButton.setVisible(True if self.ConfirmedSetting["Display__ChangeButton"] else False)
        self.StatusBar.setVisible(True if self.ConfirmedSetting["Main__DisplayStatusBar"] else False)
        self.acDisplayStatusBar.setChecked(True if self.ConfirmedSetting["Main__DisplayStatusBar"] else False)


    def ChangeSetting(self):
        for key, value in self.BeingEditedList.items():
                self.settings.setValue(key.replace("__","/"),str(value))
                self.ConfirmedSetting[key] = value
        self.Refresh()


    def file_close(self, index = -1):
        if index+1 :
            self.tab.removeTab(index)
        else:
            self.tab.removeTab(self.tab.currentIndex())


    #many times uses --do not use MainDisplaySomethings--
    def Refresh(self):
        self.ChangeButton.setVisible(True if self.ConfirmedSetting["Display__ChangeButton"] else False)
        if self.ConfirmedSetting["Main__DisplayStatusBar"]:
            self.StatusBar.setVisible(True)
            self.acDisplayStatusBar.setChecked(True)
        else:
            self.StatusBar.setVisible(False)
            self.acDisplayStatusBar.setChecked(False)
        '''if self.ConfirmedSetting["Change__OriginalFont"]:
            if "<head>" in self.nowHTML_text:
                css = self.ConfirmedSetting["Change__FontFamilyName"]
                self.nowHTML_text = self.nowHTML_text.replace("<head>", f"<head><style>{css}</style>")'''


    def showIcon(self):
        dia = InformationDialog(self.tr("アイコン"), self.tr("md2pdfViewerのアイコン"), 300, 100)
        dia.AddIcon(QPixmap("icon.ico").scaled(512, 512, Qt.IgnoreAspectRatio, Qt.FastTransformation))
        dia.exec()


    def ChangedDialog(self, Changed):
        self.wait.accept()
        if Changed and self.ConfirmedSetting["Change__ChangeCompletedDialog"]:
            QMessageBox.information(self, self.tr("変換成功"), self.tr("ファイルの変換に成功しました"))
        elif not Changed:
            QMessageBox.warning(self, self.tr("エラー"), self.tr("変換時にエラーが発生しました"))





class InformationDialog(QDialog):
    def __init__(self, wintitle = "Title", wincontent = "Content", width = 200, height = 100):
        super().__init__()
        self.setWindowTitle(wintitle)
        self.resize(width,height)
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel(wincontent))
        self.setLayout(self.layout)


    def OffCloseButton(self):
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)


    def AddIcon(self, Icon):
        iconlabel = QLabel()
        iconlabel.setPixmap(Icon)
        self.layout.addWidget(iconlabel)



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


class DocumentView(QWidget):
    def __init__(self, doc : Document):
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



if __name__ == "__main__":
    # 環境変数にPySide6を登録
    dirname = os.path.dirname(PySide6.__file__)
    plugin_path = os.path.join(dirname, 'plugins', 'platforms')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

    app = QApplication(sys.argv)    # PySide6の実行
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()           # ユーザがコーディングしたクラス
    window.show()                   # PySide6のウィンドウを表示
    sys.exit(app.exec())            # PySide6の終了