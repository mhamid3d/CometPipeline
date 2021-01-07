from qtpy import QtWidgets, QtGui, QtCore
from cometqt.widgets.ui_entity_viewer import EntityViewer
from cometqt.widgets.ui_animated_popup_message import AnimatedPopupMessage
from cometqt import util as cqtutil
from mongorm import util as mgutil
import cometpublish
import mongorm
import datetime
import logging
import shutil
import os


LOGGER = logging.getLogger("Comet.ProjectManager")
logging.basicConfig()
LOGGER.setLevel(logging.INFO)

# TODO: remove all packages, versions, contents, dependencies when removing asset or shot


def remove_confirm_dialog(dataObject):
    msgBox = QtWidgets.QMessageBox()
    msgBox.setText("Are you ABSOLUTELY sure you want to delete: [{}] ?".format(dataObject.get("path")))
    msgBox.setInformativeText("THIS IS UNDOABLE. PLEASE BE 100% SURE YOU WANT TO DO THIS!")
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Apply | QtWidgets.QMessageBox.Cancel)
    msgBox.setDefaultButton(msgBox.Cancel)
    msgBox.setIcon(msgBox.Critical)
    msgBox.setWindowTitle("CRITICAL STEP: DATABASE DELETION | {}".format(dataObject.get("label")))
    return msgBox


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
        filt.search(handler['entity'], label=assetName, parent_uuid=assetSelection.dataObject.getUuid(), job=self._currentJob.job)
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

        entityObject = handler['entity'].create(
            label=assetName,
            path=cometpublish.util.assetTargetPath(assetSelection.dataObject, assetName),
            job=self._currentJob.get("label"),
            type='asset',
            production=production,
            parent_uuid=assetSelection.dataObject.getUuid(),
            created_by=mgutil.getCurrentUser().getUuid(),
            jobpath="{}/{}".format(assetSelection.dataObject.get("jobpath"), assetName)
        )
        entityObject.save()
        cometpublish.build_entity_directory(entityObject)

        self.entityViewer.populate()

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

        confirmResult = remove_confirm_dialog(assetSelection.dataObject).exec_()

        if confirmResult == QtWidgets.QMessageBox.Apply and cqtutil.doLoginConfirm():
            recursiveChildren = assetSelection.dataObject.recursive_children()
            recursiveChildren.append_object(assetSelection.dataObject)
            recursiveChildren.sort(sort_field='jobpath')
            prunePaths = []
            for obj in recursiveChildren:
                prunePaths.append(obj.get("path"))
                LOGGER.info("Removing database entry: {}".format(obj))
                obj.delete()

            for path in prunePaths:
                if os.path.exists(path):
                    LOGGER.info("Deleting path: {}".format(path))
                    shutil.rmtree(path)

        self.entityViewer.populate()


