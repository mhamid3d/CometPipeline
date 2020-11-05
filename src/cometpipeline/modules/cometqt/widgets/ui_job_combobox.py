from qtpy import QtWidgets, QtGui, QtCore
from pipeicon import icon_paths
import mongorm
import qdarkstyle


class JobComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super(JobComboBox, self).__init__(parent=parent)
        handler = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(handler['job'])
        self._all_jobs = handler['job'].all(filt)
        self.addItem("None")

        for job in self._all_jobs:
            item = self.addItem(QtGui.QIcon(icon_paths.ICON_COMETPIPE_SML), job.get("label"))

        self.setCurrentIndex(0)

    def setIndexFromDataObject(self, dataObject):

        if dataObject:
            index = self.findText(dataObject.get("label"))
            self.setCurrentIndex(index)
        else:
            self.setCurrentIndex(0)

    def getDataObjectFromIndex(self, index):

        if index == 0:
            return None

        itemText = self.itemText(index)

        handler = mongorm.getHandler()
        filt = mongorm.getFilter()
        filt.search(handler['job'], label=itemText)

        jobObject = handler['job'].one(filt)

        return jobObject

    def currentDataObject(self):
        return self.getDataObjectFromIndex(self.currentIndex())


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = JobComboBox()
    win.show()
    sys.exit(app.exec_())