from qtpy import QtWidgets, QtGui, QtCore


class AnimatedPopupMessage(QtWidgets.QLabel):

    ERROR = "error"
    INFO = "info"
    WARNING = "warning"
    TIP = "tip"

    def __init__(self, message="Placeholder Text", type=INFO, parent=None, width=None, height=100):
        super(AnimatedPopupMessage, self).__init__()
        self.setParent(parent)
        self.setMessage(message)
        self._type = type
        self._width = width
        self._height = height
        if not self._width:
            self._width = self.parent().width()
        self.setAlignment(QtCore.Qt.AlignCenter)
        op = QtWidgets.QGraphicsOpacityEffect(self)
        op.setOpacity(0.85)
        self.setGraphicsEffect(op)
        self.setAutoFillBackground(True)
        self.colorMapping = {
            self.ERROR: {'color': 'white', 'background': '#bf2626'},
            self.INFO: {'color': 'black', 'background': '#d9d9d9'},
            self.WARNING: {'color': 'black', 'background': 'orange'},
            self.TIP: {'color': 'white', 'background': 'green'}
        }
        self.setStyleSheet("""
            QLabel{
                background: %s;
                color: %s;
                font-size: 14px;
            }
        """ % (self.colorMapping[self._type]['background'], self.colorMapping[self._type]['color']))
        self.setFixedSize(self._width, self._height)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.move(0, self.parent().height())
        self.hide()

        self.anim = QtCore.QPropertyAnimation(self, b"geometry")
        self.anim.finished.connect(lambda: self.hide() if self._should_hide else None)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reverse_anim)

    def setMessage(self, message):
        self.setText(message)

    def do_anim(self):
        self._should_hide = False
        self.show()
        self.raise_()
        self.anim.setDuration(200)
        self.anim.setStartValue(QtCore.QRect(0, self.parent().height(), self._width, self._height))
        self.anim.setEndValue(QtCore.QRect(0, self.parent().height() - self._height, self._width, self._height))
        self.anim.start()
        self.timer.start(2500)

    def reverse_anim(self):
        self._should_hide = True
        self.timer.stop()
        self.anim.stop()
        self.anim.setStartValue(QtCore.QRect(0, self.parent().height() - self._height, self._width, self._height))
        self.anim.setEndValue(QtCore.QRect(0, self.parent().height(), self._width, self._height))
        self.anim.start()
