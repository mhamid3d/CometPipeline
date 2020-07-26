from qtpy import QtWidgets, QtGui, QtCore
from pipeicon import icon_paths
from pipeqt.widgets.ui_search_bar import UiSearchBar
from pipeqt import util as pqtutil
import mongorm


class AbstractTreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent_main=None, dataObject=None, treeParent=None):
        super(AbstractTreeItem, self).__init__(treeParent)
        self.parent_main = parent_main
        self.dataObject = dataObject
        self.setText(0, self.dataObject.get("label"))
        self.setIcon(0, QtGui.QIcon(self.dataObject.get("thumbnail")))


class AbstractView(QtWidgets.QFrame):

    SEARCH_HEIGHT = 38

    def __init__(self, parent_main=None):
        super(AbstractView, self).__init__()
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.mainLayout)

        self.parent_main = parent_main

        self.topSearchLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.topSearchLayout)

        self.search_bar = UiSearchBar(height=self.SEARCH_HEIGHT)

        self.reload_button = QtWidgets.QPushButton()
        self.reload_button.setStyleSheet("""
            QPushButton{
                background: none;
                padding: 0px;
                border: none;
                border-radius: 1px;
            }
            QPushButton:hover{
                border: 1px solid #148CD2;
                background: #3e3e3e;
            }
            QPushButton:pressed{
                background: #1e1e1e;
            }
        """)
        self.reload_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.reload_button.setMinimumSize(self.SEARCH_HEIGHT, self.SEARCH_HEIGHT)
        self.reload_button.setIcon(QtGui.QIcon(icon_paths.ICON_RELOAD_LRG))

        self.filter_button = QtWidgets.QPushButton()
        self.filter_button.setStyleSheet("""
            QPushButton{
                background: none;
                padding: 0px;
                border: none;
                border-radius: 1px;
            }
            QPushButton:hover{
                border: 1px solid #148CD2;
                background: #3e3e3e;
            }
            QPushButton:pressed{
                background: #1e1e1e;
            }
        """)
        self.filter_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.filter_button.setMinimumSize(self.SEARCH_HEIGHT, self.SEARCH_HEIGHT)
        self.filter_button.setIcon(QtGui.QIcon(icon_paths.ICON_FILTER_LRG))

        self.topSearchLayout.addWidget(self.search_bar)
        self.topSearchLayout.addWidget(self.reload_button)
        self.topSearchLayout.addWidget(self.filter_button)

        self.mainLayout.addWidget(pqtutil.h_line())

        self.handler = mongorm.getHandler()
        self.filter = mongorm.getFilter()
        self.items = None

        self.setup_view()

    def setup_view(self):
        self.view_splitter = QtWidgets.QSplitter()
        self.view_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.view_splitter.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderHidden(True)
        self.tree.setIconSize(QtCore.QSize(32, 32))
        self.tree.setExpandsOnDoubleClick(False)
        self.tree.itemSelectionChanged.connect(self.populate_items)

        self.item_scroll = QtWidgets.QScrollArea()
        self.items_widget = QtWidgets.QWidget()
        self.item_scroll.setWidget(self.items_widget)
        self.item_scroll.setWidgetResizable(True)
        self.items_layout = pqtutil.FlowLayout()
        self.items_widget.setLayout(self.items_layout)

        self.view_splitter.addWidget(self.tree)
        self.view_splitter.addWidget(self.item_scroll)

        self.mainLayout.addWidget(self.view_splitter)

        self.tree.setStyleSheet("""
            QTreeView{
                background: #1e1e1e;
                color: #D9D9D9;
                border: 0px;
                selection-background-color: transparent;
                border-radius: 1px;
            }
            QTreeView:item{
                background-color: #3e3e3e;
                margin: 1px 0px 1px 0px;
                padding: 2px;
                border: 1px solid #4e4e4e;
                border-right: 0px;
            }
            QTreeView::item:hover{
                background-color: #807153;
                }
            QTreeView::item:selected{
                background-color: #128ba6;
            }
        """)
        self.item_scroll.setStyleSheet("QScrollArea{border-radius: 0px; padding: 10px;}")

    def populate_assets(self):
        raise NotImplementedError

    def populate_items(self):
        raise NotImplementedError