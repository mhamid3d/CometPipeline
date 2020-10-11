from qtpy import QtWidgets, QtGui, QtCore
from cometqt.widgets.ui_search_bar import UiSearchBar
from cometqt import util as cqtutil
from pipeicon import icon_paths
from collections import defaultdict
import cometlauncher
import subprocess
import yaml
import os


# TODO: Fix these paths once the final folder structure is made
DCC_LIBS_PATH = r"C:\builds\anaconda2\envs\mayaenv\Lib\site-packages"
COMET_LIBS_PATH = r"C:\_dev\CometPipeline\src\cometpipeline\modules"
DCC_BOOTSTRAPS_PATH = r"C:\_dev\CometPipeline\src\cometpipeline\scripts\bootstraps"


class LauncherAppWidget(QtWidgets.QPushButton):
    def __init__(self, appData=None):
        super(LauncherAppWidget, self).__init__()
        self.appData = appData
        self.setFixedSize(100, 100)
        self.setIcon(QtGui.QIcon(getattr(icon_paths, self.appData['icon'])))
        self.setIconSize(QtCore.QSize(80, 80))
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton{
                background: #3e3e3e;
                border: none;
            }
            QPushButton:hover{
                background: #4e4e4e;
            }
            QPushButton:checked{
                background: #148CD2;
            }
        """)
        self.variables = defaultdict(list)
        self.commands = []
        self.fix_msvcr90()
        self.configure_variables()
        self.configure_commands()

    def fix_msvcr90(self):
        paths = os.getenv("PATH").split(";")
        # TODO: Don't think CONDA_PREFIX will exist when distributing the tool
        unwanted_paths = [
            r"{}".format(os.getenv("CONDA_PREFIX")),
            r"{0}\Library\bin".format(os.getenv("CONDA_PREFIX"))
        ]
        paths = [x for x in paths if not x in unwanted_paths]

        self.variables['PATH'].extend(paths)

    def configure_variables(self):
        if self.appData['include-base-dcc-libs']:
            self.variables['PYTHONPATH'].append(DCC_LIBS_PATH)
        if self.appData['include-base-comet-libs']:
            self.variables['PYTHONPATH'].append(COMET_LIBS_PATH)

        for var, values in self.appData['vars'].items():
            for value in values:
                self.variables[var].append(value)

    def configure_commands(self):
        if self.appData['exec'] == str(None):
            self.appData['exec'] = None

        if not self.appData['exec'] == None:
            self.commands.append(self.appData['exec'])

    def build_final_command(self):
        command = ''
        command += '&'.join(['set {}={}'.format(var, ';'.join(values)) for var, values in self.variables.items()])
        command += '&'
        command += '&'.join(['"{}"'.format(cmd) for cmd in self.commands])

        return command

    def launch_app(self):
        subprocess.Popen(self.build_final_command(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         creationflags=subprocess.CREATE_NEW_CONSOLE)


class LaunchersPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(LaunchersPage, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.centerLayout = QtWidgets.QHBoxLayout()
        self.settingsLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.scrollMain = QtWidgets.QScrollArea()
        self.viewer = QtWidgets.QFrame()
        self.searchBar = UiSearchBar()
        self.appsButtonGroup = QtWidgets.QButtonGroup()
        self.settingsFrame = QtWidgets.QFrame()
        self.scrollMain.setWidget(self.viewer)
        self.scrollMain.setWidgetResizable(True)
        self.scrollMain.verticalScrollBar().setSingleStep(8)
        self.viewer.setStyleSheet("""
            QFrame{
                border: none;
                border-radius: 0px;
            }
        """)
        self.viewer.setContentsMargins(12, 12, 12, 12)
        self.scrollMain.setStyleSheet("""
            QScrollArea{
                border-radius: 0px;
            }
        """)
        self.settingsFrame.setStyleSheet("""
            QFrame{
                border-radius: 0px;
            }
        """)
        self.viewerLayout = cqtutil.FlowLayout(spacing=50)
        self.viewer.setLayout(self.viewerLayout)
        self.viewer.installEventFilter(self.viewer)
        self.mainLayout.addWidget(self.searchBar)
        self.mainLayout.addLayout(self.centerLayout)
        self.settingsFrame.setLayout(self.settingsLayout)
        self.centerLayout.addWidget(self.scrollMain)
        self.centerLayout.addWidget(self.settingsFrame)

        self.runButton = QtWidgets.QPushButton("RUN")
        self.runButton.setFixedHeight(64)
        self.runButton.setMinimumWidth(128)
        self.runButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.runButton.setStyleSheet("""
            QPushButton{
                border-radius: 0px;
                background: green;
            }
            QPushButton:hover{
                border: none;
            }
            QPushButton:pressed{
                background: #4e4e4e;
            }
        """)
        self.runButton.clicked.connect(self.runApp)
        self.settingsLayout.addWidget(self.runButton, alignment=QtCore.Qt.AlignBottom)

        self.searchBar.textChanged.connect(self.searchForApp)

        self.setup_ui()

    def searchForApp(self):
        allApps = [button for button in self.appsButtonGroup.buttons()]
        search = self.searchBar.text()
        for appBtn in allApps:
            if search.upper() in appBtn.appData['name'].upper():
                appBtn.setChecked(True)

    def runApp(self):
        self.appsButtonGroup.checkedButton().launch_app()

    def setup_ui(self):
        app_config_file = file(cometlauncher.APPS_CONFIG, "r")
        data = yaml.load(app_config_file, Loader=yaml.FullLoader)

        for idx, (app, appdata) in enumerate(sorted(data['apps'].items())):
            button = LauncherAppWidget(appData=appdata)
            self.viewerLayout.addWidget(button)
            self.appsButtonGroup.addButton(button, idx)
