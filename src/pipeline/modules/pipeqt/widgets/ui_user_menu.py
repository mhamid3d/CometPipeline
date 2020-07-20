from qtpy import QtWidgets, QtGui, QtCore


class UserButtonMenu(QtWidgets.QPushButton):
    def __init__(self):
        super(UserButtonMenu, self).__init__()
        self.setFixedSize(32, 32)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton{
                background: none;
                border: 2px solid #4e4e4e;
                border-radius: 16px;
            }
            QPushButton:hover{
                border: 2px solid #148CD2
            }
        """)