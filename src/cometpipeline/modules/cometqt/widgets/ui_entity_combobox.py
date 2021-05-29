from qtpy import QtWidgets, QtGui, QtCore
from pipeicon import icon_paths, util as iconutil
from cometqt.widgets.ui_entity_viewer import EntityViewer
import mongorm


class EntityPickerMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super(EntityPickerMenu, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.entityViewer = EntityViewer(parent=self)
        self.entityViewer.setFromEnvironment()
        self.entityViewer.jobSelectWidget.show()
        self.mainLayout.addWidget(self.entityViewer)

        self.entityViewer.entityTree.itemClicked.connect(self.selectionChanged)
        self.propagateToParent()

    def selectionChanged(self):
        if self.propagateToParent():
            self.close()

    def propagateToParent(self):
        sel = self.entityViewer.entityTree.selectedItems()
        if sel:
            sel = sel[0]
            self.parent().setSelectedEntity(sel.dataObject)
        else:
            self.parent().setSelectedEntity(None)

        self.parent().setSelectedJob(self.entityViewer.jobComboBox.currentDataObject())

        return sel


class EntityComboBox(QtWidgets.QPushButton):

    entityChanged = QtCore.Signal(object)
    jobChanged = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(EntityComboBox, self).__init__(parent=parent)
        self._selectedJob = None
        self._selectedEntity = None
        self.defaultText = "Please Select Entity"
        self.setText(self.defaultText)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.entityMenu = EntityPickerMenu(parent=self)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.customContextMenuRequested.emit(event.pos())
        return super(EntityComboBox, self).mousePressEvent(event)

    def contextMenu(self, event):
        pos = self.mapToGlobal(self.rect().bottomLeft())
        pos.setY(pos.y() + 3)
        self.entityMenu.setMinimumSize(self.width(), 400)
        self.entityMenu.exec_(pos)

    def getSelectedJob(self):
        return self._selectedJob

    def getSelectedEntity(self):
        return self._selectedEntity

    def setSelectedJob(self, jobObject):
        self._selectedJob = jobObject
        self.jobChanged.emit(jobObject)

    def setSelectedEntity(self, entityObject):

        self._selectedEntity = entityObject

        if entityObject:
            text = entityObject.get("label")
            icon = iconutil.dataObjectToIcon(entityObject)
        else:
            text = self.defaultText
            icon = ""

        self.setText(text)
        self.setIcon(QtGui.QIcon(icon))
        self.entityChanged.emit(entityObject)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = EntityComboBox()
    win.resize(300, 32)
    win.show()
    sys.exit(app.exec_())