from pxr import Usd, Kind
import mongorm
import cometpublish


WS = "/home/mhamid/Documents/usd_writing/pub/{}"


def auto_shot_generate(entityObject):
    assert not entityObject.get("type") == "asset", "You cannot generate a shot usd package for an asset."

    handler = mongorm.getHandler()
    flt = mongorm.getFilter()

    flt.search(handler['package'], label='pkg_{}'.format(entityObject.get("label")), parent_uuid=entityObject.getUuid())
    shotPackage = handler['package'].one(flt)

    if shotPackage:
        raise RuntimeError("Shot package for entity {} already exists.".format(entityObject.get("label")))

    comment = "Auto-generated shot usd package"

    shotPackage = handler['package'].create(
        type='pkg',
        parent_uuid=entityObject.getUuid(),
        job=entityObject.job,
        label='shot'
    )
    shotPackage.save()
    cometpublish.build_package_directory(shotPackage)

    shotVersion = handler['version'].create(
        parent_uuid=shotPackage.getUuid(),
        comment=comment,
        status='approved',
        version=1,
        job=entityObject.job
    )
    shotVersion.save()
    cometpublish.build_version_directory(shotVersion)

    shotUsdContent = handler['content'].create(
        parent_uuid=shotVersion.getUuid(),
        format='usd',
        label='shot',
        job=entityObject.job
    )
    shotUsdContent.save()

    manifestUsdContent = handler['content'].create(
        parent_uuid=shotVersion.getUuid(),
        format='usd',
        label='manifest',
        job=entityObject.job
    )
    manifestUsdContent.save()

    manifestUsd = Usd.Stage.CreateInMemory()
    world = manifestUsd.DefinePrim("/world", "Xform")
    cam = manifestUsd.DefinePrim("/world/cam", "Xform")
    geo = manifestUsd.DefinePrim("/world/geo", "Xform")
    lgt = manifestUsd.DefinePrim("/world/lgt", "Xform")
    gaffer = manifestUsd.DefinePrim("/world/lgt/gaffer", "Xform")
    manifestUsd.SetDefaultPrim(world)

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

    manifestUsd.GetRootLayer().Export(manifestUsdContent.abs_path(), comment, {'format': 'usda'})

    shotUsd = Usd.Stage.CreateInMemory()
    rootPrim = shotUsd.DefinePrim("/", "Xform")
    shotUsd.SetDefaultPrim(rootPrim)
    worldOver = shotUsd.OverridePrim("/world")
    worldOver.GetReferences().AddReference('manifest.usd')
    shotUsd.SetStartTimeCode(entityObject.get("framerange")[0])
    shotUsd.SetEndTimeCode(entityObject.get("framerange")[1])
    shotUsd.SetFramesPerSecond(24.0)
    shotUsd.GetRootLayer().Export(shotUsdContent.abs_path(), comment, {'format': 'usda'})


# db = mongorm.getHandler()
# flt = mongorm.getFilter()
# flt.search(db['entity'], job='dlr', label='muk010')
# shot = db['entity'].one(flt)
# auto_shot_generate(shot)
