from qtpy import QtWidgets, QtGui, QtCore
from cometqt.widgets.ui_search_bar import UiSearchBar
from cometqt import util as cqtutil
from pipeicon import icon_paths


class PackageViewer(QtWidgets.QWidget):

    SEARCH_HEIGHT = 32

    def __init__(self):
        super(PackageViewer, self).__init__()
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.topSearchLayout = QtWidgets.QHBoxLayout()

        self.topLabel = QtWidgets.QLabel("Packages")
        self.refreshButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_RELOAD_LRG)
        self.filterButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_FILTER_LRG)
        self.searchBar = UiSearchBar(height=self.SEARCH_HEIGHT)
        self.packageViewport = QtWidgets.QWidget()
        self.packageViewport.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.topLabel.setIndent(0)
        self.topLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.topLabel.setStyleSheet("""
            QLabel{
                background: none;
                color: #a6a6a6;
                font-size: 20px;
            }
        """)

        self.mainLayout.addWidget(self.topLabel)
        self.mainLayout.addLayout(self.topSearchLayout)
        self.topSearchLayout.addWidget(self.searchBar)
        self.topSearchLayout.addWidget(self.refreshButton)
        self.topSearchLayout.addWidget(self.filterButton)
        self.mainLayout.addWidget(cqtutil.h_line())
        self.mainLayout.addWidget(self.packageViewport)


if __name__ == '__main__':
    import sys
    import qdarkstyle
    app = QtWidgets.QApplication(sys.argv)
    win = PackageViewer()
    win.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win.show()
    sys.exit(app.exec_())