from qtpy import QtWidgets, QtGui, QtCore
from pipeqt.widgets.ui_user_avatar import AvatarLabel
from pipeqt.widgets.ui_animated_popup_message import AnimatedPopupMessage
from pipeicon import icon_paths
from pipeqt import util
import mongorm
import datetime
import bcrypt
import PIL


class ValidationLineEdit(QtWidgets.QLineEdit):

    def __init__(self, type, parent=None):
        super(ValidationLineEdit, self).__init__()
        self.setParent(parent)
        self.setStyleSheet("""
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
        """)
        self.setPlaceholderText(type)
        self.icon = QtGui.QIcon(icon_paths.ICON_CHECKGREEN_SML)
        self.type = type
        self.isValid = False
        self.textChanged.connect(self.handleTextChange)

    def getValidation(self):
        if not self.text():
            self.isValid = False
            return
        elif len(self.text()) < 2:
            self.isValid = False
            return

        if self.type == "Username":
            # Check if it already exists
            if len(self.text()) < 4:
                self.isValid = False
                return
        elif self.type == "Password":
            if len(self.text()) < 8:
                self.isValid = False
                return
        elif self.type == "Confirm Password":
            if not self.text() == self.parent().password_line.text():
                self.isValid = False
                return
        elif self.type == "Email":
            if "@" not in self.text():
                self.isValid = False
                return

        self.isValid = True

    def handleTextChange(self):
        self.getValidation()
        all_lines = [
            self.parent().firstname_line,
            self.parent().lastname_line,
            self.parent().username_line,
            self.parent().password_line,
            self.parent().confirmpass_line
        ]

        if set([x.isValid for x in all_lines]) == set([True]):
            self.parent().start_button.setEnabled(True)
        else:
            self.parent().start_button.setEnabled(False)

    def paintEvent(self, event):
        super(ValidationLineEdit, self).paintEvent(event)
        if self.isValid:
            painter = QtGui.QPainter(self)
            pixmap = self.icon.pixmap(self.height() - 24, self.height() - 24)
            x, cx = 6, pixmap.width()

            painter.drawPixmap(self.width() - pixmap.width() - x,
                               (self.height() - pixmap.height()) / 2,
                               pixmap)


class IntialForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(IntialForm, self).__init__()
        self.setParent(parent)
        self.mainLayout = QtWidgets.QVBoxLayout()

        self.setLayout(self.mainLayout)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)

        self.create_label = QtWidgets.QLabel("Create User Account")
        self.firstname_line = ValidationLineEdit("First Name", self)
        self.lastname_line = ValidationLineEdit("Last Name", self)
        self.email_line = ValidationLineEdit("Email", self)
        self.username_line = ValidationLineEdit("Username", self)
        self.password_line = ValidationLineEdit("Password", self)
        self.confirmpass_line = ValidationLineEdit("Confirm Password", self)
        self.start_button = QtWidgets.QPushButton("START")
        self.back_button = QtWidgets.QPushButton("BACK")
        self.user_exists_widget = AnimatedPopupMessage(
            message="Account already associated with username / email",
            type=AnimatedPopupMessage.ERROR,
            parent=self.parent(),
            width=self.parent().parent().width()
        )

        self.create_label.setAlignment(QtCore.Qt.AlignLeft)
        self.create_label.setIndent(0)
        self.create_label.setFixedHeight(62)
        self.start_button.setFixedHeight(36)
        self.back_button.setFixedHeight(36)
        self.start_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.back_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.password_line.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpass_line.setEchoMode(QtWidgets.QLineEdit.Password)
        self.start_button.setDisabled(True)

        self.mainLayout.addWidget(self.create_label)
        self.mainLayout.addWidget(self.firstname_line)
        self.mainLayout.addWidget(self.lastname_line)
        self.mainLayout.addWidget(self.email_line)
        self.mainLayout.addWidget(self.username_line)
        self.mainLayout.addWidget(self.password_line)
        self.mainLayout.addWidget(self.confirmpass_line)
        self.v_spacer1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addItem(self.v_spacer1)
        self.mainLayout.addWidget(self.start_button)
        self.v_spacer2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addItem(self.v_spacer2)
        self.mainLayout.addWidget(self.back_button)

        self.create_label.setStyleSheet("""
            QLabel{
                font: bold 20px;
            }
        """)
        self.start_button.setStyleSheet("""
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
            QPushButton:disabled{
                background: #093f5e;
                color: #2e2e2e;
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

        self.start_button.clicked.connect(self.initial_filled)

    def initial_filled(self):
        dh = mongorm.getHandler()
        df = mongorm.getFilter()
        df.search(dh['user'], email=self.email_line.text())
        email_exists = dh['user'].one(df)
        df.clear()
        df.search(dh['user'], username=self.username_line.text())
        username_exists = dh['user'].one(df)
        if email_exists or username_exists:
            self.user_exists_widget.do_anim()
            return
        else:
            self.user_exists_widget.hide()
            self.parent().setCurrentIndex(1)


class AvatarForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AvatarForm, self).__init__()
        self.setParent(parent)
        self.mainLayout = QtWidgets.QVBoxLayout()

        self.setLayout(self.mainLayout)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)

        self.loadApplyLayout = QtWidgets.QHBoxLayout()

        self.choose_avatar = QtWidgets.QLabel("Choose Avatar")
        self.load_button = QtWidgets.QPushButton("LOAD")
        self.apply_button = QtWidgets.QPushButton("APPLY")
        self.avatar_main = AvatarLabel(size=128)
        self.create_button = QtWidgets.QPushButton("FINISH")
        self.back_button = QtWidgets.QPushButton("BACK")

        self.choose_avatar.setAlignment(QtCore.Qt.AlignLeft)
        self.choose_avatar.setIndent(0)
        self.choose_avatar.setFixedHeight(62)
        self.create_button.setFixedHeight(36)
        self.back_button.setFixedHeight(36)
        self.load_button.setFixedHeight(30)
        self.apply_button.setFixedHeight(30)
        self.load_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.apply_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.create_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.back_button.setCursor(QtCore.Qt.PointingHandCursor)

        self.mainLayout.addWidget(self.choose_avatar)
        self.mainLayout.addWidget(self.avatar_main, alignment=QtCore.Qt.AlignCenter)
        self.mainLayout.addLayout(self.loadApplyLayout)
        self.loadApplyLayout.addWidget(self.load_button)
        self.loadApplyLayout.addWidget(self.apply_button)
        self.v_spacer1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addItem(self.v_spacer1)
        self.mainLayout.addWidget(self.create_button)
        self.v_spacer2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addItem(self.v_spacer2)
        self.mainLayout.addWidget(self.back_button)

        self.choose_avatar.setStyleSheet("""
                    QLabel{
                        font: bold 20px;
                    }
                """)
        self.create_button.setStyleSheet("""
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
            QPushButton:disabled{
                background: #093f5e;
                color: #2e2e2e;
            }
        """)
        self.load_button.setStyleSheet("""
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
        self.apply_button.setStyleSheet("""
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

        self.back_button.clicked.connect(lambda: self.parent().setCurrentIndex(0))
        self.load_button.clicked.connect(self.load_file)
        self.create_button.clicked.connect(self.parent().finish)

    def load_file(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, "Choose Avatar", "/", "Images (*.png *.jpg *.jpeg)")[0]
        if file_path:
            self.avatar_main.load(file_path)


class UserCard(QtWidgets.QWidget):
    def __init__(self, dataObject):
        super(UserCard, self).__init__()
        self.dataObject = dataObject
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.avatar = AvatarLabel(size=100, data=QtCore.QByteArray.fromRawData(self.dataObject.avatar.read()))
        self.nameLabel = QtWidgets.QLabel(self.dataObject.get("first_name") + " " + self.dataObject.get("last_name"))
        self.email_label = QtWidgets.QLabel(self.dataObject.get("email"))
        self.username_label = QtWidgets.QLabel("Username: " + self.dataObject.get("username"))
        self.warning_label = QtWidgets.QLabel("* Be sure to remember your username for loggin in.")

        self.cardWidget = QtWidgets.QWidget()
        self.cardWidgetLayout = QtWidgets.QVBoxLayout()
        self.cardWidgetLayout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.cardWidget.setLayout(self.cardWidgetLayout)

        self.nameLabel.setIndent(0)
        self.nameLabel.setAlignment(QtCore.Qt.AlignHCenter)
        self.email_label.setIndent(0)
        self.email_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.username_label.setIndent(0)
        self.username_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.warning_label.setIndent(0)
        self.warning_label.setAlignment(QtCore.Qt.AlignHCenter)

        self.mainLayout.addWidget(self.cardWidget)

        self.cardWidgetLayout.addWidget(self.avatar, alignment=QtCore.Qt.AlignHCenter)
        self.cardWidgetLayout.addWidget(self.nameLabel)
        self.cardWidgetLayout.addWidget(self.email_label)
        self.cardWidgetLayout.addWidget(util.h_line())
        self.cardWidgetLayout.addWidget(self.username_label)
        self.cardWidgetLayout.addWidget(self.warning_label, alignment=QtCore.Qt.AlignBottom)

        self.nameLabel.setStyleSheet("""
            QLabel{
                font-size: 30px;
                color: #a6a6a6;
            }
        """)
        self.email_label.setStyleSheet("""
            QLabel{
                font-size: 20px;
                color: #a6a6a6;
            }
        """)
        self.username_label.setStyleSheet("""
            QLabel{
                font-size: 18px;
                color: #ef8345;
            }
        """)
        self.warning_label.setStyleSheet("""
            QLabel{
                font-size: 12px;
                color: #a6a6a6;
            }
        """)


class SuccessForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SuccessForm, self).__init__()
        self.setParent(parent)
        self.mainLayout = QtWidgets.QVBoxLayout()

        self.setLayout(self.mainLayout)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)

        self.successLayout = QtWidgets.QHBoxLayout()
        self.successLayout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.success_label = QtWidgets.QLabel("User Created Successfully")
        self.success_icon = QtWidgets.QLabel()
        self.login_button = QtWidgets.QPushButton("LOG IN PAGE")
        self.user_card = UserCard(self.parent().save)

        self.success_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.success_label.setIndent(0)
        self.success_label.setFixedHeight(62)
        self.success_icon.setFixedSize(32, 62)
        self.success_icon.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.success_icon.setPixmap(QtGui.QPixmap(icon_paths.ICON_CHECKGREEN_SML).scaledToWidth(
            28, QtCore.Qt.SmoothTransformation
        ))
        self.login_button.setFixedHeight(36)
        self.login_button.setCursor(QtCore.Qt.PointingHandCursor)

        self.mainLayout.addLayout(self.successLayout)
        self.successLayout.addWidget(self.success_icon)
        self.successLayout.addWidget(self.success_label)
        self.mainLayout.addWidget(self.user_card)
        self.v_spacer1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addItem(self.v_spacer1)
        self.mainLayout.addWidget(self.login_button)

        self.success_label.setStyleSheet("""
                    QLabel{
                        font: bold 20px;
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
            QPushButton:disabled{
                background: #093f5e;
                color: #2e2e2e;
            }
        """)


class UiRegisterForm(QtWidgets.QStackedWidget):
    def __init__(self, parent=None):
        super(UiRegisterForm, self).__init__()
        self.setParent(parent)
        self.save = None
        self.setContentsMargins(25, 25, 25, 25)
        self.handler = mongorm.getHandler()
        self.filter = mongorm.getFilter()
        self.initialForm = IntialForm(self)
        self.avatarForm = AvatarForm(self)
        self.addWidget(self.initialForm)
        self.addWidget(self.avatarForm)

        self.initialForm.back_button.clicked.connect(lambda: self.parent().setCurrentIndex(0))

    def finish(self):
        first_name = self.initialForm.firstname_line.text()
        last_name = self.initialForm.lastname_line.text()
        username = self.initialForm.username_line.text()
        email = self.initialForm.email_line.text()
        password = self.initialForm.password_line.text()
        avatar = self.avatarForm.avatar_main.data

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12))

        user_data_object = self.handler['user'].objectPrototype()
        user_data_object._generate_id()
        user_data_object.first_name = first_name
        user_data_object.last_name = last_name
        user_data_object.username = username
        user_data_object.email = email
        user_data_object.password = hashed_pw
        user_data_object.avatar.put(open(avatar, "rb"))
        user_data_object.created = datetime.datetime.now()
        user_data_object.modified = datetime.datetime.now()
        user_data_object.jobs = ['CAIN', 'PYCL', 'LIBRARY']

        self.save = user_data_object.save()

        self.successForm = SuccessForm(self)
        self.successForm.login_button.clicked.connect(lambda: self.parent().setCurrentIndex(1))
        self.addWidget(self.successForm)

        if self.save:
            self.setCurrentWidget(self.successForm)
            self.parent().userCreated.emit()


if __name__ == '__main__':
    import sys
    import qdarkstyle
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win = UiRegisterForm()
    win.show()
    sys.exit(app.exec_())