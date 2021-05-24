from qtpy import QtWidgets, QtGui, QtCore
from cometqt.widgets.ui_entity_viewer import EntityViewer
from cometqt.widgets.ui_animated_popup_message import AnimatedPopupMessage
from cometqt.widgets.ui_user_avatar import AvatarLabel
from cometqt.widgets.ui_delete_dialog import DeleteDialog
from cometpipe.core import CREW_TYPES, DEFAULT_ASSET_TYPES
from cometqt import util as cqtutil
from mongorm import util as mgutil
from pipeicon import icon_paths
import cometpublish
import mongorm
import logging
import shutil
import qdarkstyle
import os


LOGGER = logging.getLogger("Comet.ProjectManager")
logging.basicConfig()
LOGGER.setLevel(logging.INFO)


class UserSearch(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(UserSearch, self).__init__(parent=parent)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
        self.setWindowTitle("Find User")
        self.setMinimumWidth(300)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.userComboBox = QtWidgets.QComboBox(self)
        self.userComboBox.setStyleSheet("padding: 9px;")
        self.applyButton = QtWidgets.QPushButton("Apply")
        self.mainLayout.addWidget(self.userComboBox)
        self.mainLayout.addWidget(self.applyButton, alignment=QtCore.Qt.AlignRight)

        db = mongorm.getHandler()
        flt = mongorm.getFilter()
        flt.search(db['user'])
        users = db['user'].all(flt)

        for usr in users:
            avt = AvatarLabel(size=60, data=QtCore.QByteArray(usr.avatar.read()))
            usr.avatar.seek(0)
            self.userComboBox.addItem(QtGui.QIcon(avt.getRounded()), usr.fullname(), usr)

        self.applyButton.clicked.connect(self.accept)

    def result(self):
        idx = self.userComboBox.currentIndex()
        data = self.userComboBox.itemData(idx)
        return data


class UserItem(QtWidgets.QFrame):
    def __init__(self, userObject=None, parent=None, crewType="", jobObject=None):
        super(UserItem, self).__init__(parent=parent)
        self.crewPage = parent
        self.crewType = crewType
        self.userObject = userObject
        self.jobObejct = jobObject
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(3, 3, 3, 3)
        self.setLayout(self.mainLayout)
        self.userLayout = QtWidgets.QHBoxLayout()
        self.usernameLayout = QtWidgets.QVBoxLayout()
        self.xred = QtWidgets.QPushButton(self)
        self.xred.setFixedSize(26, 26)
        self.xred.setIcon(QtGui.QIcon(icon_paths.ICON_XRED_LRG))
        self.xred.setStyleSheet("""
            QPushButton{
                background: transparent;
                border: none;
            }
        """)
        self.xred.setCursor(QtCore.Qt.PointingHandCursor)
        self.xred.hide()
        self.mainLayout.addLayout(self.userLayout)
        icon = AvatarLabel(size=60, data=QtCore.QByteArray(userObject.avatar.read()))
        userObject.avatar.seek(0)
        name = QtWidgets.QLabel(userObject.fullname())
        name.setStyleSheet("font-weight: bold;")
        username = QtWidgets.QLabel("@{}".format(userObject.get("username")))
        username.setStyleSheet("font: 14px; color: #a6a6a6;")
        self.userLayout.addWidget(icon)
        self.userLayout.addLayout(self.usernameLayout)
        self.usernameLayout.addWidget(name)
        self.usernameLayout.addWidget(username)
        self.userLayout.setContentsMargins(0, 0, 0, 0)
        self.userLayout.setSpacing(0)
        self.setStyleSheet("""
            QFrame{
                border: 2px solid #4e4e4e;
                background: transparent;
                border-radius: 12px;
                font-weight: bold;
                font: 14px;
                padding: 9px;
            }
            QFrame:hover{
                border-color: #6e6e6e;
            }
            QLabel{
                border: none;
                padding: 0px;
                padding-left: 9px;
            }
        """)
        self.setMouseTracking(True)

        self.xred.clicked.connect(self.removeUser)

    def enterEvent(self, event):
        self.xred.show()

        return super(UserItem, self).enterEvent(event)

    def leaveEvent(self, event):
        self.xred.hide()

        return super(UserItem, self).leaveEvent(event)

    def resizeEvent(self, event):
        result = super(UserItem, self).resizeEvent(event)
        self.updateXPos()
        return result

    def updateXPos(self):
        pos = self.rect().topLeft()
        pos.setX(pos.x() + 1)
        pos.setY(pos.y() + 1)

        self.xred.move(pos)

    def removeUser(self):
        self.crewPage.removeUser(self.userObject, self.crewType, self)


class AddUserButton(QtWidgets.QPushButton):
    def __init__(self, jobObject=None, parent=None, crewType=""):
        super(AddUserButton, self).__init__(parent=parent)
        self.crewPage = parent
        self.jobObject = jobObject
        self.crewType = crewType
        self.setStyleSheet("""
            QPushButton{
                border: 2px dashed #4e4e4e;
                background: transparent;
                border-radius: 15px;
            }
            QPushButton:hover{
                border-color: #6e6e6e;
            }
        """)
        self.setFixedSize(84, 84)
        self.setIcon(QtGui.QIcon(icon_paths.ICON_PLUS_LRG))
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.clicked.connect(self.addUser)

    def addUser(self):
        usrSearch = UserSearch(parent=self)
        result = usrSearch.exec_()
        if result == QtWidgets.QDialog.Rejected:
            return None
        else:
            userObject = usrSearch.result()
            if userObject:
                self.crewPage.addUser(userObject, self.crewType)


class GeneralOptionsPage(QtWidgets.QWidget):
    def __init__(self, parent=None, jobObject=None):
        super(GeneralOptionsPage, self).__init__(parent=parent)
        self.parent_main = parent
        self._currentJob = jobObject
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.mainLayout)
        label = QtWidgets.QLabel("General Options")
        label.setStyleSheet("font: 18px; font-weight: bold;")
        self.mainLayout.addWidget(label)

        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollWidget = QtWidgets.QWidget()
        self.scrollArea.setWidget(self.scrollWidget)
        self.formLayout = cqtutil.FormVBoxLayout()
        self.scrollLayout = QtWidgets.QVBoxLayout()
        self.scrollLayout.setAlignment(QtCore.Qt.AlignTop)
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollLayout.addLayout(self.formLayout)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("""
            QScrollArea{
                border-radius: 0px;
                border: none;
            }
            QScrollBar{
                width: 10px;
            }
        """)

        self.mainLayout.addWidget(self.scrollArea)

        # Full Title
        self.projectNameLine = QtWidgets.QLineEdit()
        self.projectNameLine.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[A-Za-z 0-9]{0,100}"), self))
        self.projectNameLine.setMinimumHeight(32)

        # Alias
        self.projectAliasLine = QtWidgets.QLineEdit()
        self.projectAliasLine.setReadOnly(True)
        self.projectAliasLine.setMinimumHeight(32)

        # Resolution
        self.resolutionLayout = QtWidgets.QHBoxLayout()
        self.xResSpin = QtWidgets.QSpinBox()
        self.yResSpin = QtWidgets.QSpinBox()
        self.aspectSpin = QtWidgets.QDoubleSpinBox()
        self.xResSpin.setMinimum(1)
        self.yResSpin.setMinimum(1)
        self.xResSpin.setMaximum(99999)
        self.yResSpin.setMaximum(99999)
        self.xResSpin.setValue(1920)
        self.yResSpin.setValue(1080)
        self.aspectSpin.setMinimum(0.0)
        self.aspectSpin.setMaximum(99999)
        self.aspectSpin.setValue(1.0)
        self.aspectSpin.setSingleStep(0.1)
        self.xResSpin.setSingleStep(100)
        self.yResSpin.setSingleStep(100)
        self.resolutionLayout.addWidget(self.xResSpin)
        self.resolutionLayout.addWidget(self.yResSpin)
        self.resolutionLayout.addWidget(self.aspectSpin)
        self.resolutionLayout.setContentsMargins(0, 0, 0, 0)
        self.xResSpin.setMinimumHeight(32)
        self.yResSpin.setMinimumHeight(32)
        self.aspectSpin.setMinimumHeight(32)

        # Full Title
        self.projectDescription = QtWidgets.QLineEdit()
        self.projectDescription.setMinimumHeight(32)

        # self.colorSpaceFrame = QtWidgets.QFrame()
        # self.colorSpaceLayout = QtWidgets.QHBoxLayout()
        # self.colorSpaceLayout.setContentsMargins(0, 0, 0, 0)
        # self.colorSpaceFrame.setLayout(self.colorSpaceLayout)
        # self.colorSpaceLine = QtWidgets.QLineEdit("")
        # self.colorSpaceLine.setReadOnly(True)
        # self.colorSpaceBrowse = QtWidgets.QPushButton("Browse")
        # self.colorSpaceBrowse.setFixedHeight(42)
        # self.colorSpaceLayout.addWidget(self.colorSpaceLine)
        # self.colorSpaceLayout.addWidget(self.colorSpaceBrowse)
        # self.colorSpaceBrowse.setStyleSheet("""
        #     QPushButton{
        #         color: #6e6e6e;
        #         background: none;
        #         border: 1px solid #6e6e6e;
        #         border-radius: 0px;
        #         font: bold 14px;
        #     }
        #     QPushButton:hover{
        #         color: #9e9e9e;
        #         border: 1px solid #9e9e9e;
        #     }
        #     QPushButton:pressed{
        #         background: #3e3e3e;
        #     }
        # """)
        # self.colorSpaceBrowse.setCursor(QtCore.Qt.PointingHandCursor)
        # self.colorSpaceFrame.setStyleSheet("""
        #     QFrame{
        #         border: none;
        #         background: none;
        #     }
        # """)
        # self.colorSpaceFileDialog = QtWidgets.QFileDialog()
        # # self.colorSpaceBrowse.clicked.connect(self.colorspace_browse)

        self.formLayout.addRow("Title", self.projectNameLine)
        self.formLayout.addRow("Alias", self.projectAliasLine, tip="Project code that will be used for all of production. Must be 3 characters long.")
        self.formLayout.addRow("Resolution", self.resolutionLayout, tip="(X), (Y), (ASPECT RATIO)")
        self.formLayout.addRow("Description", self.projectDescription)
        # self.formLayout.addRow("OCIO CONFIG", self.colorSpaceFrame, tip="The config will be copied and published to the job")

        self.projectNameLine.editingFinished.connect(self.updateGeneral)
        self.projectDescription.editingFinished.connect(self.updateGeneral)
        self.xResSpin.editingFinished.connect(self.updateGeneral)
        self.yResSpin.editingFinished.connect(self.updateGeneral)
        self.aspectSpin.editingFinished.connect(self.updateGeneral)

        self.setValues()

    def setValues(self):
        self.projectNameLine.setText(self._currentJob.fullname)
        self.projectAliasLine.setText(self._currentJob.job)
        self.projectDescription.setText(self._currentJob.description)

        res = self._currentJob.resolution
        self.xResSpin.setValue(res[0])
        self.yResSpin.setValue(res[1])
        self.aspectSpin.setValue(res[2])

    def updateGeneral(self):
        if not self.parent_main.userIsAdmin:

            errMsg = "Unknown error"

            if not self.parent_main.userIsAdmin:
                errMsg = "Insufficient permissions"
            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message=errMsg, type=AnimatedPopupMessage.ERROR,
                                                       parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            self.setValues()
            return False

        fullname = self.projectNameLine.text()
        description = self.projectDescription.text()
        res = [self.xResSpin.value(), self.yResSpin.value(), self.aspectSpin.value()]
        self._currentJob.fullname = fullname
        self._currentJob.description = description
        self._currentJob.resolution = res
        self._currentJob.save()


