from qtpy import QtWidgets, QtGui, QtCore
from cometqt.widgets.ui_search_bar import UiSearchBar
from cometqt.widgets.ui_job_combobox import JobComboBox
from cometqt import util as cqtutil
from pipeicon import icon_paths, util as iconutil
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


class TreeSelectionModel(QtCore.QItemSelectionModel):
    STATE_UNSELECTED = 0
    STATE_PARTIALLY_SELECTED = 1
    STATE_SELECTED = 2

    refreshRequested = QtCore.Signal()

    def __init__(self, model, parent=None):
        """
        """
        super(TreeSelectionModel, self).__init__(model, parent)
        self.__propagateSelection = True
        self.__showPartiallySelected = True
        self.__lastselectionflags = 0

    def __propagateSelectionDown(self, selection):
        childSelection = QtCore.QItemSelection()
        indexQueue = selection.indexes()
        while indexQueue:
            index = indexQueue.pop(0)
            if index.isValid():
                numChildren = self.model().rowCount(index)
                childIndexes = [self.model().index(row, 0, index) for row in range(numChildren)]
                if childIndexes:
                    # add child indexes to the selection
                    childSelection.append(QtCore.QItemSelectionRange(childIndexes[0], childIndexes[-1]))
                    indexQueue.extend(childIndexes)
        return childSelection

    def _propagateSelectionUp(self, selection, command):
        parentSelection = QtCore.QItemSelection()
        # filter out duplicates by unique id because pyside QModelIndexes are not hashable, and cannot be added to a set
        parentIndexes = map(QtCore.QModelIndex.parent, selection.indexes())
        parentIndexes = dict(zip(map(self.model().uniqueIdFromIndex, parentIndexes), parentIndexes)).values()
        for index in parentIndexes:
            while index.isValid():
                if not (selection.contains(index) or parentSelection.contains(index)):
                    if command & QtCore.QItemSelectionModel.Deselect:
                        # children are being deselected, deselect parents too
                        parentSelection.select(index, index)
                    elif command & QtCore.QItemSelectionModel.Select:
                        # children are being selected, select parent if all children are now selected
                        numChildren = self.model().rowCount(index)
                        if numChildren:
                            numSelected = 0
                            for row in range(numChildren):
                                childIndex = self.model().index(row, 0, index)
                                if selection.contains(childIndex) or \
                                        parentSelection.contains(childIndex) or \
                                        (not (command & QtCore.QItemSelectionModel.Clear) and self.isSelected(
                                            childIndex)):
                                    numSelected += 1
                                else:
                                    break
                            if numSelected == numChildren:
                                # all children are selected, select parent too
                                parentSelection.select(index, index)
                index = index.parent()
        return parentSelection

    def setPropagateSelection(self, enabled):

        self.__propagateSelection = bool(enabled)

    def propagateSelection(self):
        return self.__propagateSelection

    def setShowPartiallySelected(self, state):
        self.__showPartiallySelected = bool(state)

    def showPartiallySelected(self):
        return self.__showPartiallySelected

    def setSelectionStates(self, indexes, previous=None):

        return

        # model = self.model()
        # role = common.ROLE_SELECTION_STATE
        #
        # def selectUpstream(item, state=self.STATE_PARTIALLY_SELECTED):
        #     parent = item.parent()
        #     while parent is not None:
        #         parent.setData(state, role=role)
        #         parent = parent.parent()
        #
        # itemFromIndex = model.itemFromIndex
        # # if there is a previous selection, unselect it
        # if previous is not None:
        #     for index in previous:
        #         item = itemFromIndex(index)
        #         # always deselect upstream, in case self.__showPartiallySelected changes between selections
        #         selectUpstream(item, state=self.STATE_UNSELECTED)
        #         item.setData(self.STATE_UNSELECTED, role=role)
        # # select new
        # for item in set(map(itemFromIndex, indexes)):
        #     # if self.__showPartiallySelected is True, partial-select parents until we hit the root node
        #     if self.__showPartiallySelected is True:
        #         selectUpstream(item, state=self.STATE_PARTIALLY_SELECTED)
        #     item.setData(self.STATE_SELECTED, role=role)
        # # emit model data changed signal to trigger view repaint
        # model.dataChanged.emit(model.index(0, 0), model.index(model.rowCount(), model.columnCount()))

    def getSelectionFlags(self):
        return self.__lastselectionflags

    def select(self, selection, command):
        if self.__propagateSelection:
            # propagate selection to children/parents of selected indexes
            if isinstance(selection, QtCore.QModelIndex):
                selection = QtCore.QItemSelection(selection, selection)
            # propagate selection down to children
            childSelection = self.__propagateSelectionDown(selection)
            # propagate selection up to parents
            # parentSelection = self._propagateSelectionUp(selection, command)
            selection.merge(childSelection, QtCore.QItemSelectionModel.SelectCurrent)
            # selection.merge(parentSelection, QtCore.QItemSelectionModel.SelectCurrent)

        # NOTE: the 'command' parameter is really the 'selectionFlags'
        self.__lastselectionflags = command
        if (command & QtCore.QItemSelectionModel.Columns):
            # NOTE: I'm not sure anyone ever has this set but just in
            # case for compatibility. In future we should apptrack
            # this and if no one uses column seleciton then this
            # option should be removed.
            previousSelection = self.selectedIndexes()
        else:
            # This saves on many many duplicates in the selection
            previousSelection = self.selectedRows()

        QtCore.QItemSelectionModel.select(self, selection, command)

        # NOTE: the 'command' parameter is really 'selectionFlags'
        if (command & QtCore.QItemSelectionModel.Columns):
            # NOTE: I'm not sure anyone ever has this set but just in
            # case for compatibility. In future we should apptrack
            # this and if no one uses column seleciton then this
            # option should be removed.
            selected_now = self.selectedIndexes()
        else:
            # This saves on many many duplicates in the selection
            selected_now = self.selectedRows()

        self.setSelectionStates(selected_now, previous=previousSelection)

        self.requestRefresh()

    def requestRefresh(self):
        self.refreshRequested.emit()


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
        self.setSelectionModel(TreeSelectionModel(model=self.model()))
        self.setSelectionMode(QtWidgets.QTreeView.SingleSelection)
        self.itemSelectionChanged = self.selectionModel().selectionChanged

    def setSelectionMode(self, selectionMode):
        if selectionMode == QtWidgets.QTreeView.ExtendedSelection:
            if not self.selectionModel().propagateSelection():
                self.selectionModel().setPropagateSelection(True)
        else:
            if self.selectionModel().propagateSelection():
                self.selectionModel().setPropagateSelection(False)
        super(EntityTree, self).setSelectionMode(selectionMode)

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

    def getAllItems(self):
        objects = []
        iterator = QtWidgets.QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            objects.append(item)
            iterator += 1

        return objects


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
            f.search(h['entity'], parent_uuid=dataObject.uuid, job=dataObject.job)
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

    def __init__(self, parent=None):
        super(EntityViewer, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.topLabelLayout = QtWidgets.QHBoxLayout()
        self.topLabelLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.topSearchLayout = QtWidgets.QHBoxLayout()
        self.filtersLayout = QtWidgets.QHBoxLayout()
        self.entityTypeLayout = QtWidgets.QHBoxLayout()
        self.entityTypeLayout.setSpacing(1)
        self.filtersLayout.addLayout(self.entityTypeLayout)
        self.listTypeLayout = QtWidgets.QHBoxLayout()
        self.listTypeLayout.setAlignment(QtCore.Qt.AlignRight)
        self.listTypeLayout.setSpacing(1)
        self.filtersLayout.addLayout(self.listTypeLayout)

        self.jobSelectWidget = QtWidgets.QWidget()
        self.jobSelectLayout = QtWidgets.QVBoxLayout()
        self.jobSelectWidget.setLayout(self.jobSelectLayout)
        self.jobSelectWidget.setContentsMargins(0, 0, 0, 0)
        self.jobSelectLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.jobSelectWidget)

        self.jobComboBox = JobComboBox(parent=self)

        self.jobSelectLayout.addWidget(self.jobComboBox)
        self.jobSelectLayout.addWidget(cqtutil.h_line())

        self.refreshButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_RELOAD_LRG)
        self.filterButton = cqtutil.FlatIconButton(size=self.SEARCH_HEIGHT, icon=icon_paths.ICON_FILTER_LRG)
        self.searchBar = UiSearchBar(height=self.SEARCH_HEIGHT)
        self.entityTree = EntityTree(parent=self)

        self.entityTypesGroup = QtWidgets.QButtonGroup()
        self.entityTypesGroup.setExclusive(False)
        self.assetTypeButton = QtWidgets.QPushButton("Assets")
        self.sequenceTypeButton = QtWidgets.QPushButton("Sequences")
        self.utilTypeButton = QtWidgets.QPushButton("Util")
        self.assetTypeButton.setIcon(QtGui.QIcon(icon_paths.ICON_ASSET_LRG))
        self.sequenceTypeButton.setIcon(QtGui.QIcon(icon_paths.ICON_SEQUENCE_LRG))
        self.utilTypeButton.setIcon(QtGui.QIcon(icon_paths.ICON_COMETPIPE_LRG))
        self.entityTypesGroup.addButton(self.assetTypeButton, id=0)
        self.entityTypesGroup.addButton(self.sequenceTypeButton, id=1)
        self.entityTypesGroup.addButton(self.utilTypeButton, id=2)
        for btn in self.entityTypesGroup.buttons():
            btn.setCheckable(True)
            btn.setChecked(True)
            btn.setStyleSheet("""
                QPushButton{
                    border-radius: 0px;
                }
                QPushButton:checked{
                    border: none;
                }
            """)
        # self.entityTypesGroup.buttonClicked.connect(self.entityTypeChange)
        self.entityTypesGroup.buttonToggled.connect(self.applyAllFilters)

        self.listTypeGroup = QtWidgets.QButtonGroup()
        self.listTypeButton = QtWidgets.QPushButton()
        self.treeTypeButton = QtWidgets.QPushButton()
        self.listTypeGroup.addButton(self.listTypeButton, id=0)
        self.listTypeGroup.addButton(self.treeTypeButton, id=1)
        self.listTypeButton.setIcon(QtGui.QIcon(icon_paths.ICON_LIST_LRG))
        self.treeTypeButton.setIcon(QtGui.QIcon(icon_paths.ICON_STREAM_LRG))
        self.listTypeLayout.addWidget(self.listTypeButton, alignment=QtCore.Qt.AlignRight)
        self.listTypeLayout.addWidget(self.treeTypeButton, alignment=QtCore.Qt.AlignRight)
        self.listTypeButton.setToolTip("List View")
        self.treeTypeButton.setToolTip("Tree View")
        for btn in self.listTypeGroup.buttons():
            btn.setStyleSheet("""
                QPushButton{
                    border-radius: none;
                }
                QPushButton:checked{
                    border: none;
                    background: #1e1e1e;
                }
            """)
            btn.setCheckable(True)
        self.treeTypeButton.setChecked(True)
        self.listTypeGroup.buttonToggled.connect(lambda: self.populate(reload=True))

        self.entityTypeLayout.addWidget(self.assetTypeButton)
        self.entityTypeLayout.addWidget(self.sequenceTypeButton)
        self.entityTypeLayout.addWidget(self.utilTypeButton)

        # TODO: If things get slow switch to 'editingFinished' so that it doesn't apply filters on each keystroke
        # self.searchBar.editingFinished.connect(self.applyAllFilters)
        self.searchBar.textChanged.connect(self.applyAllFilters)
        self.refreshButton.clicked.connect(lambda: self.populate(reload=True))
        self.jobComboBox.currentIndexChanged.connect(lambda: self.setCurrentJob(
            self.jobComboBox.currentDataObject()
        ))
        self.entityChanged = self.entityTree.itemSelectionChanged

        self.mainLayout.addLayout(self.topLabelLayout)
        self.mainLayout.addLayout(self.topSearchLayout)
        self.topSearchLayout.addWidget(self.searchBar)
        self.topSearchLayout.addWidget(self.refreshButton)
        self.topSearchLayout.addWidget(self.filterButton)
        self.mainLayout.addWidget(cqtutil.h_line())
        self.mainLayout.addLayout(self.filtersLayout)
        self.mainLayout.addWidget(self.entityTree)

        self._currentJob = None
        self.setIsDialog(False)

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
        self.jobComboBox.blockSignals(True)
        self.jobComboBox.setIndexFromDataObject(self._currentJob)
        self.jobComboBox.blockSignals(False)
        self.populate()

    def setSelectedEntities(self, entities=[]):
        if not entities:
            self.entityTree.setCurrentItem(None)
            return

        selection = QtCore.QItemSelection()
        for item in self.entityTree.getAllItems():
            if item.dataObject in entities:
                selection.append(QtCore.QItemSelectionRange(self.entityTree.indexFromItem(item)))

        self.entityTree.selectionModel().select(selection, QtCore.QItemSelectionModel.ClearAndSelect)

        return

    def selectedEntities(self):
        sel = self.entityTree.selectedItems()
        if sel:
            return [x.dataObject for x in sel]
        else:
            return None

    def currentJob(self):
        return self._currentJob

    def setIsDialog(self, bool):
        self._isDialog = bool
        if self._isDialog:
            self.jobSelectWidget.show()
        else:
            self.jobSelectWidget.hide()

    def isDialog(self):
        return self._isDialog

    def applyAllFilters(self):
        hide_items = set()

        searchText = self.searchBar.text()
        entityTypes = {
            'asset': self.assetTypeButton.isChecked(),
            'shot': self.sequenceTypeButton.isChecked(),
            'sequence': self.sequenceTypeButton.isChecked(),
            'util': self.utilTypeButton.isChecked()
        }
        allItems = self.getAllItems()

        for item in allItems:

            if item.dataObject.label == "root" and item.dataObject.type == "util":
                continue

            if not entityTypes[item.dataObject.get("type")]:
                if item not in hide_items:
                    hide_items.add(item)

            if searchText and not str(searchText.upper()) in str(item.text(0).upper()):
                if item not in hide_items:
                    hide_items.add(item)

        if self.listTypeGroup.checkedId() is 1:
            for item in allItems:
                parents = []
                if item not in hide_items:
                    while item.parent():
                        item = item.parent()
                        parents.append(item)
                    for parent in parents:
                        if parent in hide_items:
                            hide_items.remove(parent)

        for item in allItems:
            item.setHidden(item in hide_items)

    def populate(self, reload=False):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        viewType = self.listTypeGroup.checkedId()

        jobObject = self._currentJob
        handler = mongorm.getHandler()
        filter = mongorm.getFilter()

        if reload:
            selection = self.selectedEntities()

        self.entityTree.clear()

        if jobObject:

            filter.search(handler['entity'], job=jobObject.job, label="root")
            rootEntityObject = handler['entity'].one(filter)
            filter.clear()

            jobRootItem = QtWidgets.QTreeWidgetItem(self.entityTree)
            jobRootItem.setText(0, rootEntityObject.get("label"))
            jobRootItem.setIcon(0, QtGui.QIcon(iconutil.dataObjectToIcon(rootEntityObject)))
            jobRootItem.dataObject = rootEntityObject

            if viewType is 0:

                filter.search(handler['entity'], job=jobObject.job)
                remainingEntities = handler['entity'].all(filter)
                remainingEntities.remove_object(rootEntityObject)
                remainingEntities.sort(sort_field='type')
                filter.clear()

                for entity in remainingEntities:
                    item = QtWidgets.QTreeWidgetItem(self.entityTree)
                    item.setText(0, entity.get("label"))
                    item.setIcon(0, QtGui.QIcon(iconutil.dataObjectToIcon(entity)))
                    item.dataObject = entity

            else:

                self.recursive_populate(jobRootItem)

        self.applyAllFilters()
        self.entityTree.expandAll()

        if reload:
            self.setSelectedEntities(selection)

        QtWidgets.QApplication.restoreOverrideCursor()

    def recursive_populate(self, rootTreeItem):
        handler = mongorm.getHandler()
        filt = mongorm.getFilter()
        rootDataObject = rootTreeItem.dataObject
        filt.search(handler['entity'], job=rootDataObject.job, parent_uuid=rootDataObject.getUuid())
        children = handler['entity'].all(filt)
        children.sort(sort_field='type')
        if children:
            for child in children:
                item = QtWidgets.QTreeWidgetItem(rootTreeItem)
                item.setText(0, child.get("label"))
                item.setIcon(0, QtGui.QIcon(iconutil.dataObjectToIcon(child)))
                item.dataObject = child
                self.recursive_populate(item)

    def setFromEnvironment(self):
        show = os.getenv("SHOW")
        shot = os.getenv("SHOT")

        if not show:
            return

        handler = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(handler['job'], label=show)
        jobObject = handler['job'].one(filt)
        if jobObject:
            self.setCurrentJob(jobObject)

        if not shot:
            return

        filt.clear()
        filt.search(handler['entity'], label=shot, job=show)

        shotObject = handler['entity'].one(filt)
        if shotObject:
            self.setSelectedEntities([shotObject])


