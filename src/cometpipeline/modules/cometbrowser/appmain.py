from qtpy import QtWidgets, QtGui, QtCore
from cometbrowser.ui.ui_login_window import UiLoginWindow
from cometbrowser.browser import ProjectBrowserMain
from cometqt import util as pqtutil
from pipeicon import icon_paths
import qdarkstyle


class SplashScreen(QtWidgets.QSplashScreen):
    def __init__(self):
        super(SplashScreen, self).__init__()
        self.pix = QtGui.QPixmap(icon_paths.ICON_COMETPIPE_LRG)
        self.setPixmap(self.pix)


class ProjectBrowserBootstrap(object):

    EXIT_CODE_REBOOT = -123

    def __init__(self):
        super(ProjectBrowserBootstrap, self).__init__()

    def run(self):
        self.login_window = UiLoginWindow(bootstrap=self)
        self.login_window.show()
        self.login_window.login_popup.loginPage.restoreSettings()

    def browser_portal(self, userObject):
        self.login_window.deleteLater()
        self.projectBrowser = ProjectBrowserMain(userObject=userObject, bootstrap=self)
        self.projectBrowser.show()

    def login_portal(self):
        self.projectBrowser.deleteLater()
        settings = pqtutil.get_settings()
        settings.beginGroup("login")
        settings.remove("remember_user")
        settings.remove("current_user")
        settings.remove("password")
        settings.endGroup()
        self.login_window = UiLoginWindow(bootstrap=self)
        self.login_window.show()


if __name__ == '__main__':
    import sys
    currentExitCode = ProjectBrowserBootstrap.EXIT_CODE_REBOOT
    while currentExitCode == ProjectBrowserBootstrap.EXIT_CODE_REBOOT:
        app = QtWidgets.QApplication.instance()
        if not app:
            app = QtWidgets.QApplication(sys.argv)
        font = QtGui.QFont("Nimbus Sans")
        font.setStyleHint(QtGui.QFont.Monospace)
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
        # app.setFont(font)
        bootstrap = ProjectBrowserBootstrap()
        bootstrap.run()
        currentExitCode = app.exec_()
