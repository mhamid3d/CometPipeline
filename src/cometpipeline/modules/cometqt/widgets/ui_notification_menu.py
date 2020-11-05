from qtpy import QtWidgets, QtGui, QtCore
from cometqt import util as pqtutil
from pipeicon import icon_paths
import datetime
import timeago
import mongorm


class NotificationThread(QtCore.QThread):
    notificationReceived = QtCore.Signal(object)

    def __init__(self, userObject=None, parent=None):
        super(NotificationThread, self).__init__(parent=parent)
        self.userObject = userObject
        self.handler = mongorm.getHandler()
        self.filter = mongorm.getFilter()
        self.client = self.handler.toMongoClient()
        self.change_stream = getattr(self.client, self.handler._DATABASE).notification.watch([
            {'$match': {
                'operationType': {'$in': ['insert', 'update', 'replace']},
                'fullDocument.receiver_uuid': self.userObject.getUuid()
            }}
        ])
        self._continue = True

    def quit(self):
        self.change_stream.close()
        self._continue = False
        super(NotificationThread, self).quit()
        self.wait(5000)

    def exit(self, *args, **kwargs):
        self.change_stream.close()
        self._continue = False
        super(NotificationThread, self).exit()
        self.wait(5000)

    def terminate(self):
        self.change_stream.close()
        self._continue = False
        super(NotificationThread, self).terminate()
        self.wait(5000)

    def run(self):
        while self._continue:
            for change in self.change_stream:
                uuid = change['fullDocument']['uuid']
                dataObject = self.handler['notification'].get(uuid)
                self.notificationReceived.emit(dataObject)


