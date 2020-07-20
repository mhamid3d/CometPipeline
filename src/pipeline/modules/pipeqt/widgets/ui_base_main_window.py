from qtpy import QtWidgets, QtGui, QtCore


class BaseMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(BaseMainWindow, self).__init__()
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.mainLayout)
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)

        self.setup_window()

    def setup_window(self):
        self.create_widgets()
        self.create_layouts()
        self.edit_widgets()
        self.build_layouts()
        self.setup_styles()
        self.handle_signals()

    def create_widgets(self):
        pass

    def create_layouts(self):
        pass

    def edit_widgets(self):
        pass

    def build_layouts(self):
        pass

    def setup_styles(self):
        pass

    def handle_signals(self):
        pass