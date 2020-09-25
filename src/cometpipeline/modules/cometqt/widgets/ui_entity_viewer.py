from qtpy import QtWidgets, QtGui, QtCore
from cometqt.widgets.ui_search_bar import UiSearchBar
from cometqt import util as cqtutil
from pipeicon import icon_paths
from cometpipe.core import ASSET_PREFIX_DICT
import mongorm


class EntityMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super(EntityMenu, self).__init__(parent=parent)

        self.copyAction = self.addAction("Copy")
        self.copyPathAction = self.addAction("Copy Path")
        self.copyUuidAction = self.addAction("Copy UUID")
        self.addSeparator()
        self.expandSelAction = self.addAction("Expand Selection")
        self.collapseSelAction = self.addAction("Collapse Selection")
        self.expandAllAction = self.addAction("Expand All")
        self.collapseAllAction = self.addAction("Collapse All")

        self.copyAction.setIcon(QtGui.QIcon(icon_paths.ICON_COPY_LRG))
        self.copyPathAction.setIcon(QtGui.QIcon(icon_paths.ICON_COPY_LRG))
        self.copyUuidAction.setIcon(QtGui.QIcon(icon_paths.ICON_COPYUUID_LRG))


class EntityTree(QtWidgets.QTreeWidget):
    def __init__(self):
        super(EntityTree, self).__init__()
        self.setStyleSheet("""
            QTreeView{
                border-radius: 0px;
            }
        """)
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

    def contextMenu(self, pos):
        selectedItems = [x for x in self.selectedItems() if hasattr(x, "dataObject")]

        if not selectedItems:
            return

        self._menu = EntityMenu(parent=self)
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
            self.expandItem(self.selectedItems()[0])
        elif self.main_action == self._menu.collapseSelAction:
            self.collapseItem(self.selectedItems()[0])


