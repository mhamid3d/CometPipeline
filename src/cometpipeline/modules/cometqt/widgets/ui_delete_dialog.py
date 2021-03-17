from qtpy import QtWidgets, QtGui, QtCore
from pipeicon import icon_paths, util as iconutil
import mongorm
import logging
import shutil
import os


LOGGER = logging.getLogger("Comet.DeleteDialog")
logging.basicConfig()
LOGGER.setLevel(logging.INFO)


class DeleteDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, dataObjects=[]):
        super(DeleteDialog, self).__init__(parent=parent)
        self.setWindowTitle("Delete Items")
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.topLayout = QtWidgets.QHBoxLayout()
        self.topLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.db_handler = mongorm.getHandler()
        self.db_flt = mongorm.getFilter()

        self.warningIcon = QtWidgets.QLabel()
        self.warningIcon.setPixmap(QtGui.QPixmap(icon_paths.ICON_CAUTIONRED_SML).scaledToHeight(
            24, QtCore.Qt.SmoothTransformation
        ))
        self.label = QtWidgets.QLabel("The following items will be deleted. This action is UNDOABLE")
        self.topLayout.addWidget(self.warningIcon)
        self.topLayout.addWidget(self.label)
        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addWidget(self.label)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.setLayout(self.mainLayout)
        self.itemsToDeleteList = QtWidgets.QListWidget()
        self._dataObjects = [item.dataObject for item in dataObjects]
        self.invalidInterfaceTypes = [
            "User",
            "Content",
            "Notifications",
            "Dependency"
        ]
        self.deleteActionMap = {
            "Entity": self.deleteEntity,
            "Job": self.deleteJob,
            "Package": self.deletePackage,
            "Version": self.deleteVersion,
        }
        self.buttons = QtWidgets.QDialogButtonBox()
        self.buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        self.mainLayout.addWidget(self.itemsToDeleteList)
        self.mainLayout.addWidget(self.buttons)

        for item in self._dataObjects:
            if not item.interfaceName() in self.invalidInterfaceTypes:
                listItem = QtWidgets.QListWidgetItem(QtGui.QIcon(iconutil.dataObjectToIcon(item)), item.get("label"))
                listItem.dataObject = item
                self.itemsToDeleteList.addItem(listItem)

        self.buttons.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.buttons.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.accept)

    def accept(self):
        count = self.itemsToDeleteList.count()
        areYouSure = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Delete {} Items".format(count),
                                           "Are You Sure You Want To Delete {} Items".format(count),
                                           QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No).exec_()

        if areYouSure == QtWidgets.QMessageBox.Yes:
            for i in range(self.itemsToDeleteList.count()):
                item = self.itemsToDeleteList.item(i)
                self.deleteActionMap[item.dataObject.interfaceName()](item.dataObject)

        QtWidgets.QDialog.accept(self)

    def deleteJob(self, jobObject):
        assert jobObject.interfaceName() == "Job", "Invalid interface deletion method: Tried deleting {} with {} method".format(
                    jobObject.interfaceName(), "Job")

        prunePaths = [jobObject.get("path")]
        pruneObjects = [jobObject]

        entities = jobObject.children()

        for object in pruneObjects:
            LOGGER.info("Removing database entry: {}".format(object))
            object.delete()

        for path in prunePaths:
            if os.path.exists(path):
                LOGGER.info("Deleting Path: {}".format(path))
                shutil.rmtree(path)

        for entity in entities:
            self.deleteEntity(entity)

        return

    def deleteEntity(self, entityObject):
        assert entityObject.interfaceName() == "Entity", "Invalid interface deletion method: Tried deleting {} with {} method".format(
                    entityObject.interfaceName(), "Entity")

        prunePaths = [entityObject.get("path")]
        pruneObjects = [entityObject]

        recursiveEntites = entityObject.recursive_children()

        for childEntity in recursiveEntites:
            pruneObjects.append(childEntity)
            prunePaths.append(childEntity.get("path"))

        for object in pruneObjects:
            for package in object.packages():
                self.deletePackage(package)
            LOGGER.info("Removing database entry: {}".format(object))
            object.delete()

        for path in prunePaths:
            if os.path.exists(path):
                LOGGER.info("Deleting Path: {}".format(path))
                shutil.rmtree(path)

        return

    def deletePackage(self, packageObject):
        assert packageObject.interfaceName() == "Package", "Invalid interface deletion method: Tried deleting {} with {} method".format(
                    packageObject.interfaceName(), "Package")

        prunePaths = [packageObject.get("path")]
        pruneObjects = [packageObject]

        versionObjects = packageObject.children()

        for object in pruneObjects:
            LOGGER.info("Removing database entry: {}".format(object))
            object.delete()

        for path in prunePaths:
            if os.path.exists(path):
                LOGGER.info("Deleting Path: {}".format(path))
                shutil.rmtree(path)

        for version in versionObjects:
            self.deleteVersion(version)

        return

    @staticmethod
    def deleteVersion(versionObject):
        assert versionObject.interfaceName() == "Version", "Invalid interface deletion method: Tried deleting {} with {} method".format(
                    versionObject.interfaceName(), "Version")

        prunePaths = [versionObject.get("path")]
        pruneObjects = [versionObject]
        contents = versionObject.children()
        dependencies = versionObject.get_dependency_masters()
        dependencies.extend(versionObject.get_dependency_slaves())

        for content in contents:
            pruneObjects.append(content)
            prunePaths.append(content.get("path"))

        for dependency in dependencies:
            pruneObjects.append(dependency)

        for object in pruneObjects:
            LOGGER.info("Removing database entry: {}".format(object))
            object.delete()

        for path in prunePaths:
            if os.path.exists(path):
                LOGGER.info("Deleting Path: {}".format(path))
                shutil.rmtree(path)

        return


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = DeleteDialog()
    win.show()
    sys.exit(app.exec_())