import PySide6
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWebEngineWidgets import QWebEngineView
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
                           "Change__ChangeTool" : settings.value("Change/ChangeTool", "weasyprint"),
                           "Change__ChangeCompletedDialog" : settings.value("Change/ChangeCompletedDialog", True, type = bool),
                           "Display__ChangeButton" : settings.value("Display/ChangeButton", True, type = bool)}
        self.BeingEditedList = {}
        for key, value in self.ConfirmedSetting.items():
                self.BeingEditedList[key.replace("/","__")] = value

    def MAKEWINDOW(self):
        self.setWindowTitle(self.tr("md2pdfViewer"))
        self.resize(800,600)
        self.makeMenuBar()
        self.MainWinMainLayout = QVBoxLayout()

        self.Preview = QWebEngineView()
        self.MainWinMainLayout.addWidget(self.Preview)
        centralWidget = QWidget()
        centralWidget.setLayout(self.MainWinMainLayout)
        self.setCentralWidget(centralWidget)
        self.StatusBar = self.statusBar()
        self.setStatusBar(self.StatusBar)

        self.MainDisplaySomethings()

    def restart(self):
        self.ChangeButton.setDisabled(True)
        self.acChange.setDisabled(True)


    def makeMenuBar(self):
        #メニューバーの作成
        MenuBar = self.menuBar()
        mFile = MenuBar.addMenu(self.tr("ファイル"))
        mEdit = MenuBar.addMenu(self.tr("編集"))
        mDisplay = MenuBar.addMenu(self.tr("表示"))
        mHelp = MenuBar.addMenu(self.tr("ヘルプ"))

        acOpenFile = QAction(self.tr("ファイルを開く"), self)
        acOpenFile.triggered.connect(self.file_choose)
        self.acChange = QAction(self.tr("変換"), self)
        self.acChange.triggered.connect(self.Change)
        self.acClose = QAction(self.tr("ソフトを終了"), self)
        self.acClose.triggered.connect(lambda _ : sys.exit())

        acSetting = QAction(self.tr("設定"),self)
        acSetting.triggered.connect(self.SettingDialog)

        self.acDisplayStatusBar = QAction(self.tr("ステータスバー"),self)
        self.acDisplayStatusBar.triggered.connect(self.DisplayChangeStatusBar)
        self.acDisplayStatusBar.setCheckable(True)

        acVersion = QAction(self.tr("バージョン情報"),self)
        acVersion.triggered.connect(self.versionInfo)

        #メニューバーにアクションを追加
        mFile.addAction(acOpenFile)
        mFile.addAction(self.acChange)
        mFile.addAction(self.acClose)
        mEdit.addAction(acSetting)
        mDisplay.addAction(self.acDisplayStatusBar)
        mHelp.addAction(acVersion)

    def file_choose(self):
        try:
            self.filename, tmp = QFileDialog.getOpenFileName(self,self.tr("ファイルを開く"),"","Text File (*.html *.htm *.md)")
        except FileNotFoundError:
            self.StatusBar.showMessage(self.tr("ファイルが選択されませんでした"))
            return
        self.StatusBar.showMessage(self.tr("ファイルを開きました : " + str(self.filename)))
        with open (self.filename,mode = "rb") as f:
            tmp = f.read()
            result = chardet.detect(tmp)["encoding"]
        if QCborStringResultByteArray == "SHIFT_JIS":
            self.encoding = "CP932"
        elif result == None:
            self.encoding = "utf-8"
        else:
            self.encoding = result["encoding"]
        with open(self.filename,"r", encoding = self.encoding, errors = "replace") as f:
            convert_text = f.read()
        extension = os.path.splitext(self.filename)[1]
        if extension == ".md":
            md = markdown.Markdown()
            self.HTML_text = md.convert(convert_text)
        elif extension == ".html" or extension == ".htm":
            self.HTML_text = convert_text
        self.Preview.setHtml(self.HTML_text)
        self.ChangeOK()

    def Change(self):
        output_filename = os.path.splitext(self.filename)[0] + ".pdf"
        if os.path.isfile(output_filename):
            if not QMessageBox.question(self, self.tr("上書き確認"), self.tr("pdfファイルは既に存在しています。\n上書きしますか？")):
                return
        if(self.ConfirmedSetting["Change__ChangeTool"] == "weasyprint"):
            from weasyprint import HTML
            HTML(string = self.HTML_text).write_pdf(output_filename)
        elif(self.ConfirmedSetting["Change__ChangeTool"] == "xhtml2pdf"):
            from xhtml2pdf import pisa
            with open(output_filename, "w+b") as file:
                pisa_status = pisa.CreatePDF(src=self.HTML_text, dest=file)
        if os.path.isfile(output_filename) and self.ConfirmedSetting["Change__ChangeCompletedDialog"]:
            QMessageBox.information(self, self.tr("変換成功"), self.tr("ファイルの変換に成功しました"))
        elif not os.path.isfile(output_filename):
            QMessageBox.warning(self, self.tr("エラー"), self.tr("変換時にエラーが発生しました"))


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
        self.ChangeButton = QPushButton(self.tr("変換"))
        self.ChangeButton.clicked.connect(self.Change)
        self.MainWinMainLayout.addWidget(self.ChangeButton)
        self.ChangeButton.setVisible(True if self.ConfirmedSetting["Display__ChangeButton"] else False)
        self.acDisplayStatusBar.setVisible(True if self.ConfirmedSetting["Main__DisplayStatusBar"] else False)
        self.acDisplayStatusBar.setChecked(True if self.ConfirmedSetting["Main__DisplayStatusBar"] else False)

    def ChangeSetting(self):
        for key, value in self.BeingEditedList.items():
                self.settings.setValue(key.replace("__","/"),str(value))
                self.ConfirmedSetting[key] = value
        self.Refresh()

    def ChangeOK(self):
        self.ChangeButton.setDisabled(False)
        self.acClose.setDisabled(False)
        #self.Refresh(self)

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
            if "<head>" in self.HTML_text:
                css = self.ConfirmedSetting["Change__FontFamilyName"]
                self.HTML_text = self.HTML_text.replace("<head>", f"<head><style>{css}</style>")'''




class InformationDialog(QDialog):
    def __init__(self, wintitle = "Title", wincontent = "Content", width = 200, height = 100):
        super().__init__()
        self.setWindowTitle(wintitle)
        self.resize(width,height)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(wincontent))
        self.setLayout(layout)


if __name__ == "__main__":
    # 環境変数にPySide6を登録
    dirname = os.path.dirname(PySide6.__file__)
    plugin_path = os.path.join(dirname, 'plugins', 'platforms')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

    app = QApplication(sys.argv)    # PySide6の実行
    window = MainWindow()           # ユーザがコーディングしたクラス
    window.show()                   # PySide6のウィンドウを表示
    sys.exit(app.exec())            # PySide6の終了