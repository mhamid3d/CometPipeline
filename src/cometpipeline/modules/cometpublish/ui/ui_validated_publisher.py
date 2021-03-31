from cometpublish.ui.ui_version_publisher import VersionPublisher
from qtpy import QtWidgets, QtGui, QtCore


class ValidatedPublisher(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ValidatedPublisher, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.mainLayout)
        self.splitter = QtWidgets.QSplitter()
        self.mainLayout.addWidget(self.splitter)

        self.validationWidget = QtWidgets.QWidget()
        self.validationLayout = QtWidgets.QVBoxLayout()
        self.validationWidget.setLayout(self.validationLayout)


        self.validationTree = QtWidgets.QTreeWidget()
        self.validateButton = QtWidgets.QPushButton("Validate")
        self.versionPublisher = VersionPublisher()


        self.validationLayout.addWidget(self.validationTree)
        self.validationLayout.addWidget(self.validateButton)

        self.splitter.addWidget(self.validationWidget)
        self.splitter.addWidget(self.versionPublisher)


if __name__ == '__main__':
    import sys
    import qdarkstyle
    app = QtWidgets.QApplication(sys.argv)
    win = ValidatedPublisher()
    win.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win.show()
    sys.exit(app.exec_())