from qtpy import QtWidgets, QtGui, QtCore
from cometqt.widgets.ui_search_bar import UiSearchBar
from cometqt import util as cqtutil
from pipeicon import icon_paths
from cometpipe.core import ASSET_PREFIX_DICT
import mongorm
import os


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
        self.addSeparator()
        self.editEntityAction = self.addAction("Edit Entity")

        if cqtutil.get_top_window(self, EntityViewer).isDialog():
            self.editEntityAction.setDisabled(True)

        self.copyAction.setIcon(QtGui.QIcon(icon_paths.ICON_COPY_LRG))
        self.copyPathAction.setIcon(QtGui.QIcon(icon_paths.ICON_COPY_LRG))
        self.copyUuidAction.setIcon(QtGui.QIcon(icon_paths.ICON_COPYUUID_LRG))


class EntityTree(QtWidgets.QTreeWidget):
    def __init__(self, parent):
        super(EntityTree, self).__init__(parent=parent)
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
        elif self.main_action == self._menu.editEntityAction:
            if self.currentItem():
                EntitySettings(parent=self, entityObject=self.currentItem().dataObject).exec_()


class EntitySettings(QtWidgets.QDialog):
    def __init__(self, parent=None, entityObject=None):
        super(EntitySettings, self).__init__(parent=parent)
        self.setWindowTitle("Edit Entity - [{}]".format(entityObject.get("label")))
        self.mainLayout = QtWidgets.QFormLayout()
        self.mainLayout.setFormAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.mainLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.setLayout(self.mainLayout)

        self.object = entityObject

        self.btnBox = QtWidgets.QDialogButtonBox()
        self.createButton = QtWidgets.QPushButton("Edit")
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.btnBox.addButton(self.createButton, QtWidgets.QDialogButtonBox.AcceptRole)
        self.btnBox.addButton(self.cancelButton, QtWidgets.QDialogButtonBox.RejectRole)

        self.btnBox.accepted.connect(self.commitChanges)
        self.btnBox.rejected.connect(self.reject)

        if self.object.INTERFACE_STRING == "entity":
            self.rndCheckBox = QtWidgets.QCheckBox()
            self.rndCheckBox.setChecked(not self.object.get("production"))
            self.rndCheckBox.setCursor(QtCore.Qt.PointingHandCursor)
            self.mainLayout.addRow("RND Entity", self.rndCheckBox)

        if self.object.get("type") == "asset":
            pass
        elif self.object.get("type") == "sequence":
            pass
        elif self.object.get("type") == "shot":
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

            inputFR = self.object.get("framerange")
            if inputFR:
                self.beginFrameSpin.setValue(inputFR[0])
                self.endFrameSpin.setValue(inputFR[1])

            self.mainLayout.addRow("Frame Range", self.resFrame)

        self.mainLayout.addWidget(self.btnBox)

    def update_rnd(self, dataObject, value):

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        dataObject.production = value
        dataObject.save()

        # TODO: do we really need to set all shots in a sequence to the same value?

        if dataObject.get("type") == "sequence":
            h = mongorm.getHandler()
            f = mongorm.getFilter()
            f.search(h['entity'], parent_uuid=dataObject.uuid)
            all_shots = h['entity'].all(f)
            for shot in all_shots:
                shot.production = value
                shot.save()

        QtWidgets.QApplication.restoreOverrideCursor()

    def update_framerange(self, dataObject, value):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        dataObject.framerange = value
        dataObject.save()

        QtWidgets.QApplication.restoreOverrideCursor()

    def commitChanges(self):
        if self.object.INTERFACE_STRING == "entity":
            self.update_rnd(self.object, not self.rndCheckBox.isChecked())
        if self.object.get("type") == "shot":
            self.update_framerange(self.object, [self.beginFrameSpin.value(), self.endFrameSpin.value()])

        self.accept()


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

        self.refreshButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_RELOAD_LRG)
        self.filterButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_FILTER_LRG)
        self.assetsButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_ASSET_LRG)
        self.productionButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_SEQUENCE_LRG)
        self.entityTypeButtonGrp = QtWidgets.QButtonGroup()
        self.searchBar = UiSearchBar(height=self.SEARCH_HEIGHT)
        self.entityTree = EntityTree(parent=self)

        self.assetsButton.setCheckable(True)
        self.productionButton.setCheckable(True)
        self.assetsButton.setChecked(True)
        self.entityTypeButtonGrp.addButton(self.assetsButton, 0)
        self.entityTypeButtonGrp.addButton(self.productionButton, 1)

        self.searchBar.editingFinished.connect(self.doSearch)
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
        # self.mainLayout.addWidget(cqtutil.h_line())

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
        self._isDialog = bool

    def isDialog(self):
        return self._isDialog

    def populate(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        jobObject = self._currentJob
        handler = mongorm.getHandler()
        filter = mongorm.getFilter()

        self.entityTree.clear()

        if jobObject:

            filter.search(handler['entity'], job=jobObject.job, type='job', label=jobObject.job)
            jobEntityObject = handler['entity'].one(filter)
            filter.clear()

            jobRootItem = QtWidgets.QTreeWidgetItem(self.entityTree)
            jobRootItem.setText(0, jobEntityObject.get("label"))
            jobRootItem.setIcon(0, QtGui.QIcon(icon_paths.ICON_COMETPIPE_LRG))
            jobRootItem.dataObject = jobEntityObject

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


class EntityPickerDialog(QtWidgets.QDialog):
    def __init__(self, setEnvOnClose=True):
        super(EntityPickerDialog, self).__init__()
        self.setWindowTitle("Set Entity")
        self._setEnvOnClose = setEnvOnClose
        handler = mongorm.getHandler()
        filt = mongorm.getFilter()
        # TODO
        filt.search(handler['job'], label="DELOREAN")
        job = handler['job'].one(filt)
        self.entityViewer = EntityViewer()
        self.entityViewer.setContentsMargins(0, 0, 0, 0)
        self.entityViewer.setCurrentJob(job)
        self.entityViewer.setIsDialog(True)
        self.entityViewer.populate()

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.diagButtonBox = QtWidgets.QDialogButtonBox()
        self.diagButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        self.mainLayout.addWidget(self.entityViewer)
        self.mainLayout.addWidget(self.diagButtonBox)

        self.diagButtonBox.accepted.connect(self.accept)
        self.diagButtonBox.rejected.connect(self.reject)

        self.loadCurrent()

    def loadCurrent(self):
        return

        entity = os.getenv("ENTITY")
        handler = mongorm.getHandler()

        filt = mongorm.getFilter()
        filt.search(handler['entity'], job=os.getenv("JOB"), label=entity)


        if etype:
            self.entityViewer.setEntityType(etype)
        if entity:
            for item in self.entityViewer.getAllItems():
                if item.text(0) == entity:
                    self.entityViewer.entityTree.setCurrentItem(item)
                    break

    def getSelection(self):
        return self.entityViewer.entityTree.selectedItems()


if __name__ == '__main__':
    import sys
    import qdarkstyle

    app = QtWidgets.QApplication(sys.argv)
    win = EntityViewer()
    win.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win.show()
    sys.exit(app.exec_())
