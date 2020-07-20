from qtpy import QtWidgets, QtGui, QtCore
from pipebrowser.ui.ui_top_interface_bar import TopInterfaceBar
from pipebrowser.ui.ui_asset_viewer import AssetViewer
from pipeqt.widgets.ui_base_main_window import BaseMainWindow
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
        self.project_menu = QtWidgets.QMenu("Project")
        self.addMenu(self.project_menu)

        self.create_new_action = self.project_menu.addAction("Create New Project")
        self.manage_project_action = self.project_menu.addAction("Manage Project")

        self.edit_menu = QtWidgets.QMenu("Edit")
        self.addMenu(self.edit_menu)

        self.view_menu = QtWidgets.QMenu("View")
        self.addMenu(self.view_menu)


class ProjectBrowserMain(BaseMainWindow):

    def __init__(self):
        super(ProjectBrowserMain, self).__init__()
        self.setWindowTitle("Project Browser")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.resize(1500, 900)
        self.handler = mongorm.getHandler()
        self.filter = mongorm.getFilter()
        self._currentJob = None
        self.job_changed()

    @property
    def currentJob(self):
        return self._currentJob

    def setCurrentJob(self, dataObject):
        self._currentJob = dataObject

    def create_widgets(self):
        # self.menu_bar = MenuBar()
        self.top_interface_bar = TopInterfaceBar()
        self.stack_main = QtWidgets.QStackedWidget()
        self.asset_viewer = AssetViewer(self)

    def edit_widgets(self):
        pass
        # self.setMenuBar(self.menu_bar)

    def build_layouts(self):
        self.mainLayout.addWidget(self.top_interface_bar, alignment=QtCore.Qt.AlignTop)
        self.mainLayout.addWidget(self.stack_main)
        self.stack_main.addWidget(self.asset_viewer)

    def handle_signals(self):
        self.top_interface_bar.projectSelector.currentIndexChanged.connect(self.job_changed)

    def job_changed(self):
        if not self.top_interface_bar.projectSelector.count():
            return False
        self._currentJob = self.top_interface_bar.projectSelector.projects[
            self.top_interface_bar.projectSelector.currentIndex()]
        self.asset_viewer.populate_assets()


if __name__ == '__main__':
    import sys
    import qdarkstyle
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    font = QtGui.QFont("Roboto")
    font.setStyleHint(QtGui.QFont.Monospace)
    app.setFont(font)
    win = ProjectBrowserMain()
    win.show()
    sys.exit(app.exec_())