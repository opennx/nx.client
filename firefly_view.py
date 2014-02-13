#!/usr/bin/env python
# -*- coding: utf-8 -*-

from firefly_common import *
from firefly_widgets import *

def format_header(key):
    return meta_types.col_alias(key, config.get("language","en-US")) 


class NXViewModel(QAbstractTableModel):
    def __init__(self, parent):
        super(NXViewModel, self).__init__(parent)
        self.parent = parent
        self.object_data  = []
        self.header_data = []


    def rowCount(self, parent):    
        return len(self.object_data)   

    def columnCount(self, parent): 
        return len(self.header_data) 

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole: 
            return format_header(self.header_data[col])
        return None


    def data(self, index, role): 
        if not index.isValid(): 
            return None 

        row = index.row()
        obj = self.object_data[row]
        tag = self.header_data[index.column()]
                  
        if   role == Qt.DisplayRole:     return obj.format_display(tag)
        elif role == Qt.ForegroundRole:  return QColor(obj.format_foreground(tag))
        elif role == Qt.BackgroundRole:  return QColor(obj.format_background(tag)) if obj.format_background(tag) else None
        elif role == Qt.EditRole:        return obj.format_edit(tag)
        elif role == Qt.UserRole:        return obj.format_sort(tag)
        elif role == Qt.DecorationRole:  return pixlib[obj.format_decoration(tag)]
        
        return None


    def setData(self, index, data, role=False):
        tag = self.header_data[index.column()] 
        self.object_data[index.row()][tag] = data
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



class NXView(QTableView):
    def __init__(self, parent):
        super(NXView, self).__init__(parent)

        self.setStyleSheet(base_css)

        self.verticalHeader().hide()
        self.setWordWrap(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(self.ExtendedSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.editor_closed_at = time.time() 

