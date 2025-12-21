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

    def loadSetting(self,settings):
        self.ConfirmedSetting = {"Main__DisplayStatusBar" : settings.value("Main/DisplayStatusBar", True, type = bool),
                           "Change__ChangeTool" : settings.value("Change/ChangeTool", "weasyprint"),
                           "Change__ChangeCompletedDialog" : settings.value("Change/ChangeCompletedDialog", True, type = bool),
                           "Display__StatusBar" : settings.value("Display/StatusBar", True, type = bool),
                           "Display__ChangeButton" : settings.value("Display/ChangeButton", True, type = bool)}
        self.BeingEditedList = {}
        for key, value in self.ConfirmedSetting.items():
                self.BeingEditedList[key.replace("/","__")] = value

    def MAKEWINDOW(self):
        self.setWindowTitle(self.tr("md2pdfViewer"))
        self.resize(800,600)
        self.makeMenuBar()
        MainLayout = QVBoxLayout()

        self.Preview = QWebEngineView()
        MainLayout.addWidget(self.Preview)
        if self.ConfirmedSetting["Display__ChangeButton"]:
            self.ChangeButton = QPushButton(self.tr("変換"))
            self.ChangeButton.clicked.connect(self.Change)
            self.ChangeButton.setDisabled(True)
            MainLayout.addWidget(self.ChangeButton)
        centralWidget = QWidget()
        centralWidget.setLayout(MainLayout)
        self.setCentralWidget(centralWidget)
        self.StatusBar = self.statusBar()
        self.setStatusBar(self.StatusBar)

        self.MainDisplaySomethings()


    def makeMenuBar(self):
        #メニューバーの作成
        MenuBar = self.menuBar()
        mFile = MenuBar.addMenu(self.tr("ファイル"))
        mEdit = MenuBar.addMenu(self.tr("編集"))
        mDisplay = MenuBar.addMenu(self.tr("表示"))
        mHelp = MenuBar.addMenu(self.tr("ヘルプ"))

        acOpenFile = QAction(self.tr("ファイルを開く"), self)
        acOpenFile.triggered.connect(self.file_choose)
        acChange = QAction(self.tr("変換"), self)
        acChange.triggered.connect(self.Change)

        acSetting = QAction(self.tr("設定"),self)
        acSetting.triggered.connect(self.SettingDialog)

        self.acDisplayStatusBar = QAction(self.tr("ステータスバー"),self)
        self.acDisplayStatusBar.triggered.connect(self.DisplayChangeStatusBar)
        self.acDisplayStatusBar.setCheckable(True)

        acVersion = QAction(self.tr("バージョン情報"),self)
        acVersion.triggered.connect(self.versionInfo)

        #メニューバーにアクションを追加
        mFile.addAction(acOpenFile)
        mFile.addAction(acChange)
        mEdit.addAction(acSetting)
        mDisplay.addAction(self.acDisplayStatusBar)
        mHelp.addAction(acVersion)

    def file_choose(self):
        self.filename, tmp = QFileDialog.getOpenFileName(self,self.tr("ファイルを開く"),"","Text File (*.html *.htm *.md)")
        self.FileName.setText(str(self.filename))
        with open (self.filename,"rb") as f:
            tmp = f.read()
            result = chardet.detect(tmp)
        if result["encoding"] == "SHIFT_JIS":
            self.encoding = "CP932"
        else:
            self.encoding = result["encoding"]
        with open(self.filename,"r", encoding = self.encoding) as f:
            convert_text = f.read()
        extension = os.path.splitext(self.filename)[1]
        if extension == ".md":
            md = markdown.Markdown()
            self.HTML_text = md.convert(convert_text)
        elif extension == ".html" or extension == ".htm":
            self.HTML_text = convert_text
        self.ChangeButton.setDisabled(False)
        if(self.ConfirmedSetting["Change__ChangeTool"] == "xhtml2pdf"):
            #self.HTML_text = self.HTML_text[:self.HTML_text.find("<html>")+6] + "\n@font-face {font-family: "my_lang\"; src: url(" + ");}" html, body {font-family: "my_lang";}"
            pass
        self.Preview.setHtml(self.HTML_text)

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
        sd = SettingDialog(self)
        sd.exec()


    def versionInfo(self):
        from version import __version__
        dig = InformationDialog(self.tr("バージョン情報"), "md2pdfViewer\nVersion : "+ __version__)
        dig.exec()

    def DisplayChangeStatusBar(self):
        if self.StatusBar.isVisible():
            self.StatusBar.setVisible(False)
            self.acDisplayStatusBar.setChecked(False)
            self.BeingEditedList["Main__DisplayStatusBar"] = False
            self.ChangeSetting()
        else:
            self.StatusBar.setVisible(True)
            self.acDisplayStatusBar.setChecked(True)
            self.BeingEditedList["Main__DisplayStatusBar"] = True
            self.StatusBar.showMessage(self.tr("ステータスバーの表示が有効になりました"))
            self.ChangeSetting()

    def MainDisplaySomethings(self):
        if self.ConfirmedSetting["Main__DisplayStatusBar"]:
            self.acDisplayStatusBar.setChecked(True)
            self.StatusBar.showMessage(self.tr("正常に起動しました"))
        else:
            self.acDisplayStatusBar.setChecked(False)

    def ChangeSetting(self):
        for key, value in self.BeingEditedList.items():
                self.settings.setValue(key.replace("__","/"),str(value))
                self.ConfirmedSetting[key] = value

