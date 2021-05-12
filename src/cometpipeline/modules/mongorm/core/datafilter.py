from mongorm.core.datainterface import DataInterface
from functools import partial


class DataFilter(object):
    def __init__(self):
        self._interface = None
        self._querySet = None
        self._filterStrings = {}
        self._objects = []
        self._omitDeleted = True
        self._omitArchived = True
        self._limit = 0
        self._offset = 0
        self._sort = []

    def clone(self):
        flt = DataFilter()
        flt._interface = self._interface
        flt._filterStrings = self._filterStrings
        flt._omitDeleted = self._omitDeleted
        flt._omitArchived = self._omitArchived
        flt._limit = self._limit
        flt._offset = self._offset
        flt._sort = self._sort
        return flt

    def querySet(self):
        self._querySet = self._interface.objectPrototype.objects(**self._filterStrings)
        self._querySet = self._querySet.skip(self._offset)
        if self._limit > 0:
            self._querySet = self._querySet.limit(self._limit)

        sortArgs = []
        for field, reverse in self._sort if self._sort else [(self._interface.objectPrototype.DEFAULT_SORT, False)]:
            sortArgs.append("{}{}".format("-" if reverse else "+", field))

        self._querySet = self._querySet.order_by(*sortArgs)

        return self._querySet

    def count(self):
        return len(self.objects())

    def filterStrings(self):
        return self._filterStrings

    def overrideFilterStrings(self, filterStrings):
        self._filterStrings = filterStrings

    def interface(self):
        return self._interface

    def setInterface(self, interface):
        self._interface = interface
        self._sort = [(self._interface.objectPrototype.DEFAULT_SORT, False)]

    def clear(self):
        self._filterStrings = {}

    def search(self, *args, **kwargs):

        if len(args) == 0:
            raise RuntimeError("First argument must be a DataInterface")

        datainterface = args[0]

        assert isinstance(datainterface, DataInterface), "First argument must be a DataInterface"

        if not self.interface() or not self.interface().name() == datainterface.name():
            self.setInterface(datainterface)
            self._filterStrings = {}

        for k, v in kwargs.items():
            self._filterStrings[k] = v

        if self._omitDeleted:
            self._filterStrings['deleted'] = False
        if self._omitArchived:
            self._filterStrings['archived'] = False

        return True

    def objects(self):
        self._objects = []

        for object in self.querySet():
            if object.get("deleted") and self.getOmitDeleted():
                continue
            elif object.get("archived") and self.getOmitArchived():
                continue

            self._objects.append(object)

        return self._objects

    def getOmitDeleted(self):
        return bool(self._omitDeleted)

    def getOmitArchived(self):
        return bool(self._omitArchived)

    def omitDeleted(self, value):
        self._omitDeleted = bool(value)

    def omitArchived(self, value):
        self._omitArchived = bool(value)

    def setOffset(self, offset):
        self._offset = offset

    def setLimit(self, limit):
        assert limit > -1
        self._limit = limit

    def clearSort(self):
        self._sort = []

    def sort(self, field, reverse=False):
        self._sort.insert(0, (field, reverse))

    def getSort(self):
        return self._sort
