from qtpy import QtWidgets, QtGui, QtCore
from pipebrowser.ui.ui_top_interface_bar import TopInterfaceBar
from pipebrowser.ui.ui_asset_viewer import AssetViewer
from pipeqt.widgets.ui_base_main_window import BaseMainWindow
from pipeqt import util as pqtutil
import mongorm


class MenuBar(QtWidgets.QMenuBar):
    def __init__(self):
        super(MenuBar, self).__init__()
        self.setup_menu()
        self.setStyleSheet("""
            QMenuBar{
                font-size: 13px;
                border: 0px;
                background: #2e2e2e;
            }
        """)

    def setup_menu(self):
        self.project_menu = self.addMenu("Project")
        self.addMenu(self.project_menu)

        self.create_new_action = self.project_menu.addAction("Create New Project")
        self.manage_project_action = self.project_menu.addAction("Manage Project")

        self.edit_menu = self.addMenu("Edit")
        self.addMenu(self.edit_menu)

        self.view_menu = self.addMenu("View")
        self.addMenu(self.view_menu)


class ProjectBrowserMain(BaseMainWindow):

    def __init__(self, userObject, bootstrap=None):
        self.userObject = userObject
        super(ProjectBrowserMain, self).__init__()
        self.setWindowTitle("Project Browser")
        self.settings = pqtutil.get_settings()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.resize(1500, 900)
        self.handler = mongorm.getHandler()
        self.filter = mongorm.getFilter()
        self._currentJob = None
        self.job_changed()
        self.bootstrap = bootstrap

    @property
    def currentJob(self):
        return self._currentJob

    def setCurrentJob(self, dataObject):
        self._currentJob = dataObject

    def create_widgets(self):
        self.top_interface_bar = TopInterfaceBar(userObject=self.userObject)
        self.stack_main = QtWidgets.QStackedWidget()
        self.asset_viewer = AssetViewer()

    def edit_widgets(self):
        self.stack_main.addWidget(self.asset_viewer)

    def build_layouts(self):
        self.mainLayout.addWidget(self.top_interface_bar, alignment=QtCore.Qt.AlignTop)
        self.mainLayout.addWidget(self.stack_main)

    def handle_signals(self):
        self.top_interface_bar.projectSelector.currentIndexChanged.connect(self.job_changed)

    def job_changed(self):
        if not self.top_interface_bar.projectSelector.count():
            return False
        self._currentJob = self.top_interface_bar.projectSelector.projects[
            self.top_interface_bar.projectSelector.currentIndex()]
        self.asset_viewer.populate_assets()
