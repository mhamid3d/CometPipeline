from . import icon_paths
from cometpipe.core import FORMAT_TO_ICON
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
    else:
        return icon_paths.ICON_COMETPIPE_LRG


def dataObjectToIcon(dataObject):
    if dataObject.interfaceName() == "Package":
        return icon_paths.ICON_PACKAGE_LRG
    elif dataObject.interfaceName() == "Version":
        return icon_paths.ICON_VERSION_LRG
    elif dataObject.interfaceName() == "Content":
        return icon_paths.ICON_FILE_LRG if str(dataObject.get("format")) not in FORMAT_TO_ICON else FORMAT_TO_ICON[
            str(dataObject.get("format"))]
    elif dataObject.interfaceName() == "Entity":
        return entityIcon(dataObject)
    elif dataObject.interfaceName() == "User":
        return icon_paths.ICON_USER_LRG
    elif dataObject.interfaceName() == "Job":
        return icon_paths.ICON_COMETPIPE_LRG
    else:
        return ""