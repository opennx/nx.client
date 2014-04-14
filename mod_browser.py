#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial

from firefly_view import *
from nx.objects import Asset
from dlg_sendto import SendTo

DEFAULT_HEADER_DATA = ["content_type", "title", "duration", "id_folder", "origin"]

class BrowserModel(NXViewModel):
    def browse(self, **kwargs):
        start_time = time.time()
        self.beginResetModel()

        self.object_data = []
        
        if "view" in kwargs:
            self.header_data = config["views"][kwargs["view"]][2]
        else:
            self.header_data =  DEFAULT_HEADER_DATA

        res, data = query("browse", kwargs)
        if success(res) and "asset_data" in data:    
            for adata in data["asset_data"]:
                self.object_data.append(Asset(from_data=adata))

        self.endResetModel()
        self.parent.status("Got %d assets in %.03f seconds." % (len(self.object_data), time.time()-start_time))


    def flags(self,index):
        flags = super(BrowserModel, self).flags(index)
        if index.isValid():
            if self.object_data[index.row()]["id_object"]:
             flags |= Qt.ItemIsEditable
             flags |= Qt.ItemIsDragEnabled # Itemy se daji dragovat
        return flags


    def mimeTypes(self):
        return ["application/nx.asset"]
     
   
    def mimeData(self, indexes):
        data        = [self.object_data[i] for i in set(index.row() for index in indexes if index.isValid())]
        encodedData = json.dumps([a.meta for a in data])
        mimeData = QMimeData()
        mimeData.setData("application/nx.asset", encodedData.encode("ascii"))

        try:
            urls =[QUrl.fromLocalFile(asset.get_file_path()) for asset in data]
            mimeData.setUrls(urls)
        except:
            pass

        return mimeData

    def dropMimeData(self, data, action, row, column, parent):
        #TODO: UPLOAD
        return False
   



class SearchWidget(QLineEdit):
    def __init__(self, parent):
        super(QLineEdit, self).__init__()
        self.parent = parent

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return,Qt.Key_Enter]:
            if event.modifiers() & Qt.ControlModifier:
                print ("extend search")
                #self.parent.OnSearch(extend=True)
            else:
                self.parent.search_query["fulltext"] = self.line_edit.text()
                self.parent.browse()
            return

        elif event.key() == Qt.Key_Escape:
            self.line_edit.setText("")

        elif event.key() == Qt.Key_Down:
            self.parent.view.setFocus()

        QLineEdit.keyPressEvent(self.line_edit, event)


class SearchBox(QWidget):
    def __init__(self,parent):
        super(SearchBox, self).__init__()
        self.parent = parent


        self.btn_view = QPushButton()
        self.btn_view.setIcon(QIcon(pixlib["menu"]))

        self.btn_clear = QPushButton()
        self.btn_clear.setIcon(QIcon(pixlib["cancel"]))

        self.btn_search = QPushButton()
        self.btn_search.setIcon(QIcon(pixlib["search"]))


        self.line_edit =  QLineEdit()
        self.line_edit.setPlaceholderText ("type something...")
        self.line_edit.keyPressEvent = self.line_keyPressEvent

        layout = QHBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(0,4,0,0)

        layout.addWidget(self.btn_view,0)
        layout.addWidget(self.line_edit,1)
        layout.addWidget(self.btn_clear,0)
        layout.addWidget(self.btn_search,0)
        self.setLayout(layout)





class Browser(BaseWidget):
    def __init__(self, parent):
        super(Browser, self).__init__(parent)
        self.parent = parent

        self.parent.setWindowTitle("Browser")
        
        self.search_query = {}
        self.column_widths = {}

        self.search_box = SearchWidget(self)

        self.view = NXView(self)
        self.view.setSortingEnabled(True)
        self.view.setItemDelegate(MetaEditItemDelegate(self.view))
        self.view.activated.connect(self.on_activate)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.model       = BrowserModel(self) 
        self.sort_model  = NXSortModel(self.model)
        self.view.setModel(self.sort_model)
        self.view.selectionChanged = self.selectionChanged



        action_clear = QAction(QIcon(pixlib["search_clear"]), '&Clear search query', parent)        

        self.action_search = QMenu("Views")
        self.action_search.menuAction().setIcon(QIcon(pixlib["search"]))
        self.action_search.menuAction().triggered.connect(self.browse)
        self.load_view_menu()

        toolbar = QToolBar()
        toolbar.addWidget(self.search_box)
        toolbar.addAction(action_clear)
        toolbar.addAction(self.action_search.menuAction())

        layout = QVBoxLayout()
        layout.setContentsMargins(2,2,2,2)
        layout.setSpacing(5)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.view, 1)
        self.setLayout(layout)

        
    def load_view_menu(self):
        for id_view in sorted(config["views"].keys(), key=lambda k: config["views"][k][0]):

            pos, title, columns = config["views"][id_view]

            if title == "-":
                self.action_search.addSeparator()
                continue

            action = QAction(title, self)
            action.triggered.connect(partial(self.set_view, id_view))
            self.action_search.addAction(action)



    def set_view(self, id_view):
        self.browse(view=id_view)


    def browse(self,**kwargs):
        if self.model.header_data:
            self.saveColumnWidths()
        self.search_query.update(kwargs)
        self.model.browse(**self.search_query)
        self.loadColumnWidths()
 
    def on_activate(self,mi):
        self.view.do_edit(mi)


    def send_to(self):
        dlg = SendTo(self, self.view.selected_objects)
        dlg.exec_()

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




    def contextMenuEvent(self, event):
        if not self.view.selected_objects: return
        menu = QMenu(self)
        
        menu.addSeparator()
        action_send_to = QAction('&Send to...', self)        
        action_send_to.setStatusTip('Create action for selected asset(s)')
        action_send_to.triggered.connect(self.send_to)
        menu.addAction(action_send_to)
                
        menu.exec_(event.globalPos()) 



    def selectionChanged(self, selected, deselected):
        rows = []
        self.view.selected_objects = []

        tot_dur = 0

        for idx in self.view.selectionModel().selectedIndexes():
            row      =  self.sort_model.mapToSource(idx).row()
            if row in rows: 
                continue
            rows.append(row)
            obj = self.model.object_data[row]
            self.view.selected_objects.append(obj)
            if obj.object_type in ["asset", "item"]:
                tot_dur += obj.get_duration()

        if self.view.selected_objects:
            self.parent.parent.focus(self.view.selected_objects)
            if len(self.view.selected_objects) > 1 and tot_dur:
                self.status("{} objects selected. Total duration {}".format(len(self.view.selected_objects), s2time(tot_dur) ))

        super(NXView, self.view).selectionChanged(selected, deselected)