class NotificationMenuAction(QtWidgets.QFrame):
    def __init__(self, dataObject=None, icon=None, exc=None):
        super(NotificationMenuAction, self).__init__()
        self.exc = exc
        self.dataObject = dataObject
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.mainLayout.setSpacing(10)
        self.setLayout(self.mainLayout)
        self.contentLayout = QtWidgets.QVBoxLayout()
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setFixedWidth(488)

        self.description = QtWidgets.QLabel(self.dataObject.get("description"))
        self.description.setWordWrap(True)
        self.description.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.pixmap = QtGui.QPixmap(icon_paths.ICON_COMETPIPE_LRG).scaled(
            24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.icon = QtWidgets.QLabel()
        self.icon.setPixmap(self.pixmap)
        self.timeLabel = QtWidgets.QLabel(timeago.format(self.dataObject.created, datetime.datetime.now()))
        self.unreadLabel = QtWidgets.QLabel()
        self.unreadLabel.setFixedSize(8, 8)
        sp = self.unreadLabel.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.unreadLabel.setSizePolicy(sp)
        if self.dataObject.read:
            self.unreadLabel.hide()
        self.settingsButton = QtWidgets.QPushButton()
        self.settingsButton.setFixedSize(32, 32)
        self.settingsButton.setIcon(QtGui.QIcon(icon_paths.ICON_VMENU_LRG))
        sp = self.settingsButton.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.settingsButton.setSizePolicy(sp)
        self.settingsButton.mousePressEvent = self.settingsMousePressEvent
        self.settingsButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.settingsButton.customContextMenuRequested.connect(self.settingsMenuRequested)
        self.settingsButton.hide()

        self.mainLayout.addWidget(self.unreadLabel)
        self.mainLayout.addWidget(self.icon)
        self.mainLayout.addLayout(self.contentLayout)
        self.contentLayout.addWidget(self.description)
        self.contentLayout.addWidget(self.timeLabel)
        self.mainLayout.addWidget(self.settingsButton, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)

        self.unreadLabel.setStyleSheet("""
            QLabel{
                background: #148CD2;
                border-radius: 4px;
                border: none;
            }
        """)
        self.icon.setStyleSheet("""
            QLabel{
                background: none;
                border: none;
            }
        """)
        self.description.setStyleSheet("""
            QLabel{
                background: none;
                border: none;
            }
        """)
        self.timeLabel.setStyleSheet("""
            QLabel{
                background: none;
                border: none;
                font-size: 14px;
                color: #a6a6a6;
            }
        """)
        self.settingsButton.setStyleSheet("""
            QPushButton{
                border: none;
                border-radius: 16px;
                background: none;
            }
            QPushButton:pressed{
                background: #6e6e6e;
            }
        """)
        self.setStyleSheet("""
            QFrame{
                background: #333333;
                border: none;
                border-radius: 1px;
            }
            QFrame:hover{
                background: #3e3e3e;
                border: none;
            }
        """)

        self.installEventFilter(self)

    def mouseReleaseEvent(self, event):
        super(NotificationMenuAction, self).mouseReleaseEvent(event)
        rectX = self.rect().width()
        rectY = self.rect().height()
        posX = event.pos().x()
        posY = event.pos().y()

        if 0 <= posX <= rectX and 0 <= posY <= rectY:

            self.dataObject.read = True
            self.dataObject.modified = datetime.datetime.now()
            self.dataObject.save()

            if callable(self.exc):
                self.exc()

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.HoverEnter:
            self.settingsButton.show()
        elif event.type() == QtCore.QEvent.HoverLeave:
            self.settingsButton.hide()
        return super(NotificationMenuAction, self).eventFilter(object, event)

    def settingsMousePressEvent(self, event):
        QtWidgets.QPushButton.mousePressEvent(self.settingsButton, event)
        if event.button() == QtCore.Qt.LeftButton:
            self.settingsButton.customContextMenuRequested.emit(event.pos())

    def settingsMenuRequested(self, event):
        self.settingsMenu = QtWidgets.QMenu(parent=self)
        self.settingsMenu.setStyleSheet("""
            QMenu{
                icon-size: 24px;
            }
            QMenu:item{
                background: #2e2e2e;
            }
            QMenu::item:selected{
                background: #4e4e4e;
            }
        """)
        self.deleteNotification = self.settingsMenu.addAction("Delete Notification")
        self.deleteNotification.setIcon(QtGui.QIcon(icon_paths.ICON_TRASH_LRG))
        self.settingsMenu.addSeparator()
        self.markUnread = self.settingsMenu.addAction("Mark as unread")
        self.markUnread.setIcon(QtGui.QIcon(icon_paths.ICON_BELL_LRG))

        globalPoint = self.settingsButton.mapToGlobal(self.settingsButton.rect().bottomRight())
        globalPoint.setX(globalPoint.x() - self.settingsMenu.sizeHint().width())
        globalPoint.setY(globalPoint.y() + 5)

        main_action = self.settingsMenu.exec_(globalPoint)

        if main_action is not None:

            if main_action == self.deleteNotification:
                self.doDeleteNotification()
            elif main_action == self.markUnread:
                self.doMarkUnread()

    def doDeleteNotification(self):
        self.dataObject.deleted = True
        self.dataObject.modified = datetime.datetime.now()
        self.dataObject.save()
        self.deleteLater()

    def doMarkUnread(self):
        self.dataObject.read = False
        self.dataObject.modified = datetime.datetime.now()
        self.dataObject.save()
        self.unreadLabel.show()


class NotificationMenu(QtWidgets.QMenu):
    def __init__(self, userObject=None, parent=None):
        super(NotificationMenu, self).__init__(parent)
        self.handler = self.parent().handler
        self.filter = self.parent().filter
        self.interface = self.parent().interface
        self.userObject = userObject
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)
        self.setFixedWidth(500)
        self.setFixedHeight(700)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.topSettingsLayout = QtWidgets.QHBoxLayout()
        self.topSettingsLayout.setContentsMargins(11, 11, 11, 11)
        self.mainLayout.addLayout(self.topSettingsLayout)

        self.notificationsScroll = QtWidgets.QScrollArea()
        self.notificationsContainer = QtWidgets.QWidget()
        self.notificationsScroll.setWidget(self.notificationsContainer)
        self.notificationsScroll.setWidgetResizable(True)
        self.notificationsLayout = QtWidgets.QVBoxLayout()
        self.notificationsContainer.setLayout(self.notificationsLayout)

        self.notificationsLayout.setAlignment(QtCore.Qt.AlignTop)
        self.notificationsScroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.notificationsScroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.notificationsScroll.setStyleSheet("""
            QScrollArea{
                background: transparent;
                padding: 0px;
                border-radius: 0px;
                border: none;
            }
            QScrollBar:vertical{
                background: #333333;
                border: none;
                border-radius: 0px;
                width: 10px;
                padding: 1px;
                margin: 0;
            }
            QScrollBar::handle:vertical,
            QScrollBar::handle:horizontal{
                background: #4e4e4e;
                border: none;
                border-radius: 0px;
            }
            QScrollBar::handle:vertical:hover,
            QScrollBar::handle:horizontal:hover{
                background: #5e5e5e;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical{
                height: 0px;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal{
                width: 0px;
            }
        """)
        self.notificationsScroll.setContentsMargins(0, 0, 0, 0)
        self.notificationsContainer.setContentsMargins(1, 0, 1, 1)
        self.notificationsLayout.setContentsMargins(0, 0, 0, 0)
        self.notificationsLayout.setSpacing(0)

        self.notificationsLabel = QtWidgets.QLabel("Notifications")
        self.notificationsLabel.setStyleSheet("""
            QLabel{
                background: none;
                border: none;
                font-size: 20px;
            }
        """)
        self.notificationsLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.notificationsLabel.setIndent(0)
        self.settingsButton = QtWidgets.QPushButton()
        self.settingsButton.setFixedSize(36, 36)
        self.settingsButton.setIcon(QtGui.QIcon(icon_paths.ICON_COG_LRG))
        self.settingsButton.setStyleSheet("""
            QPushButton{
                border-radius: 18px;
            }
            QPushButton:pressed{
                background: #4e4e4e;
            }
        """)
        self.settingsButton.setIconSize(QtCore.QSize(24, 24))
        self.settingsButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.topSettingsLayout.addWidget(self.notificationsLabel)
        self.topSettingsLayout.addWidget(self.settingsButton, alignment=QtCore.Qt.AlignRight)
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

        self.mainLayout.addWidget(self.notificationsScroll)

        self.allNotifications = None

        self.populate_notifications()

    def populate_notifications(self):
        self.filter.search(self.interface, receiver_uuid=self.userObject.getUuid())
        self.allNotifications = self.interface.all(self.filter)

        for notification in self.allNotifications:
            item = NotificationMenuAction(dataObject=notification)
            self.notificationsLayout.addWidget(item)
            line = pqtutil.h_line()
            line.setFixedHeight(1)
            self.notificationsLayout.addWidget(line)

            notification.viewed = True
            notification.modified = datetime.datetime.now()
            notification.save()


