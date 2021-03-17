from qtpy import QtCore, QtGui
from cometqt.modelview.model_item import ModelItem
from cometqt.modelview.datasource.abstract_datasource import AbstractDataSource
from cometqt.modelview import common as mvcommon
from collections import OrderedDict, defaultdict
from cometqt.widgets.ui_user_avatar import AvatarLabel
from pipeicon import icon_paths, util as iconutil
import mongorm


class PackageDataSource(AbstractDataSource):
    def __init__(self):
        self._columnNameMap = OrderedDict([
            ('label', {'display': 'Package Name', 'icon': icon_paths.ICON_PACKAGE_LRG}),
            # ('thumbnail', {'display': 'Thumbnail', 'icon': icon_paths.ICON_IMAGE_LRG}),
            ('modified', {'display': 'Modified', 'icon': icon_paths.ICON_CLOCK_LRG}),
            ('created', {'display': 'Created', 'icon': icon_paths.ICON_CLOCK_LRG}),
            ('format', {'display': 'Format', 'icon': icon_paths.ICON_FILE_LRG}),
            ('comment', {'display': 'Comment', 'icon': icon_paths.ICON_COMMENT_LRG}),
            ('framerange', {'display': 'Frame Range', 'icon': icon_paths.ICON_FRAMERANGE_LRG}),
            ('created_by', {'display': 'Created By', 'icon': icon_paths.ICON_USER_LRG})
        ])
        super(PackageDataSource, self).__init__(interfaceName='package', columnNames=[x['display'] for x in self._columnNameMap.values()])
        self.setLoadMethod(self.LOAD_METHOD_PAGINATED)
        self.setLazyLoadChildren(True)
        self.leafInterface = "Content"
        self.specialTypesMap = {
            'label': self.configure_label,
            'created': self.configure_created,
            'modified': self.configure_modified,
            'created_by': self.configure_user
        }
        self._propogateUpFields = [
            'comment'
        ]

    def propogateDataUp(self, dataObject, field):
        latestChild = dataObject.latest()
        if latestChild:
            return latestChild.get(field)
        else:
            return None

    def _createHeaderItem(self, columnNames):
        headerItem = ModelItem(len(self._columnNameMap.keys()))
        for i, columnData in enumerate(self._columnNameMap.items()):
            headerItem.setData(columnData[1]['display'], i, QtCore.Qt.DisplayRole)
            headerItem.setData(QtGui.QPixmap(columnData[1]['icon']), i, QtCore.Qt.DecorationRole)
            headerItem.setData(columnData[0], i, self.ROLE_COLUMN_FIELD)
        return headerItem

    def configure_user(self, dataObject):
        data = []
        user_uuid = dataObject.get("created_by")
        handler = mongorm.getHandler()
        flt = mongorm.getFilter()
        flt.search(handler['user'], uuid=user_uuid)
        user_object = handler['user'].one(flt)
        if not user_object:
            return []
        data.append((QtCore.Qt.DisplayRole, user_object.fullName()))

        userIcon = AvatarLabel(size=20, data=QtCore.QByteArray(user_object.avatar.read()))

        data.append((QtCore.Qt.DecorationRole, userIcon.getRounded()))

        return data

    def configure_label(self, dataObject):
        data = []

        status_icon_map = {
            'pending': icon_paths.ICON_INPROGRESS_LRG,
            'approved': icon_paths.ICON_CHECKGREEN_LRG,
            'declined': icon_paths.ICON_XRED_LRG
        }

        if dataObject.interfaceName() == "Package":
            pixmap = QtGui.QPixmap(iconutil.dataObjectToIcon(dataObject))
            pixmap = pixmap.scaledToHeight(16, QtCore.Qt.SmoothTransformation)
            compPixmap = QtGui.QPixmap(pixmap.width() + 32, pixmap.height())
            compPixmap.fill(QtGui.QColor(0, 0, 0, 0))

            painter = QtGui.QPainter(compPixmap)
            painter.drawPixmap(QtCore.QPoint(0, 0), pixmap)

            number = dataObject.childCount()
            painter.setPen(QtGui.QPen(QtGui.QColor("white")))
            painter.drawText(16, 16, str(number))

            latestChild = dataObject.latest()
            if latestChild:
                statusIconPath = status_icon_map[latestChild.get("status")]
            else:
                statusIconPath = icon_paths.ICON_XRED_LRG
            statusIcon = QtGui.QPixmap(statusIconPath)
            statusIcon = statusIcon.scaledToHeight(16, QtCore.Qt.SmoothTransformation)
            painter.drawPixmap(QtCore.QPoint(32, 0), statusIcon)

            painter.end()

            data.append((QtCore.Qt.DecorationRole, compPixmap))
            data.append((QtCore.Qt.DisplayRole, str(dataObject.get("label"))))

        elif dataObject.interfaceName() == "Version":
            pixmap = QtGui.QPixmap(iconutil.dataObjectToIcon(dataObject))
            pixmap = pixmap.scaledToHeight(16, QtCore.Qt.SmoothTransformation)
            compPixmap = QtGui.QPixmap(pixmap.width() + 32, pixmap.height())
            compPixmap.fill(QtGui.QColor(0, 0, 0, 0))

            painter = QtGui.QPainter(compPixmap)
            painter.drawPixmap(QtCore.QPoint(0, 0), pixmap)

            statusIcon = QtGui.QPixmap(status_icon_map[dataObject.get("status")])
            statusIcon = statusIcon.scaledToHeight(16, QtCore.Qt.SmoothTransformation)
            painter.drawPixmap(QtCore.QPoint(32 - 4, 0), statusIcon)

            painter.end()

            data.append((QtCore.Qt.DecorationRole, compPixmap))
            data.append((QtCore.Qt.DisplayRole, str(dataObject.get("label"))))

        elif dataObject.interfaceName() == "Content":
            pixmap = QtGui.QPixmap(iconutil.dataObjectToIcon(dataObject))
            pixmap = pixmap.scaledToHeight(16, QtCore.Qt.SmoothTransformation)

            data.append((QtCore.Qt.DecorationRole, pixmap))
            data.append((QtCore.Qt.DisplayRole, str(dataObject.get("label"))))

        return data

    def configure_created(self, dataObject):
        targetObject = dataObject

        if dataObject.interfaceName() == "Package":
            latest = dataObject.latest()
            if latest:
                targetObject = latest

        return mvcommon.configure_date(targetObject.get("created"))

    def configure_modified(self, dataObject):
        targetObject = dataObject

        if dataObject.interfaceName() == "Package":
            latest = dataObject.latest()
            if latest:
                targetObject = latest

        return mvcommon.configure_date(targetObject.get("modified"))

    def getNewItemData(self, dataObject):
        itemData = defaultdict(dict)

        for idx, field in enumerate(self._columnNameMap.keys()):
            if field in mvcommon.DB_FIELD_TYPE_MAP:
                itemData[idx][mvcommon.ROLE_DATA_TYPE] = mvcommon.DB_FIELD_TYPE_MAP[field]

            field_value = dataObject.get(field)
            if field in self._propogateUpFields and dataObject.interfaceName() == "Package":
                field_value = self.propogateDataUp(dataObject, field)

            if field in self.specialTypesMap:
                for role, value in self.specialTypesMap[field](dataObject):
                    itemData[idx][role] = value
            elif field in mvcommon.DB_FIELD_TYPE_MAP and mvcommon.DB_FIELD_TYPE_MAP[field] in mvcommon.DB_FIELD_READABLE_MAP:
                data = mvcommon.DB_FIELD_READABLE_MAP[mvcommon.DB_FIELD_TYPE_MAP[field]](field_value)
                for role, value in data:
                    itemData[idx][role] = value
            else:
                itemData[idx][QtCore.Qt.DisplayRole] = str(field_value) if field_value else None

        for col, data in list(itemData.items()):
            for role, value in list(data.items()):
                if not value:
                    itemData[col][role] = ""
                itemData[col][QtCore.Qt.ToolTipRole] = itemData[col][QtCore.Qt.DisplayRole]

        stateColorMap = {
            'working': QtGui.QColor("orange"),
            'failed': QtGui.QColor("red"),
        }

        if dataObject.interfaceName() == "Package":
            state = self.propogateDataUp(dataObject, "state")
            if state and state in stateColorMap:
                for col in itemData.keys():
                    itemData[col][QtCore.Qt.TextColorRole] = stateColorMap[state]

        return itemData

    def makeItems(self, dataContainer):
        items = []
        for dataObject in dataContainer:

            item = ModelItem(len(self._headerItem),
                             uuid=dataObject.getUuid(),
                             dataObject=dataObject,
                             itemData=self.getNewItemData(dataObject))

            if dataObject.interfaceName() == self.leafInterface:
                item.setTotalChildCount(0)

            items.append(item)

        return items

    def canFetchMore(self, parentIndex):
        if not self._lazyLoadChildren or not parentIndex.isValid():
            return False
        item = self._model.itemFromIndex(parentIndex)

        return item.totalChildCount() < 0

    def fetchMore(self, parentIndex):
        item = self._model.itemFromIndex(parentIndex)
        if item is None:
            return
        children = item.dataObject.children()
        item.setTotalChildCount(children.size())
        if item.totalChildCount() == 0:
            return

        self._model.appendItems(self.makeItems(children), parentIndex)