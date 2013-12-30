#!/usr/bin/env python
# -*- coding: utf-8 -*-

from firefly_common import *

class BrowserModel(QAbstractTableModel):
    def __init__(self, parent):
        super(BrowserModel, self).__init__(parent)
        self.parent = parent
        self.asset_data  = []
        self.header_data = []

    def rowCount(self, parent):    
        return len(self.asset_data)   

    def columnCount(self, parent): 
        return len(self.header_data) 

    def browse(self, **kwargs):
        self.beginResetModel()
        result, data = query("browse",kwargs)
        if result >= 300:
            self.asset_data = []
        else:
            if "asset_data" in data:
                for a in data["asset_data"]:
                    self.asset_data.append(Asset(json = a))
                self.header_data = ["title", "role/performer", "duration", "file/size"]

        self.endResetModel()
        print "got %d assets" % len(self.asset_data)


    def data(self, index, role): 
        if not index.isValid(): 
            return None 

        row   = index.row()
        asset = self.asset_data[row]
        tag   = self.header_data[index.column()]
                  
        if   role == Qt.DisplayRole:     return asset.format_display(tag)
        elif role == Qt.ForegroundRole:  return asset.format_foreground(tag)
        elif role == Qt.EditRole:        pass
        elif role == Qt.UserRole:        return asset[tag] # sorting by raw data
        
        return None

    def flags(self,index):
        flags = super(BrowserModel, self).flags(index)
        if index.isValid():
            if self.asset_data[index.row()].id_asset:
             #if self.parent.parent.edit_mode: 
             #   flags |= Qt.ItemIsEditable
             flags |= Qt.ItemIsDragEnabled # Itemy se daji dragovat
        return flags
   
   
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole: 
            return meta_types.col_alias(self.header_data[col], config.get("language","en-US"))
        #if orientation == Qt.Vertical   and role == Qt.DisplayRole and self.parent.parent.show_asset_ids: 
        #    return str(self.arraydata[col][0][0])
        return None
 


class SortModel(QSortFilterProxyModel):
    def __init__(self, model):
        super(SortModel, self).__init__()
        self.setSourceModel(model)
        self.setDynamicSortFilter(True)
        self.setSortRole(Qt.UserRole)

class BrowserWidget(QTableView):
    def __init__(self, parent):
        super(BrowserWidget, self).__init__(parent)
        self.parent = parent

        self.is_editing = False
        self.editor_closed_at = 0 
        self.activated.connect(self.on_activate)
  
        self.model      = BrowserModel(self) 
        self.sortModel  = SortModel(self.model)
        self.setModel(self.sortModel)
  
        self.verticalHeader().hide()
        self.setWordWrap(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSortingEnabled(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(self.ExtendedSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        
    def browse(self,**kwargs):
        if self.model.header_data:
            self.saveColumnWidths()
        self.model.browse(**kwargs)
        self.loadColumnWidths()
 
    def on_activate(self,mi):
        print "activated"
        #if not self.parent.edit_mode:
        #   row =  self.proxyModel.mapToSource(mi).row()
        #   id_asset = self.model.arraydata[row][0][0]
        #   self.parent.OpenDetail(id_asset)
        #   return False   
        #else:
        #if time.time() - self.editor_closed_at > 0.2:
        #    self.edit(mi)
        #return True  

    def loadColumnWidths(self):
        for id_column in range(self.model.columnCount(False)):
            col_tag = self.model.header_data[id_column]
            w = app_state.get("col_widths",{}).get(col_tag,False)
            if w:
                self.setColumnWidth(id_column, w) 
            else:
                self.resizeColumnToContents(id_column)

    def saveColumnWidths(self):
        if not "col_widths" in app_state:
            app_state["col_widths"] = {}

        for id_column in range(self.model.columnCount(False)):
            app_state["col_widths"][self.model.header_data[id_column]] = self.columnWidth(id_column)
        
    def hideEvent(self, event):
        self.saveColumnWidths()



 
if __name__ == "__main__":
    app = Firestarter()

    wnd = QMainWindow()
    wnd.setStyleSheet(base_css)
    browser = BrowserWidget(wnd)
    wnd.setCentralWidget(browser)    
    browser.browse()
    
    wnd.show()

    app.start()