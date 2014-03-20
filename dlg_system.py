from firefly_common import *
from firefly_widgets import *



def format_header(tag):
    return {"id_service" : "#", 
            "agent" : "Agent", 
            "title" : "Title", 
            "host" : "Host", 
            "autostart" : "Autostart", 
            "loop_delay" : "LD", 
            "settings" : "Settings", 
            "state" : "State", 
            "last_seen" : "Last seen"
            }[tag]

class ServiceViewModel(QAbstractTableModel):
    def __init__(self, parent):
        super(ServiceViewModel, self).__init__(parent)
        self.parent = parent
        self.object_data     = []
        self.header_data     = ["id_service", "agent", "host", "title", "state"]

    def rowCount(self, parent):    
        return len(self.object_data)   

    def columnCount(self, parent): 
        return len(self.header_data) 

    def headerData(self, col, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole: 
            return format_header(self.header_data[col])
        return None

    def data(self, index, role=Qt.DisplayRole): 
        if not index.isValid(): 
            return None 

        row = index.row()
        col = index.column()
        tag = self.header_data[col]
        obj = self.object_data[row]
                  
        if   role == Qt.DisplayRole:
            return obj[tag]

        return None



    def refresh(self):
        pass



class ServiceSortModel(QSortFilterProxyModel):
    def __init__(self, model):
        super(ServiceSortModel, self).__init__()
        self.setSourceModel(model)
        self.setDynamicSortFilter(True)
        self.setSortLocaleAware(True)
        #self.setSortRole(Qt.UserRole)

class ServiceView(QTableView):
    def __init__(self, parent):
        super(ServiceView, self).__init__(parent)
        self.setStyleSheet(base_css)
        self.verticalHeader().setVisible(False)
        self.setWordWrap(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(self.ExtendedSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.editor_closed_at = time.time() 
        self.selected_objects = []

        self.model       = ServiceViewModel(self) 
        self.sort_model  = ServiceSortModel(self.model)
        self.setModel(self.sort_model)












class SystemDialog(QDialog):
    def __init__(self, parent):
        super(SystemDialog, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle("System manager")

        self.view = ServiceView(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(2,2,2,2)
        layout.addWidget(self.view)

        self.setLayout(layout)
        self.load_state()
        self.load()


    def load(self, q={}):
        res, data = query("services",q)
        self.view.model.beginResetModel()
        self.view.model.object_data = data
        self.view.model.endResetModel()



    def load_state(self):
        settings = ffsettings()
        if "global/system_dlg_geometry" in settings.allKeys():
            self.restoreGeometry(settings.value("global/system_dlg_geometry"))

        if "global/services_column_widths" in settings.allKeys():
            col_widths = settings.value("global/services_column_widths")
            for id_column in range(self.view.model.columnCount(False)):
                col_tag = self.view.model.header_data[id_column]
                w = col_widths.get(col_tag,False)
                if w:
                    self.view.setColumnWidth(id_column, w) 
                else: 
                    self.view.resizeColumnToContents(id_column)

    def save_state(self):
        settings = ffsettings()
        settings.setValue("global/system_dlg_geometry", self.saveGeometry())
        col_widths = {}
        for id_column in range(self.view.model.columnCount(False)):
            col_widths[self.view.model.header_data[id_column]] = self.view.columnWidth(id_column)
        settings.setValue("global/services_column_widths", col_widths)