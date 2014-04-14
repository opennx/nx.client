from firefly_common import *
from firefly_widgets import *



def format_header(tag):
    return {"id_service" : "#", 
            "agent" : "Agent", 
            "title" : "Title", 
            "host" : "Host", 
            "autostart" : "", 
            "loop_delay" : "LD", 
            "settings" : "Settings", 
            "state" : "State", 
            "last_seen" : "Last seen",
            "ctrl" : ""
            }[tag]

SVC_STATES = {
    0 : ["Stopped",        0x0000cc],
    1 : ["Running",        0x00cc00],
    2 : ["Starting",       0xcccc00],
    3 : ["Stopping",       0xcccc00],
    4 : ["Force stopping", 0xcc0000],
}

class ServiceViewModel(QAbstractTableModel):
    def __init__(self, parent):
        super(ServiceViewModel, self).__init__(parent)
        self.parent = parent
        self.object_data     = []
        self.header_data     = ["id_service", "agent", "host", "title", "state", "last_seen","autostart", "ctrl"]

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
                  
        if role == Qt.DisplayRole:
            if tag in ["autostart", "ctrl"]:
                return None
            elif tag == "state":
                return SVC_STATES[obj[tag]][0]
            elif tag == "last_seen":
                if not obj["state"]:
                    return None
                elif obj["last_seen"] < 10:
                    return "OK"
                return "UNR: {}".format(int(obj["last_seen"]))

            return obj[tag]

        elif role == Qt.DecorationRole:
            if tag == "autostart":
                return pixlib["autostart_on"] if obj["autostart"] else pixlib["autostart_off"]
            elif tag == "ctrl":
                return pixlib["shut_down"] if obj["state"] in [1,3] else pixlib["play"] if obj["state"] == 0 else None

        elif role == Qt.ForegroundRole:
            if tag == "state":
                return QBrush(QColor(SVC_STATES[obj[tag]][1]))

        return None



    def refresh(self):
        pass



class ServiceSortModel(QSortFilterProxyModel):
    def __init__(self, model):
        super(ServiceSortModel, self).__init__()
        self.setSourceModel(model)
        self.setDynamicSortFilter(True)
        self.setSortLocaleAware(True)

class ServiceView(QTableView):
    def __init__(self, parent):
        super(ServiceView, self).__init__(parent)
        self.setStyleSheet(base_css)
        self.verticalHeader().setVisible(False)
        self.setWordWrap(False)
        self.setSortingEnabled(True)
        self.setSelectionMode(self.NoSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(self.ExtendedSelection)
        
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.selected_services = []
        self.activated.connect(self.on_activate)

        self.model       = ServiceViewModel(self) 
        self.sort_model  = ServiceSortModel(self.model)
        self.setModel(self.sort_model)
  

    def selectionChanged(self, selected, deselected):
        self.selected_services = []

        for idx in self.selectionModel().selectedIndexes():
            row =  self.sort_model.mapToSource(idx).row()
            id_service = self.model.object_data[row]["id_service"]
            if id_service in self.selected_services: 
                continue
            self.selected_services.append(id_service)

        print (self.selected_services)
        super(QTableView, self).selectionChanged(selected, deselected)



 
    def on_activate(self,mi):
        row = self.sort_model.mapToSource(mi).row()
        col = self.sort_model.mapToSource(mi).column()
        svc = self.model.object_data[row]
        id_service = svc["id_service"]

        action = self.model.header_data[col]
        if action == "ctrl":
            cmd = {
                0 : 2,
                1 : 3,
                2 : 2,
                3 : 4,
                4 : 4
                }[svc["state"]]


            query("services", {"command":cmd, "id_service":id_service})
        








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



    def update_status(self, data):
        sstat = {}
        for svc in data.data["service_status"]:
            sstat[svc[0]] = svc[1:]

        self.view.model.beginResetModel()
        for svc in self.view.model.object_data:
            if svc["id_service"] not in sstat:
                continue
            svc["state"], svc["last_seen"] = sstat[svc["id_service"]]
            svc["last_seen"] = data.timestamp - svc["last_seen"]

        self.view.model.endResetModel()



