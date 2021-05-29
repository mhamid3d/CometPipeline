import bcrypt
from pxr import Usd, Kind

walkman_asmb = Usd.Stage.CreateInMemory()
asmb_root = walkman_asmb.DefinePrim("/walkman_all", "Xform")
asmb_root.SetMetadata("kind", "assembly")
walkman_asmb.SetDefaultPrim(asmb_root)
override = walkman_asmb.OverridePrim("/walkman_all/walkman_hi")
override.GetReferences().AddReference("/home/mhamid/Documents/usd_test/walkman_cpmt.usd")
walkman_asmb.GetRootLayer().Export("/home/mhamid/Documents/usd_test/walkman_asmb.usd", "hello", {'format': 'usda'})

# cpmt = Usd.Stage.Open("/home/mhamid/Documents/usd_test/walkman_cpmt.usd")
# cpmt.SetDefaultPrim(cpmt.GetPrimAtPath("/walkman"))
# cpmt.Save()