class ProductionManagerPage(QtWidgets.QWidget):
    def __init__(self, parent=None, jobObject=None):
        super(ProductionManagerPage, self).__init__(parent=parent)
        self._currentJob = jobObject
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)

        self.editorLayout = QtWidgets.QVBoxLayout()
        self.treeLayout = QtWidgets.QVBoxLayout()
        self.editorLayout.setAlignment(QtCore.Qt.AlignTop)

        self.entityViewer = EntityViewer()
        self.entityViewer.setCurrentJob(self._currentJob)
        self.entityViewer.setEntityType(self.entityViewer.TYPE_PRODUCTION)
        self.entityViewer.topLabel.hide()
        self.entityViewer.assetsButton.hide()
        self.entityViewer.productionButton.hide()

        self.mainLayout.addLayout(self.editorLayout)
        self.mainLayout.addLayout(self.treeLayout)

        self.setup_seq_group()
        self.setup_shot_group()
        self.treeLayout.addWidget(self.entityViewer)

        self.removeSelectionButton = QtWidgets.QPushButton("REMOVE SELECTION")
        self.removeSelectionButton.setStyleSheet("""
                    QPushButton{
                        background: #bf2626;
                        border: none;
                    }
                    QPushButton:hover{
                        border: 1px solid #c9c9c9;
                    }
                """)
        self.treeLayout.addWidget(cqtutil.h_line())
        self.treeLayout.addWidget(self.removeSelectionButton)

        self.removeSelectionButton.clicked.connect(self.remove_selection)

    def setup_seq_group(self):
        self.sequenceGroupBox = QtWidgets.QGroupBox("Sequence")
        self.sequenceGroupLayout = QtWidgets.QVBoxLayout()
        self.sequenceGroupBox.setLayout(self.sequenceGroupLayout)
        self.seqSettingsLayout = cqtutil.FormVBoxLayout()
        self.seqAddRemoveLayout = QtWidgets.QHBoxLayout()
        self.sequenceGroupLayout.addLayout(self.seqSettingsLayout)
        self.sequenceGroupLayout.addWidget(cqtutil.h_line())

        self.seqNameLineEdit = QtWidgets.QLineEdit()
        self.seqProductionCheck = QtWidgets.QCheckBox()

        self.incrShotsLayout = QtWidgets.QHBoxLayout()
        self.beginRangeSpin = QtWidgets.QSpinBox()
        self.endRangeSpin = QtWidgets.QSpinBox()
        self.incrementSpin = QtWidgets.QSpinBox()
        for spin in [self.beginRangeSpin, self.endRangeSpin, self.incrementSpin]:
            spin.setRange(0, 999999)
            spin.setValue(0)
        self.incrShotsLayout.addWidget(self.beginRangeSpin)
        self.incrShotsLayout.addWidget(self.endRangeSpin)
        self.incrShotsLayout.addWidget(self.incrementSpin)
        self.incrShotsLayout.setContentsMargins(0, 0, 0, 0)

        self.paddingCheckBox = QtWidgets.QCheckBox()
        self.paddingCheckBox.setChecked(True)
        self.underScoreCheck = QtWidgets.QCheckBox()
        self.seqAddButton = QtWidgets.QPushButton("ADD SEQUENCE")

        self.seqNameLineEdit.setMinimumHeight(32)

        self.seqSettingsLayout.setContentsMargins(0, 0, 0, 0)

        self.seqSettingsLayout.addRow("SEQUENCE NAME", self.seqNameLineEdit)
        self.seqSettingsLayout.addRow("RND / TEST SEQUENCE", self.seqProductionCheck)
        self.seqSettingsLayout.addRow("SHOT NUMBER PADDING", self.paddingCheckBox, tip="ABC0010")
        self.seqSettingsLayout.addRow("INCLUDE UNDERSCORE IN SHOT", self.underScoreCheck, tip="ABC_0010")
        self.seqSettingsLayout.addRow("SHOTS", self.incrShotsLayout, tip="Begin, End, Increment")

        self.sequenceGroupLayout.addWidget(self.seqAddButton)

        self.editorLayout.addWidget(self.sequenceGroupBox)

        self.seqAddButton.clicked.connect(self.add_sequence)

    def setup_shot_group(self):
        self.shotGroupBox = QtWidgets.QGroupBox("Shot")
        self.shotGroupLayout = QtWidgets.QVBoxLayout()
        self.shotGroupBox.setLayout(self.shotGroupLayout)
        self.shotSettingsLayout = cqtutil.FormVBoxLayout()
        self.shotAddRemoveLayout = QtWidgets.QHBoxLayout()
        self.shotGroupLayout.addLayout(self.shotSettingsLayout)
        self.shotGroupLayout.addWidget(cqtutil.h_line())

        self.shotNumberLineEdit = QtWidgets.QLineEdit()
        self.shotProductionCheck = QtWidgets.QCheckBox()
        self.shotUnderscoreInclude = QtWidgets.QCheckBox()

        self.frameRangeLayout = QtWidgets.QHBoxLayout()
        self.frameRangeLayout.setContentsMargins(0, 0, 0, 0)
        self.frBegin = QtWidgets.QSpinBox()
        self.frEnd = QtWidgets.QSpinBox()
        for spin in [self.frBegin, self.frEnd]:
            spin.setRange(0, 999999)
            spin.setValue(0)
            self.frameRangeLayout.addWidget(spin)

        self.shotAddButton = QtWidgets.QPushButton("ADD SHOT")

        self.shotNumberLineEdit.setMinimumHeight(32)
        self.shotSettingsLayout.setContentsMargins(0, 0, 0, 0)

        self.shotSettingsLayout.addRow("SHOT NUMBER", self.shotNumberLineEdit)
        self.shotSettingsLayout.addRow("RND / TEST SHOT", self.shotProductionCheck)
        self.shotSettingsLayout.addRow("INCLUDE UNDERSCORE IN SHOT", self.shotUnderscoreInclude, tip="ABC_0010")
        self.shotSettingsLayout.addRow("FRAME RANGE", self.frameRangeLayout, tip="Begin, End")

        self.shotGroupLayout.addWidget(self.shotAddButton)

        self.editorLayout.addWidget(self.shotGroupBox)

        self.shotAddButton.clicked.connect(self.add_shot)

    def add_sequence(self):
        seqName = self.seqNameLineEdit.text()
        production = not self.seqProductionCheck.isChecked()
        padding = self.paddingCheckBox.isChecked()
        underscore = self.underScoreCheck.isChecked()
        shot_range = [self.beginRangeSpin.value(), self.endRangeSpin.value(), self.incrementSpin.value()]

        if not seqName:

            errMsg = "Unknown error"

            if not seqName:
                errMsg = "Sequence name is required"
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
        filt.search(handler['entity'], type='job', label=self._currentJob.job, job=self._currentJob.job)
        jobEntityObject = handler['entity'].one(filt)
        filt.clear()

        filt.search(handler['entity'], type='sequence', label="{}_seq".format(seqName), job=self._currentJob.job)
        sequenceObject = handler['entity'].one(filt)
        filt.clear()

        # If the sequence already exists, just create the shots
        if not sequenceObject:
            seqLabel = "{}_seq".format(seqName)
            sequenceObject = handler['entity'].create(
                label=seqLabel,
                path=cometpublish.util.sequenceShotTargetPath(self._currentJob, seqLabel),
                job=self._currentJob.job,
                type='sequence',
                production=production,
                parent_uuid=jobEntityObject.getUuid(),
                created_by=mgutil.getCurrentUser().getUuid(),
                jobpath="/{}".format(seqLabel)
            )
            sequenceObject.save()
            cometpublish.build_entity_directory(sequenceObject)

        # Create Shots
        if shot_range[2]:
            for i in range(shot_range[0], shot_range[1] + 1, shot_range[2]):
                shotNum = str(i).zfill(4) if padding else str(i)
                shotName = "{0}{1}{2}".format(seqName, "_" if underscore else "", shotNum)

                filt.search(handler['entity'], type='shot', label=shotName, job=self._currentJob.job)
                shotObject = handler['entity'].one(filt)
                filt.clear()

                if not shotObject:
                    shotObject = handler['entity'].create(
                        label=shotName,
                        path=cometpublish.util.sequenceShotTargetPath(self._currentJob, shotName),
                        job=self._currentJob.job,
                        type='shot',
                        production=sequenceObject.production,
                        parent_uuid=sequenceObject.getUuid(),
                        created_by=mgutil.getCurrentUser().getUuid(),
                        jobpath="{}/{}".format(sequenceObject.get("jobpath"), shotName)
                    )
                    shotObject.save()
                    cometpublish.build_entity_directory(shotObject)

        self.entityViewer.populate()

    def add_shot(self):
        shotNum = self.shotNumberLineEdit.text()
        production = not self.shotProductionCheck.isChecked()
        underscore = self.shotUnderscoreInclude.isChecked()
        frameRange = [self.frBegin.value(), self.frEnd.value()]
        selectedItem = self.entityViewer.entityTree.selectedItems()
        if selectedItem:
            selectedItem = selectedItem[0]
            if not selectedItem.dataObject.get("type") == "sequence":
                selectedItem = None

        if not shotNum or frameRange[0] > frameRange[1] or not selectedItem:
            errMsg = "Unknown error"

            if not shotNum:
                errMsg = "Shot number is required"
            elif frameRange[0] > frameRange[1]:
                errMsg = "Frame range end must be greater than frame range beginning"
            elif not selectedItem:
                errMsg = "Please select a valid sequence"

            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message=errMsg, type=AnimatedPopupMessage.ERROR,
                                      parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        shotName = "{0}{1}{2}".format(
            selectedItem.dataObject.get("label").replace("_seq", ""),
            "_" if underscore else "",
            shotNum
        )

        handler = mongorm.getHandler()
        filt = mongorm.getFilter()

        filt.search(handler['entity'], label=shotName, job=self._currentJob.job, parent_uuid=selectedItem.dataObject.getUuid())
        shotObject = handler['entity'].one(filt)
        filt.clear()

        if shotObject:
            errMsg = "Shot with name {}, already exists".format(shotName)

            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message=errMsg, type=AnimatedPopupMessage.ERROR,
                                                       parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        shotObject = handler['entity'].create(
            label=shotName,
            path=cometpublish.util.sequenceShotTargetPath(self._currentJob, shotName),
            job=self._currentJob.job,
            type='shot',
            production=production,
            parent_uuid=selectedItem.dataObject.getUuid(),
            created_by=mgutil.getCurrentUser().getUuid(),
            framerange=frameRange,
            jobpath="{}/{}".format(selectedItem.dataObject.get("jobpath"), shotName)
        )
        shotObject.save()
        cometpublish.build_entity_directory(shotObject)

        self.entityViewer.populate()

    def remove_selection(self):

        handler = mongorm.getHandler()
        flt = mongorm.getFilter()

        entitySelection = self.entityViewer.entityTree.selectedItems()
        entityIsJob = True
        if entitySelection:
            entitySelection = entitySelection[0]
            entityIsJob = entitySelection.dataObject.get("type") == "job"

        if not entitySelection or entityIsJob:
            errMsg = "Unknown error"

            if not entitySelection:
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

        confirmResult = remove_confirm_dialog(entitySelection.dataObject).exec_()

        if confirmResult == QtWidgets.QMessageBox.Apply and cqtutil.doLoginConfirm():
            # Recursive Entities
            allEntities = entitySelection.dataObject.recursive_children()
            allEntities.append_object(entitySelection.dataObject)
            allEntities.sort(sort_field='jobpath')

            allPackages = mongorm.createContainer(handler['package'])
            allVersions = mongorm.createContainer(handler['version'])
            allContent = mongorm.createContainer(handler['content'])
            allDependencies = mongorm.createContainer(handler['dependency'])

            for entity in allEntities:
                flt.search(handler['package'], job=entity.get("job"), parent_uuid=entity.getUuid())
                result = handler['package'].all(flt)
                allPackages.extend(result)
            for package in allPackages:
                allVersions.extend(package.children())
            for version in allVersions:
                allContent.extend(version.children())
                flt.clear()
                flt.search(handler['dependency'], job=version.get("job"), source_version_uuid=version.getUuid())
                allDependencies.extend(handler['dependency'].all(flt))
                flt.clear()
                flt.search(handler['dependency'], job=version.get("job"), link_version_uuid=version.getUuid())
                allDependencies.extend(handler['dependency'].all(flt))

            prunePaths = []

            for objects in [allEntities, allPackages, allVersions, allContent, allDependencies]:
                for obj in objects:
                    if not objects.interfaceName() == "Dependency":
                        prunePaths.append(obj.get("path"))
                    LOGGER.info("Removing database entry: {}".format(obj))
                    obj.delete()

            for path in prunePaths:
                if os.path.exists(path):
                    LOGGER.info("Deleting path: {}".format(path))
                    shutil.rmtree(path)

        self.entityViewer.populate()


