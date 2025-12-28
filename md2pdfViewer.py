import PySide6
from PySide6.QtWidgets import QMainWindow, QTabWidget, QPushButton, QFileDialog, QMessageBox, QVBoxLayout, QWidget, QDialog, QLabel, QApplication, QProgressBar
from PySide6.QtGui import QIcon, QPixmap, QAction
from PySide6.QtCore import Qt, QSettings, QEventLoop
import os
import sys
import md2pdf_class_Document as Doc
import md2pdf_class_DocumentView as Docv
import md2pdf_class_PdfConverter as Pdfconv



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

    def AddProgressBar(self, visable = False, min = 0, max = 100):
        self.progress = QProgressBar()
        self.progress.setTextVisible(visable)
        self.progress.setMinimum(min)
        self.progress.setMaximum(max)
        self.progress.setValue(0)
        self.layout.insertWidget(0, self.progress)

    def setProgressBarInt(self, num):
        self.progress.setValue(num)

    def ProgressBarInt(self):
        return self.progress.value()



# PySide6のアプリ本体（ユーザがコーディングしていく部分）
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        # 親クラスの初期化
        super().__init__(parent)
        self.settings = QSettings("HoshiYakiImo", "md2pdfViewer")
        self.loadSetting(self.settings)

        self.Makewindow()
        #start
        self.acCloseFile.setDisabled(True)


    def loadSetting(self,settings):
        self.ConfirmedSetting = {"Main__DisplayStatusBar" : settings.value("Main/DisplayStatusBar", True, type = bool),
                           "Change__ChangeTool" : settings.value("Change/ChangeTool", "ChromiumPrint"),
                           "Change__ChangeCompletedDialog" : settings.value("Change/ChangeCompletedDialog", True, type = bool),
                           "Display__ChangeButton" : settings.value("Display/ChangeButton", True, type = bool),
                           "Display__TabCloseButton" : settings.value("Display/TabCloseButton", False, type = bool)}


    def Makewindow(self):
        self.setWindowTitle(self.tr("md2pdfViewer"))
        self.resize(800,600)
        self.makeMenuBar()
        self.MainWinMainLayout = QVBoxLayout()

        self.tab = QTabWidget()
        self.tab.setMovable(True)
        self.tab.tabCloseRequested.connect(self.file_close)
        self.newdocview = Docv.DocumentView(Doc.Document(None))
        self.tab.addTab(self.newdocview, "NewFile")
        self.MainWinMainLayout.addWidget(self.tab)
        centralWidget = QWidget()
        centralWidget.setLayout(self.MainWinMainLayout)
        self.setCentralWidget(centralWidget)
        self.StatusBar = self.statusBar()
        self.setStatusBar(self.StatusBar)

        self.ChangeButton = QPushButton(self.tr("このファイルを変換"))
        self.ChangeButton.clicked.connect(self.Change)
        self.MainWinMainLayout.addWidget(self.ChangeButton)
        self.Refresh()


    def makeMenuBar(self):
        #メニューバーの作成
        MenuBar = self.menuBar()
        mFile = MenuBar.addMenu(self.tr("ファイル"))
        mEdit = MenuBar.addMenu(self.tr("編集"))
        mDisplay = MenuBar.addMenu(self.tr("表示"))
        mHelp = MenuBar.addMenu(self.tr("ヘルプ"))

        acOpenFile = QAction(self.tr("ファイルを開く"), self)
        acOpenFile.triggered.connect(self.file_choose)
        self.acChange = QAction(self.tr("現在のファイル"), self)
        self.acChange.triggered.connect(self.Change)
        self.acChangeAll = QAction(self.tr("すべてのファイル"), self)
        self.acChangeAll.triggered.connect(self.ChangeAll)
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
        self.mmChange = mFile.addMenu(self.tr("変換"))
        self.mmChange.addAction(self.acChange)
        self.mmChange.addAction(self.acChangeAll)
        mFile.addSeparator()
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
            doc = Doc.Document(iFilename)
            docview = Docv.DocumentView(doc)
            self.tab.addTab(docview, os.path.basename(doc.filename))
            self.tab.setCurrentWidget(docview)
        self.ChangeButton.setDisabled(False)
        self.acCloseFile.setDisabled(False)
        self.acChange.setDisabled(False)
        self.acChangeAll.setDisabled(False)
        self.mmChange.setDisabled(False)


    def Change(self, _, i = -1):
        tool = self.ConfirmedSetting["Change__ChangeTool"]
        index = i if i + 1 else self.tab.currentIndex()
        if i + 1:
            output_filename = os.path.splitext(self.tab.widget(i).viewdoc.filename)[0] + ".pdf"
            changeok = True if self.tab.count() == i + 1 else False
            if not i:
                self.Change_num = 0
                self.quelist = []
        else:
            output_filename = os.path.splitext(self.tab.currentWidget().viewdoc.filename)[0] + ".pdf"
            changeok = True
            self.quelist = []
            self.Change_num = 0

        if os.path.isfile(output_filename):
            reply = QMessageBox.question(self, self.tr("上書き確認"), self.tr(output_filename + "は既に存在しています。\n上書きしますか？"), QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                self.quelist.append([index, False, output_filename])
                self.Change_num += 1
            else:
                self.quelist.append([index, True, output_filename])
        else:
            self.quelist.append([index, True, output_filename])
        if changeok:
            self.wait = InformationDialog(self.tr("変換中"), self.tr("変換中です"))
            self.wait.AddProgressBar(True, 0, self.Change_num)
            self.wait.OffCloseButton()
            self.wait.setModal(True)
            self.wait.show()
            i = 0
            self.finishedfilenum = 0
            self.conv = Pdfconv.PdfConverter()
            self.conv.changed.connect(self.ChangedDialog)
            self.loop = QEventLoop()
            for n in self.quelist:
                i += 1
                if not n[1]:
                    continue
                self.conv.convert(n[2], tool, self.tab.widget(n[0]).viewdoc.HTML_text)
                self.loop.exec()


    def ChangedDialog(self, Changed):
        self.finishedfilenum += 1
        if Changed and self.ConfirmedSetting["Change__ChangeCompletedDialog"]:
            if self.finishedfilenum == len(self.quelist):
                self.wait.accept()
                QMessageBox.information(self, self.tr("変換成功"), self.tr("ファイルの変換に成功しました"))
            else:
                print("continue")
                self.wait.setProgressBarInt(self.wait.ProgressBarInt() + 1)
            self.loop.quit()
        elif not Changed:
            self.wait.accept()
            QMessageBox.warning(self, self.tr("エラー"), self.tr("変換時にエラーが発生しました"))


    def ChangeAll(self):
        for i in range(self.tab.count()):
            self.Change(None, i)


    def SettingDialog(self):
        import md2pdf_class_SettingDialog as s
        sd = s.SettingDialog(self)
        sd.exec()


    def versionInfo(self):
        from version import __version__
        dig = InformationDialog(self.tr("バージョン情報"), "md2pdfViewer\nVersion : "+ __version__)
        dig.exec()


    def DisplayChangeStatusBar(self):
        self.ConfirmedSetting["Main__DisplayStatusBar"] = False if self.ConfirmedSetting["Main__DisplayStatusBar"] else True
        self.settings.setValue("Main/DisplayStatusBar", False if self.ConfirmedSetting["Main__DisplayStatusBar"] else True)
        self.Refresh()


    def ChangeSetting(self, BeingEditedList):
        for key, value in BeingEditedList.items():
                self.settings.setValue(key.replace("__","/"), str(value))
                self.ConfirmedSetting[key] = value
        self.Refresh()


    def file_close(self, index = -1):
        if index+1 :
            self.tab.removeTab(index)
        else:
            self.tab.removeTab(self.tab.currentIndex())
        if self.tab.count() == 0:
            self.ChangeButton.setDisabled(True)
            self.acChange.setDisabled(True)
            self.acCloseFile.setDisabled(True)
            self.acChangeAll.setDisabled(True)
            self.mmChange.setDisabled(True)


    #many times uses --do not use MainDisplaySomethings--
    def Refresh(self):
        self.ChangeButton.setVisible(True if self.ConfirmedSetting["Display__ChangeButton"] else False)
        self.tab.setTabsClosable(True if self.ConfirmedSetting["Display__TabCloseButton"] else False)
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