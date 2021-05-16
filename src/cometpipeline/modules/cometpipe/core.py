from pipeicon import icon_paths
from cometqt import util as pqtutil
import os


DEFAULT_ROOT_ENTITIES = [
    'char',
    'crowd',
    'env',
    'fx',
    'prop',
    'vehcl',
    'util'
]

FORMAT_TO_ICON = {
    'mb': icon_paths.ICON_FILEMB_LRG,
    'ma': icon_paths.ICON_FILEMA_LRG,
    'bif': icon_paths.ICON_FILEBIF_LRG,
    'mel': icon_paths.ICON_FILEMEL_LRG,
    'py': icon_paths.ICON_FILEPY_LRG,
    'abc': icon_paths.ICON_ALEMBIC2_LRG,
    'usd': icon_paths.ICON_USD_LRG,
    'ocio': icon_paths.ICON_OCIO_LRG
}

CREW_TYPES = [
            "Creator",
            "Admins",
            "Director",
            "Producer",
            "Art Director",
            "Production",
            "Previs",
            "Matte Painting",
            "Layout",
            "Animation",
            "CFX",
            "FX",
            "Lighting",
            "Compositing",
            "Lookdev",
            "Rigging",
            "Editorial"
        ]