class EntityManagerPage(QtWidgets.QWidget):
    def __init__(self, parent=None, jobObject=None):
        super(EntityManagerPage, self).__init__(parent=parent)
        self.parent_main = parent
        self._currentJob = jobObject
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)

        self.treeLayout = QtWidgets.QVBoxLayout()

        self.entityViewer = EntityViewer()
        self.entityViewer.setCurrentJob(self._currentJob)
        self.entityViewer.entityTree.setSelectionMode(QtWidgets.QTreeView.SingleSelection)
        self.entityViewer.entityTypesGroup.setExclusive(True)
        self.entityViewer.entityTree.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)
        self.entityViewer.entityTree.selectionModel().setPropagateSelection(False)

        self.sequenceWidget = QtWidgets.QWidget()
        self.assetWidget = QtWidgets.QWidget()
        self.utilWidget = QtWidgets.QWidget()
        self.sequenceLayout = QtWidgets.QVBoxLayout()
        self.assetLayout = QtWidgets.QVBoxLayout()
        self.utilLayout = QtWidgets.QVBoxLayout()
        self.sequenceWidget.setLayout(self.sequenceLayout)
        self.assetWidget.setLayout(self.assetLayout)
        self.utilWidget.setLayout(self.utilLayout)

        for layout in [self.sequenceLayout, self.assetLayout, self.utilLayout]:
            layout.setAlignment(QtCore.Qt.AlignTop)

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setStyleSheet("""
            QTabWidget:pane{
                border-radius: 0px;
            }
        """)

        self.tabWidget.addTab(self.sequenceWidget, "Sequence")
        self.tabWidget.addTab(self.assetWidget, "Asset")
        self.tabWidget.addTab(self.utilWidget, "Util")

        self.tabWidget.currentChanged.connect(self.updateEntityType)

        self.tabEntityTypeMap = {
            self.tabWidget.indexOf(self.sequenceWidget): self.entityViewer.sequenceTypeButton,
            self.tabWidget.indexOf(self.assetWidget): self.entityViewer.assetTypeButton,
            self.tabWidget.indexOf(self.utilWidget): self.entityViewer.utilTypeButton
        }

        self.updateEntityType()

        self.removeSelectionButton = QtWidgets.QPushButton("REMOVE SELECTED ENTITY")
        self.removeSelectionButton.setStyleSheet("""
                    QPushButton{
                        background: #bf2626;
                        border: none;
                    }
                    QPushButton:hover{
                        border: 1px solid #c9c9c9;
                    }
                """)

        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addLayout(self.treeLayout)
        self.treeLayout.addWidget(self.entityViewer)
        self.treeLayout.addWidget(cqtutil.h_line())
        self.treeLayout.addWidget(self.removeSelectionButton)

        self.setup_seq_grp()
        self.setup_asset_grp()
        self.setup_util_grp()

        self.removeSelectionButton.clicked.connect(self.remove_selection)

    def updateEntityType(self):
        for btn in self.entityViewer.entityTypesGroup.buttons():
            btn.setChecked(False)
            btn.setEnabled(False)

        self.tabEntityTypeMap[self.tabWidget.currentIndex()].setChecked(True)
        self.tabEntityTypeMap[self.tabWidget.currentIndex()].setEnabled(True)
        self.entityViewer.setSelectedEntities([])

    def setup_seq_grp(self):
        self.seqSettingsLayout = cqtutil.FormVBoxLayout()
        self.sequenceLayout.addLayout(self.seqSettingsLayout)
        self.sequenceLayout.addWidget(cqtutil.h_line())

        self.seqNameLineEdit = QtWidgets.QLineEdit()
        exp = QtCore.QRegExp("[A-Za-z]{0,3}")
        validator = QtGui.QRegExpValidator(exp, self)
        self.seqNameLineEdit.setValidator(validator)

        self.incrShotsLayout = QtWidgets.QHBoxLayout()
        self.beginRangeSpin = QtWidgets.QSpinBox()
        self.endRangeSpin = QtWidgets.QSpinBox()
        self.incrementSpin = QtWidgets.QSpinBox()
        for spin in [self.beginRangeSpin, self.endRangeSpin, self.incrementSpin]:
            spin.setRange(0, 999999)
            spin.setValue(0)
            spin.valueChanged.connect(self.updateShotList)
        self.incrShotsLayout.addWidget(self.beginRangeSpin)
        self.incrShotsLayout.addWidget(self.endRangeSpin)
        self.incrShotsLayout.addWidget(self.incrementSpin)
        self.incrShotsLayout.setContentsMargins(0, 0, 0, 0)

        self.seqAddButton = QtWidgets.QPushButton("ADD ENTITIES")

        self.seqNameLineEdit.setMinimumHeight(32)

        self.seqSettingsLayout.setContentsMargins(0, 0, 0, 0)

        self.sequenceLabel = QtWidgets.QPushButton("_seq")
        self.sequenceLabel.setIcon(QtGui.QIcon(icon_paths.ICON_SEQUENCE_LRG))
        self.sequenceLabel.setFlat(True)
        self.sequenceLabel.setStyleSheet("""
            QPushButton{
                background: #3e3e3e;
                border: none;
                color: #a6a6a6;
                text-align: left;
            }
        """)

        self.shotListWidget = QtWidgets.QListWidget()
        self.shotListWidget.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)

        self.seqSettingsLayout.addRow("SEQUENCE NAME", self.seqNameLineEdit)
        self.seqSettingsLayout.addRow("SHOTS", self.incrShotsLayout, tip="Begin, End, Increment")
        self.seqSettingsLayout.addRow("", None)
        self.seqSettingsLayout.addRow("RESULTING SEQUENCE", self.sequenceLabel)
        self.seqSettingsLayout.addRow("RESULTING SHOTS", self.shotListWidget)

        self.sequenceLayout.addWidget(self.seqAddButton, alignment=QtCore.Qt.AlignBottom)

        self.seqNameLineEdit.textChanged.connect(
            lambda: self.sequenceLabel.setText("{}_seq".format(self.seqNameLineEdit.text()))
        )
        self.seqNameLineEdit.textChanged.connect(self.updateShotList)
        self.seqNameLineEdit.textEdited.connect(lambda: self.seqNameLineEdit.setText(self.seqNameLineEdit.text().lower()))
        self.seqAddButton.clicked.connect(self.add_sequence)

    def setup_asset_grp(self):
        self._childAssetCache = []
        self.assetSettingsLayout = cqtutil.FormVBoxLayout()
        self.assetLayout.addLayout(self.assetSettingsLayout)
        self.assetLayout.addWidget(cqtutil.h_line())
        self.assetNameLayout = QtWidgets.QHBoxLayout()

        self.assetNameLineEdit = QtWidgets.QLineEdit()
        exp = QtCore.QRegExp(r"[a-z*]+[A-Z]+[\w*]+$")
        validator = QtGui.QRegExpValidator(exp, self)
        self.assetNameLineEdit.setValidator(validator)

        self.childAssetLayout = QtWidgets.QHBoxLayout()
        self.childAssetNameLine = QtWidgets.QLineEdit()
        self.childAssetNameLine.setValidator(validator)
        self.addChildAssetButton = QtWidgets.QPushButton("Add")
        self.childAssetLayout.addWidget(self.childAssetNameLine)
        self.childAssetLayout.addWidget(self.addChildAssetButton)

        self.assetPrefixCombo = QtWidgets.QComboBox()
        self.assetPrefixCombo.setEditable(True)
        self.assetPrefixCombo.addItems(DEFAULT_ASSET_TYPES)
        self.assetNameLayout.addWidget(self.assetPrefixCombo)
        self.assetNameLayout.addWidget(self.assetNameLineEdit)

        self.assetAddButton = QtWidgets.QPushButton("ADD ENTITIES")

        self.assetNameLineEdit.setMinimumHeight(32)
        self.childAssetNameLine.setMinimumHeight(32)
        self.addChildAssetButton.setMinimumHeight(32)

        self.assetSettingsLayout.setContentsMargins(0, 0, 0, 0)

        self.assetLabel = QtWidgets.QPushButton("")
        self.assetLabel.setIcon(QtGui.QIcon(icon_paths.ICON_ASSET_LRG))
        self.assetLabel.setFlat(True)
        self.assetLabel.setStyleSheet("""
            QPushButton{
                background: #3e3e3e;
                border: none;
                color: #a6a6a6;
                text-align: left;
            }
        """)

        self.assetListWidget = QtWidgets.QListWidget()
        self.assetListWidget.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)

        self.assetSettingsLayout.addRow("SEQUENCE NAME", self.assetNameLayout)
        self.assetSettingsLayout.addRow("CHILD ASSET NAME", self.childAssetLayout)
        self.assetSettingsLayout.addRow("", None)
        self.assetSettingsLayout.addRow("RESULTING ASSET", self.assetLabel)
        self.assetSettingsLayout.addRow("RESULTING CHILD ASSETS", self.assetListWidget)

        self.assetLayout.addWidget(self.assetAddButton, alignment=QtCore.Qt.AlignBottom)

        self.assetNameLineEdit.textChanged.connect(
            lambda: self.assetLabel.setText("{}_{}".format(self.assetPrefixCombo.currentText(), self.assetNameLineEdit.text()))
        )
        self.assetPrefixCombo.currentTextChanged.connect(
            lambda: self.assetLabel.setText("{}_{}".format(self.assetPrefixCombo.currentText(), self.assetNameLineEdit.text()))
        )
        self.assetNameLineEdit.textChanged.connect(self.updateAssetList)
        self.assetPrefixCombo.currentTextChanged.connect(self.updateAssetList)
        self.addChildAssetButton.clicked.connect(lambda: self._childAssetCache.append(
            (self.childAssetNameLine.text(), True)) if (self.childAssetNameLine.text() and self.childAssetNameLine.text() not in [x for x, y in self._childAssetCache]) else None)
        self.addChildAssetButton.clicked.connect(self.updateAssetList)
        self.assetAddButton.clicked.connect(self.add_asset)
        self.assetListWidget.itemChanged.connect(self.updateAssetCache)

    def setup_util_grp(self):
        self.utilSettingsLayout = cqtutil.FormVBoxLayout()
        self.utilLayout.addLayout(self.utilSettingsLayout)
        self.utilLayout.addWidget(cqtutil.h_line())

        self.utilNameLineEdit = QtWidgets.QLineEdit()
        exp = QtCore.QRegExp(r"[a-z*]+[A-Z]+[\w*]+$")
        validator = QtGui.QRegExpValidator(exp, self)
        self.utilNameLineEdit.setValidator(validator)

        self.utilAddButton = QtWidgets.QPushButton("ADD ENTITY")

        self.utilNameLineEdit.setMinimumHeight(32)

        self.utilSettingsLayout.setContentsMargins(0, 0, 0, 0)

        self.utilSettingsLayout.addRow("UTIL NAME", self.utilNameLineEdit)

        self.utilLayout.addWidget(self.utilAddButton, alignment=QtCore.Qt.AlignBottom)

        self.utilAddButton.clicked.connect(self.add_util)

    def add_sequence(self):
        seqName = self.seqNameLineEdit.text()

        if not seqName or not len(seqName) == 3 or seqName == self._currentJob.job or not self.parent_main.userIsAdmin:

            errMsg = "Unknown error"

            if not seqName:
                errMsg = "Sequence name is required"
            elif not len(seqName) == 3:
                errMsg = "Sequence name must be 3 characters"
            elif seqName == self._currentJob.job:
                errMsg = "Sequence name cannot be same as job name"
            elif not self.parent_main.userIsAdmin:
                errMsg = "Insufficient permissions"
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

        filt.search(handler['entity'], type='sequence', label=self.sequenceLabel.text(), job=self._currentJob.job)
        sequenceObject = handler['entity'].one(filt)
        filt.clear()

        filt.search(handler['entity'], type='util', label='root', job=self._currentJob.job)
        rootEntityObject = handler['entity'].one(filt)
        filt.clear()

        # If the sequence does not already exist, create it
        if not sequenceObject:
            seqLabel = self.sequenceLabel.text()
            sequenceObject = handler['entity'].create(
                label=seqLabel,
                job=self._currentJob.job,
                type='sequence',
                created_by=mgutil.getCurrentUser().getUuid(),
                parent_uuid=rootEntityObject.getUuid()
            )
            sequenceObject.save()
            cometpublish.build_entity_directory(sequenceObject)

        # Create Shots
        for s in range(self.shotListWidget.count()):
            shotItem = self.shotListWidget.item(s)
            if not shotItem.checkState() == QtCore.Qt.Checked:
                continue

            shotName = shotItem.text()

            filt.search(handler['entity'], type='shot', label=shotName, job=self._currentJob.job, parent_uuid=sequenceObject.getUuid())
            shotObject = handler['entity'].one(filt)
            filt.clear()

            if not shotObject:
                shotObject = handler['entity'].create(
                    label=shotName,
                    job=self._currentJob.job,
                    type='shot',
                    parent_uuid=sequenceObject.getUuid(),
                    created_by=mgutil.getCurrentUser().getUuid(),
                )
                shotObject.save()
                cometpublish.build_entity_directory(shotObject)

        self.entityViewer.populate()

    def add_asset(self):
        assetName = self.assetNameLineEdit.text()
        prefixCombo = self.assetPrefixCombo.currentText()

        if not assetName or not prefixCombo or not self.parent_main.userIsAdmin:

            errMsg = "Unknown error"

            if not assetName:
                errMsg = "Asset name is required"
            elif not prefixCombo:
                errMsg = "Asset prefix is required"
            elif not self.parent_main.userIsAdmin:
                errMsg = "Insufficient permissions"
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

        filt.search(handler['entity'], type='asset', label=self.assetLabel.text(), job=self._currentJob.job)
        assetObject = handler['entity'].one(filt)
        filt.clear()

        filt.search(handler['entity'], type='util', label='root', job=self._currentJob.job)
        rootEntityObject = handler['entity'].one(filt)
        filt.clear()

        # If the sequence does not already exist, create it
        if not assetObject:
            assetLabel = self.assetLabel.text()
            assetObject = handler['entity'].create(
                label=assetLabel,
                job=self._currentJob.job,
                type='asset',
                created_by=mgutil.getCurrentUser().getUuid(),
                parent_uuid=rootEntityObject.getUuid()
            )
            assetObject.save()
            cometpublish.build_entity_directory(assetObject)

        # Create Child Assets
        for c in range(self.assetListWidget.count()):
            childAssetItem = self.assetListWidget.item(c)
            if not childAssetItem.checkState() == QtCore.Qt.Checked:
                continue

            childAssetName = childAssetItem.text()

            filt.search(handler['entity'], type='asset', label=childAssetName, job=self._currentJob.job,
                        parent_uuid=assetObject.getUuid())
            childAssetObject = handler['entity'].one(filt)
            filt.clear()

            if not childAssetObject:
                childAssetObject = handler['entity'].create(
                    label=childAssetName,
                    job=self._currentJob.job,
                    type='asset',
                    parent_uuid=assetObject.getUuid(),
                    created_by=mgutil.getCurrentUser().getUuid(),
                )
                childAssetObject.save()
                cometpublish.build_entity_directory(childAssetObject)

        self.entityViewer.populate()

    def add_util(self):
        utilName = self.utilNameLineEdit.text()

        if not utilName or not self.parent_main.userIsAdmin:

            errMsg = "Unknown error"

            if not utilName:
                errMsg = "Util name is required"
            elif not self.parent_main.userIsAdmin:
                errMsg = "Insufficient permissions"
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

        filt.search(handler['entity'], type='util', label=utilName, job=self._currentJob.job)
        utilObject = handler['entity'].one(filt)
        filt.clear()

        filt.search(handler['entity'], type='util', label='root', job=self._currentJob.job)
        rootEntityObject = handler['entity'].one(filt)
        filt.clear()

        # If the util does not already exist, create it
        if not utilObject:
            utilObject = handler['entity'].create(
                label=utilName,
                job=self._currentJob.job,
                type='util',
                created_by=mgutil.getCurrentUser().getUuid(),
                parent_uuid=rootEntityObject.getUuid()
            )
            utilObject.save()
            cometpublish.build_entity_directory(utilObject)

        self.entityViewer.populate()

    def updateShotList(self):
        self.shotListWidget.clear()
        if not self.seqNameLineEdit.text() or not len(self.seqNameLineEdit.text()) == 3:
            return
        shot_range = [self.beginRangeSpin.value(), self.endRangeSpin.value(), self.incrementSpin.value()]
        if all(shot_range):
            for i in range(shot_range[0], shot_range[1] + 1, shot_range[2]):
                shotNum = str(i).zfill(3)
                shotName = "{}{}".format(self.sequenceLabel.text().replace("_seq", ""), shotNum)
                item = QtWidgets.QListWidgetItem()
                item.setText(shotName)
                item.setIcon(QtGui.QIcon(icon_paths.ICON_SHOT_LRG))
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Checked)
                self.shotListWidget.addItem(item)

    def updateAssetList(self):

        self.assetListWidget.clear()

        if not self.assetNameLineEdit.text() or not self.assetPrefixCombo.currentText():
            return

        parentAssetName = self.assetLabel.text()

        for childAssetName, checked in self._childAssetCache:
            assetName = "{}_{}".format(parentAssetName, childAssetName)
            if not assetName in [self.assetListWidget.item(x).text() for x in range(self.assetListWidget.count())]:
                item = QtWidgets.QListWidgetItem()
                item.setText("{}_{}".format(parentAssetName, childAssetName))
                item.setIcon(QtGui.QIcon(icon_paths.ICON_ASSET_LRG))
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
                self.assetListWidget.addItem(item)

    def updateAssetCache(self):
        self._childAssetCache = []

        for c in range(self.assetListWidget.count()):
            item = self.assetListWidget.item(c)
            assetName = item.text().split("_")[-1]
            self._childAssetCache.append((assetName, True if item.checkState() == QtCore.Qt.Checked else False))

    def remove_selection(self):

        handler = mongorm.getHandler()
        flt = mongorm.getFilter()

        del_items = set()

        entitySelection = self.entityViewer.entityTree.selectedItems()

        if not entitySelection or not self.parent_main.userIsAdmin:
            errMsg = "Unknown error"

            if not entitySelection:
                errMsg = "Please make a selection in the tree"
            elif not self.parent_main.userIsAdmin:
                errMsg = "Insufficient permissions"
            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message=errMsg, type=AnimatedPopupMessage.ERROR,
                                                       parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        for item in entitySelection:
            if not (item.dataObject.get("type") == "util" and item.dataObject.get("label") == "root"):
                del_items.add(item)

        if cqtutil.doLoginConfirm():
            deleteDialog = DeleteDialog(parent=self, dataObjects=[x.dataObject for x in del_items])
            deleteDialog.exec_()

        self.entityViewer.populate()


