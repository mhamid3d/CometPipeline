from qtpy import QtWidgets, QtGui, QtCore
from pipeicon import icon_paths
from cometqt.widgets.ui_entity_viewer import EntityViewer
from cometqt.widgets.ui_package_viewer import PackageViewer


class ProductionPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ProductionPage, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)
        self.splitterMain = QtWidgets.QSplitter()
        self.mainLayout.addWidget(self.splitterMain)

        self.entityViewer = EntityViewer()
        self.packageViewer = PackageViewer()

        self.splitterMain.addWidget(self.entityViewer)
        self.splitterMain.addWidget(self.packageViewer)

        self.splitterMain.setSizes([250, 850])


if __name__ == '__main__':
    import sys
    import qdarkstyle
    app = QtWidgets.QApplication(sys.argv)
    win = ProductionPage()
    win.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win.show()
    sys.exit(app.exec_())
