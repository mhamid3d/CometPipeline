import os


def fullIconPath(relPath):
    return os.path.abspath(os.path.join(__file__, os.pardir, "icons", relPath.split("/")[-1]))