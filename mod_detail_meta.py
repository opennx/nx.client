from firefly_common import *
from firefly_widgets import *

def format_header(key):
    return meta_types.tag_alias(key, config.get("language","en-US")) 

class MetaViewModel(QAbstractTableModel):
    def __init__(self, parent):
        super(MetaViewModel, self).__init__(parent)
        self.object_data     = []

    def rowCount(self, parent):    
        return len(self.object_data)   

    def columnCount(self, parent): 
        return 1

    def headerData(self, idx, orientation=Qt.Vertical, role=Qt.DisplayRole):
        if orientation == Qt.Vertical and role == Qt.DisplayRole: 
            return format_header(self.object_data[idx][0])
        
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return ["value"]    

    def data(self, index, role=Qt.DisplayRole): 
        if not index.isValid(): 
            return None 

        row = index.row()
        col = index.column()
        tag, val  = self.object_data[row]
          
        if role == Qt.DisplayRole:
            return val

        return None




class MetaView(QTableView):
    def __init__(self, parent):
        super(MetaView, self).__init__(parent)
        self.setStyleSheet(base_css)
        self.verticalHeader().setVisible(True)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True);
        self.setWordWrap(False)
        self.setSelectionMode(self.ExtendedSelection)
        
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.activated.connect(self.on_activate)

        self.model = MetaViewModel(self) 
        self.setModel(self.model)
  



    def load(self, objects):
        self.model.beginResetModel()
        tags = set([tag for obj in objects for tag in obj.meta])
        self.model.object_data = []
        for tag in sorted(tags):
            s = set([obj[tag] for obj in objects])
            s = list(s)
            if len(s) == 1:
                try:
                    value = str(s[0])
                except:
                    value = s[0].encode("utf-8")
            else:
                value = ">>>MULTIPLE VALUES<<<"


            self.model.object_data.append((tag, value))
        self.model.endResetModel()

    def on_activate(self):
        pass