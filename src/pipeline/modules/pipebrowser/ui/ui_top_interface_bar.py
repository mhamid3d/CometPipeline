from qtpy import QtWidgets, QtGui, QtCore
from pipeicon import icon_paths
from pipeqt import util as pqtutil
from pipeqt.widgets.ui_notification_menu import NotificationButton
from pipeqt.widgets.ui_user_avatar import AvatarLabel
from pipeqt.widgets.ui_user_menu import UserMenu
from collections import OrderedDict
import mongorm


FLAT_BUTTON_STYLE = """
    QPushButton{
        background: none;
        border: none;
        border-radius: 0px;
        padding: 0px;
        min-width: 42px;
    }
    QPushButton:pressed{
        background: #1e1e1e;
    }
"""

TABBED_BUTTON_STYLE = """
    QPushButton,
    QToolButton{
        font-size: 12px;
        border: solid;
        border-radius: 0px;
        min-width: 100px;
    }
    QPushButton:!checked:hover,
    QToolButton:!checked:hover{
        border-bottom: 2px solid #4e4e4e;
        background: #3e3e3e;
    }
    QPushButton:checked,
    QToolButton:checked{
        background: #111111;
        border-bottom: 2px solid #148CD2;
    }
    QToolButton:pressed{
        padding: 0px;
    }
"""

PROJECT_COMBO_STYLE = """
    QComboBox{
        margin: 2px;
        border: none;
        border-radius: 1px;
        font: bold 20px;
    }
    QComboBox:drop-down{
        border: none;
    }
    QComboBox:down-arrow{
        width: 15px;
        height: 15px;
        right: 15px;
    }
"""


