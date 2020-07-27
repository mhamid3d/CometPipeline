from qtpy import QtWidgets, QtGui, QtCore
from cometqt import util as cqtutil
from pipeicon import icon_paths
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
        self.setCursor(QtCore.Qt.PointingHandCursor)
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
            QPushButton:hover{
                color: white;
            }
        """)
        # self.setIcon(QtGui.QIcon(icon_paths.ICON_CHECKGREEN_BORDERLESS_LRG))


class InitialForm(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(InitialForm, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.formLayout = CustomVBoxLayout()
        self.mainLayout.addLayout(self.formLayout)

        # Full Title
        self.projectNameLine = ValidationLineEdit("Back To The Future")

        # Alias
        self.projectAliasLine = ValidationLineEdit("DELOREAN")

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

    def directory_browse(self):
        text = self.directoryFileDialog.getExistingDirectory(parent=self, dir=str(self.directoryLine.text()), caption='Choose Color Config')
        if text:
            self.directoryLine.setText(str(text))

    def colorspace_browse(self):
        text = self.colorSpaceFileDialog.getOpenFileName(parent=self, caption='Choose Color Config', selectedFilter="OCIO Config Files (*.ocio)")
        if text and text[0]:
            self.colorSpaceLine.setText(str(text[0]))
            self.colorSpaceFileDialog.setDirectory(os.path.abspath(os.path.join(str(text[0]), os.pardir)))


class CreateProjectWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CreateProjectWindow, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.stack_main = QtWidgets.QStackedWidget(parent=self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.resize(1000, 800)
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

        self.button_group.addButton(self.projectInfoButton)
        self.button_group.addButton(self.assetsButton)
        self.button_group.addButton(self.sequencesButton)
        self.button_group.addButton(self.reviewFinishButton)

        self.projectInfoButton.setChecked(True)

        self.mainLayout.addWidget(self.top_frame)

    def create_pages(self):
        self.initalForm = InitialForm(parent=self)
        self.stack_main.addWidget(self.initalForm)


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