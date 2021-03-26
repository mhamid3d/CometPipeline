from cometpublish.util import rec_build
import os

PUBLISH_DIR_NAME = "_publish"
THUMBNAIL_DIR_NAME = "_thumbnail"
WORKING_DIR_NAME = "_work"

ENTITY_TEMPLATE_STRUCTURE = {
    PUBLISH_DIR_NAME: {},
    '_ref': {},
    THUMBNAIL_DIR_NAME: {},
    # TODO: each app should have a predefined structure, in another python module
    WORKING_DIR_NAME: {
        'houdini': {},
        'katana': {},
        'maya': {},
        'modo': {},
        'nuke': {},
        'photoshop': {},
        'unreal': {},
        'zbrush': {},
        'painter': {},
        'designer': {},
        'marvelous': {},
        'mari': {}
    }
}


JOB_TEMPLATE_STRUCTURE = {
    'assets': {},
    'editorial': {'grading': {}},
    'production': {},
    'ref': {'ocio': {}}
}


def build_job_directory(jobObject):
    assert not os.path.exists(jobObject.get("path")), "Job directory already exists."

    # Make the master job directory
    jobPath = os.path.abspath(jobObject.get("path"))
    os.mkdir(jobPath)

    # Build from template
    for dir, subDirs in JOB_TEMPLATE_STRUCTURE.items():
        rec_build(os.path.join(jobPath, dir), subDirs)


def build_entity_directory(entityObject):
    assert not os.path.exists(entityObject.get("path")), "Entity directory already exists."

    # Make the master entity directory
    entityPath = os.path.abspath(entityObject.get("path"))
    os.mkdir(entityPath)

    # Build from template
    for dir, subDirs in ENTITY_TEMPLATE_STRUCTURE.items():
        rec_build(os.path.join(entityPath, dir), subDirs)


def build_package_directory(packageObject):
    assert not os.path.exists(packageObject.get("path")), "Package directory already exists"

    packagePath = os.path.abspath(packageObject.get("path"))
    packageTypePath = os.path.abspath(os.path.join(packagePath, os.pardir))
    if not os.path.exists(packageTypePath):
        os.mkdir(packageTypePath)

    os.mkdir(packagePath)


def build_version_directory(versionObject):
    assert not os.path.exists(versionObject.get("path")), "Version directory already exists"

    os.mkdir(os.path.abspath(versionObject.get("path")))