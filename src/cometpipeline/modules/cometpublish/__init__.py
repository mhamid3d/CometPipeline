from cometpublish.util import rec_build
import os

ENTITY_TEMPLATE_STRUCTURE = {
    '_publish': {},
    '_ref': {},
    '_thumbnail': {},
    # TODO: each app should have a predefined structure, in another python module
    '_work': {
        'houdini': {},
        'katana': {},
        'maya': {},
        'modo': {},
        'nuke': {},
        'photoshop': {},
        'unreal': {},
        'zbrush': {}
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