class DangerZonePage(QtWidgets.QWidget):
    def __init__(self, parent=None, jobObject=None):
        super(DangerZonePage, self).__init__(parent=parent)
        self.parent_main = parent
        self._currentJob = jobObject
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.mainLayout)
        self.deleteProjectButton = QtWidgets.QPushButton("DELETE PROJECT")
        self.deleteProjectButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.deleteProjectButton.setStyleSheet("""
                    QPushButton{
                        background: transparent;
                        border: 1px solid red;
                        border-radius: 0px;
                        color: red;
                    }
                    QPushButton:hover{
                        border: 1px solid #a6a6a6;
                        color: #a6a6a6;
                    }
                    QPushButton:pressed{
                        background: #2e2e2e;
                    }
                """)
        self.deleteProjectButton.setFixedHeight(42)
        self.mainLayout.addWidget(self.deleteProjectButton)
        self.deleteProjectButton.clicked.connect(self.delete_project)

    def delete_project(self):

        if not mgutil.user_in_crewType(mgutil.getCurrentUser(), self._currentJob, "Creator"):

            errMsg = "Insufficient permissions"

            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message=errMsg, type=AnimatedPopupMessage.ERROR,
                                                       parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        if cqtutil.doLoginConfirm():
            deleteDialog = DeleteDialog(parent=self, dataObjects=[self._currentJob])
            deleteDialog.exec_()
        else:
            return

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


