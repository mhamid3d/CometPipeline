from qtpy import QtWidgets, QtGui, QtCore
from pipeicon import icon_paths


class AvatarLabel(QtWidgets.QLabel):
    def __init__(self, size=32, data=icon_paths.ICON_USER_LRG):
        super(AvatarLabel, self).__init__()
        self.setAlignment(QtCore.Qt.AlignCenter)
        self._radius = size / 2
        self.setFixedSize(self._radius * 2, self._radius * 2)
        self.setStyleSheet("""
            QLabel{
                background: #1e1e1e;
                border-radius: %spx;
                border: none;
                padding: 0px;
            }
        """ % self._radius)
        self.data = data
        self.load(data)

    def load(self, data):
        self.data = data
        if isinstance(self.data, QtCore.QByteArray):
            self.setFromData(self.data)
        elif isinstance(self.data, str) or isinstance(self.data, unicode):
            self.setFromPath(self.data)

    def setFromData(self, data):
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(data)

        if pixmap.isNull():
            pixmap = QtGui.QPixmap(icon_paths.ICON_USER_LRG)

        self.imgPixmap = pixmap.scaled(
            self._radius * 2, self._radius * 2, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)

    def setFromPath(self, path):
        self.imgPixmap = QtGui.QPixmap(path).scaled(
            self._radius * 2, self._radius * 2, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)

    def paintEvent(self, event):
        self.target = QtGui.QPixmap(self.size())
        self.target.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(self.target)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        path = QtGui.QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self._radius, self._radius)
        painter.setClipPath(path)
        # print self.imgPixmap.size()
        painter.drawPixmap(0, 0, self.imgPixmap)
        self.setPixmap(self.target)
        super(AvatarLabel, self).paintEvent(event)
