from pipeicon import icon_paths
import mongoengine
import datetime
import mongorm
import uuid
import re


class AbstractDataObject(object):

    INTERFACE_STRING = ""
    DEFAULT_SORT = "created"

    _id = mongoengine.UUIDField(required=True, primary_key=True, visible=False, dispName="_ID")
    uuid = mongoengine.StringField(required=True, dispName="UUID", visible=True, icon=icon_paths.ICON_FINGERPRINT_SML)
    created = mongoengine.DateTimeField(required=True, dispName="Created", icon=icon_paths.ICON_CLOCK_SML)
    modified = mongoengine.DateTimeField(required=True, dispName="Modified", icon=icon_paths.ICON_CLOCK_SML)
    deleted = mongoengine.BooleanField(required=True, dispName="Deleted", default=False, visible=False)
    archived = mongoengine.BooleanField(required=True, dispName="Archived", default=False, visible=False)

    def __init__(self, *args, **kwargs):
        super(AbstractDataObject, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "Abstract Data Object ({})".format(self.uuid)

    def __str__(self):
        return self.uuid

    def get(self, item):
        return self.getDataDict().get(item)

    def interfaceName(self):
        return self.dataInterface().name()

    def _generate_id(self):
        """
        Generate unique uuid for uuid and _id fields
        :return:
        """
        self._id = uuid.uuid4()
        self.uuid = self._id.__str__()
        return self.uuid

    @classmethod
    def dataInterface(cls):
        from mongorm.core.datainterface import DataInterface
        return DataInterface(cls.INTERFACE_STRING)

    def getFields(self):
        return self._fields.values()

    def getField(self, field):
        for field_item in self.getFields():
            if field_item.db_field == field:
                return field_item

        raise ValueError("Invalid field [{}] for data type: {}".format(field, self.dataInterface().name()))

    def getDataDict(self):
        return {k: v for k, v in [(field.db_field, self[field.db_field]) for field in self.getFields()]}

    def getUuid(self):
        return self.uuid

    def pprint(self):
        import pprint
        pprint.pprint(self.getDataDict())

    def is_saved(self):
        result = self.dataInterface().get(self.uuid)
        return True if result else False

    def save(self, update_time=True):
        if self.is_saved() and update_time:
            self.modified = datetime.datetime.now()
        mongoengine.Document.save(self)


class DataObject(AbstractDataObject):
    """
    Site base class schema for MongoDB engine.
    """

    INTERFACE_STRING = ""
    DEFAULT_SORT = "label"

    path = mongoengine.StringField(required=True, dispName="Path", icon=icon_paths.ICON_LOCATION_SML)
    label = mongoengine.StringField(required=True, dispName="Name")
    job = mongoengine.StringField(required=True, dispName="Job", visible=False)
    created_by = mongoengine.StringField(required=True, dispName="Owner", icon=icon_paths.ICON_USER_SML)

    def __init__(self, *args, **kwargs):
        super(DataObject, self).__init__(*args, **kwargs)

    def __repr__(self):
        reprstring = object.__repr__(self)
        reprstring = re.sub("object", "object [{}]".format(self.label), reprstring)
        reprstring = reprstring.replace("mongorm.interfaces.", "")

        return reprstring

    def __str__(self):
        return "{} object [{}]".format(self.interfaceName(), self.label)

    def children(self):
        raise NotImplementedError

    def child(self, index):
        children = self.children()
        if not children:
            return None
        return children[index]

    def childCount(self):
        children = self.children()
        if not children:
            return 0
        return len(children)

    def parent(self, *args, **kwargs):
        # Reimplement - the other interface children in sub-class
        interface = self.interfaceName()
        if interface == "Job":
            return None

    def siblings(self):
        raise NotImplementedError