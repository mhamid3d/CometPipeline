from mongorm.core.dataobject import DataObject, AbstractDataObject
from pipeicon import icon_paths
from cometpipe.core import CREW_TYPES
from collections import defaultdict
import mongorm
import mongoengine
import re


class Job(DataObject, mongoengine.Document):

    _name = "Job"
    meta = {'collection': 'job'}
    INTERFACE_STRING = "job"

    # Required fields
    fullname = mongoengine.StringField(required=True, dispName="Project Full Name")
    resolution = mongoengine.ListField(required=True, dispName="Resolution")
    crew = mongoengine.DictField(required=True, default={k: [] for k in CREW_TYPES})

    # Optional fields
    description = mongoengine.StringField(dispName="Description")

    def crew_dict(self):
        c = self.crew
        d = {}
        for k, v in c.items():
            d[k] = list(v)

        return d

    def children(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["entity"], job=self.label)
        children = db["entity"].all(filt)
        return children

    def siblings(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['job'])
        siblings = db['job'].all(filt)
        siblings.remove_object(self)
        return siblings

    def shots(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["entity"], job=self.label, type="shot")
        shots = db["entitiy"].all(filt)
        return shots

    def sequences(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["entity"], job=self.label, type="sequence")
        sequences = db["entitiy"].all(filt)
        return sequences

    def assets(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["entity"], job=self.label, type="asset")
        assets = db["entitiy"].all(filt)
        return assets

    def utils(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["entity"], job=self.label, type="util")
        assets = db["entitiy"].all(filt)
        return assets


class Entity(DataObject, mongoengine.Document):

    _name = "Entity"
    meta = {'collection': 'entity'}
    INTERFACE_STRING = "entity"

    # Required fields
    type = mongoengine.StringField(required=True, dispName="Type")  # eg: 'sequence', 'shot', 'asset', 'util'

    # Optional fields
    parent_uuid = mongoengine.StringField(dispName="Parent UUID", default=None)
    framerange = mongoengine.ListField(dispName="Frame Range")
    thumbnail = mongoengine.StringField(dispName="Thumbnail", icon=icon_paths.ICON_IMAGE_SML)

    def children(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["entity"], job=self.job, parent_uuid=self.uuid)
        children = db["entity"].all(filt)
        return children

    def recursive_children(self):
        from mongorm.core.datacontainer import DataContainer

        container = DataContainer(interface=mongorm.getHandler()[self.INTERFACE_STRING])

        for child in self.children():
            container.append_object(child)
            container.extend(child.recursive_children())

        container.sort(sort_field="jobpath")

        return container

    def parent(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['entity'], job=self.job, uuid=self.parent_uuid)
        parent = db['entity'].one(filt)
        return parent

    def siblings(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['entity'], job=self.job, parent_uuid=self.parent_uuid)
        siblings = db['entity'].all(filt)
        siblings.remove_object(self)
        return siblings

    def packages(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["package"], job=self.job, parent_uuid=self.uuid)
        packages = db["package"].all(filt)
        return packages


class Package(DataObject, mongoengine.Document):
    '''
    breakdown-example:
    -------------------------------------------------
    LOOK _ char_marty _ test _ varA _ lod300
    {0}       {1}       {2}    {3}     {4}
    -------------------------------------------------
    {0} - 'type' - required
    {1} - 'asset_in_shot' - not required
    {2} - 'label' - not required
    {3} - 'variation'
    {4} - 'lod'
    {3} & {4} - variation type tags, should probably come from the 'tags' field
    -------------------------------------------------
    examples:
    - LOOK_char_marty_varA_lod300                    - {type}_{entity}_{variations}
    - LOOK_char_marty_test_varA_lod300               - {type}_{entity}_{label}_{variations}
    - LOOK_ab0125_char_marty_varA_lod300             - {type}_{entity}_{assetpath}_{variations}

    - CGR_ab0125_lighting_char_marty_L010_beauty     - {type}_{entity}_{task}_{label}
    - CGR_ab0125_lighting_prop_wallet_L010_beauty    - {type}_{entity}_{task}_{label}
    - CGR_ab0125_lighting_all_id_L010_util           - {type}_{entity}_{task}_{label}

    '''

    _name = "Package"
    meta = {'collection': 'package'}
    INTERFACE_STRING = "package"

    # Required fields
    parent_uuid = mongoengine.StringField(required=True, dispName="Package UUID", visible=False)
    type = mongoengine.StringField(required=True, dispName="Type")

    # Optional fields
    thumbnail = mongoengine.StringField(dispName="Thumbnail", icon=icon_paths.ICON_IMAGE_SML)
    tags = mongoengine.ListField(dispName="Tags")

    def children(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["version"], job=self.job, parent_uuid=self.uuid)
        packages = db["version"].all(filt)
        packages.sort(sort_field='version', reverse=True)
        return packages

    def parent(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['entity'], job=self.job, uuid=self.parent_uuid)
        entity = db['entity'].one(filt)
        return entity

    def latest(self):
        children = self.children()
        if not children:
            return None

        children.sort("version", reverse=True)
        return children[0]

    def siblings(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['package'], job=self.job, parent_uuid=self.parent_uuid)
        siblings = db['package'].all(filt)
        siblings.remove_object(self)
        return siblings


