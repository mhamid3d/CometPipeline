from qtpy import QtWidgets, QtGui, QtCore
from cometqt.widgets.ui_entity_viewer import EntityViewer
from cometqt.widgets.ui_animated_popup_message import AnimatedPopupMessage
from cometqt import util as cqtutil
from mongorm import util as mgutil
import cometpublish
import datetime
import logging
import shutil
import os

LOGGER = logging.getLogger("Comet.ProjectManager")
logging.basicConfig()
LOGGER.setLevel(logging.INFO)


class GeneralOptionsPage(QtWidgets.QWidget):
    def __init__(self, parent=None, jobObject=None):
        super(GeneralOptionsPage, self).__init__(parent=parent)
        self._currentJob = jobObject


class AssetManagerPage(QtWidgets.QWidget):
    def __init__(self, parent=None, jobObject=None):
        super(AssetManagerPage, self).__init__(parent=parent)
        self._currentJob = jobObject
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.editorLayout = QtWidgets.QVBoxLayout()
        self.settingsLayout = cqtutil.FormVBoxLayout()
        self.addRemoveLayout = QtWidgets.QHBoxLayout()
        self.editorLayout.setAlignment(QtCore.Qt.AlignTop)
        self.settingsLayout.setContentsMargins(0, 0, 0, 0)

        self.nameLineEdit = QtWidgets.QLineEdit()
        self.productionCheckBox = QtWidgets.QCheckBox()
        self.addButton = QtWidgets.QPushButton("ADD TO SELECTION")
        self.removeButton = QtWidgets.QPushButton("REMOVE SELECTION")

        self.nameLineEdit.setMinimumHeight(32)
        self.removeButton.setStyleSheet("""
            QPushButton{
                background: #bf2626;
                border: none;
            }
            QPushButton:hover{
                border: 1px solid #c9c9c9;
            }
        """)

        self.settingsLayout.addRow("ASSET NAME", self.nameLineEdit)
        self.settingsLayout.addRow("RND / TEST ASSET", self.productionCheckBox)

        self.addRemoveLayout.addWidget(self.addButton)
        self.addRemoveLayout.addWidget(self.removeButton)

        self.entityViewer = EntityViewer()
        self.entityViewer.setCurrentJob(self._currentJob)
        self.entityViewer.setEntityType(self.entityViewer.TYPE_ASSETS)
        self.entityViewer.topLabel.hide()
        self.entityViewer.assetsButton.hide()
        self.entityViewer.productionButton.hide()

        self.mainLayout.addLayout(self.editorLayout)
        self.editorLayout.addLayout(self.settingsLayout)
        self.editorLayout.addWidget(cqtutil.h_line())
        self.editorLayout.addLayout(self.addRemoveLayout)
        self.mainLayout.addWidget(self.entityViewer)

        self.addButton.clicked.connect(self.add_asset)
        self.removeButton.clicked.connect(self.remove_asset)

    def add_asset(self):
        assetSelection = self.entityViewer.entityTree.selectedItems()
        if assetSelection:
            assetSelection = assetSelection[0]
        assetName = self.nameLineEdit.text()
        production = not self.productionCheckBox.isChecked()

        if not assetSelection or not assetName:

            errMsg = "Unknown error"

            if not assetSelection:
                errMsg = "Please make a selection in the tree"
            elif not assetName:
                errMsg = "Asset name field required"
            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message=errMsg, type=AnimatedPopupMessage.ERROR,
                                      parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        handler = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(handler['entity'], label=assetName, parent_uuid=assetSelection.dataObject.getUuid())
        existingObject = handler['entity'].one(filt)

        filt.clear()

        if existingObject:

            errMsg = "Asset with name '{}' and parent '{}' already exists".format(assetName,
                                                                                  assetSelection.dataObject.get("label"))
            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message=errMsg, type=AnimatedPopupMessage.ERROR,
                                      parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        # Database publish

        if assetSelection.dataObject.get("type") == "job":
            targetPath = os.path.abspath(os.path.join(
                assetSelection.dataObject.get("path"), os.pardir, os.pardir, "assets", assetName)
            )
        else:
            targetPath = os.path.abspath(os.path.join(assetSelection.dataObject.get("path"), assetName))

        entityObject = handler['entity'].objectPrototype()
        entityObject._generate_id()
        entityObject.created = datetime.datetime.now()
        entityObject.modified = entityObject.created
        entityObject.label = assetName
        entityObject.path = targetPath
        entityObject.job = self._currentJob.get("label")
        entityObject.type = 'asset'
        entityObject.production = production
        entityObject.parent_uuid = assetSelection.dataObject.getUuid()
        entityObject.created_by = mgutil.getCurrentUser().getUuid()
        entityObject.save()
        cometpublish.build_entity_directory(entityObject)

        self.entityViewer.populate()

    def remove_confirm_dialog(self, entityObj):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText("Are you ABSOLUTELY sure you want to delete: [{}] ?".format(entityObj.get("path")))
        msgBox.setInformativeText("THIS IS UNDOABLE. PLEASE BE 100% SURE YOU WANT TO DO THIS!")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Apply | QtWidgets.QMessageBox.Cancel)
        msgBox.setDefaultButton(msgBox.Cancel)
        msgBox.setIcon(msgBox.Critical)
        msgBox.setWindowTitle("CRITICAL STEP: ENTITY DELETION | {}".format(entityObj.get("label")))
        return msgBox

    def get_recursive_children(self, dataObject):
        objects = []
        handler = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(handler['entity'], parent_uuid=dataObject.getUuid())
        objs = handler['entity'].all(filt)
        for obj in objs:
            objects.append(obj)
            objects.extend(self.get_recursive_children(obj))

        return objects

    def remove_asset(self):
        assetSelection = self.entityViewer.entityTree.selectedItems()
        entityIsJob = True
        if assetSelection:
            assetSelection = assetSelection[0]
            entityIsJob = assetSelection.dataObject.get("type") == "job"

        if not assetSelection or entityIsJob:
            errMsg = "Unknown error"

            if not assetSelection:
                errMsg = "Please make a selection in the tree"
            elif entityIsJob:
                errMsg = "Cannot delete job level entity!"
            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message=errMsg, type=AnimatedPopupMessage.ERROR,
                                                       parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        confirmResult = self.remove_confirm_dialog(assetSelection.dataObject).exec_()

        if confirmResult == QtWidgets.QMessageBox.Apply and cqtutil.doLoginConfirm():
            recursiveChildren = self.get_recursive_children(assetSelection.dataObject)
            recursiveChildren.append(assetSelection.dataObject)
            prunePaths = []
            for obj in recursiveChildren:
                prunePaths.append(obj.get("path"))
                LOGGER.info("Removing database entry: {}".format(obj))
                obj.delete()

            for path in prunePaths:
                LOGGER.info("Deleting path: {}".format(path))
                if os.path.exists(path):
                    shutil.rmtree(path)

        self.entityViewer.populate()


