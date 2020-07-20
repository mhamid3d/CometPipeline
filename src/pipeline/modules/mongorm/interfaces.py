from mongorm.core.dataobject import BaseJinxObject
from pipeicon import icon_paths
import mongorm
import mongoengine


class Job(BaseJinxObject, mongoengine.Document):

    _name = "Job"
    meta = {'collection': 'job'}
    INTERFACE_STRING = "job"

    # Required fields
    fullname = mongoengine.StringField(required=True, dispName="Project Full Name")
    resolution = mongoengine.ListField(required=True, dispName="Resolution")

    # Optional fields
    description = mongoengine.StringField(dispName="Description")
    tags = mongoengine.ListField(dispName="Tags")
    thumbnail = mongoengine.StringField(dispName="Thumbnail", icon=icon_paths.ICON_IMAGE_SML)

    def children(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["package"], parent_uuid=self.uuid)
        packages = db["package"].all(filt)
        if packages.hasObjects():
            return packages
        else:
            return None

    def siblings(self, includeSelf=False):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['job'])
        siblings = db['job'].all(filt)
        if not siblings.size() < 2:
            if includeSelf:
                return siblings
            else:
                siblings.remove_object(self)
                return siblings
        else:
            return None

    def shots(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["entity"], job=self.label, type="shot")
        entities = db["entitiy"].all(filt)
        if entities.hasObjects():
            return entities
        else:
            return None

    def sequences(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["entity"], job=self.label, type="sequence")
        entities = db["entitiy"].all(filt)
        if entities.hasObjects():
            return entities
        else:
            return None

    def assets(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["entity"], job=self.label, type="asset")
        entities = db["entitiy"].all(filt)
        if entities.hasObjects():
            return entities
        else:
            return None


class Entity(BaseJinxObject, mongoengine.Document):

    _name = "Entity"
    meta = {'collection': 'entity'}
    INTERFACE_STRING = "entity"

    # Required fields
    type = mongoengine.StringField(required=True, dispName="Type")  # eg: 'sequence', 'shot', 'asset'
    production = mongoengine.BooleanField(required=True, dispName="Active")  # Set false for testing / rnd stems
    parent_uuid = mongoengine.StringField(dispName="Parent UUID")

    # Optional fields
    prefix = mongoengine.StringField(required=True, dispName="Prefix")  # eg: 'char', 'environ', 'vehicle', etc
    framerange = mongoengine.ListField(dispName="Frame Range")
    thumbnail = mongoengine.StringField(dispName="Thumbnail", icon=icon_paths.ICON_IMAGE_SML)

    def children(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["package"], parent_uuid=self.uuid)
        packages = db["package"].all(filt)
        if packages.hasObjects():
            return packages
        else:
            return None

    def parent(self):
        if self.type == "sequence" or self.type == "asset":
            interface = "job"
        else:
            interface = "entitiy"
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db[interface], uuid=self.parent_uuid)
        packages = db[interface].one(filt)
        if packages.hasObjects():
            return packages
        else:
            return None

    def siblings(self, includeSelf=False):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['entity'], parent_uuid=self.parent_uuid)
        siblings = db['entity'].all(filt)
        if not siblings.size() < 2:
            if includeSelf:
                return siblings
            else:
                siblings.remove_object(self)
                return siblings
        else:
            return None