class NotificationButton(QtWidgets.QPushButton):
    def __init__(self, userObject=None):
        super(NotificationButton, self).__init__()
        self.handler = mongorm.getHandler()
        self.filter = mongorm.getFilter()
        self.interface = self.handler['notification']
        self.userObject = userObject
        self.setFixedSize(32, 32)
        self.setIcon(QtGui.QIcon(icon_paths.ICON_BELL_LRG))
        self.setIconSize(QtCore.QSize(24, 24))
        self.setStyleSheet("""
            QPushButton,
            QPushButton:pressed
            QPushButton:hover{
                border: none;
                background: none;
                border-radius: 0px;
            }
        """)
        self.setCursor(QtCore.Qt.PointingHandCursor)

        self.notificationCountLabel = QtWidgets.QLabel()
        self.notificationCountLabel.setFixedSize(14, 14)
        self.notificationCountLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.notificationCountLabel.setStyleSheet("""
            QLabel{
                font: bold 12px;
                border-radius: 7px;
                border: 2px solid #2B2B2B;
                background: red;
            }
        """)
        self.notificationCountLabel.move(16, 3)
        self.notificationCountLabel.setParent(self)

        self.notificationThread = NotificationThread(userObject=self.userObject, parent=self)
        self.notificationThread.notificationReceived.connect(self.notificationReceived)
        self.notificationThread.start()

        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

        self.filter.search(self.interface, receiver_uuid=self.userObject.getUuid())
        all_notifications = self.interface.all(self.filter)

        if False in set([notification.get("viewed") for notification in all_notifications]):
            self.hasUnviewed = True
        else:
            self.hasUnviewed = False

    @property
    def hasUnviewed(self):
        return self._hasUnviewed

    @hasUnviewed.setter
    def hasUnviewed(self, value):
        if value:
            self.notificationCountLabel.show()
        else:
            self.notificationCountLabel.hide()

        self._hasUnviewed = value

    def mousePressEvent(self, event):
        super(NotificationButton, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.LeftButton:
            self.hasUnviewed = False
            self.customContextMenuRequested.emit(event.pos())

    def contextMenu(self, event):
        self._menu = NotificationMenu(userObject=self.userObject, parent=self)
        globalPoint = self.mapToGlobal(self.rect().bottomRight())
        globalPoint.setX(globalPoint.x() - self._menu.width())
        globalPoint.setY(globalPoint.y() + 5)
        self.main_action = self._menu.exec_(globalPoint)

    def notificationReceived(self, dataObject):
        self.hasUnviewed = True
