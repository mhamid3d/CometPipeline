import sys
from qtpy.QtWidgets import *
from qtpy.QtCore import *

TEXT = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam malesuada tellus in ex elementum, vitae rutrum enim vestibulum."""

#==============================================================================
class Window(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        # Widgets
        self.label = QLabel(TEXT)
        self.label.setWordWrap(True)

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.label)
        # self.setMinimumSize(self.sizeHint())
        self.setMaximumWidth(250)
        self.show()



#==============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())