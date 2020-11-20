import logging

LOGGER = logging.getLogger(__name__)
logging.basicConfig()


def getHandler():
    from .base.db_handler import DbHandler
    return DbHandler()


def getFilter():
    from .core.datafilter import DataFilter
    return DataFilter()


def createContainer(interface=None):
    assert interface, "Please provide a valid interface"
    from .core.datacontainer import DataContainer
    return DataContainer(interface=interface)