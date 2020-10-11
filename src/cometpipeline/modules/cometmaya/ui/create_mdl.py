from qtpy import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
import os


class CustomVBoxLayout(QtWidgets.QVBoxLayout):
    def __init__(self):
        super(CustomVBoxLayout, self).__init__()
        self.setAlignment(QtCore.Qt.AlignTop)
        self.setContentsMargins(9, 12, 9, 9)

    def addRow(self, label, widget, tip="", height=28):
        widget.setFixedHeight(height)
        text_template = """
        <html>
        <head/>
            <body>
                <p>
                    <span>{0}</span>
                    <span style=" font-size:8pt; color:#757575;">{1}</span>
                </p>
            </body>
        </html>
                """.format(label, tip)
        label = QtWidgets.QLabel(text_template)
        label.setTextFormat(QtCore.Qt.RichText)
        label.setStyleSheet("""
            QLabel{
                color: #a6a6a6;
            }
        """)
        label.setAlignment(QtCore.Qt.AlignLeft)
        label.setIndent(0)
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(label)
        layout.addWidget(widget)
        layout.setContentsMargins(9, 9, 9, 10)
        self.addLayout(layout)


class CreateMDL(QtWidgets.QWidget):
    def __init__(self):
        super(CreateMDL, self).__init__()
        self.setMinimumWidth(300)
        self.setWindowTitle("Create New Model")
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.formLayout = CustomVBoxLayout()
        self.mainLayout.addLayout(self.formLayout)
        self.formLayout.setContentsMargins(0, 0, 0, 0)

        self.assetNameLine = QtWidgets.QLineEdit()
        self.formLayout.addRow("Asset Name", self.assetNameLine)

        self.okButton = QtWidgets.QPushButton("Create")
        self.mainLayout.addWidget(self.okButton)

        self.okButton.clicked.connect(self.createModel)

    def createModel(self):
        assetName = self.assetNameLine.text()
        if not assetName:
            return False

        master_grp = cmds.group(em=True, name=str(assetName) + "_model_grp")
        locator_grp = cmds.group(em=True, name="locator_grp", parent=master_grp)

        self.close()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = CreateMDL()
    win.show()
    sys.exit(app.exec_())