class ProductionManagerPage(QtWidgets.QWidget):
    def __init__(self, parent=None, jobObject=None):
        super(ProductionManagerPage, self).__init__(parent=parent)
        self._currentJob = jobObject
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.editorLayout = QtWidgets.QVBoxLayout()
        self.settingsLayout = cqtutil.FormVBoxLayout()
        self.addRemoveLayout = QtWidgets.QHBoxLayout()
        self.editorLayout.setAlignment(QtCore.Qt.AlignTop)
        self.settingsLayout.setContentsMargins(0, 0, 0, 0)

        self.nameLineEdit = QtWidgets.QLineEdit()
        self.productionCheckBox = QtWidgets.QCheckBox()
        self.addButton = QtWidgets.QPushButton("ADD SEQUENCE")
        self.removeButton = QtWidgets.QPushButton("REMOVE SEQUENCE")

        self.nameLineEdit.setMinimumHeight(32)
        self.removeButton.setStyleSheet("""
            QPushButton{
                background: #bf2626;
                border: none;
            }
            QPushButton:hover{
                border: 1px solid #c9c9c9;
            }
        """)

        self.settingsLayout.addRow("SEQUENCE NAME", self.nameLineEdit)
        self.settingsLayout.addRow("RND / TEST SEQUENCE", self.productionCheckBox)

        self.addRemoveLayout.addWidget(self.addButton)
        self.addRemoveLayout.addWidget(self.removeButton)

        self.entityViewer = EntityViewer()
        self.entityViewer.setCurrentJob(self._currentJob)
        self.entityViewer.setEntityType(self.entityViewer.TYPE_PRODUCTION)
        self.entityViewer.topLabel.hide()
        self.entityViewer.assetsButton.hide()
        self.entityViewer.productionButton.hide()

        self.mainLayout.addLayout(self.editorLayout)
        self.editorLayout.addLayout(self.settingsLayout)
        self.editorLayout.addWidget(cqtutil.h_line())
        self.editorLayout.addLayout(self.addRemoveLayout)
        self.mainLayout.addWidget(self.entityViewer)

        self.addButton.clicked.connect(self.add_asset)
        self.removeButton.clicked.connect(self.remove_asset)

    def add_asset(self):
        assetSelection = self.entityViewer.entityTree.selectedItems()
        if assetSelection:
            assetSelection = assetSelection[0]
        assetName = self.nameLineEdit.text()
        production = not self.productionCheckBox.isChecked()

        if not assetSelection or not assetName:

            errMsg = "Unknown error"

            if not assetSelection:
                errMsg = "Please make a selection in the tree"
            elif not assetName:
                errMsg = "Asset name field required"
            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message=errMsg, type=AnimatedPopupMessage.ERROR,
                                      parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        handler = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(handler['entity'], label=assetName, parent_uuid=assetSelection.dataObject.getUuid())
        existingObject = handler['entity'].one(filt)

        filt.clear()

        if existingObject:

            errMsg = "Asset with name '{}' and parent '{}' already exists".format(assetName,
                                                                                  assetSelection.dataObject.get("label"))
            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message=errMsg, type=AnimatedPopupMessage.ERROR,
                                      parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        # Database publish

        if assetSelection.dataObject.get("type") == "job":
            targetPath = os.path.abspath(os.path.join(
                assetSelection.dataObject.get("path"), os.pardir, os.pardir, "assets", assetName)
            )
        else:
            targetPath = os.path.abspath(os.path.join(assetSelection.dataObject.get("path"), assetName))

        entityObject = handler['entity'].objectPrototype()
        entityObject._generate_id()
        entityObject.created = datetime.datetime.now()
        entityObject.modified = entityObject.created
        entityObject.label = assetName
        entityObject.path = targetPath
        entityObject.job = self._currentJob.get("label")
        entityObject.type = 'asset'
        entityObject.production = production
        entityObject.parent_uuid = assetSelection.dataObject.getUuid()
        entityObject.created_by = mgutil.getCurrentUser().getUuid()
        entityObject.save()
        cometpublish.build_entity_directory(entityObject)

        self.entityViewer.populate()

    def remove_confirm_dialog(self, entityObj):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText("Are you ABSOLUTELY sure you want to delete: [{}] ?".format(entityObj.get("path")))
        msgBox.setInformativeText("THIS IS UNDOABLE. PLEASE BE 100% SURE YOU WANT TO DO THIS!")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Apply | QtWidgets.QMessageBox.Cancel)
        msgBox.setDefaultButton(msgBox.Cancel)
        msgBox.setIcon(msgBox.Critical)
        msgBox.setWindowTitle("CRITICAL STEP: ENTITY DELETION | {}".format(entityObj.get("label")))
        return msgBox

    def get_recursive_children(self, dataObject):
        objects = []
        handler = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(handler['entity'], parent_uuid=dataObject.getUuid())
        objs = handler['entity'].all(filt)
        for obj in objs:
            objects.append(obj)
            objects.extend(self.get_recursive_children(obj))

        return objects

    def remove_asset(self):
        assetSelection = self.entityViewer.entityTree.selectedItems()
        entityIsJob = True
        if assetSelection:
            assetSelection = assetSelection[0]
            entityIsJob = assetSelection.dataObject.get("type") == "job"

        if not assetSelection or entityIsJob:
            errMsg = "Unknown error"

            if not assetSelection:
                errMsg = "Please make a selection in the tree"
            elif entityIsJob:
                errMsg = "Cannot delete job level entity!"
            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message=errMsg, type=AnimatedPopupMessage.ERROR,
                                                       parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        confirmResult = self.remove_confirm_dialog(assetSelection.dataObject).exec_()

        if confirmResult == QtWidgets.QMessageBox.Apply and cqtutil.doLoginConfirm():
            recursiveChildren = self.get_recursive_children(assetSelection.dataObject)
            recursiveChildren.append(assetSelection.dataObject)
            prunePaths = []
            for obj in recursiveChildren:
                prunePaths.append(obj.get("path"))
                LOGGER.info("Removing database entry: {}".format(obj))
                obj.delete()

            for path in prunePaths:
                LOGGER.info("Deleting path: {}".format(path))
                if os.path.exists(path):
                    shutil.rmtree(path)

        self.entityViewer.populate()