class DangerZonePage(QtWidgets.QWidget):
    def __init__(self, parent=None, jobObject=None):
        super(DangerZonePage, self).__init__(parent=parent)
        self._currentJob = jobObject
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.mainLayout)
        self.deleteProjectButton = QtWidgets.QPushButton("DELETE PROJECT")
        self.deleteProjectButton.setStyleSheet("""
                    QPushButton{
                        background: #bf2626;
                        border: none;
                    }
                    QPushButton:hover{
                        border: 1px solid #c9c9c9;
                    }
                    QPushButton:pressed{
                        background: #2e2e2e;
                    }
                """)
        self.deleteProjectButton.setFixedHeight(42)
        self.mainLayout.addWidget(self.deleteProjectButton)
        self.deleteProjectButton.clicked.connect(self.delete_project)

    def delete_project(self):
        confirm_delete = remove_confirm_dialog(self._currentJob).exec_()
        user_confirm = cqtutil.doLoginConfirm()

        all_objects = []
        prune_paths = []

        if confirm_delete and user_confirm:
            handler = mongorm.getHandler()
            filt = mongorm.getFilter()

            filt.search(handler['entity'], job=self._currentJob.job)
            all_objects.extend([x for x in handler['entity'].all(filt)])
            filt.clear()
            filt.search(handler['package'], job=self._currentJob.job)
            all_objects.extend([x for x in handler['package'].all(filt)])
            filt.clear()
            filt.search(handler['version'], job=self._currentJob.job)
            all_objects.extend([x for x in handler['version'].all(filt)])
            filt.clear()
            filt.search(handler['content'], job=self._currentJob.job)
            all_objects.extend([x for x in handler['content'].all(filt)])
            filt.clear()
            filt.search(handler['dependency'], job=self._currentJob.job)
            all_objects.extend([x for x in handler['dependency'].all(filt)])
            filt.clear()

            all_objects.append(self._currentJob)

        for obj in all_objects:
            if not obj._name == "Dependency":
                prune_paths.append(obj.get("path"))
            LOGGER.info("Removing database entry: {}".format(obj))
            obj.delete()

        for path in prune_paths:
            if os.path.exists(path):
                LOGGER.info("Deleting path: {}".format(path))
                shutil.rmtree(path)

        from cometbrowser.browser import ProjectBrowserMain
        dialog = cqtutil.get_top_window(self, ProjectManager)
        dialog.close()
        top_window = cqtutil.get_top_window(dialog, ProjectBrowserMain)
        top_window.close()

        LOGGER.info("Removing user project settings...")
        settings = cqtutil.get_settings()
        settings.beginGroup("project")
        settings.setValue("current_job", "none")
        settings.setValue("current_entity", "none")
        settings.endGroup()

        from cometbrowser.appmain import ProjectBrowserBootstrap
        LOGGER.info("Restarting Comet Browser")
        QtGui.qApp.exit(ProjectBrowserBootstrap.EXIT_CODE_REBOOT)


