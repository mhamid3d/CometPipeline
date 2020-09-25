# import mongorm
#
#
# handler = mongorm.getHandler()
# filter = mongorm.getFilter()
#
# filter.search(handler['entity'])
#
# all = handler['entity'].all(filter)
#
# for x in all:
#     x.delete()


from cometqt.widgets.ui_entity_viewer import EntityViewer


if __name__ == '__main__':
    import sys
    import mongorm
    from qtpy import QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    win = EntityViewer()
    h = mongorm.getHandler()
    f = mongorm.getFilter()
    f.search(h['job'], label='DELOREAN')
    job = h['job'].one(f)
    win.setCurrentJob(job)
    win.populate()
    win.setIsDialog(True)
    win.show()
    sys.exit(app.exec_())