class EntitySettings(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(EntitySettings, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QFormLayout()
        self.mainLayout.setFormAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.mainLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.setLayout(self.mainLayout)

    def update_with_entity(self, selection):

        for child in range(self.mainLayout.count()):
            widget = self.mainLayout.itemAt(child).widget()
            widget.deleteLater()

        if not selection:
            return

        self.selection = selection[0]
        entityObject = self.selection.dataObject

        if entityObject.INTERFACE_STRING == "entity":
            self.rndCheckBox = QtWidgets.QCheckBox()
            self.rndCheckBox.setChecked(not entityObject.get("production"))
            self.rndCheckBox.setCursor(QtCore.Qt.PointingHandCursor)
            self.rndCheckBox.stateChanged.connect(lambda: self.update_rnd(entityObject, not self.rndCheckBox.isChecked()))
            self.mainLayout.addRow("RND Entity", self.rndCheckBox)

        if entityObject.get("type") == "asset":
            pass
        elif entityObject.get("type") == "sequence":
            pass
        elif entityObject.get("type") == "shot":
            self.resFrame = QtWidgets.QFrame()
            self.resFrame.setContentsMargins(0, 0, 0, 0)
            self.resFrame.setStyleSheet("""
                QFrame{
                    border: none;
                }
            """)
            self.resLayout = QtWidgets.QHBoxLayout()
            self.resLayout.setContentsMargins(0, 0, 0, 0)
            self.resFrame.setLayout(self.resLayout)
            self.beginFrameSpin = QtWidgets.QSpinBox()
            self.endFrameSpin = QtWidgets.QSpinBox()
            self.resLayout.addWidget(self.beginFrameSpin)
            self.resLayout.addWidget(self.endFrameSpin)
            self.beginFrameSpin.setRange(0, 99999)
            self.endFrameSpin.setRange(0, 99999)

            inputFR = entityObject.get("framerange")
            if inputFR:
                self.beginFrameSpin.setValue(inputFR[0])
                self.endFrameSpin.setValue(inputFR[1])

            self.mainLayout.addRow("Frame Range", self.resFrame)

            self.beginFrameSpin.editingFinished.connect(lambda: self.update_framerange(entityObject,
                                                                                       [self.beginFrameSpin.value(),
                                                                                        self.endFrameSpin.value()]))
            self.endFrameSpin.editingFinished.connect(lambda: self.update_framerange(entityObject,
                                                                                       [self.beginFrameSpin.value(),
                                                                                        self.endFrameSpin.value()]))

    def update_rnd(self, dataObject, value):

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        dataObject.production = value
        dataObject.save()

        if dataObject.get("type") == "sequence":
            h = mongorm.getHandler()
            f = mongorm.getFilter()
            f.search(h['entity'], parent_uuid=dataObject.uuid)
            all_shots = h['entity'].all(f)
            for shot in all_shots:
                shot.production = value
                shot.save()

            for c in range(self.selection.childCount()):
                ch = self.selection.child(c)
                ch.dataObject.production = value
                ch.dataObject.save()

        QtWidgets.QApplication.restoreOverrideCursor()

    def update_framerange(self, dataObject, value):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        dataObject.framerange = value
        dataObject.save()

        QtWidgets.QApplication.restoreOverrideCursor()


class EntityViewer(QtWidgets.QWidget):
    SEARCH_HEIGHT = 32
    TYPE_ASSETS = "assets"
    TYPE_PRODUCTION = "production"
    TYPE_DEFAULT = TYPE_ASSETS

    def __init__(self):
        super(EntityViewer, self).__init__()
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.topLabelLayout = QtWidgets.QHBoxLayout()
        self.topLabelLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.topSearchLayout = QtWidgets.QHBoxLayout()

        self.topLabel = QtWidgets.QLabel("Entities")
        self.topLabel.setIndent(0)
        self.topLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.topLabel.setStyleSheet("""
            QLabel{
                background: none;
                color: #a6a6a6;
                font-size: 20px;
            }
        """)

        self.settingsLabel = QtWidgets.QLabel("Entity Settings")
        self.settingsLabel.setIndent(0)
        self.settingsLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.settingsLabel.setStyleSheet(self.topLabel.styleSheet())

        self.refreshButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_RELOAD_LRG)
        self.filterButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_FILTER_LRG)
        self.assetsButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_ASSET_LRG)
        self.productionButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_SEQUENCE_LRG)
        self.entityTypeButtonGrp = QtWidgets.QButtonGroup()
        self.searchBar = UiSearchBar(height=self.SEARCH_HEIGHT)
        self.entityTree = EntityTree()
        self.entitySettings = EntitySettings(parent=self)

        self.assetsButton.setCheckable(True)
        self.productionButton.setCheckable(True)
        self.assetsButton.setChecked(True)
        self.entityTypeButtonGrp.addButton(self.assetsButton, 0)
        self.entityTypeButtonGrp.addButton(self.productionButton, 1)

        self.searchBar.editingFinished.connect(self.doSearch)
        self.updateEntityFunc = lambda: self.entitySettings.update_with_entity(self.entityTree.selectedItems())
        self.entityTree.itemSelectionChanged.connect(self.updateEntityFunc)
        self.refreshButton.clicked.connect(self.populate)
        self.productionButton.clicked.connect(lambda: self.setEntityType(self.TYPE_PRODUCTION))
        self.assetsButton.clicked.connect(lambda: self.setEntityType(self.TYPE_ASSETS))

        self.mainLayout.addLayout(self.topLabelLayout)
        self.topLabelLayout.addWidget(self.topLabel)
        self.topLabelLayout.addWidget(self.assetsButton)
        self.topLabelLayout.addWidget(self.productionButton)
        self.mainLayout.addLayout(self.topSearchLayout)
        self.topSearchLayout.addWidget(self.searchBar)
        self.topSearchLayout.addWidget(self.refreshButton)
        self.topSearchLayout.addWidget(self.filterButton)
        self.mainLayout.addWidget(cqtutil.h_line())
        self.mainLayout.addWidget(self.entityTree)
        self.mainLayout.addWidget(self.settingsLabel)
        self.mainLayout.addWidget(cqtutil.h_line())
        self.mainLayout.addWidget(self.entitySettings)

        self._currentJob = None
        self._isDialog = False
        self.setIsDialog(False)
        self._entityType = self.TYPE_DEFAULT

    @property
    def entityType(self):
        return self._entityType

    def setEntityType(self, entityType):
        assert entityType in [self.TYPE_ASSETS, self.TYPE_PRODUCTION], "Invalid entity type"

        self._entityType = entityType
        if self._entityType == self.TYPE_ASSETS:
            self.assetsButton.setChecked(True)
        elif self._entityType == self.TYPE_PRODUCTION:
            self.productionButton.setChecked(True)
        self.populate()

    def getAllItems(self, dataItemsOnly=False):
        objects = []
        iterator = QtWidgets.QTreeWidgetItemIterator(self.entityTree)
        while iterator.value():
            item = iterator.value()
            if dataItemsOnly:
                if hasattr(item, "dataObject"):
                    objects.append(item)
            else:
                objects.append(item)
            iterator += 1

        return objects

    def setCurrentJob(self, jobObject):
        self._currentJob = jobObject
        self.populate()

    def currentJob(self):
        return self._currentJob

    def setIsDialog(self, bool):
        if bool:
            self.entityTree.itemSelectionChanged.disconnect(self.updateEntityFunc)
            self.settingsLabel.hide()
            self.entitySettings.hide()
            self._isDialog = True
        else:
            self.entityTree.itemSelectionChanged.connect(self.updateEntityFunc)
            self.settingsLabel.show()
            self.entitySettings.show()
            self._isDialog = False

    def isDialog(self):
        return self._isDialog

    def populate(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        jobObject = self._currentJob
        handler = mongorm.getHandler()
        filter = mongorm.getFilter()

        self.entityTree.clear()

        jobRootItem = QtWidgets.QTreeWidgetItem(self.entityTree)
        jobRootItem.setText(0, jobObject.get("label"))
        jobRootItem.setIcon(0, QtGui.QIcon(icon_paths.ICON_COMETPIPE_LRG))
        jobRootItem.dataObject = jobObject

        if self._entityType == self.TYPE_ASSETS:
            filter.search(handler['entity'], job=jobObject.job, type='asset')
            all_assets = handler['entity'].all(filter)

            for catFull, cat in ASSET_PREFIX_DICT.items():

                catItem = QtWidgets.QTreeWidgetItem(jobRootItem)
                catItem.setText(0, catFull)
                catItem.setIcon(0, QtGui.QIcon(icon_paths.ICON_ASSETGROUP_LRG))
                catItem.setFlags(QtCore.Qt.ItemIsEnabled)

                for asset in all_assets:
                    if asset.get("prefix") == cat:
                        asset_item = QtWidgets.QTreeWidgetItem(catItem)
                        asset_item.setText(0, asset.get("label"))
                        asset_item.setIcon(0, QtGui.QIcon(icon_paths.ICON_ASSET_LRG))
                        asset_item.dataObject = asset

        elif self._entityType == self.TYPE_PRODUCTION:
            filter.search(handler['entity'], job=jobObject.job, type='sequence')
            all_sequences = handler['entity'].all(filter)
            filter.clear()
            filter.search(handler['entity'], job=jobObject.job, type='shot')
            all_shots = handler['entity'].all(filter)

            for sequence in all_sequences:

                seq_item = QtWidgets.QTreeWidgetItem(jobRootItem)
                seq_item.setText(0, sequence.get("label"))
                seq_item.setIcon(0, QtGui.QIcon(icon_paths.ICON_SEQUENCE_LRG))
                seq_item.dataObject = sequence

                for shot in all_shots:
                    if shot.get("parent_uuid") == sequence.uuid:
                        shot_item = QtWidgets.QTreeWidgetItem(seq_item)
                        shot_item.setText(0, shot.get("label"))
                        shot_item.setIcon(0, QtGui.QIcon(icon_paths.ICON_SHOT_LRG))
                        shot_item.dataObject = shot

        self.doSearch()
        self.entityTree.expandAll()

        QtWidgets.QApplication.restoreOverrideCursor()

    def doSearch(self):
        currentText = self.searchBar.text()
        keep_items = []
        for item in self.getAllItems():
            item.setHidden(True)
            if currentText is None:
                item.setHidden(False)
            elif currentText.upper() in item.text(0).upper():
                keep_items.append(item)

        for kp in keep_items:
            kp.setHidden(False)
            all_parent = []
            while kp.parent():
                kp = kp.parent()
                all_parent.append(kp)
            for parent in all_parent:
                parent.setHidden(False)


if __name__ == '__main__':
    import sys
    import qdarkstyle

    app = QtWidgets.QApplication(sys.argv)
    win = EntityViewer()
    win.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win.show()
    sys.exit(app.exec_())
