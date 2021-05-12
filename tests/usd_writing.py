from pxr import Usd, UsdGeom

WS = "/home/mhamid/Documents/usd_writing/{}"


assetUsd = Usd.Stage.CreateNew(WS.format("asset.usda"))
asmbPrim = assetUsd.DefinePrim("/walkman_all", "Xform")
cmptPrim = assetUsd.DefinePrim("/walkman_all/walkman", "Xform")
asmbPrim.SetMetadata('kind', 'assembly')
cmptPrim.SetMetadata('kind', 'component')

assetUsd.SetDefaultPrim(asmbPrim)

definitionUsd = Usd.Stage.CreateNew(WS.format("definition.usda"))
lodPrim = definitionUsd.DefinePrim("/walkman_all/walkman/lod_hi", "Xform")
lodPrim.GetReferences().AddReference('/jobs/DELOREAN/assets/prop/walkman/_publish/MODEL/MODEL_prop_walkman_varA_lod300/MODEL_prop_walkman_varA_lod300_v014/cache.abc')

definitionUsd.GetRootLayer().Save()

asmbPrim.GetReferences().AddReference(WS.format("definition.usda"))

assetUsd.GetRootLayer().Save()