class CrewManagerPage(QtWidgets.QWidget):
    def __init__(self, parent=None, jobObject=None):
        super(CrewManagerPage, self).__init__(parent=parent)
        self.parent_main = parent
        self._currentJob = jobObject
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.mainLayout)
        label = QtWidgets.QLabel("Crew Manager")
        label.setStyleSheet("font: 18px; font-weight: bold;")
        self.mainLayout.addWidget(label)
        self.crewTypes = CREW_TYPES

        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollWidget = QtWidgets.QWidget()
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollLayout = QtWidgets.QVBoxLayout()
        self.scrollLayout.setAlignment(QtCore.Qt.AlignTop)
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("""
            QScrollArea{
                border-radius: 0px;
                border: none;
            }
            QScrollBar{
                width: 10px;
            }
        """)

        self.mainLayout.addWidget(self.scrollArea)

        self._layoutCache = {}
        db = mongorm.getHandler()

        for crewType in self.crewTypes:
            label = QtWidgets.QLabel(crewType)
            label.setStyleSheet("font: 12px; font-weight: bold; color: #6e6e6e")
            self.scrollLayout.addWidget(label)
            crewWidget = QtWidgets.QWidget()
            crewLayout = cqtutil.FlowLayout()
            crewWidget.setLayout(crewLayout)
            self.scrollLayout.addWidget(crewWidget)

            self._layoutCache[crewType] = crewLayout

            crewMemebers = db['user'].get(self._currentJob.crew[crewType])

            if crewMemebers:
                for member in crewMemebers:
                    userButton = UserItem(userObject=member, parent=self, crewType=crewType, jobObject=self._currentJob)
                    if crewType == "Creator":
                        userButton.xred.setDisabled(True)
                    crewLayout.addWidget(userButton)

            if crewType is not "Creator":
                addNewWidget = AddUserButton(jobObject=self._currentJob, parent=self, crewType=crewType)
                crewLayout.addWidget(addNewWidget)

    def addUser(self, userObject, crewType):
        if not self._layoutCache[crewType]:
            raise RuntimeError("No Layout found for crew type: {}".format(crewType))

        if not userObject:
            raise RuntimeError("Tried to add a None object to {}".format(crewType))

        if not self.parent_main.userIsAdmin:
            errMsg = "Unknown error"

            if not self.parent_main.userIsAdmin:
                errMsg = "Insufficient permissions"
            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message=errMsg, type=AnimatedPopupMessage.ERROR,
                                                       parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        layout = self._layoutCache[crewType]
        existingUsrWidgets = [x.widget() for x in layout.itemList if isinstance(x.widget(), UserItem)]
        existingUsrUuids = [x.userObject.getUuid() for x in existingUsrWidgets]

        if userObject.getUuid() in existingUsrUuids:
            return False

        jobCrew = self._currentJob.crew_dict()
        crewMem = jobCrew[crewType]
        if userObject.getUuid() not in crewMem:
            crewMem.append(userObject.getUuid())
        jobCrew[crewType] = crewMem
        self._currentJob.crew = jobCrew
        self._currentJob.save()

        userButton = UserItem(userObject=userObject, parent=self, crewType=crewType, jobObject=self._currentJob)
        layout.insertWidget(layout.count() - 2, userButton)

    def removeUser(self, userObject, crewType, userItem):
        if not self._layoutCache[crewType]:
            raise RuntimeError("No Layout found for crew type: {}".format(crewType))

        if not userObject:
            raise RuntimeError("Tried to remove a None object to {}".format(crewType))

        userIsInvincible = False
        if mgutil.user_in_crewType(userObject, self._currentJob, "Creator"):
            userIsInvincible = True

        if not self.parent_main.userIsAdmin or (userIsInvincible and (not mgutil.getCurrentUser() == userObject or crewType == "Admins")):
            errMsg = "Unknown error"

            if not self.parent_main.userIsAdmin:
                errMsg = "Insufficient permissions"
            elif userIsInvincible and (not mgutil.getCurrentUser() == userObject or crewType == "Admins"):
                errMsg = "You cannot remove a creator from this crew type"
            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message=errMsg, type=AnimatedPopupMessage.ERROR,
                                                       parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        areYouSure = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Remove {} From {}".format(userObject.fullname(), crewType),
                                           "Are You Sure You Want To Remove {} From {}".format(userObject.fullname(), crewType),
                                           QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No).exec_()

        if areYouSure == QtWidgets.QMessageBox.No:
            return False

        jobCrew = self._currentJob.crew_dict()
        crewMem = jobCrew[crewType]
        if userObject.getUuid() in crewMem:
            crewMem.remove(userObject.getUuid())
        jobCrew[crewType] = crewMem
        self._currentJob.crew = jobCrew
        self._currentJob.save()

        userItem.deleteLater()
        del userItem


