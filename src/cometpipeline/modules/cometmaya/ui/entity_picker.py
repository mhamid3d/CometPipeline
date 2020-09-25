from cometqt.widgets.ui_entity_viewer import EntityViewer
from qtpy import QtGui, QtWidgets, QtCore
import mongorm
import os


class EntityPicker(QtWidgets.QDialog):
    def __init__(self):
        super(EntityPicker, self).__init__()
        self.setWindowTitle("Set Entity")
        handler = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(handler['job'], label="DELOREAN")
        job = handler['job'].one(filt)
        self.entityViewer = EntityViewer()
        self.entityViewer.setContentsMargins(0, 0, 0, 0)
        self.entityViewer.setCurrentJob(job)
        self.entityViewer.setIsDialog(True)
        self.entityViewer.populate()

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.diagButtonBox = QtWidgets.QDialogButtonBox()
        self.diagButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        self.mainLayout.addWidget(self.entityViewer)
        self.mainLayout.addWidget(self.diagButtonBox)

        self.diagButtonBox.accepted.connect(lambda: self.diagFinished(True))
        self.diagButtonBox.rejected.connect(lambda: self.diagFinished(False))

        self.loadCurrent()

    def loadCurrent(self):
        etype = os.getenv("ENTITY_TYPE")
        entity = os.getenv("ENTITY")

        if etype:
            self.entityViewer.setEntityType(etype)
        if entity:
            for item in self.entityViewer.getAllItems():
                if item.text(0) == entity:
                    self.entityViewer.entityTree.setCurrentItem(item)
                    break

    def diagFinished(self, accepted):
        if not accepted:
            self.close()

        selection = self.entityViewer.entityTree.selectedItems()
        if not selection:
            return False
        else:
            selection = selection[0]
            obj = selection.dataObject
            label = obj.get("label")
            os.environ['ENTITY'] = label
            etype = self.entityViewer.entityType
            os.environ['ENTITY_TYPE'] = etype
            self.close()


def run():
    ent = EntityPicker()
    ent.resize(450, 600)
    ent.exec_()