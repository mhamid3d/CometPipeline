from qtpy import QtWidgets, QtGui, QtCore
from cometqt.widgets.ui_search_bar import UiSearchBar
from cometqt import util as cqtutil
from pipeicon import icon_paths
from cometpublish import package_util
from cometqt.modelview.model import Model
from cometqt.modelview.tree_view import TreeView
from cometqt.modelview.datasource.package_datasource import PackageDataSource
from cometqt.widgets.ui_delete_dialog import DeleteDialog
import math
import subprocess
import os


class AbstractViewerMenu(QtWidgets.QMenu):
    def __init__(self, parent=None, dataObjects=[]):
        super(AbstractViewerMenu, self).__init__(parent=parent)

        self._dataObjects = dataObjects
        self._formatToApp = {
            'mb': ['Maya', icon_paths.ICON_MAYA_LRG, ["cmaya", "-file"]],
            'ma': ['Maya', icon_paths.ICON_MAYA_LRG, ["cmaya", "-file"]],
            'bif': ['Maya', icon_paths.ICON_MAYA_LRG, ["cmaya", "-file"]],
            'mel': ['Maya', icon_paths.ICON_MAYA_LRG, ["cmaya", "-file"]],
            'py': ['PyCharm', icon_paths.ICON_PYCHARM_LRG, ["pycharm"]],
            'abc': ['USD View', icon_paths.ICON_USD_LRG, ["usdview"]]
        }

        self.copyAction = self.addAction(QtGui.QIcon(icon_paths.ICON_COPY_LRG), "Copy")
        self.copyPathAction = self.addAction(QtGui.QIcon(icon_paths.ICON_COPY_LRG), "Copy Path")
        self.copyUuidAction = self.addAction(QtGui.QIcon(icon_paths.ICON_COPYUUID_LRG), "Copy UUID")
        self.addSeparator()
        self.expandSelAction = self.addAction("Expand Selection")
        self.collapseSelAction = self.addAction("Collapse Selection")
        self.expandAllAction = self.addAction("Expand All")
        self.collapseAllAction = self.addAction("Collapse All")
        self.addSeparator()
        self.setStatusMenu = self.addMenu(QtGui.QIcon(icon_paths.ICON_MONITOR_LRG), "Set Status")
        self.approvedAction = self.setStatusMenu.addAction(QtGui.QIcon(icon_paths.ICON_CHECKGREEN_LRG), "Approved")
        self.pendingAction = self.setStatusMenu.addAction(QtGui.QIcon(icon_paths.ICON_INPROGRESS_LRG), "Pending")
        self.declinedAction = self.setStatusMenu.addAction(QtGui.QIcon(icon_paths.ICON_XRED_LRG), "Declined")
        self.addSeparator()
        self.openInMenu = self.addMenu("Open In")
        self.openInAppsMap = {}
        self.openInExplorerAction = self.openInMenu.addAction("Explorer")
        self.openInTerminalAction = self.openInMenu.addAction("Terminal")
        self.openInMenu.addSeparator()
        self.deleteAction = self.addAction(QtGui.QIcon(icon_paths.ICON_TRASH_LRG), "Delete")
        self.populateOpenInTypes()

    def populateOpenInTypes(self):
        for item, command in self.openInAppsMap:
            self.openInMenu.removeAction(item)
            item.deleteLater()
            del item
        self.openInAppsMap.clear()

        if self._dataObjects and len(self._dataObjects) == 1:
            dataObject = self._dataObjects[0]
            if hasattr(dataObject, "format"):
                title, icon, cmd = self._formatToApp[dataObject.get("format")]
                item = self.openInMenu.addAction(QtGui.QIcon(icon), title)
                cmd.append(dataObject.get("path"))
                self.openInAppsMap[item] = cmd