class ProjectManager(QtWidgets.QDialog):

    @property
    def userIsAdmin(self):
        return mgutil.is_user_admin(mgutil.getCurrentUser(), self._currentJob)

    def __init__(self, parent=None, jobObject=None):
        super(ProjectManager, self).__init__(parent=parent)
        self._currentJob = jobObject
        if not self._currentJob:
            self.reject()
            return
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)
        self.setup_ui()

    def setup_ui(self):

        self.setWindowTitle("Project Manager: [{}]".format(self._currentJob.get("label")))

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollWidget = QtWidgets.QWidget()
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMaximumWidth(300)
        self.settingsLayout = QtWidgets.QVBoxLayout()
        self.scrollWidget.setLayout(self.settingsLayout)
        self.settingsLayout.setAlignment(QtCore.Qt.AlignTop)

        self.settingsButtonGroup = QtWidgets.QButtonGroup()
        self.generalOptionsButton = QtWidgets.QPushButton("General Options")
        self.entityManagerButton = QtWidgets.QPushButton("Entity Manager")
        self.dangerZoneButton = QtWidgets.QPushButton("Danger Zone")

        self.crewManagerButton = QtWidgets.QPushButton("Crew Manager")

        self.closeButton = QtWidgets.QPushButton("CLOSE")
        self.closeButton.setMinimumSize(QtCore.QSize(85, 42))
        self.closeButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.settingsButtonGroup.buttonClicked.connect(self.page_changed)
        self.closeButton.clicked.connect(self.accept)

        self.settingsButtonGroup.addButton(self.generalOptionsButton, id=0)
        self.settingsButtonGroup.addButton(self.entityManagerButton, id=1)
        self.settingsButtonGroup.addButton(self.dangerZoneButton, id=2)
        self.settingsButtonGroup.addButton(self.crewManagerButton, id=3)

        self.mainAreaLayout = QtWidgets.QHBoxLayout()
        self.bottomLayout = QtWidgets.QHBoxLayout()
        self.bottomLayout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        self.mainLayout.addLayout(self.mainAreaLayout)
        self.mainAreaLayout.addWidget(self.scrollArea)
        self.settingsLayout.addWidget(self.generalOptionsButton)
        self.settingsLayout.addWidget(self.entityManagerButton)
        self.settingsLayout.addWidget(self.dangerZoneButton)
        self.settingsLayout.addWidget(cqtutil.h_line())
        self.settingsLayout.addWidget(self.crewManagerButton)
        self.bottomLayout.addWidget(self.closeButton)
        self.bottomLayout.setContentsMargins(9, 9, 9, 9)

        self.scrollArea.setStyleSheet("""
            QScrollArea{
                border-radius: 0px;
                border: none;
            }
            QScrollBar{
                width: 10px;
            }
            QLabel{
                color: #5e5e5e;
                font: bold;
            }
        """)
        self.scrollWidget.setStyleSheet("QWidget{background: #2f2f2f;}")
        for button in self.settingsButtonGroup.buttons():
            button.setCheckable(True)
            button.setStyleSheet("""
                QPushButton{
                    text-align: left;
                    border: none;
                    border-radius: 5px;
                    border-bottom-left-radius: 0px;
                    border-top-left-radius: 0px;
                    background: transparent;
                    padding: 9px;
                    font-size: 13px;
                }
                QPushButton:!checked:hover{
                    background: #333333;
                }
                QPushButton:checked{
                    background: #3e3e3e;
                    border-left: 4px solid #148CD2;
                }
            """)
            button.setCursor(QtCore.Qt.PointingHandCursor)

        self.settingsButtonGroup.button(0).setChecked(True)

        self.workingAreaLayout = QtWidgets.QVBoxLayout()
        self.workingAreaLayout.setContentsMargins(9, 9, 9, 9)

        self.pagesStack = QtWidgets.QStackedWidget()
        self.generalOptionsPage = GeneralOptionsPage(parent=self, jobObject=self._currentJob)
        self.entityManagerPage = EntityManagerPage(parent=self, jobObject=self._currentJob)
        self.dangerZonePage = DangerZonePage(parent=self, jobObject=self._currentJob)
        self.crewManagerPage = CrewManagerPage(parent=self, jobObject=self._currentJob)
        self.pagesStack.addWidget(self.generalOptionsPage)
        self.pagesStack.addWidget(self.entityManagerPage)
        self.pagesStack.addWidget(self.dangerZonePage)
        self.pagesStack.addWidget(self.crewManagerPage)
        self.mainAreaLayout.addLayout(self.workingAreaLayout)
        self.workingAreaLayout.addWidget(self.pagesStack)
        self.workingAreaLayout.addWidget(cqtutil.h_line())
        self.workingAreaLayout.addLayout(self.bottomLayout)

    def page_changed(self):
        current_idx = self.settingsButtonGroup.id(self.settingsButtonGroup.checkedButton())
        self.pagesStack.setCurrentIndex(current_idx)


if __name__ == '__main__':
    import sys

    h = mongorm.getHandler()
    f = mongorm.getFilter()
    f.search(h['job'], label='dlr')
    job = h['job'].one(f)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win = ProjectManager(jobObject=job)
    win.resize(900, 700)
    win.show()
    sys.exit(app.exec_())
