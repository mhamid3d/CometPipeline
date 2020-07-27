from qtpy import QtWidgets, QtGui, QtCore
from cometqt import util as pqtutil
from cometqt.widgets.ui_animated_popup_message import AnimatedPopupMessage
import mongorm
import bcrypt


class UiLoginForm(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(UiLoginForm, self).__init__()
        self.settings = pqtutil.get_settings()
        self.setParent(parent)
        self.mainLayout = QtWidgets.QVBoxLayout()

        self.setLayout(self.mainLayout)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)
        self.mainLayout.setContentsMargins(25, 25, 25, 25)

        self.login_label = QtWidgets.QLabel("Log In Project User")
        self.username_line = QtWidgets.QLineEdit()
        self.password_line = QtWidgets.QLineEdit()
        self.login_button = QtWidgets.QPushButton("LOG IN")
        self.back_button = QtWidgets.QPushButton("BACK")
        self.forgot_label = QtWidgets.QLabel("Forgot Password?")
        self.remember_check = QtWidgets.QCheckBox("Remember Me")

        self.login_label.setAlignment(QtCore.Qt.AlignLeft)
        self.login_label.setIndent(0)
        self.login_button.setFixedHeight(36)
        self.back_button.setFixedHeight(36)
        self.login_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.back_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.remember_check.setCursor(QtCore.Qt.PointingHandCursor)
        self.forgot_label.setCursor(QtCore.Qt.PointingHandCursor)
        self.username_line.setPlaceholderText("Username")
        self.password_line.setPlaceholderText("Password")
        self.password_line.setEchoMode(QtWidgets.QLineEdit.Password)
        self.remember_check.setChecked(True)

        self.mainLayout.addWidget(self.login_label)
        self.mainLayout.addWidget(self.username_line)
        self.mainLayout.addWidget(self.password_line)
        self.mainLayout.addWidget(self.forgot_label, alignment=QtCore.Qt.AlignRight)
        self.mainLayout.addWidget(self.remember_check)
        self.mainLayout.addWidget(self.login_button)
        self.v_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addItem(self.v_spacer)
        self.mainLayout.addWidget(self.back_button)

        self.forgot_label.setStyleSheet("""
            QLabel{
                font-size: 15px;
                color: #a6a6a6;
                padding-bottom: 15px;
            }
        """)
        self.remember_check.setStyleSheet("""
            QCheckBox{
                background: #3e3e3e;
                border: none;
                padding-top: 15px;
                padding-left: 5px;
                padding-bottom: 15px;
                color: #a6a6a6;
                font-size: 13px;
            }
            QCheckBox:indicator{
                width: 20px;
                height: 20px;
            }
        """)
        self.login_label.setStyleSheet("""
            QLabel{
                font: bold 20px;
                padding-bottom: 10px;
                padding-top: 20px;
                padding-left: 0px;
            }
        """)
        self.login_button.setStyleSheet("""
            QPushButton{
                background: #148CD2;
                border: none;
                border-radius: 2px;
                font: bold 14px;
            }
            QPushButton:hover{
                border: 1px solid #D9D9D9;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        self.back_button.setStyleSheet("""
            QPushButton{
                background: #4e4e4e;
                border: none;
                border-radius: 2px;
                font: bold 14px;
            }
            QPushButton:hover{
                border: 1px solid #D9D9D9;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)
        line_style = """
            QLineEdit{
                font-size: 15px;
                padding: 12px;
                border-radius: 0px;
                border: none;
                background: black;
            }
            QLineEdit:hover{
                border: 1px solid #148CD2;
            }
        """
        self.password_line.setStyleSheet(line_style)
        self.username_line.setStyleSheet(line_style)

        self.back_button.clicked.connect(lambda: self.parent().setCurrentIndex(0))
        self.login_button.clicked.connect(self.do_login)

        self.error_widget = AnimatedPopupMessage(
            message="Invalid Username / Password Combination",
            type=AnimatedPopupMessage.ERROR,
            parent=self,
            width=self.parent().width(),
        )

    def keyPressEvent(self, event):
        super(UiLoginForm, self).keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Return:
            self.do_login()

    def do_login(self):
        handler = mongorm.getHandler()
        filter = mongorm.getFilter()
        filter.search(handler['user'], username=self.username_line.text())
        user_object = handler['user'].one(filter)
        password = self.password_line.text().encode("utf-8")

        if user_object:
            hashed = user_object.get("password").encode("utf-8")
            if bcrypt.checkpw(password, hashed):
                return self.valid_login(user_object)

        return self.error_widget.do_anim()

    def writeSettings(self, dataObject):
        self.settings.beginGroup("login")
        self.settings.setValue("remember_user", self.remember_check.isChecked())
        self.settings.setValue("username", dataObject.get("username"))
        self.settings.setValue("email", dataObject.get("email"))
        self.settings.setValue("password", dataObject.get("password"))
        self.settings.endGroup()

    def restoreSettings(self):
        if not self.settings.value("login/remember_user") == "true":
            return False

        if not self.settings.value("login/username") and self.settings.value("password"):
            return False

        handler = mongorm.getHandler()
        filter = mongorm.getFilter()
        filter.search(handler['user'], username=self.settings.value("login/username"))
        user_object = handler['user'].one(filter)

        if not user_object:
            return False

        if not user_object.get("email") == self.settings.value("login/email"):
            return False

        return self.valid_login(user_object)

    def valid_login(self, dataObject):
        self.writeSettings(dataObject)
        self.parent().valid_login(dataObject)

        return True


if __name__ == '__main__':
    import sys
    import qdarkstyle
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win = UiLoginForm()
    win.show()
    sys.exit(app.exec_())