from qtpy import QtWidgets, QtGui, QtCore
from pipeicon import icon_paths
from cometqt import util as cqtutil
from cometqt.widgets.ui_job_combobox import JobComboBox
from cometbrowser.ui.ui_project_manager import ProjectManager
from cometbrowser.ui.ui_create_project_window import CreateProjectWindow


class CometMenuAction(QtWidgets.QFrame):
    def __init__(self, label=None, icon=None, parent=None, exc=None):
        super(CometMenuAction, self).__init__(parent=parent)
        self.exc = exc
        self.label = label
        self.icon = icon
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(self.mainLayout)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.labelWidget = QtWidgets.QLabel(self.label)
        self.iconWidget = QtWidgets.QLabel()
        self.iconWidget.setPixmap(QtGui.QPixmap(self.icon).scaled(20, 20, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.mainLayout.addWidget(self.iconWidget)
        self.mainLayout.addWidget(self.labelWidget)

        self.setStyleSheet("""
            QFrame{
                border-radius: 5px;
            }
        """)

    def mouseReleaseEvent(self, event):
        super(CometMenuAction, self).mouseReleaseEvent(event)
        if callable(self.exc):
            self.exc()


class CometMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super(CometMenu, self).__init__(parent=parent)
        self.setMinimumWidth(350)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.setStyleSheet("""
            QMenu{
                background: #333333;
                border: 1px solid #3e3e3e;
            }
        """)
        self.create_actions()

    def addAction(self, label=None, icon=None, exc=None):
        ca = CometMenuAction(label=label, icon=icon, exc=exc, parent=self)
        self.mainLayout.addWidget(ca)

        return ca

    def addSeparator(self):
        line = cqtutil.h_line()
        line.setFixedHeight(1)
        self.mainLayout.addWidget(line)
        return line

    def create_actions(self):
        self.createNewProject = self.addAction(label="Create New Project", icon=icon_paths.ICON_CRAFT_LRG, exc=self.doCreateProject)
        self.manageProject = self.addAction(label="Manage Project", icon=icon_paths.ICON_SLIDERS_LRG, exc=self.doManageProject)
        self.switchProject = self.addAction(label="Switch Project", icon=icon_paths.ICON_RELOADGREY_LRG, exc=self.doSwitchProject)
        self.addSeparator()
        self.closeBrowser = self.addAction(label="Quit Comet Browser", icon=icon_paths.ICON_DOOROPEN_LRG, exc=self.doCloseBrowser)

    def doCloseBrowser(self):
        from cometbrowser.browser import ProjectBrowserMain

        top_window = cqtutil.get_top_window(self, ProjectBrowserMain)
        top_window.close()

    def doCreateProject(self):
        from cometbrowser.browser import ProjectBrowserMain
        top_window = cqtutil.get_top_window(self, ProjectBrowserMain)
        self.createProjectWindow = CreateProjectWindow(parent=top_window)
        self.createProjectWindow.exec_()

    def doSwitchProject(self):

        diag = QtWidgets.QDialog()
        diag.setWindowTitle("Switch Project")
        lyt = QtWidgets.QVBoxLayout()
        diag.setLayout(lyt)

        jobComboBox = JobComboBox(parent=self)
        jobComboBox.setIndexFromDataObject(self.parent().browserMain.currentJob())

        btnBox = QtWidgets.QDialogButtonBox()
        createButton = QtWidgets.QPushButton("Switch")
        cancelButton = QtWidgets.QPushButton("Cancel")
        btnBox.addButton(createButton, QtWidgets.QDialogButtonBox.AcceptRole)
        btnBox.addButton(cancelButton, QtWidgets.QDialogButtonBox.RejectRole)

        btnBox.accepted.connect(diag.accept)
        btnBox.rejected.connect(diag.reject)

        lyt.addWidget(jobComboBox)
        lyt.addWidget(btnBox)

        diag.resize(300, 100)

        value = diag.exec_()

        if value == QtWidgets.QDialog.Accepted:
            selectedJob = jobComboBox.currentDataObject()
            self.parent().browserMain.setCurrentJob(selectedJob)

    def doManageProject(self):
        mngr = ProjectManager(parent=self.parent().browserMain, jobObject=self.parent().browserMain.currentJob())
        result = mngr.exec_()

        if result == mngr.Accepted:
            self.parent().browserMain.productionPage.entityViewer.populate()

        self.parent().setProjectLabel(self.parent().browserMain.currentJob())


class CometMenuButton(QtWidgets.QFrame):

    @property
    def browserMain(self):
        from cometbrowser.browser import ProjectBrowserMain
        return cqtutil.get_top_window(self, ProjectBrowserMain)

    def __init__(self, parent=None):
        super(CometMenuButton, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.setContentsMargins(9, 0, 9, 0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.cometIcon = QtWidgets.QLabel()
        self.cometIcon.setPixmap(QtGui.QPixmap(icon_paths.ICON_COMETPIPE_LRG).scaled(
            32, 32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        ))
        self.cometIcon.setStyleSheet("""
            QLabel{
                background: transparent;
                border: none;
            }
        """)

        self.projectLabel = QtWidgets.QLabel()
        self.projectLabel.setTextFormat(QtCore.Qt.RichText)
        self.setProjectLabel(self.browserMain.currentJob())
        self.projectLabel.setStyleSheet("""
            QLabel{
                background: transparent;
                border: none;
            }
        """)

        self.downArrow = QtWidgets.QLabel()
        self.downArrow.setPixmap(QtGui.QPixmap(icon_paths.ICON_ARROWDOWN_LRG).scaled(
            10, 10, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        ))
        self.downArrow.setStyleSheet("""
            QLabel{
                background: transparent;
                border: none;
            }
        """)

        self.mainLayout.addWidget(self.cometIcon)
        self.mainLayout.addWidget(self.projectLabel)
        self.mainLayout.addWidget(self.downArrow)

        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setStyleSheet("""
            QFrame{
                border-radius: 0px;
                margin: 0px;
                padding: 0px;
                border: none;
                background: none;
            }
            QFrame:hover{
                background: #3e3e3e;
            }
            QFrame:pressed{
                background: #1e1e1e;
            }
        """)
        self.installEventFilter(self)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.customContextMenuRequested.emit(event.pos())
        return super(CometMenuButton, self).mousePressEvent(event)

    def setProjectLabel(self, jobObject):
        if jobObject:
            TEMPLATE = """
            <html>
            <head/>
                <body>
                    <p>
                        <span style=" font-size:12pt; font-weight:600; color:#ffffff;">{0}</span>
                        <span style=" font-size:10pt; color:#a6a6a6;">{1}</span>
                    </p>
                </body>
            </html>
                    """.format(jobObject.label, jobObject.fullname)

            return self.projectLabel.setText(TEMPLATE)

        return self.projectLabel.setText("No Project Set")

    def contextMenu(self):
        self._menu = CometMenu(parent=self)
        self._menu.exec_(self.mapToGlobal(self.rect().bottomLeft()))