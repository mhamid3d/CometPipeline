# import mongorm
#
#
# db = mongorm.getHandler()
# fl = mongorm.getFilter()
#
# obj = db['version'].create(
#     label="APKG_ab_seq_lighting_lod300_v003",
#     path="/jobs/DELOREAN/ab_seq/apkg",
#     job="DELOREAN",
#     parent_uuid="187865ae-c94c-4a89-9b1e-e1b63fbe1e14",
#     created_by="mhamid",
#     version=3,
#     comment="hello",
#     status="in progress",
#     state="complete"
# )
#
# obj.save()

from cometpublish import package_util
from collections import OrderedDict

def packageType():
    return package_util.getPackageTypesDict().items()[0]




for k, v in packageTypeNameFields().items():
    print k, v