class Version(DataObject, mongoengine.Document):

    _name = 'Version'
    meta = {'collection': 'version'}
    INTERFACE_STRING = "version"

    # Required fields
    comment = mongoengine.StringField(required=True, dispName="Comment", icon=icon_paths.ICON_COMMENT_SML)
    status = mongoengine.StringField(required=True, dispName="Status", choices=['pending', 'approved', 'declined'],
                                     default='pending')
    version = mongoengine.IntField(required=True, dispName="Version")
    parent_uuid = mongoengine.StringField(required=True, dispName="Package UUID", visible=False)
    state = mongoengine.StringField(required=True, dispName="State", visible=False,
                                    choices=['complete', 'working', 'failed'],
                                    default='complete')

    # Optional fields
    framerange = mongoengine.ListField(dispName="Frame Range")
    thumbnail = mongoengine.StringField(dispName="Thumbnail", icon=icon_paths.ICON_IMAGE_SML)

    def children(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["content"], job=self.job, parent_uuid=self.uuid)
        children = db["content"].all(filt)
        return children

    def parent(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['package'], job=self.job, uuid=self.parent_uuid)
        parent = db['package'].one(filt)
        return parent

    def siblings(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['version'], job=self.job, parent_uuid=self.parent_uuid)
        siblings = db['version'].all(filt)
        siblings.remove_object(self)
        return siblings

    def get_dependency_masters(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['dependency'], job=self.job, source_version_uuid=self.uuid)
        dependencies = db['dependency'].all(filt)
        return dependencies

    def get_dependency_slaves(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['dependency'], job=self.job, link_version_uuid=self.uuid)
        dependencies = db['dependency'].all(filt)
        return dependencies

    def default_content(self):
        return self.children()[0]


class Content(DataObject, mongoengine.Document):

    _name = 'Content'
    meta = {'collection': 'content'}
    INTERFACE_STRING = "content"

    # Required fields
    parent_uuid = mongoengine.StringField(required=True, dispName="Version UUID", visible=False)
    format = mongoengine.StringField(required=True, dispName="Format")
    created_by = mongoengine.StringField(required=False)

    # Optional fields
    resolution = mongoengine.ListField(dispName="Resolution")
    framerange = mongoengine.ListField(dispName="Frame Range")
    thumbnail = mongoengine.StringField(dispName="Thumbnail", icon=icon_paths.ICON_IMAGE_SML)

    def children(self):
        return None

    def parent(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['version'], job=self.job, uuid=self.parent_uuid)
        parent = db['version'].one(filt)
        return parent

    def siblings(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['content'], job=self.job, parent_uuid=self.parent_uuid)
        siblings = db['content'].all(filt)
        siblings.remove_object(self)
        return siblings


class Dependency(DataObject, mongoengine.Document):

    _name = 'Dependency'
    meta = {'collection': 'dependency'}
    INTERFACE_STRING = "dependency"

    # Required fields
    source_version_uuid = mongoengine.StringField(required=True, dispName="Source Version UUID")
    link_version_uuid = mongoengine.StringField(required=True, dispName="Link Version UUID")

    path = mongoengine.StringField(required=False, default=None)

    # SOURCE DEPENDS ON LINK

    def children(self):
        return None

    def siblings(self):
        return None

    def get_same_source(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['dependency'], job=self.job, source_version_uuid=self.source_version_uuid)
        siblings = db['dependecy'].all(filt)
        siblings.remove_object(self)
        return siblings

    def get_same_link(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['dependency'], job=self.job, link_version_uuid=self.link_version_uuid)
        siblings = db['dependecy'].all(filt)
        siblings.remove_object(self)
        return siblings


class User(AbstractDataObject, mongoengine.Document):

    _name = "User"
    meta = {'collection': 'user'}
    INTERFACE_STRING = "user"
    DEFAULT_SORT = "first_name"

    # Required fields
    first_name = mongoengine.StringField(required=True)
    last_name = mongoengine.StringField(required=True)
    email = mongoengine.EmailField(required=True)
    password = mongoengine.StringField(required=True)
    username = mongoengine.StringField(required=True)
    avatar = mongoengine.ImageField(required=True, size=(128, 128, True))

    def __repr__(self):
        reprstring = object.__repr__(self)
        reprstring = re.sub("object", "object [{}]".format(self.username), reprstring)
        reprstring = reprstring.replace("mongorm.interfaces.", "")

        return reprstring

    def __str__(self):
        return "{} object [{}]".format(self.interfaceName(), self.username)

    def fullname(self):
        return "{} {}".format(self.first_name, self.last_name)


class Notification(AbstractDataObject, mongoengine.Document):

    _name = "Notification"
    meta = {'collection': 'notification'}
    INTERFACE_STRING = "notification"

    # Required fields
    receiver_uuid = mongoengine.StringField(required=True)
    description = mongoengine.StringField(required=True)
    read = mongoengine.BooleanField(required=True, default=False)
    viewed = mongoengine.BooleanField(required=True, default=False)

    def __repr__(self):
        reprstring = object.__repr__(self)
        reprstring = re.sub("object", "object [{}]".format(self.description), reprstring)
        reprstring = reprstring.replace("mongorm.interfaces.", "")

        return reprstring

    def __str__(self):
        return "{} object [{}]".format(self.interfaceName(), self.description)