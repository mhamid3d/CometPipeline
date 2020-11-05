import yaml
import os
from collections import OrderedDict

PKG_CONFIG_FILE = os.path.abspath(os.path.join(
    __file__, os.pardir, "packageConfig.yaml"
))
PKG_CONFIG_DATA = yaml.load(file(PKG_CONFIG_FILE, "r"), Loader=yaml.FullLoader)


def getNameFieldsDict():
    dict = OrderedDict()
    for item in PKG_CONFIG_DATA.get("publish").get("nameFields"):
        dict.update(item)
    return dict


def getPackageTypesDict():
    dict = OrderedDict()
    for item in sorted(PKG_CONFIG_DATA.get("packageTypes")):
        key = item.keys()[0]
        value = item[key]
        if value.has_key('required'):
            value['required'] = [x for x in getNameFieldsDict().keys() if x in value['required']] + \
                                [x for x in value['required'] if x not in getNameFieldsDict().keys()]
        item[key] = value
        dict.update(item)
    return dict