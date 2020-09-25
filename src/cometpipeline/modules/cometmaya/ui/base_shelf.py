import maya.cmds as mc


class BaseShelf():
    def __init__(self, name='baseCustomShelf'):
        self.name = name
        self.labelBackground = (0, 0, 0, 0)
        self.labelColor = (0.9, 0.9, 0.9)
        self.clean_old_shelf()
        self.build()

    def build(self):
        pass

    def addButton(self, label, icon=None, command=None):
        mc.shelfButton(width=37, height=37, image=icon, command=command, label=label, olb=self.labelBackground, olc=self.labelColor, parent=self.mainShelf)

    def addSeparator(self):
        mc.separator(w=12, h=35, hr=False, st='shelf', p=self.name)

    def clean_old_shelf(self):
        if mc.shelfLayout(self.name, q=1, ex=1):
            mc.deleteUI(self.name)
            self.mainShelf = mc.shelfLayout(self.name, p='ShelfLayout')
        else:
            self.mainShelf = mc.shelfLayout(self.name, p='ShelfLayout')