class ProjectManager(QtWidgets.QDialog):

    def __init__(self, parent=None, jobObject=None):
        super(ProjectManager, self).__init__(parent=parent)
        self._currentJob = jobObject
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)
        self.setup_ui()

    def setup_ui(self):
        if not self._currentJob:
            self.reject()

        self.setWindowTitle("Project Manager: [{}]".format(self._currentJob.get("label")))

        self.settingsButtonGroup = QtWidgets.QButtonGroup()
        self.generalOptionsButton = QtWidgets.QPushButton("General Options")
        self.assetManagerButton = QtWidgets.QPushButton("Asset Manager")
        self.productionManagerButton = QtWidgets.QPushButton("Production Manager")
        self.dangerZoneButton = QtWidgets.QPushButton("Danger Zone")
        self.closeButton = QtWidgets.QPushButton("CLOSE")
        self.closeButton.setMinimumSize(QtCore.QSize(85, 42))
        self.settingsButtonGroup.buttonClicked.connect(self.page_changed)
        self.closeButton.clicked.connect(self.accept)

        self.settingsButtonGroup.addButton(self.generalOptionsButton, id=0)
        self.settingsButtonGroup.addButton(self.assetManagerButton, id=1)
        self.settingsButtonGroup.addButton(self.productionManagerButton, id=2)
        self.settingsButtonGroup.addButton(self.dangerZoneButton, id=3)

        self.mainAreaLayout = QtWidgets.QHBoxLayout()
        self.settingsButtonsWidget = QtWidgets.QWidget()
        self.settingsButtonsLayout = QtWidgets.QVBoxLayout()
        self.bottomLayout = QtWidgets.QHBoxLayout()
        self.bottomLayout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
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
        self.settingsButtonsLayout.addWidget(self.dangerZoneButton)
        self.mainLayout.addLayout(self.bottomLayout)
        self.bottomLayout.addWidget(self.closeButton)
        self.bottomLayout.setContentsMargins(9, 9, 9, 9)

        for button in self.settingsButtonGroup.buttons():
            button.setCheckable(True)
            button.setStyleSheet("""
                QPushButton{
                    border: none;
                    border-radius: none;
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
        self.dangerZonePage = DangerZonePage(parent=self, jobObject=self._currentJob)
        self.pagesStack.addWidget(self.generalOptionsPage)
        self.pagesStack.addWidget(self.assetManagerPage)
        self.pagesStack.addWidget(self.productionManagerPage)
        self.pagesStack.addWidget(self.dangerZonePage)
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
