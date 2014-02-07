#!/usr/bin/env python
# -*- coding: utf-8 -*-

from firefly_view import *
from nx.assets import *


class BrowserModel(NXViewModel):
    def browse(self, **kwargs):
        start_time = time.time()
        self.beginResetModel()
        result, data = query("browse",kwargs)
        self.object_data = []
        if result >= 300:
            print ("error message")
        else:
            if "asset_data" in data:
                for adata in data["asset_data"]:
                    self.object_data.append(Asset(from_data=adata))
                self.header_data = ["content_type", "title", "role/performer", "duration", "file/size"]

        self.endResetModel()
        self.parent.status("Got %d assets in %.03f seconds." % (len(self.object_data), time.time()-start_time))


    def flags(self,index):
        flags = super(BrowserModel, self).flags(index)
        if index.isValid():
            if self.object_data[index.row()]["id_object"]:
             #if self.parent.parent.edit_mode: 
             flags |= Qt.ItemIsEditable
             flags |= Qt.ItemIsDragEnabled # Itemy se daji dragovat
        return flags



class SearchBox(QWidget):
    def __init__(self,parent):
        super(SearchBox, self).__init__()
        self.parent = parent

        self.line_edit =  QLineEdit()
        self.line_edit.setPlaceholderText ("type something...")
        self.line_edit.keyPressEvent = self.line_keyPressEvent

        layout = QHBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(0,4,0,0)

        layout.addWidget(self.line_edit,1)
        self.setLayout(layout)

    def setText(self, text):
        self.line_edit.setText(text)

    def line_keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return,Qt.Key_Enter]:
            if event.modifiers() & Qt.ControlModifier:
                print ("extend search")
                #self.parent.OnSearch(extend=True)
            else:
                self.parent.search_query["fulltext"] = self.line_edit.text()
                self.parent.browse()
            return True
        elif event.key() == Qt.Key_Escape:
            self.line_edit.setText("")
        elif event.key() == Qt.Key_Down:
            self.parent.view.setFocus()
        return QLineEdit.keyPressEvent(self.line_edit, event)



class Browser(BaseWidget):
    def __init__(self, parent):
        super(Browser, self).__init__(parent)
        self.parent = parent

        self.parent.setWindowTitle("Browser")
        
        self.search_query = {}
        self.column_widths = {}

        self.search_box = SearchBox(self)

        self.view = NXView(self)
        self.view.setSortingEnabled(True)
        self.view.setItemDelegate(MetaEditItemDelegate(self.view))
        self.view.activated.connect(self.on_activate)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.view.editor_closed_at = time.time()

        self.model      = BrowserModel(self) 
        self.sortModel  = NXSortModel(self.model)
        self.view.setModel(self.sortModel)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5)
        layout.addWidget(self.search_box, 0)
        layout.addWidget(self.view, 1)
        self.setLayout(layout)

        
    def browse(self,**kwargs):
        if self.model.header_data:
            self.saveColumnWidths()
        self.search_query.update(kwargs)
        self.model.browse(**self.search_query)
        self.loadColumnWidths()
 
    def on_activate(self,mi):
        if time.time() - self.view.editor_closed_at > 0.2:
            self.view.edit(mi)


    def getState(self):
        self.saveColumnWidths()
        state = {}
        state["class"]  = "browser"
        state["search_query"]  = self.search_query
        state["column_widths"] = self.column_widths
        return state


    def setState(self, state):
        self.search_query = state.get("search_query", {})
        self.column_widths = state.get("column_widths", {})
        q = self.search_query.get("fulltext","")
        if q:
            self.search_box.setText(q)
        self.browse()


    def loadColumnWidths(self):
        for id_column in range(self.model.columnCount(False)):
            col_tag = self.model.header_data[id_column]
            w = self.column_widths.get(col_tag,False)
            if w:
                self.view.setColumnWidth(id_column, w) 
            else: 
                self.view.resizeColumnToContents(id_column)

    def saveColumnWidths(self):
        for id_column in range(self.model.columnCount(False)):
            self.column_widths[self.model.header_data[id_column]] = self.view.columnWidth(id_column)
        

    def hideEvent(self, event):
        self.saveColumnWidths()





