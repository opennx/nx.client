#!/usr/bin/env python
# -*- coding: utf-8 -*-

from firefly_common import *
from firefly_widgets import *

def format_header(key):
    return meta_types.col_alias(key, config.get("language","en-US")) 


class NXViewModel(QAbstractTableModel):
    def __init__(self, parent):
        super(NXViewModel, self).__init__(parent)
        self.object_data     = []
        self.header_data     = []
        self.changed_objects = []

        self.font_normal  = QFont()
        self.font_virtual = QFont()
        self.font_virtual.setItalic(True)
        

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
        obj = self.object_data[row]
        obj.model = self
        tag = self.header_data[index.column()]
                  
        if   role == Qt.DisplayRole:     return obj.format_display(tag)
        elif role == Qt.ForegroundRole:  return QColor(obj.format_foreground(tag))
        elif role == Qt.BackgroundRole:  
            bkg = obj.format_background(tag, self)
            if bkg: 
                return QColor(bkg)
        elif role == Qt.EditRole:        return obj.format_edit(tag)
        elif role == Qt.UserRole:        return obj.format_sort(tag)
        elif role == Qt.DecorationRole:  return pixlib[obj.format_decoration(tag)]
        elif role == Qt.ToolTipRole:     return str(obj.meta)
       # elif role == Qt.FontRole:        return self.font_normal #if obj.id  else self.font_virtual
        
        return None


    def setData(self, index, data, role=False):
        tag = self.header_data[index.column()] 
        id_object = self.object_data[index.row()].id
        self.object_data[index.row()][tag] = data
        
        if not id_object in self.changed_objects:
            self.changed_objects.append(id_object)
        
        self.model.dataChanged.emit(index, index)
        self.update()

        self.refresh()
        return True

    def refresh(self):
        pass


class NXSortModel(QSortFilterProxyModel):
    def __init__(self, model):
        super(NXSortModel, self).__init__()
        self.setSourceModel(model)
        self.setDynamicSortFilter(True)
        self.setSortLocaleAware(True)
        self.setSortRole(Qt.UserRole)

    @property 
    def object_data(self):
        return self.sourceModel().object_data




class NXView(QTableView):
    def __init__(self, parent):
        super(NXView, self).__init__(parent)
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
        self.focus_enabled = True

    def do_edit(self, mi):
        if time.time() - self.editor_closed_at > 0.1:
            self.edit(mi)
