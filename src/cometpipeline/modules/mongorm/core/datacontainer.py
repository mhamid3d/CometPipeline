from mongorm.core.dataobject import DataObject, AbstractDataObject


class DataContainer(object):
    def __init__(self, interface, querySet=None):
        self._objects = []
        self._interface = interface
        self._sortField = interface.objectPrototype.DEFAULT_SORT
        if querySet:
            for object in querySet:
                self.append_object(object)
            self.sort()

    def append_object(self, object):

        assert isinstance(object, AbstractDataObject), "Object must be DataObject instance"

        if not object.interfaceName() == self.interfaceName():
            raise TypeError("Data Object of type ({}) does not match with DataContainer type ({})".format(
                object.interfaceName(), self.interfaceName()))

        if object.getUuid() not in [x.getUuid() for x in self._objects]:
            self._objects.append(object)

        self.sort()

    def remove_object(self, object):
        try:
            self._objects.remove(object)
            self.sort()
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
        assert dataContainer.interfaceName() == self.interfaceName()
        for dataObject in dataContainer:
            self.append_object(dataObject)
        self.sort()

    def dataInterface(self):
        return self._interface

    def interfaceName(self):
        return self.dataInterface().name()

    def sort(self, sort_field=None, reverse=False):
        if sort_field:
            if sort_field not in [field.db_field for field in self._interface.getFields()]:
                raise TypeError(
                    "Invalid sort field ({}) for DataInterface ({})".format(sort_field, self.interfaceName()))
            self._sortField = sort_field

        self._objects = sorted(self._objects, key=lambda i: i.get(self._sortField), reverse=reverse)