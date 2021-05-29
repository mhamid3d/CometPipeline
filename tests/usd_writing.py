from pxr import Usd, Sdf, Kind

WS = "/home/mhamid/Documents/usd_writing/{}"


shotUsd = Usd.Stage.CreateNew(WS.format("shot.usda"))
rootPrim = shotUsd.DefinePrim("/", "Xform")
shotUsd.SetDefaultPrim(rootPrim)
shotUsd.SetStartTimeCode(1001)
shotUsd.SetEndTimeCode(1101)
shotUsd.GetRootLayer().Save()

manifestUsd = Usd.Stage.CreateNew(WS.format("manifest.usda"))

world = manifestUsd.DefinePrim("/world", "Xform")
cam = manifestUsd.DefinePrim("/world/cam", "Xform")
geo = manifestUsd.DefinePrim("/world/geo", "Xform")
lgt = manifestUsd.DefinePrim("/world/lgt", "Xform")
gaffer = manifestUsd.DefinePrim("/world/lgt/gaffer", "Xform")

for grp in [world, cam, geo]:
    m = Usd.ModelAPI(grp)
    m.SetKind(Kind.Tokens.group)


camAsmb = manifestUsd.DefinePrim("/world/cam/renderCam", "Xform")
camCmpt = manifestUsd.DefinePrim("/world/cam/renderCam/renderCam_main", "Xform")
camShape = manifestUsd.DefinePrim("/world/cam/renderCam/renderCam_main/renderCam_mainShape", "Camera")

charAsmb = manifestUsd.DefinePrim("/world/geo/char_master", "Xform")
propAsmb = manifestUsd.DefinePrim("/world/geo/prop_master", "Xform")
fxAsmb = manifestUsd.DefinePrim("/world/geo/fx_master", "Xform")
envAsmb = manifestUsd.DefinePrim("/world/geo/env_master", "Xform")

for cmpt in [camCmpt]:
    m = Usd.ModelAPI(cmpt)
    m.SetKind(Kind.Tokens.component)

for asmb in [charAsmb, propAsmb, fxAsmb, envAsmb, camAsmb]:
    m = Usd.ModelAPI(asmb)
    m.SetKind(Kind.Tokens.assembly)

manifestUsd.GetRootLayer().Save()
