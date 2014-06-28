#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

from functools import partial

from firefly_view import *
from mod_browser_model import BrowserModel


from dlg_sendto import SendTo


DEFAULT_HEADER_DATA = ["content_type", "title", "duration", "id_folder", "origin"]


class SearchWidget(QLineEdit):
    def __init__(self, parent):
        super(QLineEdit, self).__init__()

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return,Qt.Key_Enter]:
            if event.modifiers() & Qt.ControlModifier:
                print ("extend search")
                self.parent().OnSearch(extend=True)
            else:
                self.parent().parent().browse()
            return

        elif event.key() == Qt.Key_Escape:
            self.line_edit.setText("")

        elif event.key() == Qt.Key_Down:
            self.parent().view.setFocus()

        QLineEdit.keyPressEvent(self, event)




class Browser(BaseWidget):
    def __init__(self, parent):
        super(Browser, self).__init__(parent)    
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
        self.action_search.setStyleSheet(base_css)
        self.action_search.menuAction().setIcon(QIcon(pixlib["search"]))
        self.action_search.menuAction().triggered.connect(self.browse)
        self.load_view_menu()

        toolbar = QToolBar()
        toolbar.addAction(action_clear)
        toolbar.addWidget(self.search_box)
        toolbar.addAction(self.action_search.menuAction())

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        #layout.setSpacing(5)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.view, 1)
        self.setLayout(layout)
        self.setMinimumWidth(300)

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
            for id_column in range(self.model.columnCount(False)):
                if meta_types[self.model.header_data[id_column]].class_ != BLOB:
                    self.view.resizeColumnToContents(id_column)

        self.parent().setWindowTitle("{}".format(config["views"][id_view][1]))

    def on_clear(self):
        self.search_box.setText("")
        self.browse(fulltext="")

    def browse(self,**kwargs):
        self.search_query["fulltext"] = self.search_box.text()
        self.search_query.update(kwargs)
        self.model.browse(**self.search_query)
 
    def on_activate(self,mi):
        self.view.do_edit(mi)
        self.view.update()


    def send_to(self):
        dlg = SendTo(self, self.view.selected_objects)
        dlg.exec_()


        

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

        days = math.floor(tot_dur / (24*3600))
        durstr = "{} days {}".format(days, s2time(tot_dur)) if days else s2time(tot_dur)

        if self.view.selected_objects:
            self.parent().parent().focus(self.view.selected_objects)
            if len(self.view.selected_objects) > 1 and tot_dur:
                self.status("{} objects selected. Total duration {}".format(len(self.view.selected_objects), durstr ))

        super(NXView, self.view).selectionChanged(selected, deselected)

