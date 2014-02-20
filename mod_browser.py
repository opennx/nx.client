#!/usr/bin/env python
# -*- coding: utf-8 -*-

from firefly_view import *
from nx.objects import Asset


class BrowserModel(NXViewModel):
    def browse(self, **kwargs):
        start_time = time.time()
        self.beginResetModel()

        self.object_data = []
        self.header_data = ["content_type", "title", "role/performer", "duration", "file/size","promoted"]
        
        res, data = query("browse",kwargs)
        if success(res) and "asset_data" in data:    
            for adata in data["asset_data"]:
                self.object_data.append(Asset(from_data=adata))

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


    def mimeTypes(self):
        return ["application/nx.asset"]
     
   
    def mimeData(self, indexes):
        data        = [self.object_data[i] for i in set(index.row() for index in indexes if index.isValid())]
        encodedData = json.dumps([a.meta for a in data])
        mimeData = QMimeData()
        mimeData.setData("application/nx.asset", encodedData)

        try:
            urls =[QUrl.fromLocalFile(asset.get_file_path()) for asset in data]
            mimeData.setUrls(urls)
        except:
            pass

        return mimeData

    def dropMimeData(self, data, action, row, column, parent):
        #TODO: UPLOAD
        return False
   




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

        self.model      = BrowserModel(self) 

        self.sort_model  = NXSortModel(self.model)
        self.view.setModel(self.sort_model)
        self.view.selectionChanged = self.selectionChanged

        layout = QVBoxLayout()
        layout.setContentsMargins(2,2,2,2)
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
        self.view.do_edit(mi)


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



    def selectionChanged(self, selected, deselected):     
        objects = []
        rows = []
        tot_dur = 0

        for idx in self.view.selectionModel().selectedIndexes():
            row      =  self.sort_model.mapToSource(idx).row()
            if row in rows: 
                continue
            rows.append(row)
            objects.append(self.model.object_data[row])
            

#            data = self.browser_view.model.arraydata[row]
#            dur      = float(data[1].get("Duration",0))
#            mark_in  = float(data[1].get("MarkIn",0))
#            mark_out = float(data[1].get("MarkOut",0))
#            if not dur: continue
#            if mark_out > 0: dur -= dur - mark_out
#            if mark_in  > 0: dur -= mark_in
#            tot_dur += dur

        if objects:
            self.parent.parent.focus(objects)

        super(NXView, self.view).selectionChanged(selected, deselected)

