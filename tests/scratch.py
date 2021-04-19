from qtpy import QtWidgets, QtGui, QtCore


class ScreenshotTool(QtWidgets.QDialog):
    def __init__(self):
        super(ScreenshotTool, self).__init__()
        self.setWindowTitle("Capture Asset Screenshot")
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.captureButton = QtWidgets.QPushButton("Capture")
        self.useLastVersionButton = QtWidgets.QPushButton("Use Last Version")
        self.useLastVersionButton.setDisabled(True)
        self.captureButton.setFixedSize(120, 64)
        self.useLastVersionButton.setFixedSize(120, 64)
        self.mainLayout.addWidget(self.captureButton)
        self.mainLayout.addWidget(self.useLastVersionButton)

        self.pix = None


if __name__ == '__main__':
    import sys
    import qdarkstyle
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win = ScreenshotTool()
    win.exec_()
    win.hide()
    sys.exit(app.exec_())
