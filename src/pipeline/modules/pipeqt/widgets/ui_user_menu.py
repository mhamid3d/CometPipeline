from qtpy import QtWidgets, QtGui, QtCore
from pipeicon import icon_paths
from pipeqt.widgets.ui_user_avatar import AvatarLabel
from pipeqt import util as pqtutil


class UserMenuAction(QtWidgets.QFrame):
    def __init__(self, label=None, icon=None, exc=None):
        super(UserMenuAction, self).__init__()
        self.exc = exc
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.mainLayout.setSpacing(10)
        self.setLayout(self.mainLayout)
        self.label = QtWidgets.QLabel(label)
        self.pixmap = QtGui.QPixmap(icon).scaled(
            22, 22, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )
        self.icon = QtWidgets.QLabel()
        self.icon.setPixmap(self.pixmap)

        self.mainLayout.addWidget(self.icon)
        self.mainLayout.addWidget(self.label)

        self.icon.setStyleSheet("""
            QLabel{
                background: none;
                border: none;
            }
        """)
        self.label.setStyleSheet("""
            QLabel{
                background: none;
                border: none;
            }
        """)
        self.setStyleSheet("""
            QFrame{
                background: none;
                border: none;
                border-radius: 1px;
            }
            QFrame:hover{
                background: #4e4e4e;
                border: none;
            }
        """)

    def mouseReleaseEvent(self, event):
        super(UserMenuAction, self).mouseReleaseEvent(event)
        rectX = self.rect().width()
        rectY = self.rect().height()
        posX = event.pos().x()
        posY = event.pos().y()

        if 0 <= posX <= rectX and 0 <= posY <= rectY:
            if callable(self.exc):
                self.exc()


class UserMenu(QtWidgets.QMenu):
    def __init__(self, userObject=None, parent=None):
        super(UserMenu, self).__init__(parent)
        self.userObject = userObject
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setContentsMargins(0, 9, 0, 9)
        self.topUserLayout = QtWidgets.QHBoxLayout()
        self.topUserLayout.setContentsMargins(9, 9, 9, 9)
        self.mainLayout.addLayout(self.topUserLayout)
        self.userIcon = AvatarLabel(size=42, data=QtCore.QByteArray(self.userObject.avatar.read()))
        self.userObject.avatar.seek(0)
        self.nameLabel = QtWidgets.QLabel()
        self.nameLabel.setTextFormat(QtCore.Qt.RichText)
        self.nameLabel.setText("""
            <html>
                <head/>
                    <body>
                        <p>
                            <span style=" font-size: 15pt;">{}</span><br>
                            <span style=" font-size: 11pt; color:#a6a6a6;">@{}</span>
                        </p>
                    </body>
            </html>
        """.format(
            self.userObject.get("first_name") + " " + self.userObject.get("last_name"),
            self.userObject.get("username")
        ))
        self.nameLabel.setIndent(10)
        self.nameLabel.setStyleSheet("""
            QLabel{
                border-radius: 3px;
                background: none;
            }
        """)
        self.topUserLayout.addWidget(self.userIcon)
        self.topUserLayout.addWidget(self.nameLabel)
        self.mainLayout.addWidget(pqtutil.h_line())
        self.setStyleSheet("""
            QMenu{
                icon-size: 60px;
                background: #333333;
                border: 1px solid #3e3e3e;
            }
            QMenu:item{
                background: transparent;
            }
        """)

        self.setup_actions()

    def setup_actions(self):
        self.account_action = UserMenuAction(label="My Account", icon=icon_paths.ICON_USER_LRG)
        self.signout_action = UserMenuAction(label="Sign Out", icon=icon_paths.ICON_SIGNOUT_LRG, exc=self.signout_exc)

        self.mainLayout.addWidget(self.account_action)
        self.mainLayout.addWidget(self.signout_action)

    def signout_exc(self):
        main_window = self.parent().parent().parent().parent()
        main_window.bootstrap.login_portal()