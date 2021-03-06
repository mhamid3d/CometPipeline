from qtpy import QtWidgets, QtGui, QtCore
from cometqt.widgets.ui_entity_combobox import EntityComboBox
from cometqt import util as cqtutil
from cometpublish import package_util
from pipeicon import icon_paths
from collections import OrderedDict, defaultdict
from mongorm import util as mgutil
import mongorm
import cometpublish
import os


class VersionComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super(VersionComboBox, self).__init__(parent=parent)
        self.parent = parent
        self._versionsContainer = None
        self.populate_versions()

    @property
    def versionsContainer(self):
        return self._versionsContainer

    def populate_versions(self):
        self.blockSignals(True)
        self.clear()
        self._versionsContainer = None
        self.addItem(QtGui.QIcon(icon_paths.ICON_VERSION_LRG), "v [NEXT]")
        existingPackage = self.parent.existingPackageCombo.getSelectedPackage()

        if existingPackage:
            self._versionsContainer = existingPackage.children()
            if self._versionsContainer:
                self._versionsContainer.sort(sort_field="version", reverse=True)
            for version in self._versionsContainer:
                self.addItem(QtGui.QIcon(icon_paths.ICON_VERSION_LRG), "v {}".format(str(version.get("version"))))

            self.setCurrentIndex(0)

        self.blockSignals(False)
        return

    def getSelectedVersion(self):
        if not self.parent.existingPackageCombo.getSelectedPackage() or not self._versionsContainer:
            return 1
        elif self.currentIndex() == 0:
            return self._versionsContainer[0].get("version") + 1
        else:
            return self._versionsContainer[self.currentIndex() - 1].get("version")


class PackageComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super(PackageComboBox, self).__init__()
        self.parent = parent
        self.handler = mongorm.getHandler()
        self.filter = mongorm.getFilter()
        self._packageContainer = None
        self.updateList()

    @property
    def packageContainer(self):
        return self._packageContainer

    def getSelectedPackage(self):
        if self.currentText() == "":
            return None

        return self._packageContainer[self.currentIndex()]

    def updateList(self):
        self.blockSignals(True)
        self.clear()
        self._packageContainer = None

        job = self.parent.entityComboBox.getSelectedJob()
        entity = self.parent.entityComboBox.getSelectedEntity()
        type = self.parent.packageType[0]

        if not job or not entity:
            return

        self.filter.search(self.handler['package'], job=job.label, type=type, parent_uuid=entity.getUuid())
        self._packageContainer = self.handler['package'].all(self.filter)
        self.filter.clear()
        for package in self._packageContainer:
            self.addItem(QtGui.QIcon(icon_paths.ICON_PACKAGE_LRG), package.get("label"))

        self.addItem("")
        self.model().item(self.count() - 1).setEnabled(False)
        self.blockSignals(False)
        self.setCurrentText("")


