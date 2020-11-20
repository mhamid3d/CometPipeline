from mongorm.core.dataobject import DataObject, AbstractDataObject


class DataContainer(object):
    def __init__(self, interface, querySet=None):
        self._objects = []
        self._interface = interface
        self._sort = [(interface.objectPrototype.DEFAULT_SORT, False)]
        if querySet:
            for object in querySet:
                self.append_object(object)

    def append_object(self, object):

        assert isinstance(object, AbstractDataObject), "Object must be DataObject instance"

        if not object.interfaceName() == self.interfaceName():
            raise TypeError("Data Object of type ({}) does not match with DataContainer type ({})".format(
                object.interfaceName(), self.interfaceName()))

        if object.getUuid() not in [x.getUuid() for x in self._objects]:
            self._objects.append(object)

        # self.sort()

    def remove_object(self, object):
        try:
            self._objects.remove(object)
            # self.sort()
        except ValueError as e:
            raise e("Object does not exist in DataContainer")

    def size(self):
        return len(self._objects)

    def hasObjects(self):
        return False if self.size() == 0 else True

    def __len__(self):
        return self.size()

    def __iter__(self):
        return iter(self._objects)

    def __getitem__(self, item):
        return self._objects[item]

    def get(self, idx):
        try:
            item = self[idx]
            return item
        except IndexError as ie:
            raise ie("Index {} out of range for data container".format(idx))

    def extend(self, dataContainer):
        if not dataContainer:
            return
        assert dataContainer.interfaceName() == self.interfaceName()
        for dataObject in dataContainer:
            self.append_object(dataObject)
        # self.sort()

    def dataInterface(self):
        return self._interface

    def interfaceName(self):
        return self.dataInterface().name()

    def clearSort(self):
        self._sort = []
        self.doDefaultSort()

    def getSort(self):
        return self._sort

    def doDefaultSort(self):
        self._objects.sort(key=lambda i: i.get(self._interface.objectPrototype.DEFAULT_SORT))

    def sort(self, sort_field=None, reverse=False):
        if sort_field:
            if sort_field not in [field.db_field for field in self._interface.getFields()]:
                raise TypeError(
                    "Invalid sort field ({}) for DataInterface ({})".format(sort_field, self.interfaceName()))
            if sort_field in [x[0] for x in self._sort]:
                for idx, sortData in enumerate(self._sort):
                    if sortData[0] == sort_field:
                        self._sort[idx] = (sort_field, reverse)
                        break
            else:
                self._sort.insert(0, (sort_field, reverse))

        if not self._sort:
            self.doDefaultSort()

        for sf, rv in reversed(self._sort):
            self._objects.sort(key=lambda i: i.get(sf), reverse=rv)