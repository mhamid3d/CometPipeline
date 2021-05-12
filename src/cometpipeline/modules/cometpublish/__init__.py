from cometpublish.util import rec_build
import os

PUBLISH_DIR_NAME = "publish"
THUMBNAIL_DIR_NAME = "thumbnail"
WORKING_DIR_NAME = "work"

ENTITY_TEMPLATE_STRUCTURE = {
    PUBLISH_DIR_NAME: {},
    'ref': {},
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
    'editorial': {},
    'ref': {}
}


def build_job_directory(jobObject):
    assert not os.path.exists(jobObject.abs_path()), "Job directory already exists."

    # Make the master job directory
    jobPath = os.path.abspath(jobObject.abs_path())
    os.mkdir(jobPath)

    # Build from template
    for dir, subDirs in JOB_TEMPLATE_STRUCTURE.items():
        rec_build(os.path.join(jobPath, dir), subDirs)


def build_entity_directory(entityObject):
    assert not os.path.exists(entityObject.abs_path()), "Entity directory already exists."

    # Make the master entity directory
    entityPath = os.path.abspath(entityObject.abs_path())
    os.mkdir(entityPath)

    # Build from template
    for dir, subDirs in ENTITY_TEMPLATE_STRUCTURE.items():
        rec_build(os.path.join(entityPath, dir), subDirs)


def build_package_directory(packageObject):
    assert not os.path.exists(packageObject.abs_path()), "Package directory already exists"

    packagePath = os.path.abspath(packageObject.abs_path())
    packageTypePath = os.path.abspath(os.path.join(packagePath, os.pardir))
    if not os.path.exists(packageTypePath):
        os.mkdir(packageTypePath)

    os.mkdir(packagePath)


def build_version_directory(versionObject):
    assert not os.path.exists(versionObject.abs_path()), "Version directory already exists"

    os.mkdir(os.path.abspath(versionObject.abs_path()))