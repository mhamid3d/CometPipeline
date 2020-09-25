from qtpy import QtWidgets, QtGui, QtCore
from cometbrowser.ui.ui_top_interface_bar import TopInterfaceBar
from cometbrowser.ui.ui_production_page import ProductionPage
from cometbrowser.ui.ui_launchers_page import LaunchersPage
from cometqt.widgets.ui_base_main_window import BaseMainWindow
from cometqt import util as pqtutil
from pipeicon import icon_paths
import mongorm
import os


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

    jobChanged = QtCore.Signal(object)
    userChanged = QtCore.Signal(object)

    def __init__(self, userObject, bootstrap=None):
        self._currentUser = None
        self._currentJob = None
        self.settings = pqtutil.get_settings()
        self.setCurrentUser(userObject)
        super(ProjectBrowserMain, self).__init__()
        self.setWindowIcon(QtGui.QIcon(icon_paths.ICON_COMETPIPE_LRG))
        self.setWindowTitle("Comet Browser")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.resize(1500, 900)
        self.handler = mongorm.getHandler()
        self.filter = mongorm.getFilter()
        self.setPageFromCurrentButton()
        self.bootstrap = bootstrap
        self.loadSettings()

    def setCurrentJob(self, jobObject):
        if jobObject:
            assert self._currentUser.uuid in jobObject.allowed_users, "Insufficient permissions to access this job: {}".format(jobObject.label)

        self._currentJob = jobObject

        self.settings.beginGroup("project")
        self.settings.setValue("current_job", self._currentJob.label if self._currentJob else "none")
        self.settings.endGroup()

        self.jobChanged.emit(self._currentJob)

    def currentJob(self):
        return self._currentJob

    def setCurrentUser(self, userObject):
        self._currentUser = userObject

    def currentUser(self):
        return self._currentUser

    def create_widgets(self):
        self.top_interface_bar = TopInterfaceBar(userObject=self._currentUser, parent=self)
        self.stack_main = QtWidgets.QStackedWidget()
        self.productionPage = ProductionPage(parent=self)
        self.launchersPage = LaunchersPage(parent=self)
        self.syncPage = QtWidgets.QWidget()
        self.analyticsPage = QtWidgets.QWidget()
        self.settingsPage = QtWidgets.QWidget()

    def edit_widgets(self):
        self.stack_main.addWidget(self.productionPage)
        self.stack_main.addWidget(self.launchersPage)
        self.stack_main.addWidget(self.syncPage)
        self.stack_main.addWidget(self.analyticsPage)
        self.stack_main.addWidget(self.settingsPage)

    def build_layouts(self):
        self.mainLayout.addWidget(self.top_interface_bar, alignment=QtCore.Qt.AlignTop)
        self.mainLayout.addWidget(self.stack_main)

    def handle_signals(self):
        self.jobChanged.connect(self.top_interface_bar.cometButton.setProjectLabel)
        self.jobChanged.connect(self.productionPage.entityViewer.setCurrentJob)

        self.top_interface_bar.typeButtonGroup.buttonClicked.connect(self.setPageFromCurrentButton)
        self.stack_main.currentChanged.connect(self.setButtonFromCurrentPage)

    def setButtonFromCurrentPage(self):
        idx = self.stack_main.currentIndex()
        self.top_interface_bar.typeButtonGroup.button(idx).setChecked(True)

    def setPageFromCurrentButton(self):
        idx = self.top_interface_bar.typeButtonGroup.checkedId()
        self.stack_main.setCurrentIndex(idx)

    def doCloseBrowser(self):
        self.saveSettings()
        self.close()

    def saveSettings(self):
        self.settings.beginGroup("project")
        self.settings.setValue("current_job", self._currentJob.label if self._currentJob else "none")
        self.settings.setValue("entity_type", self.productionPage.entityViewer.entityType)
        curr_entity = self.productionPage.entityViewer.entityTree.currentItem()
        if curr_entity:
            self.settings.setValue("current_entity", curr_entity.text(0))
        else:
            self.settings.setValue("current_entity", "none")

        self.settings.endGroup()

    def loadSettings(self):
        handler = mongorm.getHandler()
        filter = mongorm.getFilter()

        current_job = self.settings.value("project/current_job")
        if current_job == "none":
            self.setCurrentJob(None)
        else:
            filter.search(handler['job'], label=current_job)
            jobObject = handler['job'].one(filter)
            self.setCurrentJob(jobObject)

        entity_type = self.settings.value("project/entity_type")
        self.productionPage.entityViewer.setEntityType(entity_type)
        os.environ['ENTITY_TYPE'] = entity_type

        current_entity = self.settings.value("project/current_entity")
        if not current_entity == "none":
            os.environ['ENTITY'] = current_entity
            for item in self.productionPage.entityViewer.getAllItems():
                if item.text(0) == current_entity:
                    self.productionPage.entityViewer.entityTree.setCurrentItem(item)
                    break