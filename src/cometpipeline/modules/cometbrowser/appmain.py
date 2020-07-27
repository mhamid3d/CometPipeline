from qtpy import QtWidgets, QtGui
from cometbrowser.ui.ui_login_window import UiLoginWindow
from cometbrowser.browser import ProjectBrowserMain
from cometqt import util as pqtutil
import qdarkstyle


class ProjectBrowserBootstrap(object):
    def __init__(self):
        super(ProjectBrowserBootstrap, self).__init__()

    def run(self):
        self.login_window = UiLoginWindow(bootstrap=self)
        self.login_window.show()
        self.login_window.login_popup.loginPage.restoreSettings()

    def browser_portal(self, userObject):
        self.login_window.deleteLater()
        self.projectBrowser = ProjectBrowserMain(userObject=userObject, bootstrap=self)
        self.projectBrowser.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
        self.projectBrowser.show()

    def login_portal(self):
        self.projectBrowser.deleteLater()
        settings = pqtutil.get_settings()
        settings.beginGroup("login")
        settings.remove("remember_user")
        settings.remove("username")
        settings.remove("email")
        settings.remove("password")
        settings.endGroup()
        self.login_window = UiLoginWindow(bootstrap=self)
        self.login_window.show()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    font = QtGui.QFont("Roboto")
    font.setStyleHint(QtGui.QFont.Monospace)
    app.setFont(font)
    bootstrap = ProjectBrowserBootstrap()
    bootstrap.run()
    sys.exit(app.exec_())
