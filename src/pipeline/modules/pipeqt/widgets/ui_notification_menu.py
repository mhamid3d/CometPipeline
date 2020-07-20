from qtpy import QtWidgets, QtGui, QtCore
from pipeicon import icon_paths


class NotificationMenu(QtWidgets.QPushButton):
    def __init__(self):
        super(NotificationMenu, self).__init__()
        self.setFixedSize(32, 32)
        self.setIcon(QtGui.QIcon(icon_paths.ICON_BELL_LRG))
        self.setIconSize(QtCore.QSize(24, 24))
        self.setStyleSheet("""
            QPushButton,
            QPushButton:pressed,
            QPushButton:hover{
                border: none;
                background: none;
                border-radius: 0px;
            }
        """)
        self.setCursor(QtCore.Qt.PointingHandCursor)

        self.notificationCountLabel = QtWidgets.QLabel()
        self.notificationCountLabel.setFixedSize(18, 18)
        self.notificationCountLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.notificationCountLabel.setStyleSheet("""
            QLabel{
                font: bold 12px;
                border-radius: 9px;
                border: 2px solid #2e2e2e;
                background: red;
            }
        """)
        self.notificationCountLabel.setText("6")
        self.notificationCountLabel.move(12, 0)
        self.notificationCountLabel.setParent(self)