class EntityPickerDialog(QtWidgets.QDialog):
    def __init__(self, singleSelection=True, parent=None):
        super(EntityPickerDialog, self).__init__(parent=parent)
        self.setWindowTitle("Set Entity")
        self.entityViewer = EntityViewer()
        self.entityViewer.setContentsMargins(0, 0, 0, 0)
        self.entityViewer.setIsDialog(True)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.diagButtonBox = QtWidgets.QDialogButtonBox()
        self.diagButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        for btn in self.diagButtonBox.buttons():
            btn.setStyleSheet("""
                QPushButton{
                    border-radius: 0px;
                    padding: 9px;
                }
            """)

        if singleSelection:
            self.entityViewer.entityTree.setSelectionMode(QtWidgets.QTreeView.SingleSelection)

        self.mainLayout.addWidget(self.entityViewer)
        self.mainLayout.addWidget(self.diagButtonBox)

        self.diagButtonBox.accepted.connect(self.accept)
        self.diagButtonBox.rejected.connect(self.reject)

        self.entityViewer.setFromEnvironment()

    def getSelection(self):
        return self.entityViewer.selectedEntities()


if __name__ == '__main__':
    import sys
    import qdarkstyle

    app = QtWidgets.QApplication(sys.argv)
    win = EntityPickerDialog()
    # win.setFromEnvironment()
    win.resize(400, 800)
    win.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win.show()
    sys.exit(app.exec_())
