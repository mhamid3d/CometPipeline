from cometpublish.ui import ui_version_publisher as uvp
from mongorm import util as mgutil

import imp
imp.reload(uvp)


def pp(**kwargs):
    package = kwargs.get("packageObject")
    version = kwargs.get("versionObject")
    entity = kwargs.get("entityObject")

    handler = mongorm.getHandler()

    contentObject1 = handler['content'].create(
        label="alembic",
        created_by=mgutil.getCurrentUser().getUuid(),
        parent_uuid=version.getUuid(),
        job=version.get("job"),
        path=os.path.abspath(os.path.join(version.get("path"), "{}.abc".format(version.get("label")))),
        format="abc"
    )

    contentObject2 = handler['content'].create(
        label="main",
        created_by=mgutil.getCurrentUser().getUuid(),
        parent_uuid=version.getUuid(),
        job=version.get("job"),
        path=os.path.abspath(os.path.join(version.get("path"), "{}.mb".format(version.get("label")))),
        format="mb"
    )

    contentObject1.save()
    contentObject2.save()

    import maya.cmds as mc
    abcExportCommand = "-frameRange 1 1 -uvWrite -worldSpace -writeUVSets -dataFormat ogawa -root {rootObject} -file {filePath}".format(rootObject=str(mc.ls(sl=True)[0]), filePath=contentObject1.get("path"))
    mc.AbcExport(j=abcExportCommand)
    mc.file(contentObject2.get("path"), type="mayaBinary", ea=True)
    
    return True



win = uvp.VersionPublisher()
win.post_process = pp
win.show()