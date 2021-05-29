from mongorm.core.datainterface import DataInterface
from requests import get
import mongoengine as me
import pymongo
import os


class DbHandler(object):
    _DATABASE = os.getenv('MONGO_DATABASE')
    _PORT = int(os.getenv('MONGO_PORT'))
    _THIS_EXT_IP = get("https://api.ipify.org").text
    _MONGO_EXT_IP = os.getenv('MONGO_EXT_IP')
    _MONGO_INT_IP = os.getenv('MONGO_INT_IP')
    # TODO: remove
    _USER = 'god'
    _GOD_PWD = os.getenv('GOD_PWD')

    if _THIS_EXT_IP == _MONGO_EXT_IP:
        _HOST = _MONGO_INT_IP
    else:
        _HOST = _MONGO_EXT_IP

    def __init__(self):
        me.connect(db=self._DATABASE,
                   host=self._HOST,
                   port=self._PORT,
                   username=self._USER,
                   password=self._GOD_PWD,
                   authentication_source='admin')

    def __getitem__(self, item):
        assert item in self.list_interface_names(), "Invalid interface: {}".format(item)
        return DataInterface(item)

    def list_interface_names(self):
        db = me.connection.get_db()
        return db.list_collection_names()

    def getDataInterface(self, dataInterface):
        return self.__getitem__(dataInterface)

    def toMongoClient(self, host=None, port=None, usr=None, pwd=None):
        host = self._HOST if not host else host
        port = self._PORT if not port else port
        usr = self._USER if not usr else usr
        pwd = self._GOD_PWD if not pwd else pwd

        return pymongo.MongoClient(host=host, port=port, username=usr, password=pwd)