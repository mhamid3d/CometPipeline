from . import icon_paths
import os


def fullIconPath(relPath):
    return os.path.abspath(os.path.join(__file__, os.pardir, "icons", relPath.split("/")[-1]))


def entityIcon(entityObject):
    if entityObject:
        type = entityObject.get("type")
    else:
        return ""

    if type == "asset":
        return icon_paths.ICON_ASSET_LRG
    elif type == "sequence":
        return icon_paths.ICON_SEQUENCE_LRG
    elif type == "shot":
        return icon_paths.ICON_SHOT_LRG
    elif type == "job":
        return icon_paths.ICON_COMETPIPE_LRG