class Package(BaseJinxObject, mongoengine.Document):

    _name = "Package"
    meta = {'collection': 'package'}
    INTERFACE_STRING = "package"

    # Required fields
    parent_uuid = mongoengine.StringField(required=True, dispName="Entity UUID", visible=False)
    task = mongoengine.StringField(required=True, dispName="Task")
    type = mongoengine.StringField(required=True, dispName="Type")

    # Optional fields
    comment = mongoengine.StringField(dispName="Comment", icon=icon_paths.ICON_COMMENT_SML)
    thumbnail = mongoengine.StringField(dispName="Thumbnail", icon=icon_paths.ICON_IMAGE_SML)
    tags = mongoengine.ListField(dispName="Tags")

    def children(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["version"], parent_uuid=self.uuid)
        packages = db["version"].all(filt)
        if packages.hasObjects():
            return packages
        else:
            return None

    def parent(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['entity'], uuid=self.parent_uuid)
        entity = db['entitiy'].one(filt)
        if entity:
            return entity
        else:
            filt.search(db['job'], uuid=self.parent_uuid)
            job = db['job'].one(filt)
            return job

    def latest(self):
        children = self.children()
        if not children:
            return False

        children.sort("version", reverse=True)
        return children[0]

    def siblings(self, includeSelf=False):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['twig'], stem_uuid=self.stem_uuid)
        siblings = db['twig'].all(filt)
        if not siblings.size() < 2:
            if includeSelf:
                return siblings
            else:
                siblings.remove_object(self)
                return siblings
        else:
            return None


class Version(BaseJinxObject, mongoengine.Document):

    _name = 'Version'
    meta = {'collection': 'version'}
    INTERFACE_STRING = "version"

    # Required fields
    comment = mongoengine.StringField(required=True, dispName="Comment", icon=icon_paths.ICON_COMMENT_SML)
    status = mongoengine.StringField(required=True, dispName="Status")
    version = mongoengine.IntField(required=True, dispName="Version")
    parent_uuid = mongoengine.StringField(required=True, dispName="Package UUID", visible=False)
    state = mongoengine.StringField(required=True, dispName="State", visible=False)  # 'complete', 'working', 'failed', eg: ip rendering means 'working'

    # Optional fields
    framerange = mongoengine.ListField(dispName="Frame Range")
    thumbnail = mongoengine.StringField(dispName="Thumbnail", icon=icon_paths.ICON_IMAGE_SML)

    def children(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db["content"], parent_uuid=self.uuid)
        packages = db["content"].all(filt)
        if packages.hasObjects():
            return packages
        else:
            return None

    def parent(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['package'], uuid=self.parent_uuid)
        package = db['package'].one(filt)
        if package:
            return package
        else:
            return None

    def siblings(self, includeSelf=False):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['version'], parent_uuid=self.parent_uuid)
        siblings = db['version'].all(filt)
        if not siblings.size() < 2:
            if includeSelf:
                return siblings
            else:
                siblings.remove_object(self)
                return siblings
        else:
            return None


class Content(BaseJinxObject, mongoengine.Document):

    _name = 'content'
    meta = {'collection': 'content'}
    INTERFACE_STRING = "content"

    # Required fields
    parent_uuid = mongoengine.StringField(required=True, dispName="Version UUID", visible=False)
    format = mongoengine.StringField(required=True, dispName="Format")

    # Optional fields
    resolution = mongoengine.ListField(dispName="Resolution")
    framerange = mongoengine.ListField(dispName="Frame Range")
    thumbnail = mongoengine.StringField(dispName="Thumbnail", icon=icon_paths.ICON_IMAGE_SML)

    def children(self):
        return None

    def parent(self):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['version'], uuid=self.parent_uuid)
        version = db['version'].one(filt)
        if version:
            return version
        else:
            return None

    def siblings(self, includeSelf=False):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['content'], parent_uuid=self.parent_uuid)
        siblings = db['content'].all(filt)
        if not siblings.size() < 2:
            if includeSelf:
                return siblings
            else:
                siblings.remove_object(self)
                return siblings
        else:
            return None


class Dependency(BaseJinxObject, mongoengine.Document):

    _name = 'Dependency'
    meta = {'collection': 'dependency'}
    INTERFACE_STRING = "dependency"

    # Required fields
    source_version_uuid = mongoengine.StringField(required=True, dispName="Source Version UUID")
    link_version_uuid = mongoengine.StringField(required=True, dispName="Link Version UUID")

    def children(self):
        return None

    def siblings(self, includeSelf=False):
        db = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(db['dependency'], source_version_uuid=self.source_version_uuid)
        siblings = db['dependecy'].all(filt)
        if not siblings.size() < 2:
            if includeSelf:
                return siblings
            else:
                siblings.remove_object(self)
                return siblings
        else:
            return None
