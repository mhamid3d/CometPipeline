import shutil

from qtpy import QtWidgets, QtCore, QtGui
import tempfile
import sys
import os


class ScreenGrabber(QtWidgets.QDialog):

    def __init__(self, parent=None, squareAspectRatio=False):
        super(ScreenGrabber, self).__init__(parent)

        self._opacity = 1
        self._click_pos = None
        self._capture_rect = QtCore.QRect()
        self._hide_cursor = False
        self._squareAspectRatio = squareAspectRatio

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.CustomizeWindowHint
            | QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setCursor(QtCore.Qt.CrossCursor)
        self.setMouseTracking(True)

        desktop = QtWidgets.QApplication.desktop()
        desktop.resized.connect(self._fit_screen_geometry)
        desktop.screenCountChanged.connect(self._fit_screen_geometry)

    @property
    def capture_rect(self):
        return self._capture_rect

    def paintEvent(self, event):
        mouse_pos = self.mapFromGlobal(QtGui.QCursor.pos())
        click_pos = None
        if self._click_pos is not None:
            click_pos = self.mapFromGlobal(self._click_pos)
            if self._squareAspectRatio:
                mx = mouse_pos.x() - click_pos.x()
                my = mouse_pos.y() - click_pos.y()
                mmax = max([mx, my])
                mouse_pos = QtCore.QPoint(click_pos.x() + mmax, click_pos.y() + mmax)

        painter = QtGui.QPainter(self)

        painter.setBrush(QtGui.QColor(0, 0, 0, self._opacity))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(event.rect())

        if click_pos is not None:
            capture_rect = QtCore.QRect(click_pos, mouse_pos)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
            painter.drawRect(capture_rect)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)

        pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 64), 1, QtCore.Qt.DotLine)
        painter.setPen(pen)

        if not self._hide_cursor:

            if click_pos is not None:
                painter.drawLine(
                    event.rect().left(), click_pos.y(), event.rect().right(), click_pos.y()
                )
                painter.drawLine(
                    click_pos.x(), event.rect().top(), click_pos.x(), event.rect().bottom()
                )

            painter.drawLine(
                event.rect().left(), mouse_pos.y(), event.rect().right(), mouse_pos.y()
            )
            painter.drawLine(
                mouse_pos.x(), event.rect().top(), mouse_pos.x(), event.rect().bottom()
            )

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._click_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self._click_pos is not None:
            globalPos = event.globalPos()
            if self._squareAspectRatio:
                mx = globalPos.x() - self._click_pos.x()
                my = globalPos.y() - self._click_pos.y()
                mmax = max([mx, my])
                globalPos = QtCore.QPoint(self._click_pos.x() + mmax, self._click_pos.y() + mmax)
            self._capture_rect = QtCore.QRect(self._click_pos, globalPos).normalized()
            self._click_pos = None
        self._set_opacity(0)
        self._hide_cursor = True
        self.update()
        QtCore.QTimer.singleShot(1000, self.close)

    def mouseMoveEvent(self, event):
        self.repaint()

    @classmethod
    def screen_capture(cls, squareAspectRatio=False):

        tool = ScreenGrabber(squareAspectRatio=squareAspectRatio)
        tool.exec_()

        return tool.capture_rect

    def showEvent(self, event):
        self._fit_screen_geometry()

        fade_anim = QtCore.QPropertyAnimation(self, b"_opacity_anim_prop", self)
        fade_anim.setStartValue(self._opacity)
        fade_anim.setEndValue(127)
        fade_anim.setDuration(300)
        fade_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        fade_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def _set_opacity(self, value):
        self._opacity = value
        self.repaint()

    def _get_opacity(self):
        return self._opacity

    _opacity_anim_prop = QtCore.Property(int, _get_opacity, _set_opacity)

    def _fit_screen_geometry(self):
        desktop = QtWidgets.QApplication.desktop()
        workspace_rect = QtCore.QRect()
        for i in range(desktop.screenCount()):
            workspace_rect = workspace_rect.united(desktop.screenGeometry(i))
        self.setGeometry(workspace_rect)


