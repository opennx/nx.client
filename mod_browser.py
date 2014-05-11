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
        
        try:
            self.header_data = config["views"][kwargs["view"]][2]
        except:
            self.header_data =  DEFAULT_HEADER_DATA

        res, data = query("browse", kwargs)
        if success(res) and "asset_data" in data:    
            for adata in data["asset_data"]:
                self.object_data.append(Asset(from_data=adata))

        self.endResetModel()
        self.parent().status("Got %d assets in %.03f seconds." % (len(self.object_data), time.time()-start_time))


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


    def setData(self, index, data, role=False):
        tag = self.header_data[index.column()] 
        value = data
        id_object = self.object_data[index.row()].id
        
        res, data = query("set_meta", {"id_object":id_object, "tag":tag, "value":value })

        if success(res):
            #self.beginResetModel()
            self.object_data[index.row()] = Asset(from_data=data)
            #self.endResetModel()
            self.dataChanged.emit(index, index)
        else:
            QMessageBox.error(self, "Error", "Unable to save")

        #self.object_data[index.row()][tag] = data
        #if not id_object in self.changed_objects:
        #    self.changed_objects.append(id_object)
        #self.endResetModel()

        #self.refresh()
        return True
   



class SearchWidget(QLineEdit):
    def __init__(self, parent):
        super(QLineEdit, self).__init__()

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return,Qt.Key_Enter]:
            if event.modifiers() & Qt.ControlModifier:
                print ("extend search")
                #self.parent().OnSearch(extend=True)
            else:
                self.parent().browse()
            return

        elif event.key() == Qt.Key_Escape:
            self.line_edit.setText("")

        elif event.key() == Qt.Key_Down:
            self.parent().view.setFocus()

        QLineEdit.keyPressEvent(self, event)




class Browser(BaseWidget):
    def __init__(self, parent):
        super(Browser, self).__init__(parent)
        parent.setWindowTitle("Browser")
        
        self.search_query = {}

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
        action_clear.triggered.connect(self.on_clear)

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



    def set_view(self, id_view, initial=False):
        if not initial:
            self.parent().save()
        self.state.get("{}c".format("id_view"), DEFAULT_HEADER_DATA)
        self.browse(view=id_view)
        cw = self.state.get("{}cw".format(id_view), False)
        if cw:
            self.view.horizontalHeader().restoreState(cw)
        else:
            #TODO: Resize to content
            pass

    def on_clear(self):
        self.search_box.setText("")
        self.browse(fulltext="")

    def browse(self,**kwargs):
        self.search_query["fulltext"] = self.search_box.text()
        self.search_query.update(kwargs)
        self.model.browse(**self.search_query)
 
    def on_activate(self,mi):
        self.view.do_edit(mi)


    def send_to(self):
        dlg = SendTo(self, self.view.selected_objects)
        dlg.exec_()


    def save_state(self):
        state = self.state
        id_view = self.search_query.get("view",0)
        #state["{}c".format(id_view)] = self.model.header_data
        state["{}cw".format(id_view)] = self.view.horizontalHeader().saveState()
        state["class"]  = "browser"
        state["search_query"]  = self.search_query
        return state


    def load_state(self, state):
        self.search_query = state.get("search_query", {})
        q = self.search_query.get("fulltext","")
        if q:
            self.search_box.setText(q)
        self.state = state
        default_view = sorted(config["views"].keys())[0]
        self.set_view(self.search_query.get("view",default_view), initial=True)

        

    def hideEvent(self, event):
        pass




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
            self.parent().parent().focus(self.view.selected_objects)
            if len(self.view.selected_objects) > 1 and tot_dur:
                self.status("{} objects selected. Total duration {}".format(len(self.view.selected_objects), s2time(tot_dur) ))

        super(NXView, self.view).selectionChanged(selected, deselected)

