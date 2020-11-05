import os
import mongorm
import cometpublish


def rec_build(dir, subDirs):
    os.mkdir(dir)
    if subDirs:
        for k, v in subDirs.items():
            rec_build(os.path.join(dir, k), v)


def sequenceShotTargetPath(jobObject, seqName):
    return os.path.abspath(os.path.join(jobObject.path, "production", seqName))


def assetTargetPath(parentObject, assetName):
    if parentObject.get("type") == "job":
        return os.path.abspath(os.path.join(parentObject.get("path"), os.pardir, os.pardir,
                                            "assets", assetName))
    else:
        return os.path.abspath(os.path.join(parentObject.get("path"), assetName))


def packageTargetPath(entityObject, pkgType, pkgName):
    return os.path.abspath(os.path.join(entityObject.get("path"), cometpublish.PUBLISH_DIR_NAME, pkgType, pkgName))