class ProjectManager(QtWidgets.QWidget):
    def __init__(self, parent=None, jobObject=None):
        super(ProjectManager, self).__init__(parent=parent)
        self._currentJob = jobObject
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)
        self.setup_ui()

    def setup_ui(self):
        if not self._currentJob:
            self.close()

        self.setWindowTitle("Project Manager: [{}]".format(self._currentJob.get("label")))

        self.settingsButtonGroup = QtWidgets.QButtonGroup()
        self.generalOptionsButton = QtWidgets.QPushButton("General Options")
        self.assetManagerButton = QtWidgets.QPushButton("Asset Manager")
        self.productionManagerButton = QtWidgets.QPushButton("Production Manager")
        self.settingsButtonGroup.buttonClicked.connect(self.page_changed)

        self.settingsButtonGroup.addButton(self.generalOptionsButton, id=0)
        self.settingsButtonGroup.addButton(self.assetManagerButton, id=1)
        self.settingsButtonGroup.addButton(self.productionManagerButton, id=2)

        self.mainAreaLayout = QtWidgets.QHBoxLayout()
        self.settingsButtonsWidget = QtWidgets.QWidget()
        self.settingsButtonsLayout = QtWidgets.QVBoxLayout()
        self.settingsButtonsWidget.setMinimumWidth(200)
        self.settingsButtonsWidget.setLayout(self.settingsButtonsLayout)
        self.settingsButtonsLayout.setAlignment(QtCore.Qt.AlignTop)
        self.settingsButtonsLayout.setContentsMargins(0, 0, 0, 0)
        self.settingsButtonsLayout.setSpacing(0)

        self.mainLayout.addLayout(self.mainAreaLayout)
        self.mainAreaLayout.addWidget(self.settingsButtonsWidget)
        self.settingsButtonsLayout.addWidget(self.generalOptionsButton)
        self.settingsButtonsLayout.addWidget(self.assetManagerButton)
        self.settingsButtonsLayout.addWidget(self.productionManagerButton)

        for button in self.settingsButtonGroup.buttons():
            button.setCheckable(True)
            button.setStyleSheet("""
                QPushButton{
                    border: none;
                }
                QPushButton:checked{
                    border-left: 4px solid #148CD2;
                }
            """)

        self.settingsButtonGroup.button(0).setChecked(True)

        self.pagesStack = QtWidgets.QStackedWidget()
        self.generalOptionsPage = GeneralOptionsPage(parent=self, jobObject=self._currentJob)
        self.assetManagerPage = AssetManagerPage(parent=self, jobObject=self._currentJob)
        self.productionManagerPage = ProductionManagerPage(parent=self, jobObject=self._currentJob)
        self.pagesStack.addWidget(self.generalOptionsPage)
        self.pagesStack.addWidget(self.assetManagerPage)
        self.pagesStack.addWidget(self.productionManagerPage)
        self.mainAreaLayout.addWidget(self.pagesStack)

    def page_changed(self):
        current_idx = self.settingsButtonGroup.id(self.settingsButtonGroup.checkedButton())
        self.pagesStack.setCurrentIndex(current_idx)


if __name__ == '__main__':
    import sys
    import qdarkstyle
    import mongorm

    h = mongorm.getHandler()
    f = mongorm.getFilter()
    f.search(h['job'], label='DELOREAN')
    job = h['job'].one(f)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win = ProjectManager(jobObject=job)
    win.resize(900, 700)
    win.show()
    sys.exit(app.exec_())
