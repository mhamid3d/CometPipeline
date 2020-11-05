from qtpy import QtWidgets, QtGui, QtCore
from cometpipe.core import DEFAULT_ROOT_ENTITIES
from cometqt import util as cqtutil
from cometqt.widgets.ui_animated_popup_message import AnimatedPopupMessage
from pipeicon import icon_paths
from mongorm import util as mgutil
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

        self.formLayout = cqtutil.FormVBoxLayout()
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
        self.xResSpin.setFixedHeight(42)
        self.yResSpin.setFixedHeight(42)
        self.aspectSpin.setFixedHeight(42)

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

        # Create Default Assets
        self.createDefaultAssetsCheck = QtWidgets.QCheckBox()
        self.createDefaultAssetsCheck.setChecked(True)
        self.createDefaultAssetsCheck.setCursor(QtCore.Qt.PointingHandCursor)
        self.createDefaultAssetsCheck.setStyleSheet("""
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

        self.formLayout.addRow("FULL TITLE", self.projectNameLine)
        self.formLayout.addRow("ALIAS", self.projectAliasLine, tip="Project code that will be used for all of production. Keep it simple and short.")
        self.formLayout.addRow("DIRECTORY", self.directoryFrame)
        self.formLayout.addRow("COLOR SPACE CONFIG", self.colorSpaceFrame, tip="Config will be cloned to project directory.")
        self.formLayout.addRow("RESOLUTION", self.resolutionLayout)
        self.formLayout.addRow("CREATE DEFAULT ASSETS", self.createDefaultAssetsCheck)

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
        createDefaultAssets = self.createDefaultAssetsCheck.isChecked()

        handler = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(handler['job'], label=alias)
        jobObject = handler['job'].one(filt)

        if not fullTitle or len(fullTitle) < 2:
            self.error_widget.setMessage("Full Title of project is required")
            self.error_widget.do_anim()
            return
        elif jobObject:
            self.error_widget.setMessage("Job '{}', already exists".format(alias))
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
            'jobResolution': resolution,
            'createDefaultAssets': createDefaultAssets
        }
        self.parent().setCurrentIndex(self.parent().currentIndex() + 1)


class ReviewFinishForm(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(ReviewFinishForm, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.topLayout = QtWidgets.QHBoxLayout()
        self.topLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addWidget(cqtutil.h_line())
        self.formLayout = cqtutil.FormVBoxLayout()
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
        self.reviewFinishButton = PageButton("Review and Finish")

        self.top_frame_layout.addWidget(self.projectInfoButton)
        self.top_frame_layout.addWidget(self.reviewFinishButton)

        self.button_group.addButton(self.projectInfoButton, 0)
        self.button_group.addButton(self.reviewFinishButton, 1)

        self.projectInfoButton.setChecked(True)

        self.mainLayout.addWidget(self.top_frame)

    def create_pages(self):
        self.initalForm = InitialForm(parent=self)
        self.reviewFinishForm = None

        self.stack_main.addWidget(self.initalForm)
        self.stack_main.addWidget(QtWidgets.QFrame())

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

        handler = mongorm.getHandler()

        currentUser = mgutil.getCurrentUser()

        # Create Job Object
        jobObject = handler['job'].create(
            label=initialForm['jobAlias'],
            path=os.path.abspath(os.path.join(initialForm['jobDirectory'], initialForm['jobAlias'])),
            job=initialForm['jobAlias'],
            created_by=currentUser.uuid,
            fullname=initialForm['jobFullTitle'],
            resolution=initialForm['jobResolution'],
            admins=[currentUser.uuid],
            allowed_users=[currentUser.uuid]
        )
        jobObject.save()
        cometpublish.build_job_directory(jobObject)

        # Create Job Entity
        jobEntityObject = handler['entity'].create(
            label=jobObject.label,
            path=cometpublish.util.sequenceShotTargetPath(jobObject, jobObject.label),
            job=jobObject.job,
            type='job',
            production=True,
            parent_uuid=None,
            created_by=currentUser.uuid,
            jobpath="/"
        )
        jobEntityObject.save()
        cometpublish.build_entity_directory(jobEntityObject)

        if initialForm['createDefaultAssets']:
            default_asset_list = sorted(DEFAULT_ROOT_ENTITIES)
            for default_asset in default_asset_list:
                assetObject = handler['entity'].create(
                    label=default_asset,
                    path=cometpublish.util.assetTargetPath(jobEntityObject, default_asset),
                    job=jobObject.job,
                    type='asset',
                    production=True,
                    parent_uuid=jobEntityObject.uuid,
                    created_by=currentUser.uuid,
                    jobpath="/{}".format(default_asset)
                )
                assetObject.save()
                cometpublish.build_entity_directory(assetObject)

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