class PackageTypeNavigator(QtWidgets.QScrollArea):

    filteredTypesChanged = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(PackageTypeNavigator, self).__init__(parent=parent)
        self.mainWidget = QtWidgets.QWidget(self)
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.mainWidget.setLayout(self.mainLayout)
        self.setWidget(self.mainWidget)
        self.setWidgetResizable(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.setStyleSheet("""
            QScrollArea{
                border: none;
            }
        """)
        self.mainWidget.setSizePolicy(self.sizePolicy())
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.packageTypeButtonGroup = QtWidgets.QButtonGroup()
        self.packageTypeButtonGroup.setExclusive(False)
        self.packageTypes = list(package_util.getPackageTypesDict().keys())
        self.packageTypes.insert(0, "All")
        self.defaultButtonStyle = """
                QPushButton{
                    border: none;
                }
                QPushButton:!checked:hover{
                    background: #4e4e4e;
                }
                QPushButton:pressed{
                    background: #1e1e1e;
                }
            """
        self.setup_ui()

        self.packageTypeButtonGroup.buttonClicked.connect(self.updateButtonsToggle)
        self.updateButtonsToggle()

    def setup_ui(self):
        for idx, packageType in enumerate(self.packageTypes):
            packageTypeButton = QtWidgets.QPushButton(packageType)
            packageTypeButton.setCursor(QtCore.Qt.PointingHandCursor)
            packageTypeButton.setCheckable(True)
            packageTypeButton.setIcon(QtGui.QIcon(icon_paths.ICON_PACKAGE_LRG))
            packageTypeButton.setStyleSheet(self.defaultButtonStyle)
            self.packageTypeButtonGroup.addButton(packageTypeButton, idx)
            self.mainLayout.addWidget(packageTypeButton)
            if idx == 0:
                packageTypeButton.setToolTip("Show all package types")
                self.mainLayout.addWidget(cqtutil.v_line())
                packageTypeButton.setIcon(QtGui.QIcon(icon_paths.ICON_VMENU_LRG))
            else:
                tooltip = package_util.getPackageTypesDict()[packageType]['desc']
                packageTypeButton.setToolTip(tooltip)

        self.packageTypeButtonGroup.button(0).setChecked(True)

    def getFilteredTypes(self):
        if self.packageTypeButtonGroup.button(0).isChecked():
            return self.packageTypes[1:]

        filteredTypes = []
        for button in self.packageTypeButtonGroup.buttons()[1:]:
            if button.isChecked():
                filteredTypes.append(self.packageTypes[self.packageTypeButtonGroup.id(button)])

        return filteredTypes

    def setFilteredTypes(self, filteredTypes=[]):
        if filteredTypes == self.packageTypes[1:]:
            self.packageTypeButtonGroup.button(0).setChecked(True)
            self.updateButtonsToggle(self.packageTypeButtonGroup.button(0))
            return

        buttonIds = [self.packageTypes.index(type) for type in filteredTypes]
        for button in self.packageTypeButtonGroup.buttons():
            id = self.packageTypeButtonGroup.id(button)
            button.blockSignals(True)
            button.setChecked(False)
            if id in buttonIds:
                button.setChecked(True)
            button.blockSignals(False)

        self.updateButtonsToggle(button)

    def updateButtonsToggle(self, *args):

        releasedButton = None
        if args:
            releasedButton = args[0]

        allButtonChecked = self.packageTypeButtonGroup.button(0).isChecked()

        if releasedButton:
            # If the 'All' button was just toggled on
            if allButtonChecked and releasedButton == self.packageTypeButtonGroup.button(0):
                for button in self.packageTypeButtonGroup.buttons()[1:]:
                    button.setChecked(False)
                    button.setStyleSheet("""
                    QPushButton{
                        background: #0e5f8e;
                        border: none;
                    }
                """)
            # If the 'All' is already toggled and another button was just pressed
            elif allButtonChecked and not releasedButton == self.packageTypeButtonGroup.button(0):
                self.packageTypeButtonGroup.button(0).setChecked(False)
                for button in self.packageTypeButtonGroup.buttons()[1:]:
                    button.setStyleSheet(self.defaultButtonStyle)
            # If the 'All' button was just toggled off
            elif not allButtonChecked and releasedButton == self.packageTypeButtonGroup.button(0):
                for button in self.packageTypeButtonGroup.buttons()[1:]:
                    button.setStyleSheet(self.defaultButtonStyle)

        self.filteredTypesChanged.emit(self.getFilteredTypes())


class PaginatorWidget(QtWidgets.QFrame):

    @property
    def currentPage(self):
        return self.pageButtonsGroup.checkedId()

    @property
    def batchSize(self):
        return int(self.batchSizeComboBox.currentText())

    pageChanged = QtCore.Signal(int)
    batchSizeChanged = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(PaginatorWidget, self).__init__(parent)
        self.model = self.parent().model
        self.dataSource = self.parent().dataSource
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)

        self.batchSizeComboBox = QtWidgets.QComboBox()
        self.batchSizeComboBox.addItems([str(x) for x in [5, 10, 25, 50, 100]])
        self.batchSizeComboBox.setCurrentText("100")

        rpp = QtWidgets.QLabel("Results Per Page: ")
        rpp.setIndent(0)
        rpp.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        rpp.setStyleSheet("font-size: 14px;")
        self.mainLayout.addWidget(rpp)
        self.mainLayout.addWidget(self.batchSizeComboBox)

        spacer = QtWidgets.QSpacerItem(150, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer)

        self.totalCount = QtWidgets.QLabel()
        self.mainLayout.addWidget(self.totalCount)

        spacer2 = QtWidgets.QSpacerItem(150, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(spacer2)

        self.pageButtonsGroup = QtWidgets.QButtonGroup()

        self.populate_page_buttons()
        self.update_total_count()

        self.batchSizeComboBox.currentIndexChanged.connect(lambda: self.batchSizeChanged.emit(self.batchSize))
        self.pageButtonsGroup.buttonToggled.connect(lambda: self.pageChanged.emit(self.currentPage))

        self.batchSizeChanged.connect(self.populate_page_buttons)
        self.batchSizeChanged.connect(self.dataSource.setBatchSize)
        self.pageChanged.connect(lambda: self.dataSource.setPage(self.currentPage - 1))

    def update_total_count(self):
        self.totalCount.setText("{} results".format(self.dataSource.getPotentialResults().size()))

    def populate_page_buttons(self):
        for button in self.pageButtonsGroup.buttons():
            self.pageButtonsGroup.removeButton(button)
            button.deleteLater()

        all_results = self.dataSource.getPotentialResults().size()

        pageCount = int(math.ceil((float(all_results) if all_results else 1) / float(self.batchSize)))

        for i in range(pageCount):
            i += 1
            btn = QtWidgets.QPushButton(str(i))
            btn.setFixedSize(26, 26)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton::checked{
                    border: 0;
                }
            """)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            self.pageButtonsGroup.addButton(btn, i)
            self.mainLayout.addWidget(btn)

        self.pageButtonsGroup.button(1).setChecked(True)


class PackageTree(TreeView):
    def __init__(self, parent=None):
        super(PackageTree, self).__init__(parent=parent)
        # self.header().moveSection(0, 1)
        # self.header().setFirstSectionMovable(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

    def contextMenu(self, pos):

        selectedItems = []
        for idx in self.selectedIndexes():
            item = self.model().itemFromIndex(idx)
            if hasattr(item, "dataObject"):
                selectedItems.append(item)
        selectedItems = list(set(selectedItems))
        selectedItems = sorted(selectedItems, key=lambda i: self.model().indexFromItem(i).row())

        if not selectedItems:
            return

        self._menu = AbstractViewerMenu(parent=self, dataObjects=[x.dataObject for x in selectedItems])
        self.main_action = self._menu.exec_(self.mapToGlobal(pos))

        if not self.main_action:
            return

        if self.main_action == self._menu.copyAction:
            copyStr = "\n".join([x.dataObject.get("label") for x in selectedItems])
            cb = QtWidgets.QApplication.clipboard()
            cb.clear(mode=cb.Clipboard)
            cb.setText(copyStr, mode=cb.Clipboard)
        elif self.main_action == self._menu.copyPathAction:
            copyStr = "\n".join([x.dataObject.get("path") for x in selectedItems])
            cb = QtWidgets.QApplication.clipboard()
            cb.clear(mode=cb.Clipboard)
            cb.setText(copyStr, mode=cb.Clipboard)
        elif self.main_action == self._menu.copyUuidAction:
            copyStr = "\n".join([x.dataObject.get("uuid") for x in selectedItems])
            cb = QtWidgets.QApplication.clipboard()
            cb.clear(mode=cb.Clipboard)
            cb.setText(copyStr, mode=cb.Clipboard)
        elif self.main_action == self._menu.expandAllAction:
            self.expandAll()
        elif self.main_action == self._menu.collapseAllAction:
            self.collapseAll()
        elif self.main_action == self._menu.expandSelAction:
            self.expand(self.selectedIndexes()[0])
        elif self.main_action == self._menu.collapseSelAction:
            self.collapse(self.selectedIndexes()[0])
        elif self.main_action in [self._menu.approvedAction, self._menu.declinedAction, self._menu.pendingAction]:
            statusMap = {
                self._menu.approvedAction: 'approved',
                self._menu.pendingAction: 'pending',
                self._menu.declinedAction: 'declined'
            }
            statusStr = statusMap[self.main_action]
            dataObjects = []
            for sel in selectedItems:
                if not hasattr(sel, "dataObject"):
                    continue
                do = sel.dataObject
                if do._name == "Package" and do.latest():
                    dataObjects.append(do.latest())
                    continue
                dataObjects.append(do)
            dataObjects = set(dataObjects)

            if not dataObjects:
                return

            for dataObject in dataObjects:
                dataObject.status = statusStr
                dataObject.save(update_time=False)

            self.model().dataNeedsRefresh.emit()
        elif self.main_action in [self._menu.openInExplorerAction, self._menu.openInTerminalAction]:
            filePaths = [x.dataObject.get("path") for x in selectedItems]
            for path in filePaths:
                if self.main_action == self._menu.openInExplorerAction:
                    subprocess.Popen(["nemo", path])
                elif self.main_action == self._menu.openInTerminalAction:
                    if os.path.isfile(path):
                        path = os.path.abspath(os.path.join(path, os.pardir))
                    subprocess.Popen(["gnome-terminal", "--working-directory={}".format(path)])
        elif self.main_action in list(self._menu.openInAppsMap.keys()):
            subprocess.Popen(self._menu.openInAppsMap[self.main_action])
        elif self.main_action == self._menu.deleteAction:
            deleteResult = DeleteDialog(parent=self, dataObjects=selectedItems)
            deleteResult.exec_()
            self.model().dataNeedsRefresh.emit()


class PackageViewer(QtWidgets.QWidget):

    SEARCH_HEIGHT = 32

    def __init__(self, parent=None):
        super(PackageViewer, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.topSearchLayout = QtWidgets.QHBoxLayout()

        self.topLabel = QtWidgets.QLabel("Packages")
        self.refreshButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_RELOAD_LRG)
        self.filterButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_FILTER_LRG)
        self.searchBar = UiSearchBar(height=self.SEARCH_HEIGHT)
        self.packageViewport = QtWidgets.QWidget()
        self.packageViewportLayout = QtWidgets.QVBoxLayout()
        self.packageViewportLayout.setAlignment(QtCore.Qt.AlignTop)
        self.packageViewportLayout.setContentsMargins(0, 0, 0, 0)
        self.packageViewport.setLayout(self.packageViewportLayout)
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

        self.packageTypeNavigator = PackageTypeNavigator(parent=self)
        self.packageViewportLayout.addWidget(self.packageTypeNavigator)

        self.packageTree = PackageTree(parent=self)
        self.model = Model()
        self.model.setAlternatingRowColors(True)
        self.dataSource = PackageDataSource()
        self.paginatorWidget = PaginatorWidget(parent=self)
        self.dataSource.setBatchSize(self.paginatorWidget.batchSize)
        self.model.setDataSource(self.dataSource)
        self.packageTree.setModel(self.model)
        self.packageViewportLayout.addWidget(self.packageTree)
        self.packageViewportLayout.addWidget(self.paginatorWidget)

        self.packageTypeNavigator.filteredTypesChanged.connect(self.populate_viewport)
        self.refreshButton.clicked.connect(lambda: self.dataSource.setNeedToRefresh(True))

    @property
    def productionPage(self):
        from cometbrowser.ui.ui_production_page import ProductionPage
        return cqtutil.get_top_window(self, ProductionPage)

    def populate_viewport(self):

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        filteredTypes = self.packageTypeNavigator.getFilteredTypes()
        entities = self.productionPage.entityViewer.selectedEntities()

        if entities:
            self.dataSource.dataFilter.clear()
            self.dataSource.dataFilter.search(self.dataSource.interface,
                                              parent_uuid__in=[entity.getUuid() for entity in entities],
                                              type__in=filteredTypes)
            self.dataSource.setNeedToRefresh(True)
            self.packageTree._resizeAllColumnsToContents()
        else:
            self.model.clear()

        self.paginatorWidget.update_total_count()
        self.paginatorWidget.populate_page_buttons()

        QtWidgets.QApplication.restoreOverrideCursor()


if __name__ == '__main__':
    import sys
    import qdarkstyle
    app = QtWidgets.QApplication(sys.argv)
    win = PackageViewer()
    win.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win.show()
    sys.exit(app.exec_())