class VersionPublisher(QtWidgets.QDialog):

    def __init__(self, parent=None, validationDialog=None, postProcess=None):
        super(VersionPublisher, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.mainLayout)
        self._nameFieldWidgetMap = {}
        self._nameFieldData = OrderedDict()
        for nameField in package_util.getNameFieldsDict():
            self._nameFieldData[nameField] = ""
        self.setup_ui()
        self._validation_dialog = None
        self._post_process = None
        self.publishButton.setDisabled(True)
        self.validationDialog = validationDialog
        self.postProcess = postProcess
        self.resize(500, 800)

    @property
    def packageType(self):
        currentIdx = self.packageTypeComboBox.currentIndex()
        return list(package_util.getPackageTypesDict().items())[currentIdx]

    @property
    def packageTypeNameFields(self):
        pkgType = self.packageType
        requiredFields = []
        optionalFields = []
        dict = {}
        if 'required' in pkgType[1]:
            requiredFields = pkgType[1]['required']
        if 'optional' in pkgType[1]:
            optionalFields = pkgType[1]['optional']
        for field in requiredFields:
            data = package_util.getNameFieldsDict()[field]
            data['required'] = True
            dict[field] = data
        for field in optionalFields:
            data = package_util.getNameFieldsDict()[field]
            data['required'] = False
            dict[field] = data

        orderedDict = OrderedDict()
        for field in package_util.getNameFieldsDict().keys():
            if field in dict:
                orderedDict[field] = dict[field]

        return orderedDict

    @property
    def packagePublishName(self):
        packageType = self.packageType[0] or "[packageType]"
        entity = self.entityComboBox.getSelectedEntity().get("label") if self.entityComboBox.getSelectedEntity() else "[entity]"

        labelStr = "_".join([packageType, entity])

        for nameField, nameFieldData in self.packageTypeNameFields.items():
            if not self._nameFieldData[nameField] and not nameFieldData['required']:
                continue
            value = self._nameFieldData[nameField] or "[{}]".format(nameField)
            labelStr = "_".join([labelStr, value])

        return labelStr

    @property
    def versionPublishName(self):
        version = "v{}".format(str(self.versionComboBox.getSelectedVersion())) or "[version]"
        return "_".join([self.packagePublishName, version])

    @property
    def postProcess(self):
        return self._post_process

    @postProcess.setter
    def postProcess(self, func):
        assert callable(func), "Post Process must be a callable function"
        self._post_process = func
        self.publishButton.setEnabled(True)

    @property
    def validationDialog(self):
        return self._validation_dialog

    @validationDialog.setter
    def validationDialog(self, diag):
        assert issubclass(diag, ValidationDialog), "Validation Dialog must be instance of Validation Dialog Class"
        self._validation_dialog = diag

    def setup_ui(self):
        self.versionLabelGroupBox = QtWidgets.QGroupBox("Version Name")
        self.versionLabelGroupLayout = QtWidgets.QHBoxLayout()
        self.versionLabelGroupBox.setLayout(self.versionLabelGroupLayout)
        self.versionLabelGroupLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.versionLabel = QtWidgets.QLabel()
        self.versionLabelGroupLayout.addWidget(self.versionLabel)

        self.contextGroupBox = QtWidgets.QGroupBox("Context")
        self.contextGroupLayout = cqtutil.FormVBoxLayout()
        self.contextGroupBox.setLayout(self.contextGroupLayout)
        self.versionParamsGroupBox = QtWidgets.QGroupBox("Version Parameters")
        self.versionParamsLayout = cqtutil.FormVBoxLayout()
        self.versionParamsGroupBox.setLayout(self.versionParamsLayout)

        self.entityComboBox = EntityComboBox(parent=self)
        self.entityComboBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                          QtWidgets.QSizePolicy.Minimum)
        self.packageTypeComboBox = QtWidgets.QComboBox()
        for packageTypeName, packageTypeData in package_util.getPackageTypesDict().items():
            packageTypeDesc = packageTypeData['desc']
            self.packageTypeComboBox.addItem(QtGui.QIcon(icon_paths.ICON_PACKAGE_LRG),
                                             "{} - {}".format(packageTypeName, packageTypeDesc))
        self.packageTypeComboBox.setSizePolicy(self.entityComboBox.sizePolicy())

        self.existingPackageCombo = PackageComboBox(parent=self)
        self.existingPackageCombo.setSizePolicy(self.entityComboBox.sizePolicy())

        self.nameFieldsGroupBox = QtWidgets.QGroupBox("")
        self.nameFieldsGroupLayout = QtWidgets.QFormLayout()
        self.nameFieldsGroupBox.setLayout(self.nameFieldsGroupLayout)
        self.nameFieldsGroupBox.setStyleSheet("""
            QGroupBox{
                margin-top: 0px;
            }
        """)
        self.nameFieldsGroupBox.setSizePolicy(self.entityComboBox.sizePolicy())

        self.versionComboBox = VersionComboBox(parent=self)
        self.versionComboBox.setSizePolicy(self.entityComboBox.sizePolicy())

        self.autoStatusComboBox = QtWidgets.QComboBox()
        self.autoStatusComboBox.addItem(QtGui.QIcon(icon_paths.ICON_INPROGRESS_LRG), "Pending")
        self.autoStatusComboBox.addItem(QtGui.QIcon(icon_paths.ICON_CHECKGREEN_LRG), "Approved")
        self.autoStatusComboBox.addItem(QtGui.QIcon(icon_paths.ICON_XRED_LRG), "Declined")
        self.autoStatusComboBox.setSizePolicy(self.entityComboBox.sizePolicy())

        self.commentLineEdit = QtWidgets.QLineEdit()
        self.commentLineEdit.setMinimumHeight(32)
        self.commentLineEdit.setSizePolicy(self.entityComboBox.sizePolicy())

        self.contextGroupLayout.addRow("JOB AND ENTITY", self.entityComboBox)
        self.contextGroupLayout.addRow("PACKAGE TYPE", self.packageTypeComboBox)
        self.contextGroupLayout.addRow("EXISTING PACKAGE", self.existingPackageCombo)
        self.contextGroupLayout.addRow("NAME FIELDS", self.nameFieldsGroupBox)
        self.contextGroupLayout.addRow("VERSION", self.versionComboBox)

        self.versionParamsLayout.addRow("AUTO STATUS", self.autoStatusComboBox)
        self.versionParamsLayout.addRow("COMMENT", self.commentLineEdit)

        self.mainLayout.addWidget(self.versionLabelGroupBox)
        self.mainLayout.addWidget(self.contextGroupBox)
        self.mainLayout.addWidget(self.versionParamsGroupBox)

        bottomLayout = QtWidgets.QHBoxLayout()
        bottomLayout.setAlignment(QtCore.Qt.AlignRight)

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addItem(spacer)
        self.mainLayout.addLayout(bottomLayout)

        closeButton = QtWidgets.QPushButton("CLOSE")
        self.publishButton = QtWidgets.QPushButton("PUBLISH")

        closeButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.publishButton.setCursor(QtCore.Qt.PointingHandCursor)
        closeButton.setIcon(QtGui.QIcon(icon_paths.ICON_XRED_LRG))
        self.publishButton.setIcon(QtGui.QIcon(icon_paths.ICON_VERSION_LRG))
        closeButton.setFixedSize(84, 42)
        self.publishButton.setFixedSize(84, 42)

        self.publishButton.setStyleSheet("""
            QPushButton{
                color: #148CD2;
            }
        """)

        bottomLayout.addWidget(closeButton)
        bottomLayout.addWidget(self.publishButton)

        closeButton.clicked.connect(self.close)
        self.publishButton.clicked.connect(self.doPublish)

        self.entityComboBox.entityChanged.connect(self.handleEntity)
        self.packageTypeComboBox.currentIndexChanged.connect(self.handlePackageType)
        self.existingPackageCombo.currentIndexChanged.connect(self.handleExistingPackage)
        self.versionComboBox.currentIndexChanged.connect(self.updateLabel)

        self.handlePackageType()

    def setCurrentType(self, currentType):
        packageTypeNames = [x[0] for x in package_util.getPackageTypesDict().items()]
        try:
            self.packageTypeComboBox.setCurrentIndex(packageTypeNames.index(currentType))
            return True
        except ValueError:
            return False

    def setFixedType(self, fixedType):
        self.packageTypeComboBox.setDisabled(fixedType)

    def getValueByWidget(self, widget):
        if isinstance(widget, QtWidgets.QComboBox):
            return widget.currentText()
        elif isinstance(widget, QtWidgets.QLineEdit):
            return widget.text()

    def setValueByWidget(self, widget, value):
        if isinstance(widget, QtWidgets.QComboBox):
            return widget.setCurrentText(value)
        elif isinstance(widget, QtWidgets.QLineEdit):
            return widget.setText(value)

    def updateNameFields(self):

        self._nameFieldWidgetMap = {}

        # Get existing widgets and delete them
        widgetsToDelete = []
        for c in range(self.nameFieldsGroupLayout.rowCount()):
            for role in [QtWidgets.QFormLayout.FieldRole, QtWidgets.QFormLayout.LabelRole]:
                widget = self.nameFieldsGroupLayout.itemAt(c, role)
                if widget and widget.widget() and not isinstance(widget.widget(), QtWidgets.QWidgetItem):
                    widgetsToDelete.append(widget.widget())

        for delWidget in widgetsToDelete:
            delWidget.deleteLater()

        # Add the name fields to the data dictionary and add the widgets
        for nameField, nfData in self.packageTypeNameFields.items():
            widgetStr = nfData['widget']
            widget = getattr(QtWidgets, widgetStr)(parent=self)
            widget.setFixedHeight(32)
            if 'editable' in nfData:
                widget.setEditable(nfData['editable'])
            if 'options' in nfData:
                widget.addItems(sorted(nfData['options']))

            self._nameFieldWidgetMap[nameField] = widget

            if isinstance(widget, QtWidgets.QComboBox):
                widget.currentTextChanged.connect(self.nameFieldEdit)
            elif isinstance(widget, QtWidgets.QLineEdit):
                widget.textChanged.connect(self.nameFieldEdit)

            if self._nameFieldData[nameField]:
                widget.blockSignals(True)
                self.setValueByWidget(widget, self._nameFieldData[nameField])
                widget.blockSignals(False)
            else:
                self._nameFieldData[nameField] = self.getValueByWidget(widget)

            self.nameFieldsGroupLayout.addRow("{}: ".format(str(nameField)), widget)

    def handleEntity(self):
        self.existingPackageCombo.updateList()
        self.checkForExisting()
        self.updateLabel()

    def handlePackageType(self):
        self.existingPackageCombo.updateList()
        self.updateNameFields()
        self.checkForExisting()
        self.updateLabel()

    def handleExistingPackage(self):
        selectedPackage = self.existingPackageCombo.getSelectedPackage()
        if not selectedPackage:
            return

        labelMap = selectedPackage.get("labelmap")
        for nameField in self.packageTypeNameFields:
            widget = self._nameFieldWidgetMap[nameField]
            value = labelMap[nameField] if nameField in labelMap else ""
            widget.blockSignals(True)
            self.setValueByWidget(widget, value)
            widget.blockSignals(False)

        self.nameFieldEdit()

    def nameFieldEdit(self):
        for nameField in self.packageTypeNameFields:
            widget = self._nameFieldWidgetMap[nameField]
            self._nameFieldData[str(nameField)] = self.getValueByWidget(widget)

        self.checkForExisting()
        self.updateLabel()

    def getPublishLabelMap(self):
        dict = {}
        for nameField in self.packageTypeNameFields:
            value = self._nameFieldData[nameField]
            if value:
                dict[nameField] = self._nameFieldData[nameField]

        return dict

    def checkForExisting(self):
        if self.existingPackageCombo.packageContainer:
            for idx, x in enumerate(self.existingPackageCombo.packageContainer):
                if x.get("labelmap") == self.getPublishLabelMap():
                    self.existingPackageCombo.blockSignals(True)
                    self.existingPackageCombo.setCurrentIndex(idx)
                    self.existingPackageCombo.blockSignals(False)
                    self.versionComboBox.populate_versions()
                    return True

        self.existingPackageCombo.setCurrentText("")
        self.versionComboBox.populate_versions()
        return False

    def updateLabel(self):
        self.versionLabel.setText(self.versionPublishName)

    def doPublish(self):
        validationDialog = self.validationDialog(parent=self)
        validationDialog.exec_()

        if not validationDialog.isValid():
            return

        # UI form validation
        missingRequiredFields = []
        for nameField, nameFieldData in self.packageTypeNameFields.items():
            required = nameFieldData['required']
            if not self._nameFieldData[nameField] and required:
                missingRequiredFields.append(nameField)

        if missingRequiredFields:
            raise RuntimeError("Missing required fields: {}".format(", ".join(missingRequiredFields)))
        if not self.commentLineEdit.text():
            raise RuntimeError("Missing version comment")

        # Check if package exists, if not, create it

        handler = mongorm.getHandler()
        filter = mongorm.getFilter()
        filter.search(handler['package'], job=self.entityComboBox.getSelectedJob().get("label"),
                      parent_uuid=self.entityComboBox.getSelectedEntity().getUuid(),
                      type=self.packageType[0],
                      label=self.packagePublishName)
        packageObject = handler['package'].one(filter)

        if not packageObject:
            packageObject = handler['package'].create(
                label=self.packagePublishName,
                created_by=mgutil.getCurrentUser().getUuid(),
                type=self.packageType[0],
                job=self.entityComboBox.getSelectedJob().get("label"),
                path=cometpublish.util.packageTargetPath(self.entityComboBox.getSelectedEntity(),
                                                         self.packageType[0],
                                                         self.packagePublishName),
                parent_uuid=self.entityComboBox.getSelectedEntity().getUuid(),
                labelmap=self.getPublishLabelMap()
            )
            packageObject.save()
            cometpublish.build_package_directory(packageObject)

        # Create version

        status = ['pending', 'approved', 'declined']
        versionObject = handler['version'].create(
            label=self.versionPublishName,
            created_by=mgutil.getCurrentUser().getUuid(),
            parent_uuid=packageObject.getUuid(),
            job=self.entityComboBox.getSelectedJob().get("label"),
            path=os.path.abspath(os.path.join(packageObject.abs_path(), self.versionPublishName)),
            version=self.versionComboBox.getSelectedVersion(),
            comment=self.commentLineEdit.text(),
            status=status[self.autoStatusComboBox.currentIndex()],
            state="complete"
        )
        versionObject.save()
        cometpublish.build_version_directory(versionObject)

        kwargs = {
            'packageObject': packageObject,
            'versionObject': versionObject,
            'entityObject': self.entityComboBox.getSelectedEntity()
        }

        if self.postProcess:
            postProcess = self.postProcess(**kwargs)
            if postProcess:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msgBox.setWindowTitle("Publish Successful!")
                successMessage = "{} successfully published!".format(versionObject.get("label"))
                msgBox.setText(successMessage)

                notificationObject = handler['notification'].create(
                    receiver_uuid=versionObject.get("created_by"),
                    description=successMessage
                )
                notificationObject.save()

                result = msgBox.exec_()
                self.close()
            else:
                #TODO: reverse the publish, delete the files, and the db entry.
                pass


class ValidationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ValidationDialog, self).__init__(parent=parent)
        self._isValid = False

        self._validatorMap = {}

        self.setupBaseUI()
        self.validate()

    def setupBaseUI(self):
        self.setWindowTitle("Validation Check")
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.mainLayout)
        self.mainGroupBox = QtWidgets.QGroupBox("Validation Checks")
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        self.mainLayout.addWidget(self.mainGroupBox)
        self.mainLayout.addWidget(self.buttonBox, alignment=QtCore.Qt.AlignRight)

        self.groupLayout = QtWidgets.QHBoxLayout()
        self.leftLayout = QtWidgets.QVBoxLayout()
        self.mainGroupBox.setLayout(self.groupLayout)
        self.groupLayout.addLayout(self.leftLayout)

        self.textLayout = QtWidgets.QVBoxLayout()
        self.textLayout.setAlignment(QtCore.Qt.AlignTop)
        descriptionHeader = QtWidgets.QLabel("Description")
        self.descriptionTextBox = QtWidgets.QTextEdit()
        detailsHeader = QtWidgets.QLabel("Details")
        self.detailsTextBox = QtWidgets.QTextEdit()
        self.detailsTextBox.setReadOnly(True)
        self.descriptionTextBox.setReadOnly(True)
        self.textLayout.addWidget(descriptionHeader)
        self.textLayout.addWidget(self.descriptionTextBox)
        self.textLayout.addWidget(detailsHeader)
        self.textLayout.addWidget(self.detailsTextBox)

        for label in [descriptionHeader, detailsHeader]:
            label.setStyleSheet("font: bold; font-size: 14px;")

        self.groupLayout.addLayout(self.textLayout)

        self.validationTree = QtWidgets.QTreeWidget()
        self.validationTree.setHeaderHidden(True)
        self.leftLayout.addWidget(self.validationTree)
        self.bottomButtonsLayout = QtWidgets.QHBoxLayout()
        self.fixSelectedButton = QtWidgets.QPushButton("Fix Selected")
        self.refreshButton = QtWidgets.QPushButton("Refresh")
        self.fixSelectedButton.setDisabled(True)
        self.fixSelectedButton.setIcon(QtGui.QIcon(icon_paths.ICON_CRAFT_LRG))
        self.refreshButton.setIcon(QtGui.QIcon(icon_paths.ICON_RELOAD_LRG))
        self.bottomButtonsLayout.setAlignment(QtCore.Qt.AlignRight)
        self.bottomButtonsLayout.addWidget(self.fixSelectedButton)
        self.bottomButtonsLayout.addWidget(self.refreshButton)
        self.leftLayout.addLayout(self.bottomButtonsLayout)

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Close).clicked.connect(self.reject)
        self.validationTree.itemSelectionChanged.connect(self.validationItemChanged)
        self.refreshButton.clicked.connect(self.validate)
        self.fixSelectedButton.clicked.connect(self.fixSelected)

        self.setupValidators()

    def fixSelected(self):
        selection = self.validationTree.currentItem()
        fixer = self._validatorMap[selection.text(0)]['fixer']
        fixer()

        self.validate()

    def validationItemChanged(self):

        selection = self.validationTree.currentItem()
        self.fixSelectedButton.setDisabled(True)
        if not selection:
            return

        validationData = self._validatorMap[selection.text(0)]

        if validationData['fixer'] and not validationData['result']:
            self.fixSelectedButton.setEnabled(True)

        self.updateTextFields()

    def updateTextFields(self):
        selection = self.validationTree.currentItem()

        if not selection:
            self.descriptionTextBox.setText("")
            self.detailsTextBox.setText("")
            return

        validationData = self._validatorMap[selection.text(0)]

        self.descriptionTextBox.setText(validationData['description'])
        self.detailsTextBox.setText(validationData['errorMsg'])

    def setupValidators(self):
        raise NotImplementedError

    def validate(self):
        for validationTask, payload in self._validatorMap.items():
            result, errorMsg = payload['validator']()

            self.editValidator(name=validationTask, field='result', value=result)
            self.editValidator(name=validationTask, field='errorMsg', value=errorMsg)
            payload['treeItem'].setIcon(0, QtGui.QIcon(
                icon_paths.ICON_CHECKGREEN_LRG if result else icon_paths.ICON_XRED_LRG))

        self.updateTextFields()

    def isValid(self):
        if any([not x['result'] for x in list(self._validatorMap.values())]):
            self._isValid = False
        else:
            self._isValid = True

        return self._isValid

    def installValidator(self, name=None, result=False, errorMsg=None, description=None, validator=None, fixer=None):
        assert name, "A name for the validator is required"
        assert description, "A description for the validtor is required"
        assert validator, "A validator function for the validator is required"

        treeItem = QtWidgets.QTreeWidgetItem(self.validationTree)
        treeItem.setText(0, name)

        self._validatorMap[name] = {
            'result': result,
            'treeItem': treeItem,
            'errorMsg': errorMsg,
            'description': description,
            'validator': validator,
            'fixer': fixer
        }

    def removeValidator(self, name):
        self._validatorMap.pop(name)

    def editValidator(self, name, field, value):

        fields = ['result', 'treeItem', 'errorMsg', 'description', 'validator', 'fixer']

        assert name, "Please provide a valid name for the validator"
        assert name in self._validatorMap, "Validator {} does not exist. Please install it first.".format(name)
        assert field in fields, "Invalid field for validator: {}".format(name)

        if field == "result":
            assert isinstance(value, bool)
        elif field == "treeItem":
            assert isinstance(value, QtWidgets.QTreeWidgetItem)
        elif field == "validator" or field == "fixer":
            assert callable(value)

        data = self._validatorMap[name]
        data[field] = value
        self._validatorMap[name] = data


if __name__ == '__main__':
    import sys
    import qdarkstyle
    import mongorm
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win = VersionPublisher()
    win.show()
    sys.exit(app.exec_())