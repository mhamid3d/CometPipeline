import itertools
import operator

from qtpy import QtCore, QtGui, QtWidgets
from cometqt.modelview.model_item import ModelItem
from mongorm.core.datacontainer import DataContainer
from cometqt.modelview import common as mvcommon


def calcGroupingKey(pairing):
    (i, x) = pairing
    return i - x


class Model(QtCore.QAbstractItemModel):

    dataNeedsRefresh = QtCore.Signal()
    dataAboutToBeRefreshed = QtCore.Signal()
    dataRefreshed = QtCore.Signal()

    @property
    def dataSource(self):
        return self._dataSource

    def __init__(self):
        super(Model, self).__init__()
        self._columnCount = 0
        self._totalItemCount = 0
        self._uuidLookup = {}
        self._headerItem = self.newItem()
        self._rootItem = self.newItem()
        self._rootItem.setModel(self)
        self._rootItem.setTotalChildCount(-1)
        self._dataSource = None
        self._alternatingRowColors = False
        self.dataNeedsRefresh.connect(self.requestRefresh)

    def setAlternatingRowColors(self, enable):
        self._alternatingRowColors = enable

    def addToTotalItemCount(self, count):
        self._totalItemCount += count

    def num_items(self):
        return self._totalItemCount

    def setColumnCount(self, columnCount):
        countExcess = columnCount - self._columnCount
        if countExcess > 0:
            self.insertColumns(self._columnCount, countExcess)
        elif countExcess < 0:
            self.removeColumns(self._columnCount + countExcess, -countExcess)

    def columnCount(self, parentIndex=QtCore.QModelIndex()):
        return self._columnCount

    def rowCount(self, parentIndex=QtCore.QModelIndex()):
        return self.itemFromIndex(parentIndex).childCount()

    def index(self, row, column, parentIndex=QtCore.QModelIndex()):
        if self.hasIndex(row, column, parentIndex):
            childItem = self.itemFromIndex(parentIndex).child(row)
            if childItem:
                return self.createIndex(row, column, childItem)
        return QtCore.QModelIndex()

    def parent(self, index):
        if index.isValid():
            parentItem = self.itemFromIndex(index, False).parent()
            return self.indexFromItem(parentItem)
        return QtCore.QModelIndex()

    def flags(self, index):
        if not index.isValid():
            return self._rootItem.flags()
        return self.itemFromIndex(index, False).flags(index.column())

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            itemData = self.itemFromIndex(index, False).data(index.column(), role)
            if role == QtCore.Qt.BackgroundRole and not itemData and self._alternatingRowColors:
                if (index.row() % 2) == 0:
                    return QtGui.QColor("#2e2e2e")
                else:
                    return itemData
            return itemData
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            return self._headerItem.data(section, role)
        return None

    def indexFromItem(self, item):
        if item and item.model is self and item.parent():
            row = item.parent().childPosition(item)
            if row >= 0:
                return self.createIndex(row, 0, item)
        return QtCore.QModelIndex()

    def itemFromIndex(self, index, validate=True):
        if validate:
            if not index.isValid():
                return self._rootItem
        return index.internalPointer()

    def uuidFromIndex(self, index):
        item = self.itemFromIndex(index)
        if item:
            return item.uuid
        return None

    def indexFromUuid(self, uuid):
        if uuid is not None:
            if self._uuidLookup.has_key(uuid):
                return self.indexFromItem(self._uuidLookup[uuid])

            for item in self.iterItems():
                if item.uuid == uuid:
                    self._uuidLookup[uuid] = item
                    return self.indexFromItem(item)

        return QtCore.QModelIndex()

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        return self.setItemData(index, {role: value})

    def setItemData(self, index, roles):
        item = self.itemFromIndex(index)
        column = index.column()
        for role, value in roles.items():
            item.setData(value, column, role)

        self.dataChanged.emit(index, index)
        return True

    def setHeaderData(self, section, orientation, value, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if self._headerItem.setData(value, section, role):
                self.headerDataChanged.emit(orientation, section, section)
                return True

        return False

    def newItem(self):
        item = ModelItem(self._columnCount)
        return item

    def clear(self):
        self.beginResetModel()
        self._rootItem.removeAllChildren()
        self._rootItem.setTotalChildCount(-1)
        self._uuidLookup = {}
        self._totalItemCount = 0
        self.endResetModel()

    def appendRow(self, parentIndex=QtCore.QModelIndex()):
        return self.appendRows(1, parentIndex)

    def appendRows(self, count, parentIndex=QtCore.QModelIndex()):
        return self.insertRows(self.rowCount(parentIndex), count, parentIndex)

    def insertRows(self, position, count, parentIndex=QtCore.QModelIndex()):
        return self.insertItems(position, [self.newItem() for i in range(count)], parentIndex)

    def insertItem(self, position, item, parentIndex=QtCore.QModelIndex()):
        return self.insertItems(position, [item], parentIndex)

    def insertItems(self, position, itemList, parentIndex=QtCore.QModelIndex()):
        parentItem = self.itemFromIndex(parentIndex)

        if not 0 <= position <= parentItem.childCount():
            return False
        if not itemList:
            return True

        self.beginInsertRows(parentIndex, position, position + len(itemList) - 1)

        for item in itemList:
            uuid = item.uuid
            if uuid is not None:
                self._uuidLookup[uuid] = item
            if item.hasChildren():
                for descendant in item.iterTree(includeRoot=False):
                    uuid = descendant.uuid
                    if uuid is not None:
                        self._uuidLookup[uuid] = descendant

        assert parentItem.insertChildren(position, itemList)

        self.endInsertRows()

        return True

    def appendItem(self, item, parentIndex=QtCore.QModelIndex()):
        return self.appendItems([item], parentIndex)

    def appendItems(self, itemList, parentIndex=QtCore.QModelIndex()):
        return self.insertItems(self.rowCount(parentIndex), itemList, parentIndex)

    def setItems(self, itemList):
        self.beginResetModel()
        self._rootItem.removeAllChildren()
        self._uuidLookup = {}
        self._rootItem.appendChildren(itemList)
        for item in self.iterItems():
            if item.uuid is not None:
                self._uuidLookup[item.uuid] = item
        self.endResetModel()
        self._rootItem.setTotalChildCount(len(itemList))

    def setDataSource(self, dataSource):
        if self._dataSource:
            self._dataSource.dataNeedsRefresh.disconnect(self.dataNeedsRefresh)
            self._dataSource.setModel(None)
            self._dataSource.setParent(None)
        self._dataSource = dataSource
        self.clear()
        if self._dataSource:
            self._dataSource.setModel(self)
            self._dataSource.setParent(self)
            self.setColumnCount(len(self._dataSource.headerItem))
            self._headerItem = self._dataSource.headerItem
            self._dataSource.dataNeedsRefresh.connect(self.dataNeedsRefresh)
            self.dataNeedsRefresh.emit()
        else:
            self.setColumnCount(0)

    def requestRefresh(self):
        if self._dataSource and self._dataSource.needToRefresh:
            self._dataSource.setNeedToRefresh(False)

        self.dataAboutToBeRefreshed.emit()

        itemList = self._dataSource.fetchItems(QtCore.QModelIndex())

        self.setItems(itemList)

        self.dataRefreshed.emit()

        return True

    def removeRows(self, position, count, parentIndex=QtCore.QModelIndex()):
        if count < 0 or position < 0:
            return False
        if count == 0:
            return True
        parentItem = self.itemFromIndex(parentIndex)
        if position + count > parentItem.childCount():
            return False
        return self.removeItems([parentItem.child(i) for i in range(position, position + count)])

    def removeItem(self, item):
        return self.removeItems([item])

    def removeItems(self, itemList):
        if not itemList:
            return True
        for item in itemList:
            if item.model is not self:
                return False
        itemsToRemove = set(itemList)
        for item in itemsToRemove:
            for descendant in item.iterTree(includeRoot=True):
                if descendant.uuid is not None and self._uuidLookup.has_key(descendant.uuid):
                    del self._uuidLookup[descendant.uuid]
        segments = list(self._splitContiguousSegments(itemsToRemove))
        for (parentItem, first, last) in reversed(segments):
            if parentItem.model is self:
                parentIndex = self.indexFromItem(parentItem)
                self.beginRemoveRows(parentIndex, first, last)
                parentItem.removeChildren(first, last - first + 1)
                self._totalItemCount -= last - first + 1
                self.endRemoveRows()

        return True

    def moveRow(self, fromPosition, toPosition, fromParent=QtCore.QModelIndex(), toParent=QtCore.QModelIndex()):
        return self.moveRows(fromPosition, 1, toPosition, fromParent, toParent)

    def moveRows(self, fromPosition, count, toPosition, fromParent=QtCore.QModelIndex(), toParent=QtCore.QModelIndex()):
        if fromPosition < 0 or count < 0:
            return False
        if count == 0:
            return True
        fromParentItem = self.itemFromIndex(fromParent)
        toParentItem = self.itemFromIndex(toParent)
        if fromPosition + count > fromParentItem.childCount() or toPosition > toParentItem.childCount():
            return False
        if fromParentItem is toParentItem and fromPosition <= toPosition < fromPosition + count:
            return True
        itemsToMove = fromParentItem.children()[fromPosition:fromPosition + count]

        assert len(itemsToMove) == count

        sourceLast = fromPosition + count - 1

        if fromPosition <= toPosition <= sourceLast and fromParent == toParent:
            return True

        if toPosition > sourceLast:
            toPosition += 1

        if not self.beginMoveRows(fromParent, fromPosition, sourceLast, toParent, toPosition):
            return False

        assert fromParentItem.removeChildren(fromPosition, count)
        if fromParentItem is toParentItem and fromPosition + count < toPosition:
            toPosition -= count

        assert toParentItem.insertChildren(toPosition, itemsToMove)
        self.endMoveRows()
        return True

    def moveItem(self, item, toPosition, toParent=QtCore.QModelIndex()):
        return self.moveItems([item], toPosition, toParent)

    def moveItems(self, itemList, toPosition, toParent=QtCore.QModelIndex()):
        if not itemList:
            return True
        for item in itemList:
            if item.model is not self:
                return False

        toParentItem = self.itemFromIndex(toParent)

        if toPosition < 0:
            toPosition = toParentItem.childCount() - 1
        elif toPosition > toParentItem.childCount() - 1:
            toPosition = 0

        itemSet = set(itemList)
        parentItem = toParentItem
        while parentItem:
            if parentItem in itemSet:
                return False
            parentItem = parentItem.parent()
        segments = list(self._splitContiguousSegments(itemList))

        for (fromParentItem, first, last) in reversed(segments):
            fromParentIndex = self.indexFromItem(fromParentItem)
            toParentIndex = self.indexFromItem(toParentItem)
            count = last - first + 1
            if not self.moveRows(first, count, toPosition, fromParentIndex, toParentIndex):
                return False
            if fromParentItem is toParentItem and toPosition > last:
                toPosition -= count
        self._emitDataChanged(itemList)
        return True

    def insertColumns(self, position, count, parentIndex=QtCore.QModelIndex()):
        if position < 0 or position > self._columnCount:
            return False
        if count > 0:
            self.beginInsertColumns(QtCore.QModelIndex(), position, position + count - 1)
            self._headerItem.insertColumns(position, count)
            self._rootItem.insertColumns(position, count)
            self._columnCount += count
            self.endInsertColumns()
        return True

    def removeColumns(self, position, count, parentIndex=QtCore.QModelIndex()):
        if position < 0 or position + count > self._columnCount:
            return False
        if count > 0:
            self.beginRemoveColumns(QtCore.QModelIndex(), position, position + count - 1)
            self._headerItem.removeColumns(position, count)
            self._rootItem.removeColumns(position, count)
            self._columnCount -= count
            self.endRemoveColumns()
        return True

    def hasChildren(self, parentIndex=QtCore.QModelIndex()):
        item = self.itemFromIndex(parentIndex)
        if item.childCount() > 0:
            return True
        elif self._dataSource and self._dataSource.lazyLoadChildren:
            return item.totalChildCount() != 0
        return False

    def iterItems(self, includeRoot=True):
        return self._rootItem.iterTree(includeRoot=includeRoot)

    def _splitContiguousSegments(self, itemList):
        partitions = {}
        for item in itemList:
            index = self.indexFromItem(item)
            parentIndex = index.parent()

            if parentIndex not in partitions:
                partitions[parentIndex] = set()
            parentIndex[parentIndex].add(index.row())

        for parentIndex in sorted(partitions):
            parentItem = self.itemFromIndex(parentIndex)
            rowList = partitions[parentIndex]
            sequences = [map(operator.itemgetter(1), g) for k, g in
                         itertools.groupby(enumerate(sorted(rowList)), calcGroupingKey)]

            for seq in sequences:
                yield (parentItem, seq[0], seq[-1])

    def canFetchMore(self, parentIndex):
        if hasattr(self, "_dataSource") and self._dataSource:
            return self._dataSource.canFetchMore(parentIndex)

        return False

    def fetchMore(self, parentIndex):
        if self._dataSource:
            return self._dataSource.fetchMore(parentIndex)

    def sort(self, column, order=None):
        return self._dataSource.sortByColumns([column], [order])