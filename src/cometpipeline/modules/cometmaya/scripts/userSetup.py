from cometmaya.ui.base_shelf import BaseShelf
from pipeicon import icon_paths
from pipeicon.util import fullIconPath
import maya.cmds as mc

# Function Imports
from cometmaya.ui.entity_picker import run as entprun

mc.evalDeferred('CometShelf()')


class CometShelf(BaseShelf):
    def __init__(self, name='Comet'):
        BaseShelf.__init__(self, name)

    def build(self):
        self.addButton(label='Set Entity', icon=fullIconPath(icon_paths.ICON_SHOT_LRG), command='entprun()')
        self.addSeparator()