from qtpy import QtWidgets, QtGui, QtCore
from pipeicon import icon_paths


class TopHeaderView(QtWidgets.QHeaderView):
    def __init__(self, parent=None):
        super(TopHeaderView, self).__init__(QtCore.Qt.Horizontal, parent)
        self.setDefaultAlignment(QtCore.Qt.AlignLeft)
        self.setStyleSheet("""
            QHeaderView{
                background: transparent;
                font: bold 10pt;
                border-bottom: 1px solid #1e1e1e;
            }
            QHeaderView::section{
                background: transparent;
                margin: 4px 1px 4px 1px;
                color: #8e8e8e;
                border: none;
            }
            QHeaderView::down-arrow{
                background: transparent;
            }
            QHeaderView::up-arrow{
                background: transparent;
            }
        """)
        self.setSectionsMovable(True)
        self.setMinimumSectionSize(75)
        self.setStretchLastSection(True)
        self.setTextElideMode(QtCore.Qt.ElideRight)

    def paintEvent(self, e):
        super(TopHeaderView, self).paintEvent(e)
        style = self.styleSheet()
        self.setStyleSheet("")
        self.setStyleSheet(style)
