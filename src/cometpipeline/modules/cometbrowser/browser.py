from qtpy import QtWidgets, QtGui, QtCore
from cometbrowser.ui.ui_top_interface_bar import TopInterfaceBar
from cometbrowser.ui.ui_production_page import ProductionPage
from cometbrowser.ui.ui_launchers_page import LaunchersPage
from cometqt.widgets.ui_base_main_window import BaseMainWindow
from cometqt import util as pqtutil
from pipeicon import icon_paths
from mongorm.core.datacontainer import DataContainer
import logging
import mongorm
import os


LOGGER = logging.getLogger("Comet.CometBrowser")
logging.basicConfig()
LOGGER.setLevel(logging.INFO)


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None):
        super(SystemTrayIcon, self).__init__(parent)
        self.setIcon(QtGui.QIcon(icon_paths.ICON_COMETPIPE_LRG))


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
        self.tray = SystemTrayIcon(self)
        self.tray.show()
        self.loadSettings()

    def setCurrentJob(self, jobObject):
        if jobObject:
            crews = [v for k, v in jobObject.crew.items()]
            crewMembers = set([uid for crewTypeList in crews for uid in crewTypeList])
            if not self._currentUser.getUuid() in crewMembers:
                # TODO: need a more global solution for this, this is kind of ridiculous
                LOGGER.error("Insufficient permissions to access this job: {}".format(jobObject.label))
                self.setCurrentJob(None)
                return
            else:
                os.environ['SHOW'] = jobObject.get("label")

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

    def closeEvent(self, event):
        self.doCloseBrowser()
        super(ProjectBrowserMain, self).closeEvent(event)

    def doCloseBrowser(self):
        self.saveSettings()
        notificationThread = self.top_interface_bar.notificationButton.notificationThread
        notificationReceived = self.top_interface_bar.notificationButton.notificationReceived
        notificationThread.notificationReceived.disconnect(notificationReceived)
        notificationThread.quit()

    def saveSettings(self):
        self.settings.beginGroup("project")
        self.settings.setValue("current_job", self._currentJob.label if self._currentJob else "none")
        curr_item = self.productionPage.entityViewer.entityTree.currentItem()
        if curr_item:
            entity = curr_item.dataObject
            if entity:
                entity = entity.getUuid()
                self.settings.setValue("current_entity", entity)
            else:
                self.settings.setValue("current_entity", "none")

        self.settings.endGroup()

        self.settings.beginGroup("packageViewer")
        self.settings.setValue("filteredPackageTypes", ";".join(self.productionPage.packageViewer.packageTypeNavigator.getFilteredTypes()))
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
            if jobObject:
                self.setCurrentJob(jobObject)

                if self.currentJob():
                    current_entity = self.settings.value("project/current_entity")
                    if current_entity:
                        data = handler['entity'].get(current_entity)
                        if data:
                            if not isinstance(data, DataContainer):
                                data = [data]
                            self.productionPage.entityViewer.setSelectedEntities(data)
            else:
                self.setCurrentJob(None)

        filteredPackageTypes = self.settings.value("packageViewer/filteredPackageTypes")
        if filteredPackageTypes:
            self.productionPage.packageViewer.packageTypeNavigator.setFilteredTypes(filteredPackageTypes.split(";"))