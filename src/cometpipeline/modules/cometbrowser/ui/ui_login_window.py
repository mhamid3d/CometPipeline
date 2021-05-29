from qtpy import QtWidgets, QtGui, QtCore
from cometbrowser.ui.ui_login_form import UiLoginForm
from cometbrowser.ui.ui_register_form import UiRegisterForm
from pipeicon import icon_paths


class HomePage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(HomePage, self).__init__()
        self.setParent(parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)
        self.mainLayout.setContentsMargins(25, 25, 25, 25)
        self.mainLayout.setSpacing(20)

        self.buttonsLayout = QtWidgets.QHBoxLayout()

        self.pipeicon = QtWidgets.QLabel()
        self.login_button = QtWidgets.QPushButton("LOG IN")
        self.sign_up_button = QtWidgets.QPushButton("SIGN UP")
        self.close_button = QtWidgets.QPushButton("CLOSE")

        self.buttonsLayout.setSpacing(20)
        self.login_button.setFixedHeight(36)
        self.sign_up_button.setFixedHeight(36)
        self.close_button.setFixedHeight(36)
        self.pipeicon.setFixedSize(256, 256)
        self.login_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.sign_up_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.close_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.pipeicon.setAlignment(QtCore.Qt.AlignCenter)
        self.pipeicon.setPixmap(QtGui.QPixmap(icon_paths.ICON_COMETPIPE_LRG).scaled(
            128, 128, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        ))

        self.mainLayout.addWidget(self.pipeicon, alignment=QtCore.Qt.AlignCenter)
        self.mainLayout.addLayout(self.buttonsLayout)
        self.buttonsLayout.addWidget(self.login_button)
        self.buttonsLayout.addWidget(self.sign_up_button)
        self.mainLayout.addWidget(self.close_button)

        self.login_button.setStyleSheet("""
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
        self.sign_up_button.setStyleSheet("""
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
        self.close_button.setStyleSheet("""
            QPushButton{
                color: #6e6e6e;
                background: none;
                border: 1px solid #6e6e6e;
                border-radius: 2px;
                font: bold 14px;
            }
            QPushButton:hover{
                color: #9e9e9e;
                border: 1px solid #9e9e9e;
            }
            QPushButton:pressed{
                background: #3e3e3e;
            }
        """)

        self.login_button.clicked.connect(lambda: self.parent().setCurrentIndex(1))
        self.sign_up_button.clicked.connect(lambda: self.parent().setCurrentIndex(2))


class UiLoginPopup(QtWidgets.QStackedWidget):

    userCreated = QtCore.Signal()
    userLoggedIn = QtCore.Signal()

    def __init__(self, parent):
        super(UiLoginPopup, self).__init__()
        self.setParent(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setFixedSize(400, 550)
        self.homePage = HomePage(self)
        self.loginPage = UiLoginForm(self)
        self.registerPage = UiRegisterForm(self)
        self.setObjectName("UiLoginPopup")
        self.setStyleSheet("""
            QStackedWidget#UiLoginPopup{
                border: 1px solid #3e3e3e;
            }
        """)

        self.addWidget(self.homePage)
        self.addWidget(self.loginPage)
        self.addWidget(self.registerPage)

        self.homePage.close_button.clicked.connect(lambda: self.parent().close())
        self.currentChanged.connect(self.reset_register_page)

    def reset_register_page(self):
        if not self.currentWidget() == self.registerPage:
            self.removeWidget(self.registerPage)
            self.registerPage = UiRegisterForm(self)
            self.addWidget(self.registerPage)

    def valid_login(self, userObject):
        self.setStyleSheet("""
                        QStackedWidget{
                            border: 1px solid #148CD2;
                        }
                    """)
        widgets = [self.widget(i) for i in range(self.count())]
        for widget in widgets:
            self.removeWidget(widget)
            widget.deleteLater()
        self.anim = QtCore.QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(200)
        self.anim.setStartValue(QtCore.QRect(350, 75, 400, 550))
        self.setMinimumHeight(200)
        self.setMaximumHeight(550)
        self.anim.setEndValue(QtCore.QRect(350, 250, 400, 200))

        def anim_finished():
            self.setFixedSize(self.anim.endValue().width(), self.anim.endValue().height())

        self.anim.finished.connect(anim_finished)

        self.loggingInWidget = QtWidgets.QWidget()
        self.loggingInLayout = QtWidgets.QVBoxLayout()
        self.loggingInWidget.setLayout(self.loggingInLayout)
        self.loggingInLabel = QtWidgets.QLabel("Logging you in...")
        self.loggingInLayout.addWidget(self.loggingInLabel)
        self.loggingInLabel.setIndent(0)
        self.loggingInLabel.setStyleSheet("""
            QLabel{
                font: bold 16px;
            }
        """)
        self.loggingInLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(self.loggingInWidget)

        self.userLoggedIn.emit()

        self.parent().redirect_login(userObject)


class UiLoginWindow(QtWidgets.QWidget):
    def __init__(self, bootstrap=None):
        super(UiLoginWindow, self).__init__()
        self.setFixedSize(1100, 700)
        self.setWindowIcon(QtGui.QIcon(icon_paths.ICON_COMETPIPE_LRG))
        self.bootstrap = bootstrap
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.mainLayout)
        self.login_popup = UiLoginPopup(self)
        self.mainLayout.addWidget(self.login_popup)
        self.setObjectName("UiLoginWindow")

    def redirect_login(self, userObject):
        self.bootstrap.browser_portal(userObject)

    def paintEvent(self, *args, **kwargs):
        opt = QtWidgets.QStyleOption()
        opt.init(self)
        p = QtGui.QPainter(self)
        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, p, self)


if __name__ == '__main__':
    import sys
    import qdarkstyle
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win = UiLoginWindow()
    win.show()
    sys.exit(app.exec_())
