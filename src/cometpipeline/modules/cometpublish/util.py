import os
import mongorm
import cometpublish


def rec_build(dir, subDirs):
    os.mkdir(dir)
    if subDirs:
        for k, v in subDirs.items():
            rec_build(os.path.join(dir, k), v)


def packageTargetPath(entityObject, pkgType, pkgName):
    return os.path.join(entityObject.rel_path(),
                        cometpublish.PUBLISH_DIR_NAME,
                        pkgType,
                        pkgName)

