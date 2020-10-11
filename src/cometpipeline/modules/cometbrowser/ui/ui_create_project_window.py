from qtpy import QtWidgets, QtGui, QtCore
from cometpipe.core import ASSET_PREFIX_DICT
from cometqt import util as cqtutil
from cometqt.widgets.ui_animated_popup_message import AnimatedPopupMessage
from pipeicon import icon_paths
import cometpublish
import mongorm
import datetime
import os


class ValidationLineEdit(QtWidgets.QLineEdit):

    def __init__(self, type, parent=None):
        super(ValidationLineEdit, self).__init__()
        self.setParent(parent)
        self.setStyleSheet("""
            QLineEdit{
                font-size: 15px;
                border-radius: 0px;
                background: black;
                padding-left: 8px;
            }
            QLineEdit:hover{
                border: 1px solid #148CD2;
            }
        """)
        self.setFixedHeight(42)
        self.setPlaceholderText(type)


class CustomVBoxLayout(QtWidgets.QVBoxLayout):
    def __init__(self):
        super(CustomVBoxLayout, self).__init__()
        self.setAlignment(QtCore.Qt.AlignTop)
        self.setContentsMargins(9, 12, 9, 9)

    def addRow(self, label, widget, tip=""):
        text_template = """
        <html>
        <head/>
            <body>
                <p>
                    <span>{0}</span>
                    <span style=" font-size:8pt; color:#757575;">{1}</span>
                </p>
            </body>
        </html>
                """.format(label, tip)
        label = QtWidgets.QLabel(text_template)
        label.setTextFormat(QtCore.Qt.RichText)
        label.setStyleSheet("""
            QLabel{
                color: #a6a6a6;
            }
        """)
        label.setAlignment(QtCore.Qt.AlignLeft)
        label.setIndent(0)
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(label)
        layout.addWidget(widget)
        layout.setContentsMargins(9, 9, 9, 10)
        self.addLayout(layout)