class UserIconButton(AvatarLabel):
    def __init__(self, userObject=None, size=32):
        self.userObject = userObject
        super(UserIconButton, self).__init__(size=size, data=QtCore.QByteArray(self.userObject.avatar.read()))
        self.userObject.avatar.seek(0)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

    def mousePressEvent(self, event):
        super(UserIconButton, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.LeftButton:
            self.customContextMenuRequested.emit(event.pos())

    def contextMenu(self, event):
        self._menu = UserMenu(userObject=self.userObject, parent=self)
        self._menu.setFixedWidth(300)
        globalPoint = self.mapToGlobal(self.rect().bottomRight())
        globalPoint.setX(globalPoint.x() - self._menu.width())
        globalPoint.setY(globalPoint.y() + 5)
        self.main_action = self._menu.exec_(globalPoint)


class TopInterfaceBar(QtWidgets.QFrame):
    def __init__(self, userObject=None):
        super(TopInterfaceBar, self).__init__()
        self._typeSelection = 0
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.setFixedHeight(46)
        self.mainLayout.setContentsMargins(9, 0, 9, 0)

        self.userObject = userObject

        self.projectSelector = QtWidgets.QComboBox()
        self.settingsButton = QtWidgets.QPushButton()
        self.typeButtonGroup = QtWidgets.QButtonGroup()
        self.typeLayout = QtWidgets.QHBoxLayout()

        self.setStyleSheet("border-bottom: 2px solid #1e1e1e; border-top: 2px solid #1e1e1e;")

        self.typeLayout.setContentsMargins(0, 0, 0, 0)

        self.cometButton = QtWidgets.QPushButton()
        self.cometButton.setFixedSize(42, 42)
        self.cometButton.setIcon(QtGui.QIcon(icon_paths.ICON_COMETPIPE_LRG))
        self.cometButton.setIconSize(QtCore.QSize(32, 32))
        self.cometButton.setStyleSheet("""
            QPushButton{
                background: none;
                border: none;
            }
            QPushButton:hover{
                background: none;
                border: none;
            }
            QPushButton:pressed{
                background: none;
                border: none;
            }
        """)

        self.projectSelector.setStyleSheet(PROJECT_COMBO_STYLE)
        self.projectSelector.setIconSize(QtCore.QSize(28, 28))

        self.mainLayout.addWidget(self.cometButton, alignment=QtCore.Qt.AlignLeft)
        self.mainLayout.addWidget(self.projectSelector, alignment=QtCore.Qt.AlignLeft)
        self.h_spacer1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(self.h_spacer1)
        self.mainLayout.addLayout(self.typeLayout)
        self.h_spacer2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainLayout.addItem(self.h_spacer2)

        self.userIconMenu = UserIconButton(userObject=self.userObject, size=30)
        self.notificationButton = NotificationButton(userObject=self.userObject)

        self.mainLayout.addWidget(self.notificationButton)
        self.mainLayout.addWidget(self.userIconMenu)

        self.setup_page_buttons()

        self.fetch_jobs()

    def setup_page_buttons(self):

        self.assetsButton = QtWidgets.QToolButton()
        self.assetsButton.setText("Assets")
        self.assetsButton.setFixedSize(100, 42)
        self.assetsButton.setIcon(QtGui.QIcon(icon_paths.ICON_ASSET_LRG))
        self.assetsButton.setCheckable(True)
        self.assetsButton.setIconSize(QtCore.QSize(18, 18))
        self.assetsButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.assetsButton.setStyleSheet(TABBED_BUTTON_STYLE)

        self.productionButton = QtWidgets.QToolButton()
        self.productionButton.setText("Production")
        self.productionButton.setFixedSize(100, 42)
        self.productionButton.setIcon(QtGui.QIcon(icon_paths.ICON_SEQUENCE_LRG))
        self.productionButton.setCheckable(True)
        self.productionButton.setIconSize(QtCore.QSize(18, 18))
        self.productionButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.productionButton.setStyleSheet(TABBED_BUTTON_STYLE)

        self.launchersButton = QtWidgets.QToolButton()
        self.launchersButton.setText("Launchers")
        self.launchersButton.setFixedSize(100, 42)
        self.launchersButton.setIcon(QtGui.QIcon(icon_paths.ICON_LAUNCHER_LRG))
        self.launchersButton.setCheckable(True)
        self.launchersButton.setIconSize(QtCore.QSize(18, 18))
        self.launchersButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.launchersButton.setStyleSheet(TABBED_BUTTON_STYLE)

        self.syncButton = QtWidgets.QToolButton()
        self.syncButton.setText("Sync")
        self.syncButton.setFixedSize(100, 42)
        self.syncButton.setIcon(QtGui.QIcon(icon_paths.ICON_SYNC_LRG))
        self.syncButton.setCheckable(True)
        self.syncButton.setIconSize(QtCore.QSize(18, 18))
        self.syncButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.syncButton.setStyleSheet(TABBED_BUTTON_STYLE)

        self.analyticsButton = QtWidgets.QToolButton()
        self.analyticsButton.setText("Analytics")
        self.analyticsButton.setFixedSize(100, 42)
        self.analyticsButton.setIcon(QtGui.QIcon(icon_paths.ICON_ANALYTICS_LRG))
        self.analyticsButton.setCheckable(True)
        self.analyticsButton.setIconSize(QtCore.QSize(18, 18))
        self.analyticsButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.analyticsButton.setStyleSheet(TABBED_BUTTON_STYLE)

        self.settingsButton = QtWidgets.QToolButton()
        self.settingsButton.setText("Settings")
        self.settingsButton.setFixedSize(100, 42)
        self.settingsButton.setIcon(QtGui.QIcon(icon_paths.ICON_COG_LRG))
        self.settingsButton.setCheckable(True)
        self.settingsButton.setIconSize(QtCore.QSize(18, 18))
        self.settingsButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.settingsButton.setStyleSheet(TABBED_BUTTON_STYLE)

        self.typeButtonGroup.addButton(self.assetsButton, 0)
        self.typeButtonGroup.addButton(self.productionButton, 1)
        self.typeButtonGroup.addButton(self.launchersButton, 2)
        self.typeButtonGroup.addButton(self.syncButton, 3)
        self.typeButtonGroup.addButton(self.analyticsButton, 4)
        self.typeButtonGroup.addButton(self.settingsButton, 5)
        self.typeButtonGroup.button(0).setChecked(True)

        self.typeLayout.addWidget(self.assetsButton)
        self.typeLayout.addWidget(self.productionButton)
        self.typeLayout.addWidget(self.launchersButton)
        self.typeLayout.addWidget(self.syncButton)
        self.typeLayout.addWidget(self.analyticsButton)
        self.typeLayout.addWidget(self.settingsButton)

    def v_line(self):
        v_line = pqtutil.v_line()
        v_line.setStyleSheet("QFrame{background: #3e3e3e; border: 0px;}")
        v_line.setFixedHeight(34)
        return v_line

    def fetch_jobs(self):
        self.projectSelector.clear()
        self.projectSelector.projects = OrderedDict()

        dh = mongorm.getHandler()
        df = mongorm.getFilter()
        df.search(dh['job'])

        jobs = dh['job'].all(df)

        for idx, job in enumerate(jobs):
            self.projectSelector.addItem(QtGui.QIcon(job.thumbnail), job.label)
            self.projectSelector.projects[idx] = job


if __name__ == '__main__':
    import sys
    import qdarkstyle
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win = TopInterfaceBar()
    win.resize(900, 100)
    win.show()
    sys.exit(app.exec_())