from qtpy import QtWidgets, QtGui, QtCore
from top_header import TopHeaderView


class TreeDelegate(QtWidgets.QStyledItemDelegate):

    MARGIN = 10

    def __init__(self, view):
        super(TreeDelegate, self).__init__()
        self._view = view

    def sizeHint(self, option, index):
        hint = super(TreeDelegate, self).sizeHint(option, index)
        if hint:
            hint.setHeight(hint.height() + self.MARGIN)

        return hint

    def paint(self, painter, option, index):
        super(TreeDelegate, self).paint(painter, option, index)
        painter.save()
        gridColor = QtGui.QColor("#333333")
        painter.setPen(QtGui.QPen(gridColor, 0, QtCore.Qt.SolidLine))
        painter.drawLine(option.rect.right(), option.rect.top(), option.rect.right(), option.rect.bottom())
        painter.restore()


class TreeView(QtWidgets.QTreeView):

    LOCKED_COLUMNS = []

    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent=parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAnimated(True)
        self.setItemDelegate(TreeDelegate(self))
        self.setHeader(TopHeaderView(self))
        self.setSortingEnabled(True)
        self.expanded.connect(self._expanded)
        self.collapsed.connect(self._collapsed)
        self.setStyleSheet("""
            QTreeView{
                selection-background-color: transparent;
            }
            QTreeView::branch{
                border-image: none;
            }
        """)

    def _expanded(self, index):
        self._resizeColumnToContents(index.column())

    def _collapsed(self, index):
        self._resizeColumnToContents(index.column())

    def sizeHintForColumn(self, column):
        return QtWidgets.QTreeView.sizeHintForColumn(self, column) + 1

    def drawRow(self, painter, option, index):
        super(TreeView, self).drawRow(painter, option, index)

        painter.save()
        gridColor = QtGui.QColor("#333333")
        painter.setPen(QtGui.QPen(gridColor, 0, QtCore.Qt.SolidLine))
        linePadding = 0
        if self.model():
            linePadding = self.visualRect(index).left()
        painter.drawLine(option.rect.left() + linePadding, option.rect.bottom(), option.rect.right(), option.rect.bottom())
        painter.restore()

    def drawBranches(self, painter, rect, index):
        super(TreeView, self).drawBranches(painter, rect, index)

    def _resizeColumnToContents(self, columnIndex):
        topHeader = self.header()

        if not topHeader.isSectionHidden(columnIndex) and topHeader.sectionResizeMode(
                columnIndex) == QtWidgets.QHeaderView.Interactive:
            # change the resize mode to fit contents
            topHeader.setSectionResizeMode(columnIndex, QtWidgets.QHeaderView.ResizeToContents)
            # set size explicitly and restore the resize mode
            topHeader.resizeSection(columnIndex, topHeader.sectionSize(columnIndex))
            topHeader.setSectionResizeMode(columnIndex, QtWidgets.QHeaderView.Interactive)

    def _resizeAllColumnsToContents(self):
        for index in range(self.header().count()):
            self._resizeColumnToContents(index)


if __name__ == '__main__':
    import mongorm
    import sys
    import qdarkstyle
    from model import Model
    from datasource.package_datasource import PackageDataSource
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    win = TreeView()
    win.resize(1000, 1000)
    model = Model()
    model.setAlternatingRowColors(True)
    db = mongorm.getHandler()
    dataSource = PackageDataSource()
    model.setDataSource(dataSource)
    win.setModel(model)
    win._resizeAllColumnsToContents()
    win.show()
    sys.exit(app.exec_())
