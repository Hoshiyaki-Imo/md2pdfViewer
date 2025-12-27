from PySide6.QtWidgets import *
class SettingDialog(QDialog):
    def __init__(self, mainwin):
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
        self.sdetail.addWidget(self.wrap_scroll(Setting_Display(self.mainwin)))

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
        ChangeTool.addItems(["weasyprint","xhtml2pdf", "ChromiumPrint"])
        ChangeTool.setCurrentText(self.mainwin.ConfirmedSetting["Change__ChangeTool"])
        ChangeTool.currentIndexChanged.connect(lambda _ : (self.mainwin.BeingEditedList.update(Change__ChangeTool = ChangeTool.currentText())))
        ChangeCompletedDialog = QCheckBox(self.tr("表示する"))
        ChangeCompletedDialog.setChecked(self.mainwin.ConfirmedSetting["Change__ChangeCompletedDialog"])
        ChangeCompletedDialog.stateChanged.connect(lambda _ : (self.mainwin.BeingEditedList.update(Change__ChangeCompletedDialog = ChangeCompletedDialog.isChecked())))

        self.SCLayout.addRow(self.tr("変換ツール"), ChangeTool)
        self.SCLayout.addRow(self.tr("変換完了通知"), ChangeCompletedDialog)

class Setting_Display(QWidget):
    def __init__(self, mainwin):
        super().__init__()
        self.mainwin = mainwin
        self.SDLayout = QFormLayout()
        self.setLayout(self.SDLayout)
        DisplayChangeButton = QCheckBox(self.tr("表示する"))
        DisplayChangeButton.setChecked(self.mainwin.ConfirmedSetting["Display__ChangeButton"])
        DisplayChangeButton.stateChanged.connect(lambda _ : (self.mainwin.BeingEditedList.update(Display__ChangeButton = DisplayChangeButton.isChecked())))

        self.SDLayout.addRow(self.tr("変換ボタン"), DisplayChangeButton)