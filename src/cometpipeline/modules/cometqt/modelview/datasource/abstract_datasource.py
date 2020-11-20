from qtpy import QtCore
from cometqt.modelview.model_item import ModelItem
from mongorm.core.datacontainer import DataContainer
from cometqt.modelview import common as mvcommon
import mongorm


class AbstractDataSource(QtCore.QObject):

    LOAD_METHOD_ALL = "all"
    LOAD_METHOD_PAGINATED = "paginated"
    DEFAULT_LOAD_METHOD = LOAD_METHOD_ALL
    DEFAULT_BATCH_SIZE = 100
    ROLE_COLUMN_FIELD = mvcommon.registerRole()

    dataNeedsRefresh = QtCore.Signal()
    totalCountChanged = QtCore.Signal(int)
    pageChanged = QtCore.Signal(int)

    @property
    def model(self):
        return self._model

    @property
    def headerItem(self):
        return self._headerItem

    @property
    def loadMethod(self):
        return self._loadMethod

    @property
    def lazyLoadChildren(self):
        return self._lazyLoadChildren

    @property
    def batchSize(self):
        return self._batchSize

    @property
    def needToRefresh(self):
        return self._needToRefresh

    @property
    def isValid(self):
        return self._isValid

    @property
    def handler(self):
        return self._handler

    @property
    def dataFilter(self):
        return self._filter

    @property
    def interface(self):
        return self._interface

    def __init__(self, interfaceName, columnNames=[], parent=None):
        super(AbstractDataSource, self).__init__(parent)
        self._handler = mongorm.getHandler()
        self._filter = mongorm.getFilter()
        self._interface = self._handler[interfaceName]
        self._filter.setInterface(self._interface)
        self._dataContainer = DataContainer(self._interface)
        self._model = None
        self._loadMethod = self.DEFAULT_LOAD_METHOD
        self._needToRefresh = True
        self._isValid = True
        self._lazyLoadChildren = False
        self._pageNum = 0
        self._batchSize = self.DEFAULT_BATCH_SIZE
        self._totalCount = -1
        self._headerItem = self._createHeaderItem(columnNames)

    def _setTotalCount(self, totalCount):
        if self._totalCount != totalCount:
            self._totalCount = totalCount
            self.totalCountChanged.emit(self._totalCount)

    def _createHeaderItem(self, columnNames):
        headerItem = ModelItem(len(columnNames))
        for i, columnName in enumerate(columnNames):
            headerItem.setData(columnName, i, QtCore.Qt.DisplayRole)
        return headerItem

    def setModel(self, model):
        self._model = model

    def setLoadMethod(self, loadMethod):
        self._loadMethod = loadMethod

    def setLazyLoadChildren(self, enabled):
        self._lazyLoadChildren = bool(enabled)

    def setNeedToRefresh(self, needToRefresh):
        if self._needToRefresh != needToRefresh:
            self._needToRefresh = needToRefresh
            if self._needToRefresh:
                self.dataNeedsRefresh.emit()

    def setBatchSize(self, batchSize):
        if self._batchSize != batchSize:
            self._batchSize = batchSize
            self.setNeedToRefresh(True)

    def setPage(self, pageNum):
        if self._loadMethod == self.LOAD_METHOD_PAGINATED and self._pageNum != pageNum:
            self._pageNum = pageNum
            self.pageChanged.emit(pageNum)
            self.setNeedToRefresh(True)

    def makeItems(self, dataContainer):
        raise NotImplementedError

    def canFetchMore(self, parentIndex):
        if self._isValid and (self._loadMethod == self._lazyLoadChildren):
            item = self._model.itemFromIndex(parentIndex)
            if self._lazyLoadChildren and item.totalChildCount() < 0:  # totalChildCount is uninitialized, so item is unpopulated
                return True
        return False

    def fetchMore(self, parentIndex):
        assert self._isValid and self._lazyLoadChildren
        offset = self._model.rowCount(parentIndex)
        limit = 0
        itemList = self._fetchBatch(parentIndex, offset, limit, False)
        # self._model.sorter.sortItems(itemList)
        if self._lazyLoadChildren:
            parentItem = self._model.itemFromIndex(parentIndex)
            parentItem.setTotalChildCount(len(itemList))
        self._model.appendItems(itemList, parentIndex)

    def fetchItems(self, parentIndex):
        assert not parentIndex.isValid()
        if not self._isValid:
            self._setTotalCount(-1)
            return []
        limit = 0
        offset = 0
        if self._loadMethod == self.LOAD_METHOD_PAGINATED and not parentIndex.isValid():
            limit = self._batchSize
            offset = self._pageNum * self._batchSize
        itemList = self._fetchBatch(parentIndex, offset, limit)
        # self._model.sorter.sortItems(itemList)
        return itemList

    @property
    def dataContainer(self):
        if not self._dataContainer:
            self._dataContainer = DataContainer(self._interface)
        return self._dataContainer

    def getPotentialResults(self):
        flt = self._filter.clone()
        flt.setOffset(0)
        flt.setLimit(0)
        return self._interface.all(flt)

    def _fetchBatch(self, parentIndex, offset, limit):
        assert not parentIndex.isValid()

        self._filter.setOffset(offset)
        self._filter.setLimit(limit)
        self._dataContainer = self._interface.all(self._filter)
        return self.createNewItems()

    def createNewItems(self):
        itemList = self.makeItems(self._dataContainer)
        self._setTotalCount(self._dataContainer.size())
        return itemList

    def sortByColumns(self, columns, directions, refresh=True):
        filter = self._filter.clone()
        filter.clearSort()
        for column, direction in zip(columns, directions):
            field = self._headerItem.data(column, role=self.ROLE_COLUMN_FIELD)
            if not field or not field in [fld.db_field for fld in self._interface.getFields()]:
                continue
            filter.sort(field=field, reverse=False if direction == QtCore.Qt.AscendingOrder else True)

        self._filter = filter
        if refresh:
            self.setNeedToRefresh(True)