class ScreenShotTool(QtWidgets.QDialog):
    def __init__(self, parent=None, format='png', versionObject=None):
        super(ScreenShotTool, self).__init__(parent)
        self.setWindowTitle("Capture Asset Screenshot")
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.buttonsLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.buttonsLayout)
        self.captureButton = QtWidgets.QPushButton("Capture")
        self.useLastVersionButton = QtWidgets.QPushButton("Use Last Available")
        self.useLastVersionButton.setDisabled(True)
        self.captureButton.setFixedSize(120, 64)
        self.useLastVersionButton.setFixedSize(120, 64)
        self.buttonsLayout.addWidget(self.captureButton)
        self.buttonsLayout.addWidget(self.useLastVersionButton)
        self.captureButton.clicked.connect(self.capture)
        self.useLastVersionButton.clicked.connect(self.useLastVersion)
        self.squareAspectRatio = QtWidgets.QCheckBox("Square Thumbnail")
        self.squareAspectRatio.setChecked(True)
        self.mainLayout.addWidget(self.squareAspectRatio)

        self.pix = None
        self._outputPath = None
        self._format = format
        self._lastAvailable = None
        self._versionObject = versionObject

        if self._versionObject:
            package = self._versionObject.parent()
            allVersions = package.children()
            for version in allVersions:
                if version.get("thumbnail") and os.path.exists(version.get("thumbnail")):
                    self.useLastVersionButton.setEnabled(True)
                    self._lastAvailable = version.get("thumbnail")

    @property
    def outputPath(self):
        return self._outputPath

    def useLastVersion(self):
        if not self._lastAvailable:
            self.useLastVersionButton.setDisabled(True)
            return
        self._outputPath = tempfile.NamedTemporaryFile(
                suffix=".{}".format(self._format), prefix="cmt_gaze_", delete=False
            ).name
        shutil.copy(self._lastAvailable, self._outputPath)
        self.close()

    def capture(self):
        self.captureButton.setDisabled(True)

        rect = ScreenGrabber.screen_capture(squareAspectRatio=self.squareAspectRatio.isChecked())

        desktop_id = QtWidgets.QApplication.desktop().winId()
        x_y_w_h = rect.x(), rect.y(), rect.width(), rect.height()

        screen = QtWidgets.QApplication.primaryScreen()
        pixmap = screen.grabWindow(desktop_id, *x_y_w_h)

        self.pix = pixmap
        self.displayResult()

    def displayResult(self):
        if not self.pix:
            return
        diag = QtWidgets.QDialog()
        diag.setWindowTitle("Preview Result")
        lyt = QtWidgets.QVBoxLayout()
        diag.setLayout(lyt)
        label = QtWidgets.QLabel()
        label.setPixmap(self.pix)
        lyt.addWidget(label)
        btnBox = QtWidgets.QDialogButtonBox()
        acceptButton = QtWidgets.QPushButton("Accept")
        retakeButton = QtWidgets.QPushButton("Retake")
        btnBox.addButton(acceptButton, QtWidgets.QDialogButtonBox.AcceptRole)
        btnBox.addButton(retakeButton, QtWidgets.QDialogButtonBox.RejectRole)
        acceptButton.clicked.connect(diag.accept)
        retakeButton.clicked.connect(diag.reject)
        lyt.addWidget(btnBox)
        result = diag.exec_()
        if result:
            self.saveCapture()
            self.close()
        else:
            self.pix = None
            self._outputPath = None
            self.captureButton.setEnabled(True)

    def saveCapture(self, output_path=None):
        if output_path is None:
            output_path = tempfile.NamedTemporaryFile(
                suffix=".{}".format(self._format), prefix="cmt_gaze_", delete=False
            ).name
        self.pix.save(output_path)
        self._outputPath = output_path


if __name__ == '__main__':
    import qdarkstyle
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win = ScreenShotTool()
    win.show()
    sys.exit(app.exec_())
