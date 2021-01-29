import yaml
import os
from collections import OrderedDict

PKG_CONFIG_FILE = os.path.abspath(os.path.join(
    __file__, os.pardir, "packageConfig.yaml"
))
PKG_CONFIG_DATA = yaml.load(open(PKG_CONFIG_FILE, "r"), Loader=yaml.FullLoader)


def getNameFieldsDict():
    dict = OrderedDict()
    for item in PKG_CONFIG_DATA.get("publish").get("nameFields"):
        dict.update(item)
    return dict


def getPackageTypesDict():
    dict = OrderedDict()
    packageTypes = PKG_CONFIG_DATA.get("packageTypes")
    packageTypes.sort(key=lambda x: list(x.keys())[0])
    for item in packageTypes:
        key = list(item.keys())[0]
        value = item[key]
        if 'required' in value:
            value['required'] = [x for x in list(getNameFieldsDict().keys()) if x in value['required']] + \
                                [x for x in value['required'] if x not in list(getNameFieldsDict().keys())]
        item[key] = value
        dict.update(item)
    return dict