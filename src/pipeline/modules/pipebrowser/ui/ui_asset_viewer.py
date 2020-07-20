from qtpy import QtWidgets, QtGui, QtCore
from pipeicon import icon_paths
from pipebrowser.ui.ui_abstract_view import AbstractView, AbstractTreeItem
import mongorm
import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PackageItem(QtWidgets.QWidget):
    def __init__(self):
        super(PackageItem, self).__init__()
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setFixedSize(192, 192)
        self.label = QtWidgets.QLabel("LOOK_char_ellie_lod300")
        self.thumbnail = QtWidgets.QLabel()
        self._pixmap = QtGui.QPixmap("C:/Users/mhamid/Pictures/Carrack_Landed_Final_Gurmukh.png")
        self._pixmap = self._pixmap.scaledToWidth(192, QtCore.Qt.SmoothTransformation)
        self.thumbnail.setPixmap(self._pixmap)
        self.thumbnail.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setContentsMargins(1, 1, 1, 1)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet("""
            QWidget{
                border-radius: 1px;
                border: 1px solid #4e4e4e;
                background: #3e3e3e;
            }
            QWidget:hover{
                border: 1px solid #148CD2;
            }
        """)
        self.label.setStyleSheet("""
            QLabel{
                font-size: 13px;
                background: #5e5e5e;
                border: none;
            }
            QLabel:hover{
                border: none;
            }
        """)
        self.thumbnail.setStyleSheet("""
            QLabel{
                border: none;
            }
            QLabel:hover{
                border: none;
            }
        """)
        self.mainLayout.addWidget(self.label, alignment=QtCore.Qt.AlignTop)
        self.mainLayout.addWidget(self.thumbnail, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)

    def paintEvent(self, event):
        opt = QtWidgets.QStyleOption()
        opt.init(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, painter, self)


class AssetViewer(AbstractView):
    def __init__(self, parent_main=None):
        super(AssetViewer, self).__init__(parent_main=parent_main)
        self.view_splitter.setSizes([200, 900])

    def populate_assets(self):
        self.filter.search(self.handler['entity'], type='asset', job=self.parent_main.currentJob.get("label"))
        self.items = self.handler['entity'].all(self.filter)
        print self.parent_main.currentJob.get("label")

        job_root_item = AbstractTreeItem(parent_main=self.parent_main, dataObject=self.parent_main.currentJob,
                                         treeParent=self.tree)

        for asset in self.items:
            asset_item = QtWidgets.QTreeWidgetItem(job_root_item)
            asset_item.setText(0, asset.label)
            asset_item.setIcon(0, QtGui.QIcon(asset.thumbnail))
            asset_item.object = asset

        self.tree.expandAll()

    def populate_items(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        try:
            current_asset = self.tree.selectedItems()[0]
        except IndexError:
            current_asset = None

        if current_asset:
            for rc in range(50):
                item_widget = PackageItem()

                self.items_layout.addWidget(item_widget)

        QtWidgets.QApplication.restoreOverrideCursor()