class PageButton(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super(PageButton, self).__init__(*args, **kwargs)
        self.setCheckable(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setStyleSheet("""
            QPushButton{
                font-size: 16px;
                color: #757575;
                background: none;
                border: none;
                border-radius: 0px;
                padding: 16px;
            }
            QPushButton:checked{
                color: white;
                border-bottom: 4px solid #148CD2;
            }
        """)

    def mousePressEvent(self, event):
        event.ignore()

    def keyPressEvent(self, event):
        event.ignore()


class InitialForm(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(InitialForm, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self._isValid = False
        self.validationData = {}

        self.formLayout = CustomVBoxLayout()
        self.mainLayout.addLayout(self.formLayout)

        # Full Title
        self.projectNameLine = ValidationLineEdit("Back To The Future")

        # Alias
        self.projectAliasLine = ValidationLineEdit("DELOREAN")
        self.projectAliasLine.textEdited.connect(self.alias_to_upper)
        exp = QtCore.QRegExp("[a-z-A-Z\\.\\-0-9]{0,8}")
        self.aliasValidator = QtGui.QRegExpValidator(exp, self)
        self.projectAliasLine.setValidator(self.aliasValidator)

        # Resolution
        self.resolutionFrame = QtWidgets.QFrame()
        self.resolutionLayout = QtWidgets.QHBoxLayout()
        self.resolutionFrame.setLayout(self.resolutionLayout)
        self.resolutionComboBox = QtWidgets.QComboBox()
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
        # self.resolutionLayout.addWidget(self.resolutionComboBox)
        self.resolutionLayout.addWidget(self.xResSpin)
        self.resolutionLayout.addWidget(self.yResSpin)
        self.resolutionLayout.addWidget(self.aspectSpin)
        self.resolutionFrame.setStyleSheet("""
            QFrame{
                background: none;
                border: none;
            }
        """)
        self.resolutionFrame.setContentsMargins(0, 0, 0, 0)
        self.resolutionLayout.setContentsMargins(0, 0, 0, 0)
        spinStyle = """
            QSpinBox,
            QDoubleSpinBox{
                border-radius: 0px;
                background: background;
            }
        """
        self.xResSpin.setStyleSheet(spinStyle)
        self.yResSpin.setStyleSheet(spinStyle)
        self.aspectSpin.setStyleSheet(spinStyle)
        self.resolutionComboBox.setStyleSheet("""
            QComboBox{
                border-radius: 0px;
                background: black;
            }
        """)
        self.xResSpin.setFixedHeight(42)
        self.yResSpin.setFixedHeight(42)
        self.aspectSpin.setFixedHeight(42)
        self.resolutionComboBox.setFixedHeight(42)

        # Color Space
        self.colorSpaceFrame = QtWidgets.QFrame()
        self.colorSpaceLayout = QtWidgets.QHBoxLayout()
        self.colorSpaceLayout.setContentsMargins(0, 0, 0, 0)
        self.colorSpaceFrame.setLayout(self.colorSpaceLayout)
        self.colorSpaceLine = ValidationLineEdit("")
        self.colorSpaceLine.setReadOnly(True)
        self.colorSpaceBrowse = QtWidgets.QPushButton("Browse")
        self.colorSpaceBrowse.setFixedHeight(42)
        self.colorSpaceLayout.addWidget(self.colorSpaceLine)
        self.colorSpaceLayout.addWidget(self.colorSpaceBrowse)
        self.colorSpaceBrowse.setStyleSheet("""
            QPushButton{
                color: #6e6e6e;
                background: none;
                border: 1px solid #6e6e6e;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                color: #9e9e9e;
                border: 1px solid #9e9e9e;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.colorSpaceBrowse.setCursor(QtCore.Qt.PointingHandCursor)
        self.colorSpaceFrame.setStyleSheet("""
            QFrame{
                border: none;
                background: none;
            }
        """)
        self.colorSpaceFileDialog = QtWidgets.QFileDialog()
        self.colorSpaceBrowse.clicked.connect(self.colorspace_browse)

        # Location
        self.directoryFrame = QtWidgets.QFrame()
        self.directoryLayout = QtWidgets.QHBoxLayout()
        self.directoryLayout.setContentsMargins(0, 0, 0, 0)
        self.directoryFrame.setLayout(self.directoryLayout)
        self.directoryLine = ValidationLineEdit("")
        self.directoryLine.setReadOnly(True)
        self.directoryLine.setText(str(os.path.abspath("/jobs")).replace("\\", "/"))
        self.directoryBrowse = QtWidgets.QPushButton("Browse")
        self.directoryBrowse.setFixedHeight(42)
        self.directoryLayout.addWidget(self.directoryLine)
        self.directoryLayout.addWidget(self.directoryBrowse)
        self.directoryBrowse.setStyleSheet("""
            QPushButton{
                color: #6e6e6e;
                background: none;
                border: 1px solid #6e6e6e;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                color: #9e9e9e;
                border: 1px solid #9e9e9e;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.directoryBrowse.setCursor(QtCore.Qt.PointingHandCursor)
        self.directoryFrame.setStyleSheet("""
            QFrame{
                border: none;
                background: none;
            }
        """)
        self.directoryFileDialog = QtWidgets.QFileDialog()
        self.directoryBrowse.clicked.connect(self.directory_browse)

        self.formLayout.addRow("FULL TITLE", self.projectNameLine)
        self.formLayout.addRow("ALIAS", self.projectAliasLine, tip="Project code that will be used for all of production. Keep it simple and short.")
        self.formLayout.addRow("DIRECTORY", self.directoryFrame)
        self.formLayout.addRow("COLOR SPACE CONFIG", self.colorSpaceFrame, tip="Config will be cloned to project directory.")
        self.formLayout.addRow("RESOLUTION", self.resolutionFrame)

        self.closeButton = QtWidgets.QPushButton("CLOSE")
        self.nextButton = QtWidgets.QPushButton("NEXT")
        self.closeButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.nextButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.closeButton.setFixedSize(84, 42)
        self.nextButton.setFixedSize(84, 42)
        self.closeButton.clicked.connect(self.parent().close)
        self.nextButton.clicked.connect(self.validate_page)

        self.closeButton.setStyleSheet("""
            QPushButton{
                color: #6e6e6e;
                background: none;
                border: 1px solid #6e6e6e;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                color: #9e9e9e;
                border: 1px solid #9e9e9e;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.nextButton.setStyleSheet("""
            QPushButton{
                background: #148CD2;
                border: none;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                border: 1px solid #D9D9D9;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)

        self.v_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addItem(self.v_spacer)

        self.bottomButtonsLayout = QtWidgets.QHBoxLayout()
        self.bottomButtonsLayout.setAlignment(QtCore.Qt.AlignRight)
        self.mainLayout.addLayout(self.bottomButtonsLayout)
        self.bottomButtonsLayout.addWidget(self.closeButton)
        self.bottomButtonsLayout.addWidget(self.nextButton)

        self.error_widget = AnimatedPopupMessage(parent=self.parent(), width=self.parent().width(), type=AnimatedPopupMessage.ERROR)

    def directory_browse(self):
        text = self.directoryFileDialog.getExistingDirectory(parent=self, dir=str(self.directoryLine.text()), caption='Choose Color Config')
        if text:
            self.directoryLine.setText(str(text))

    def colorspace_browse(self):
        text = self.colorSpaceFileDialog.getOpenFileName(parent=self, caption='Choose Color Config', filter="OCIO Config Files (*.ocio)")
        if text and text[0]:
            self.colorSpaceLine.setText(str(text[0]))
            self.colorSpaceFileDialog.setDirectory(os.path.abspath(os.path.join(str(text[0]), os.pardir)))

    def alias_to_upper(self, *args):
        text = args[0]
        self.projectAliasLine.setText(text.upper())

    @property
    def isValid(self):
        return self._isValid

    @isValid.setter
    def isValid(self, value):
        self._isValid = value
        button = self.parent().parent().button_group.button(self.parent().currentIndex())
        if value:
            button.setIcon(
                QtGui.QIcon(icon_paths.ICON_CHECKGREEN_BORDERLESS_LRG))
        else:
            button.setIcon(QtGui.QIcon())

    def validate_page(self):
        self.isValid = False
        fullTitle = self.projectNameLine.text()
        alias = self.projectAliasLine.text()
        directory = self.directoryLine.text()
        colorConfig = self.colorSpaceLine.text()
        resolution = [self.xResSpin.value(), self.yResSpin.value(), self.aspectSpin.value()]

        if not fullTitle or len(fullTitle) < 2:
            self.error_widget.setMessage("Full Title of project is required")
            self.error_widget.do_anim()
            return
        elif not alias or len(alias) < 3:
            self.error_widget.setMessage("Alias of project is required")
            self.error_widget.do_anim()
            return
        elif not os.path.exists(directory):
            self.error_widget.setMessage("Invalid Project Directory. Make sure the folder exists")
            self.error_widget.do_anim()
            return
        elif not os.path.exists(colorConfig):
            self.error_widget.setMessage("Invalid Color Config file")
            self.error_widget.do_anim()
            return
        elif not resolution:
            self.error_widget.setMessage("Invalid Resolution")
            self.error_widget.do_anim()
            return

        self.isValid = True
        self.validationData = {
            'jobFullTitle': fullTitle,
            'jobAlias': alias,
            'jobDirectory': directory,
            'jobColorConfig': colorConfig,
            'jobResolution': resolution
        }
        self.parent().setCurrentIndex(self.parent().currentIndex() + 1)


class AssetsForm(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(AssetsForm, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainHLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.mainHLayout)
        self.formLayout = CustomVBoxLayout()
        self.mainHLayout.addLayout(self.formLayout)
        self.treeLayout = QtWidgets.QVBoxLayout()
        self.mainHLayout.addLayout(self.treeLayout)

        self._isValid = False
        self.validationData = {}

        self.assetTree = QtWidgets.QTreeWidget()
        self.assetTree.setHeaderLabels(['Assets'])
        self.assetTree.setIconSize(QtCore.QSize(24, 24))
        self.assetTree.setStyleSheet("""
            QTreeView{
                border-radius: 0px;
            }
        """)
        self.assetTree.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)
        for prefix in sorted(ASSET_PREFIX_DICT.keys()):
            item = QtWidgets.QTreeWidgetItem(self.assetTree)
            item.setIcon(0, QtGui.QIcon(icon_paths.ICON_ASSETGROUP_LRG))
            item.setText(0, prefix)
        self.removeButton = QtWidgets.QPushButton("Remove Selection")
        self.removeButton.setFixedHeight(42)
        self.removeButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.removeButton.clicked.connect(self.remove_asset)
        self.removeButton.setStyleSheet("""
            QPushButton{
                background: #148CD2;
                border: none;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                border: 1px solid #D9D9D9;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.treeLayout.addWidget(self.assetTree)
        self.treeLayout.addWidget(self.removeButton)

        self.nameLine = ValidationLineEdit("Marty")

        self.prefixComboBox = QtWidgets.QComboBox()
        self.prefixComboBox.setFixedHeight(42)
        self.prefixComboBox.addItems(sorted(ASSET_PREFIX_DICT.keys()))
        self.prefixComboBox.setStyleSheet("""
            QComboBox{
                border-radius: 0px;
                background: black;
                min-height: 42px;
                padding-left: 8px;
            }
        """)

        self.productionCheckBox = QtWidgets.QCheckBox()
        self.productionCheckBox.setCursor(QtCore.Qt.PointingHandCursor)
        self.productionCheckBox.setStyleSheet("""
            QCheckBox::indicator{
                border: 1px solid #6e6e6e;
                border-radius: 0px;
                padding: 2px;
            }
            QCheckBox::indicator:hover{
                border: 1px solid white;
            }
            QCheckBox::indicator:checked{
                background: #148CD2;
                border: 1px solid #148CD2;
                image: url(%s);
            }
            QCheckBox::indicator:unchecked{
                background: none;
                image: none;
            }
        """ % icon_paths.ICON_TICK_SML)

        self.thumbnailFrame = QtWidgets.QFrame()
        self.thumbnailLayout = QtWidgets.QHBoxLayout()
        self.thumbnailLayout.setContentsMargins(0, 0, 0, 0)
        self.thumbnailFrame.setLayout(self.thumbnailLayout)
        self.thumbnailLine = ValidationLineEdit("")
        self.thumbnailLine.setReadOnly(True)
        self.thumbnailBrowse = QtWidgets.QPushButton("Browse")
        self.thumbnailBrowse.setFixedHeight(42)
        self.thumbnailLayout.addWidget(self.thumbnailLine)
        self.thumbnailLayout.addWidget(self.thumbnailBrowse)
        self.thumbnailBrowse.setStyleSheet("""
            QPushButton{
                color: #6e6e6e;
                background: none;
                border: 1px solid #6e6e6e;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                color: #9e9e9e;
                border: 1px solid #9e9e9e;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.thumbnailBrowse.setCursor(QtCore.Qt.PointingHandCursor)
        self.thumbnailFrame.setStyleSheet("""
            QFrame{
                border: none;
                background: none;
            }
        """)
        self.thumbnailFileDialog = QtWidgets.QFileDialog()
        self.thumbnailBrowse.clicked.connect(self.thumbnail_browse)

        self.addButton = QtWidgets.QPushButton("ADD")
        self.addButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.addButton.setFixedSize(84, 42)
        self.addButton.setStyleSheet("""
            QPushButton{
                background: #148CD2;
                border: none;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                border: 1px solid #D9D9D9;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.addButton.clicked.connect(self.add_asset)

        self.formLayout.addRow("NAME", self.nameLine)
        self.formLayout.addRow("TYPE", self.prefixComboBox)
        self.formLayout.addRow("IS THIS ASSET FOR TESTING / RND ?", self.productionCheckBox)
        self.formLayout.addRow("THUMBNAIL", self.thumbnailFrame, tip="You can change this later.")
        self.formLayout.addRow("", self.addButton)

        self.backButton = QtWidgets.QPushButton("BACK")
        self.skipButton = QtWidgets.QPushButton("SKIP")
        self.nextButton = QtWidgets.QPushButton("NEXT")
        self.backButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.skipButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.nextButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.backButton.setFixedSize(84, 42)
        self.skipButton.setFixedSize(84, 42)
        self.nextButton.setFixedSize(84, 42)
        self.backButton.clicked.connect(lambda: self.parent().setCurrentIndex(self.parent().currentIndex() - 1))
        self.skipButton.clicked.connect(self.validate_page)
        self.nextButton.clicked.connect(self.validate_page)

        self.backButton.setStyleSheet("""
            QPushButton{
                color: #6e6e6e;
                background: none;
                border: 1px solid #6e6e6e;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                color: #9e9e9e;
                border: 1px solid #9e9e9e;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.skipButton.setStyleSheet("""
            QPushButton{
                color: #6e6e6e;
                background: none;
                border: 1px solid #6e6e6e;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                color: #9e9e9e;
                border: 1px solid #9e9e9e;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.nextButton.setStyleSheet("""
            QPushButton{
                background: #148CD2;
                border: none;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                border: 1px solid #D9D9D9;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)

        self.v_spacer = QtWidgets.QSpacerItem(40, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(self.v_spacer)

        self.bottomButtonsLayout = QtWidgets.QHBoxLayout()
        self.bottomButtonsLayout.setAlignment(QtCore.Qt.AlignRight)
        self.mainLayout.addLayout(self.bottomButtonsLayout)
        self.bottomButtonsLayout.addWidget(self.skipButton)
        self.bottomButtonsLayout.addWidget(self.backButton)
        self.bottomButtonsLayout.addWidget(self.nextButton)

    def thumbnail_browse(self):
        text = self.thumbnailFileDialog.getOpenFileName(parent=self, caption='Choose Asset Thumbnail', filter="Image Files (*.jpg *.jpeg *.png)")
        if text and text[0]:
            self.thumbnailLine.setText(str(text[0]))
            self.thumbnailFileDialog.setDirectory(os.path.abspath(os.path.join(str(text[0]), os.pardir)))

    def add_asset(self):
        assetName = self.nameLine.text()
        assetProduction = not self.productionCheckBox.isChecked()
        assetThumbnail = self.thumbnailLine.text()
        assetThumbnail = assetThumbnail if assetThumbnail else None
        assetCategory = self.prefixComboBox.currentText()

        if not self.nameLine.text():
            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message="Name field required", type=AnimatedPopupMessage.ERROR,
                                      parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        itemExists = self.assetTree.findItems(str(assetName), QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)
        if itemExists:
            categories = [item.parent().text(0) for item in itemExists]
            if assetCategory in categories:
                try:
                    self.itemExistsError.deleteLater()
                except:
                    pass
                self.itemExistsError = AnimatedPopupMessage(
                    message="Asset with name {} and category {} already exists".format(assetName, assetCategory),
                    type=AnimatedPopupMessage.ERROR,
                    parent=self.parent(),
                    width=self.parent().width()
                )
                self.itemExistsError.do_anim()
                return False

        prefixItem = self.assetTree.findItems(str(assetCategory), QtCore.Qt.MatchExactly, 0)[0]
        assetItem = QtWidgets.QTreeWidgetItem(prefixItem)
        assetItem.setText(0, assetName)
        assetItem.setIcon(0, QtGui.QIcon(assetThumbnail if assetThumbnail else icon_paths.ICON_ASSET_LRG))
        assetItem.assetData = {
            'assetName': assetName,
            'assetProduction': assetProduction,
            'assetThumbnail': assetThumbnail,
            'assetCategory': assetCategory
        }

        self.assetTree.expandAll()

    def remove_asset(self):
        selected_items = self.assetTree.selectedItems()
        for item in selected_items:
            par = item.parent()
            if par:
                par.takeChild(par.indexOfChild(item))

    @property
    def isValid(self):
        return self._isValid

    @isValid.setter
    def isValid(self, value):
        self._isValid = value
        button = self.parent().parent().button_group.button(self.parent().currentIndex())
        if value:
            button.setIcon(
                QtGui.QIcon(icon_paths.ICON_CHECKGREEN_BORDERLESS_LRG))
        else:
            button.setIcon(QtGui.QIcon())

    def validate_page(self):
        self.isValid = False

        self.isValid = True

        for cat in [self.assetTree.topLevelItem(i) for i in range(self.assetTree.topLevelItemCount())]:
            catText = cat.text(0)
            catCount = cat.childCount()
            if catCount is not 0:
                self.validationData[catText] = [cat.child(i) for i in range(catCount)]

        self.parent().setCurrentIndex(self.parent().currentIndex() + 1)


class SequencesForm(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(SequencesForm, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainHLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.mainHLayout)
        self.formLayout = CustomVBoxLayout()
        self.mainHLayout.addLayout(self.formLayout)
        self.treeLayout = QtWidgets.QVBoxLayout()
        self.mainHLayout.addLayout(self.treeLayout)

        self._isValid = False
        self.validationData = {}

        self.sequenceTree = QtWidgets.QTreeWidget()
        self.sequenceTree.setHeaderLabels(['Sequences'])
        self.sequenceTree.setIconSize(QtCore.QSize(24, 24))
        self.sequenceTree.setSortingEnabled(True)
        self.sequenceTree.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)
        self.sequenceTree.setStyleSheet("""
            QTreeView{
                border-radius: 0px;
            }
        """)
        self.removeButton = QtWidgets.QPushButton("Remove Selection")
        self.removeButton.setFixedHeight(42)
        self.removeButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.removeButton.clicked.connect(self.remove_sequence)
        self.removeButton.setStyleSheet("""
            QPushButton{
                background: #148CD2;
                border: none;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                border: 1px solid #D9D9D9;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.treeLayout.addWidget(self.sequenceTree)
        self.treeLayout.addWidget(self.removeButton)

        self.nameLine = ValidationLineEdit("LTK")

        # Shots
        self.shotsFrame = QtWidgets.QFrame()
        self.shotsLayout = QtWidgets.QHBoxLayout()
        self.shotsFrame.setLayout(self.shotsLayout)
        self.beginRangeSpin = QtWidgets.QSpinBox()
        self.endRangeSpin = QtWidgets.QSpinBox()
        self.incrementSpin = QtWidgets.QSpinBox()
        self.beginRangeSpin.setMinimum(0)
        self.endRangeSpin.setMinimum(0)
        self.beginRangeSpin.setMaximum(99999)
        self.endRangeSpin.setMaximum(99999)
        self.beginRangeSpin.setValue(0)
        self.endRangeSpin.setValue(0)
        self.incrementSpin.setMinimum(0)
        self.incrementSpin.setMaximum(99999)
        self.incrementSpin.setValue(0)
        self.shotsLayout.addWidget(self.beginRangeSpin)
        self.shotsLayout.addWidget(self.endRangeSpin)
        self.shotsLayout.addWidget(self.incrementSpin)
        self.shotsFrame.setStyleSheet("""
            QFrame{
                background: none;
                border: none;
            }
        """)
        self.shotsFrame.setContentsMargins(0, 0, 0, 0)
        self.shotsLayout.setContentsMargins(0, 0, 0, 0)
        spinStyle = """
            QSpinBox,
            QDoubleSpinBox{
                border-radius: 0px;
                background: background;
            }
        """
        self.beginRangeSpin.setStyleSheet(spinStyle)
        self.endRangeSpin.setStyleSheet(spinStyle)
        self.incrementSpin.setStyleSheet(spinStyle)
        self.beginRangeSpin.setFixedHeight(42)
        self.endRangeSpin.setFixedHeight(42)
        self.incrementSpin.setFixedHeight(42)

        self.productionCheckBox = QtWidgets.QCheckBox()
        self.productionCheckBox.setCursor(QtCore.Qt.PointingHandCursor)

        self.underscoreCheckBox = QtWidgets.QCheckBox()
        # self.underscoreCheckBox.setChecked(True)
        self.underscoreCheckBox.setCursor(QtCore.Qt.PointingHandCursor)

        self.paddingCheckBox = QtWidgets.QCheckBox()
        self.paddingCheckBox.setChecked(True)
        self.paddingCheckBox.setCursor(QtCore.Qt.PointingHandCursor)

        self.addSeqStrCheckBox = QtWidgets.QCheckBox()
        self.addSeqStrCheckBox.setChecked(True)
        self.addSeqStrCheckBox.setCursor(QtCore.Qt.PointingHandCursor)

        self.addButton = QtWidgets.QPushButton("ADD")
        self.addButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.addButton.setFixedSize(84, 42)
        self.addButton.setStyleSheet("""
            QPushButton{
                background: #148CD2;
                border: none;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                border: 1px solid #D9D9D9;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.addButton.clicked.connect(self.add_sequence)

        self.formLayout.addRow("NAME", self.nameLine)
        self.formLayout.addRow("SHOTS", self.shotsFrame, tip="Begin, End, Increment")
        self.formLayout.addRow("SHOT NUMBER PADDING 4X", self.paddingCheckBox, tip="LTK0010")
        self.formLayout.addRow("ADD '_seq' suffix to sequence", self.addSeqStrCheckBox, tip="LTK_seq")
        self.formLayout.addRow("INCLUDE UNDERSCORE IN SHOT", self.underscoreCheckBox, tip="LTK_0010")
        self.formLayout.addRow("IS THIS SEQUENCE FOR TESTING / RND ?", self.productionCheckBox)
        self.formLayout.addRow("", self.addButton)

        self.backButton = QtWidgets.QPushButton("BACK")
        self.skipButton = QtWidgets.QPushButton("SKIP")
        self.nextButton = QtWidgets.QPushButton("NEXT")
        self.backButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.skipButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.nextButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.backButton.setFixedSize(84, 42)
        self.skipButton.setFixedSize(84, 42)
        self.nextButton.setFixedSize(84, 42)
        self.backButton.clicked.connect(lambda: self.parent().setCurrentIndex(self.parent().currentIndex() - 1))
        self.skipButton.clicked.connect(self.validate_page)
        self.nextButton.clicked.connect(self.validate_page)

        self.backButton.setStyleSheet("""
            QPushButton{
                color: #6e6e6e;
                background: none;
                border: 1px solid #6e6e6e;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                color: #9e9e9e;
                border: 1px solid #9e9e9e;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.skipButton.setStyleSheet("""
            QPushButton{
                color: #6e6e6e;
                background: none;
                border: 1px solid #6e6e6e;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                color: #9e9e9e;
                border: 1px solid #9e9e9e;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.nextButton.setStyleSheet("""
            QPushButton{
                background: #148CD2;
                border: none;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                border: 1px solid #D9D9D9;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)

        self.v_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(self.v_spacer)

        self.bottomButtonsLayout = QtWidgets.QHBoxLayout()
        self.bottomButtonsLayout.setAlignment(QtCore.Qt.AlignRight)
        self.mainLayout.addLayout(self.bottomButtonsLayout)
        self.bottomButtonsLayout.addWidget(self.skipButton)
        self.bottomButtonsLayout.addWidget(self.backButton)
        self.bottomButtonsLayout.addWidget(self.nextButton)

    @property
    def isValid(self):
        return self._isValid

    @isValid.setter
    def isValid(self, value):
        self._isValid = value
        button = self.parent().parent().button_group.button(self.parent().currentIndex())
        if value:
            button.setIcon(
                QtGui.QIcon(icon_paths.ICON_CHECKGREEN_BORDERLESS_LRG))
        else:
            button.setIcon(QtGui.QIcon())

    def validate_page(self):
        self.isValid = False

        self.isValid = True

        for seq in [self.sequenceTree.topLevelItem(i) for i in range(self.sequenceTree.topLevelItemCount())]:
            shots = [seq.child(c) for c in range(seq.childCount())]
            self.validationData[seq] = shots

        self.parent().setCurrentIndex(self.parent().currentIndex() + 1)

    def add_sequence(self):
        sequenceName = self.nameLine.text()
        sequenceProduction = not self.productionCheckBox.isChecked()
        shotRange = [self.beginRangeSpin.value(), self.endRangeSpin.value(), self.incrementSpin.value()]
        padding = self.paddingCheckBox.isChecked()
        seqStrSuffix = self.addSeqStrCheckBox.isChecked()
        underscore = self.underscoreCheckBox.isChecked()

        sequenceNameStr = sequenceName

        if seqStrSuffix:
            sequenceNameStr += "_seq"

        if not self.nameLine.text():
            try:
                self.emptyNameError.deleteLater()
            except:
                pass
            self.emptyNameError = AnimatedPopupMessage(message="Name field required", type=AnimatedPopupMessage.ERROR,
                                      parent=self.parent(), width=self.parent().width())
            self.emptyNameError.do_anim()
            return False

        sequenceItem = self.sequenceTree.findItems(str(sequenceNameStr), QtCore.Qt.MatchExactly, 0)
        if not sequenceItem:
            sequenceItem = QtWidgets.QTreeWidgetItem(self.sequenceTree)
            sequenceItem.sequenceData = {
                "sequenceName": sequenceNameStr,
                "sequenceProduction": sequenceProduction
            }
            sequenceItem.setText(0, sequenceNameStr)
            sequenceItem.setIcon(0, QtGui.QIcon(icon_paths.ICON_SEQUENCE_LRG))
        else:
            sequenceItem = sequenceItem[0]
        if shotRange[2]:
            begin = shotRange[0]
            end = shotRange[1]
            inc = shotRange[2]
            for shotNum in range(begin, end, inc):
                shotNum = str(shotNum).zfill(4) if padding else str(shotNum)
                shotName = "{0}{1}{2}".format(
                    sequenceName, "_" if underscore else "", shotNum
                )
                shotItem = self.sequenceTree.findItems(str(shotName), QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)
                if not shotItem:
                    shotItem = QtWidgets.QTreeWidgetItem(sequenceItem)
                    shotItem.shotData = {
                        "shotName": shotName,
                        "shotProduction": sequenceItem.sequenceData['sequenceProduction']
                    }
                    shotItem.setText(0, shotName)
                    shotItem.setIcon(0, QtGui.QIcon(icon_paths.ICON_SHOT_LRG))

        self.sequenceTree.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.sequenceTree.expandAll()

    def remove_sequence(self):
        selected_items = self.sequenceTree.selectedItems()
        for item in selected_items:
            par = item.parent()
            if par:
                par.takeChild(par.indexOfChild(item))
            else:
                self.sequenceTree.takeTopLevelItem(self.sequenceTree.indexOfTopLevelItem(item))


class ReviewFinishForm(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(ReviewFinishForm, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.topLayout = QtWidgets.QHBoxLayout()
        self.topLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addWidget(cqtutil.h_line())
        self.formLayout = CustomVBoxLayout()
        self.formLayout.setSpacing(10)
        self.mainLayout.addLayout(self.formLayout)

        self.backButton = QtWidgets.QPushButton("BACK")
        self.createButton = QtWidgets.QPushButton("CREATE")
        self.backButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.createButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.backButton.setFixedSize(84, 42)
        self.createButton.setFixedSize(84, 42)
        self.backButton.clicked.connect(lambda: self.parent().setCurrentIndex(self.parent().currentIndex() - 1))
        self.createButton.clicked.connect(self.parent().doCreateJob)

        self.backButton.setStyleSheet("""
            QPushButton{
                color: #6e6e6e;
                background: none;
                border: 1px solid #6e6e6e;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                color: #9e9e9e;
                border: 1px solid #9e9e9e;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.createButton.setStyleSheet("""
            QPushButton{
                background: #148CD2;
                border: none;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                border: 1px solid #D9D9D9;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)

        self.v_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addItem(self.v_spacer)

        self.bottomButtonsLayout = QtWidgets.QHBoxLayout()
        self.bottomButtonsLayout.setAlignment(QtCore.Qt.AlignRight)
        self.mainLayout.addLayout(self.bottomButtonsLayout)
        self.bottomButtonsLayout.addWidget(self.backButton)
        self.bottomButtonsLayout.addWidget(self.createButton)

        self.setup_summary()

    def setup_summary(self):
        initial = self.parent().initalForm.validationData
        assetsForm = self.parent().assetsForm.validationData
        sequencesForm = self.parent().sequencesForm.validationData

        self.productionIcon = QtWidgets.QLabel()
        self.productionIcon.setPixmap(QtGui.QPixmap(icon_paths.ICON_FILMCLAPBOARD_LRG).scaled(
            42, 42, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        ))
        self.productionLabel = QtWidgets.QLabel()
        self.productionLabel.setTextFormat(QtCore.Qt.RichText)
        self.productionLabel.setText("""
        <html>
        <head/>
            <body>
                <p>
                    <span style=" font-size:16pt; font-weight:600; color:#ffffff;">{0}&nbsp;</span>
                    <span style=" font-size:13pt; color:#a6a6a6;"> "{1}"</span>
                </p>
            </body>
        </html>
                """.format(initial['jobAlias'], initial['jobFullTitle']))
        self.topLayout.addWidget(self.productionIcon)
        self.topLayout.addWidget(self.productionLabel)

        self.formLayout.addRow("DIRECTORY", QtWidgets.QLabel(initial['jobDirectory']))
        self.formLayout.addRow("RESOLUTION", QtWidgets.QLabel("{} x {} x {}".format(
            initial['jobResolution'][0], initial['jobResolution'][1], initial['jobResolution'][2]
        )))
        self.formLayout.addRow("COLOR CONFIG", QtWidgets.QLabel(initial['jobColorConfig']))
        assetString = ""
        for assetCat in assetsForm:
            assetString += "  {} ({})  ".format(assetCat, len(assetsForm[assetCat]))
        self.assetsLabel = QtWidgets.QLabel(assetString)
        self.formLayout.addRow("ASSETS", self.assetsLabel)
        seqString = ""
        for seq in sequencesForm:
            seqString += "  {} ({})  ".format(seq.text(0), len(sequencesForm[seq]))
        self.sequencesLabel = QtWidgets.QLabel(seqString)
        # TODO: can't get the sequences to word wrap properly. Need to figure it out
        # self.sequencesLabel.setWordWrap(True)
        self.formLayout.addRow("SEQUENCES", self.sequencesLabel)


class CreateProjectWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CreateProjectWindow, self).__init__(parent=parent)
        self.setWindowTitle("Create New Project")
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.stack_main = QtWidgets.QStackedWidget(parent=self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.resize(700, 700)
        self.setStyleSheet("""
            QDialog{
                background: #1e1e1e;
            }
        """)
        self.move(
            self.parent().width() / 2 - self.width() / 2 + self.parent().pos().x(),
            self.parent().height() / 2 - self.height() / 2 + self.parent().pos().y()
        )
        self.setup_top_buttons()
        self.create_pages()

        self.mainLayout.addWidget(self.stack_main)

        self.stack_main.currentChanged.connect(self.indexChanged)

    def setup_top_buttons(self):
        self.top_frame = QtWidgets.QFrame(parent=self)
        self.button_group = QtWidgets.QButtonGroup()
        self.top_frame_layout = QtWidgets.QHBoxLayout()
        self.top_frame.setLayout(self.top_frame_layout)
        self.top_frame.setStyleSheet("""
            QFrame{
                border: none;
                background: #3e3e3e;
                border-radius: 0px;
            }
        """)
        self.top_frame_layout.setContentsMargins(9, 0, 9, 0)
        self.top_frame_layout.setAlignment(QtCore.Qt.AlignHCenter)

        self.projectInfoButton = PageButton("Project Info")
        self.assetsButton = PageButton("Assets")
        self.sequencesButton = PageButton("Sequences / Shots")
        self.reviewFinishButton = PageButton("Review and Finish")

        self.top_frame_layout.addWidget(self.projectInfoButton)
        self.top_frame_layout.addWidget(self.assetsButton)
        self.top_frame_layout.addWidget(self.sequencesButton)
        self.top_frame_layout.addWidget(self.reviewFinishButton)

        self.button_group.addButton(self.projectInfoButton, 0)
        self.button_group.addButton(self.assetsButton, 1)
        self.button_group.addButton(self.sequencesButton, 2)
        self.button_group.addButton(self.reviewFinishButton, 3)

        self.projectInfoButton.setChecked(True)

        self.mainLayout.addWidget(self.top_frame)

    def create_pages(self):
        self.initalForm = InitialForm(parent=self)
        self.assetsForm = AssetsForm(parent=self)
        self.sequencesForm = SequencesForm(parent=self)
        self.reviewFinishForm = None

        self.stack_main.addWidget(self.initalForm)
        self.stack_main.addWidget(self.assetsForm)
        self.stack_main.addWidget(self.sequencesForm)
        self.stack_main.addWidget(QtWidgets.QFrame())

    def pageButtonClicked(self, button):
        idx = self.button_group.id(button)
        self.stack_main.setCurrentIndex(idx)

    def indexChanged(self):
        idx = self.stack_main.currentIndex()
        self.button_group.button(idx).setChecked(True)
        if self.stack_main.currentIndex() == self.stack_main.count() - 1:
            self.stack_main.blockSignals(True)
            self.stack_main.removeWidget(self.stack_main.currentWidget())
            self.reviewFinishForm = ReviewFinishForm(parent=self)
            self.stack_main.addWidget(self.reviewFinishForm)
            self.stack_main.setCurrentWidget(self.reviewFinishForm)
            self.stack_main.blockSignals(False)

    def doCreateJob(self):
        QtWidgets.QApplication.instance().setOverrideCursor(QtCore.Qt.WaitCursor)

        initialForm = self.initalForm.validationData
        assetsForm = self.assetsForm.validationData
        sequencesForm = self.sequencesForm.validationData

        handler = mongorm.getHandler()

        currentUser = self.parent().currentUser()

        # Create Job Object
        jobObject = handler['job'].objectPrototype()
        jobObject._generate_id()
        jobObject.created = datetime.datetime.now()
        jobObject.modified = jobObject.created
        jobObject.label = initialForm['jobAlias']
        jobObject.path = os.path.abspath(os.path.join(initialForm['jobDirectory'], jobObject.label))
        jobObject.job = jobObject.label
        jobObject.created_by = currentUser.uuid
        jobObject.fullname = initialForm['jobFullTitle']
        jobObject.resolution = initialForm['jobResolution']
        jobObject.admins = [jobObject.created_by]
        jobObject.allowed_users = jobObject.admins
        jobObject.save()
        cometpublish.build_job_directory(jobObject)

        # Create Job Entity
        jobEntityObject = handler['entity'].objectPrototype()
        jobEntityObject._generate_id()
        jobEntityObject.created = datetime.datetime.now()
        jobEntityObject.modified = jobEntityObject.created
        jobEntityObject.label = jobObject.label
        jobEntityObject.path = os.path.abspath(os.path.join(
            jobObject.path, "production", jobEntityObject.label))
        jobEntityObject.job = jobObject.job
        jobEntityObject.type = 'job'
        jobEntityObject.production = True
        jobEntityObject.parent_uuid = None
        jobEntityObject.created_by = currentUser.uuid
        jobEntityObject.save()
        cometpublish.build_entity_directory(jobEntityObject)

        # Create Asset Objects
        for assetCategory, assetItems in assetsForm.items():
            assetType = ASSET_PREFIX_DICT[assetCategory]
            for assetItem in assetItems:
                assetObject = handler['entity'].objectPrototype()
                assetObject._generate_id()
                assetObject.created = datetime.datetime.now()
                assetObject.modified = assetObject.created
                assetObject.label = assetItem.assetData['assetName']
                assetObject.path = os.path.abspath(os.path.join(jobObject.path, "assets", assetCategory, assetObject.label))
                assetObject.job = jobObject.job
                assetObject.type = 'asset'
                assetObject.production = assetItem.assetData['assetProduction']
                assetObject.prefix = assetType
                assetObject.parent_uuid = jobEntityObject.uuid
                if assetItem.assetData['assetThumbnail']:
                    assetObject.thumbnail = assetItem.assetData['assetThumbnail']
                assetObject.created_by = currentUser.uuid
                assetObject.save()
                cometpublish.build_entity_directory(assetObject)

        # Create Sequence Objects
        for sequence, shots in sequencesForm.items():
            sequenceObject = handler['entity'].objectPrototype()
            sequenceObject._generate_id()
            sequenceObject.created = datetime.datetime.now()
            sequenceObject.modified = sequenceObject.created
            sequenceObject.label = sequence.sequenceData['sequenceName']
            sequenceObject.path = os.path.abspath(os.path.join(
                jobObject.path, "production", sequenceObject.label))
            sequenceObject.job = jobObject.job
            sequenceObject.type = 'sequence'
            sequenceObject.production = sequence.sequenceData['sequenceProduction']
            sequenceObject.parent_uuid = jobEntityObject.uuid
            sequenceObject.created_by = currentUser.uuid
            sequenceObject.save()
            cometpublish.build_entity_directory(sequenceObject)

            # Create Shot Objects
            for shot in shots:
                shotObject = handler['entity'].objectPrototype()
                shotObject._generate_id()
                shotObject.created = datetime.datetime.now()
                shotObject.modified = shotObject.created
                shotObject.label = shot.shotData['shotName']
                shotObject.path = os.path.abspath(os.path.join(
                    jobObject.path, "production", shotObject.label))
                shotObject.job = jobObject.job
                shotObject.type = 'shot'
                shotObject.production = sequenceObject.production
                shotObject.parent_uuid = sequenceObject.uuid
                shotObject.created_by = currentUser.uuid
                shotObject.save()
                cometpublish.build_entity_directory(shotObject)

        self.setCursor(QtCore.Qt.ArrowCursor)

        QtWidgets.QApplication.instance().restoreOverrideCursor()

        successDialog = QtWidgets.QDialog(parent=self)
        successDialog.setWindowTitle("Job Created")
        successLayout = QtWidgets.QVBoxLayout()
        successDialog.setLayout(successLayout)
        successIcon = QtWidgets.QLabel()
        successIcon.setPixmap(QtGui.QPixmap(icon_paths.ICON_CHECKGREEN_BORDERLESS_LRG).scaled(
            24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        ))
        successLabel = QtWidgets.QLabel("Job Created Successfully.")
        successLabel.setStyleSheet("""
            QLabel{
                background: none;
            }
        """)
        successIcon.setStyleSheet("""
            QLabel{
                background: none;
            }
        """)
        labelLayout = QtWidgets.QHBoxLayout()
        labelLayout.setAlignment(QtCore.Qt.AlignCenter)
        successLayout.addLayout(labelLayout)
        labelLayout.addWidget(successIcon)
        labelLayout.addWidget(successLabel)
        closeButton = QtWidgets.QPushButton("CLOSE")
        closeButton.setFixedSize(84, 42)
        closeButton.setCursor(QtCore.Qt.PointingHandCursor)
        successLayout.addWidget(closeButton, alignment=QtCore.Qt.AlignRight)
        closeButton.setStyleSheet("""
            QPushButton{
                color: #6e6e6e;
                background: none;
                border: 1px solid #6e6e6e;
                border-radius: 0px;
                font: bold 14px;
            }
            QPushButton:hover{
                color: #9e9e9e;
                border: 1px solid #9e9e9e;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        closeButton.clicked.connect(lambda: self.exitJobCreate(jobObject=jobObject, extraDiags=[successDialog]))
        successDialog.exec_()

        return True

    def exitJobCreate(self, jobObject=None, extraDiags=[]):
        for diag in extraDiags:
            diag.close()
        self.close()
        if jobObject:
            self.parent().setCurrentJob(jobObject)


if __name__ == '__main__':
    import sys
    import qdarkstyle
    app = QtWidgets.QApplication(sys.argv)
    font = QtGui.QFont("Roboto")
    font.setStyleHint(QtGui.QFont.Monospace)
    app.setFont(font)
    p = QtWidgets.QMainWindow()
    win = CreateProjectWindow(parent=p)
    win.move(1300, 400)
    p.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win.show()
    sys.exit(app.exec_())