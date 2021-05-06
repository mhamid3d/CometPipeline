from pipeicon import icon_paths

DEFAULT_ROOT_ENTITIES = [
    'char',
    'crowd',
    'environ',
    'fx',
    'prop',
    'vehicle',
    'utility'
]

PACKAGE_TYPES = {
    'APKG': 'Asset Package',
    'CACHE': 'Geometry Cache',
    'CGR': 'CG Render',
    'EDIT': 'Editing',
    'ELEM': '2D Element',
    'KMOD': 'Katana Module',
    'LGTR': 'Light Rig',
    'LOOK': 'Asset Look File',
    'MODEL': 'Asset Model',
    'OUT': 'Presentable 2D Image Sequence',
    'PLAY': 'Playblast',
    'QC': 'Quality Assurance Check',
    'RIG': 'Asset Rig',
    'ROTO': 'Rotoscope Element',
    'SCAN': 'Plate from source',
    'TEX': 'Asset Texture',
    'TRACK': '2D Camera Track',
}

FORMAT_TO_ICON = {
    'mb': icon_paths.ICON_FILEMB_LRG,
    'ma': icon_paths.ICON_FILEMA_LRG,
    'bif': icon_paths.ICON_FILEBIF_LRG,
    'mel': icon_paths.ICON_FILEMEL_LRG,
    'py': icon_paths.ICON_FILEPY_LRG,
    'abc': icon_paths.ICON_ALEMBIC2_LRG,
    'usd': icon_paths.ICON_USD_LRG
}