class SettingDialog(QDialog):
    def __init__(self,mainwin):
        super().__init__()
        self.mainwin = mainwin

        self.setWindowTitle(self.tr("設定"))
        mainlayout = QVBoxLayout()
        abovelayout = QHBoxLayout()

        self.stab = QListWidget()
        self.stab.addItems([self.tr("変換"),self.tr("表示")])
        self.stab.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.stab.setFixedWidth(80)
        self.sdetail = QStackedWidget()
        self.sdetail.addWidget(self.wrap_scroll(Setting_Change(self.mainwin)))
        self.sdetail.addWidget(self.wrap_scroll(Setting_Display()))

        self.save_button = QPushButton(self.tr("設定を反映"))
        self.save_button.clicked.connect(self.SaveSetting)

        self.stab.currentRowChanged.connect(self.sdetail.setCurrentIndex)
        self.stab.setCurrentRow(0)


        self.setLayout(mainlayout)
        mainlayout.addLayout(abovelayout)
        mainlayout.addWidget(self.save_button)
        abovelayout.addWidget(self.stab,1)
        abovelayout.addWidget(self.sdetail)



    def wrap_scroll(self, widget : QWidget):
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        return scroll

    def SaveSetting(self):
        if self.mainwin.BeingEditedList == self.mainwin.ConfirmedSetting:
            QMessageBox.information(self,self.tr("一応通知"), self.tr("設定は変更されていません"))
        else:
            self.mainwin.ChangeSetting()


class Setting_Change(QWidget):
    def __init__(self, mainwin):
        super().__init__()
        self.mainwin = mainwin
        self.SCLayout = QFormLayout()
        self.setLayout(self.SCLayout)

        ChangeTool = QComboBox()
        ChangeTool.addItems(["weasyprint","xhtml2pdf"])
        ChangeTool.setCurrentText(self.mainwin.ConfirmedSetting["Change__ChangeTool"])
        ChangeTool.currentIndexChanged.connect(lambda _ : (self.mainwin.BeingEditedList.update(Change__ChangeTool = ChangeTool.currentText())))
        ChangeCompletedDialog = QCheckBox(self.tr("表示する"))
        ChangeCompletedDialog.setChecked(self.mainwin.ConfirmedSetting["Change__ChangeCompletedDialog"])
        ChangeCompletedDialog.stateChanged.connect(lambda _ : (self.mainwin.BeingEditedList.update(Change__ChangeCompletedDialog = ChangeCompletedDialog.isChecked())))

        self.SCLayout.addRow(self.tr("変換ツール"), ChangeTool)
        self.SCLayout.addRow(self.tr("変換完了通知"), ChangeCompletedDialog)

class Setting_Display(QWidget):
    def __init__(self):
        super().__init__()

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