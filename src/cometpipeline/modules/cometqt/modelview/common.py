from qtpy import QtCore

ROLE_LAST = QtCore.Qt.UserRole + 1


def registerRole():
    global ROLE_LAST
    ROLE_LAST += 1
    return ROLE_LAST


ROLE_DATA_TYPE = registerRole()

TYPE_STRING = "stringline"
TYPE_DATE = "date"
TYPE_FRAMERANGE = "framerange"
TYPE_PATH = "path"
TYPE_RESOLUTION = "resolution"
TYPE_FORMAT = "format"

DB_FIELD_TYPE_MAP = {
    'label': TYPE_STRING,
    'created': TYPE_DATE,
    'modified': TYPE_DATE,
    'framerange': TYPE_FRAMERANGE,
    'path': TYPE_PATH,
    'resolution': TYPE_RESOLUTION,
    'format': TYPE_FORMAT
}


def configure_date(value):
    displayText = value.strftime("%b %d %Y %I:%M %p")
    return [(QtCore.Qt.DisplayRole, displayText)]


def configure_format(value):
    return [(QtCore.Qt.DisplayRole, value), (QtCore.Qt.TextAlignmentRole, QtCore.Qt.AlignCenter)]


DB_FIELD_READABLE_MAP = {
    TYPE_DATE: configure_date,
    TYPE_FORMAT: configure_format
}