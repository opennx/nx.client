#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

from functools import partial

from firefly_view import *
from mod_browser_model import BrowserModel


from dlg_sendto import SendTo


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
            self.parent().parent().view.setFocus()

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
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.view, 1)
        self.setLayout(layout)


    def save_state(self):
        state = self.state
        id_view = self.search_query.get("view",0)
        state["{}c".format(id_view)] = self.model.header_data
        state["{}cw".format(id_view)] = self.view.horizontalHeader().saveState()
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
            action = QAction(title, self, checkable=True)
            action.id_view = id_view
            action.triggered.connect(partial(self.set_view, id_view))
            self.action_search.addAction(action)

        self.action_search.addSeparator()

        action = QAction("Reset view", self)
        action.triggered.connect(self.reset_view)
        self.action_search.addAction(action)




    def set_view(self, id_view, initial=False):
        if not initial:
            self.parent().save()
        self.browse(view=id_view)

        self.model.header_data = self.state.get("{}c".format("id_view"), config["views"][id_view][2])
        cw = self.state.get("{}cw".format(id_view), False)
        if cw:
            self.view.horizontalHeader().restoreState(cw)
        else:
            for id_column in range(self.model.columnCount(False)):
                if meta_types[self.model.header_data[id_column]].class_ != BLOB:
                    self.view.resizeColumnToContents(id_column)
        self.parent().setWindowTitle("{}".format(config["views"][id_view][1]))

        for action in self.action_search.actions():
            if not hasattr(action, "id_view"):
                continue
            if action.id_view == id_view:
                action.setChecked(True)
            else:
                action.setChecked(False)


    def reset_view(self):
        self.model.header_data = config["views"][self.search_query["view"]][2]
        for id_column in range(self.model.columnCount(False)):
            if meta_types[self.model.header_data[id_column]].class_ != BLOB:
                self.view.resizeColumnToContents(id_column)


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

    def hideEvent(self, event):
        pass

    def contextMenuEvent(self, event):
        if not self.view.selected_objects:
            return
        menu = QMenu(self)

        action_focus = QAction('Focus', self)
        action_focus.setStatusTip('Focus selection')
        action_focus.triggered.connect(self.on_focus)
        menu.addAction(action_focus)

        statuses = [obj["status"] for obj in self.view.selected_objects ]

        if len(statuses) == 1 and statuses[0] == TRASHED:
            action_untrash = QAction('Untrash', self)
            action_untrash.setStatusTip('Take selected asset(s) to trash')
            action_untrash.triggered.connect(self.on_untrash)
            menu.addAction(action_untrash)
        else:
            action_move_to_trash = QAction('Move to trash', self)
            action_move_to_trash.setStatusTip('Move selected asset(s) to trash')
            action_move_to_trash.triggered.connect(self.on_trash)
            menu.addAction(action_move_to_trash)

        # action_move_to_archive = QAction('Move to archive', self)
        # action_move_to_archive.setStatusTip('Move selected asset(s) to archive')
        # action_move_to_archive.triggered.connect(self.on_archive)
        # menu.addAction(action_move_to_archive)

        action_reset = QAction('Reset', self)
        action_reset.setStatusTip('Reload asset metadata')
        action_reset.triggered.connect(self.on_reset)
        menu.addAction(action_reset)

        menu.addSeparator()

        action_send_to = QAction('&Send to...', self)
        action_send_to.setStatusTip('Create action for selected asset(s)')
        action_send_to.triggered.connect(self.on_send_to)
        menu.addAction(action_send_to)

        menu.addSeparator()

        action_columns = QAction('Choose columns', self)
        action_columns.setStatusTip('Choose header columns')
        action_columns.triggered.connect(self.on_choose_columns)
        menu.addAction(action_columns)

        menu.exec_(event.globalPos())

    def on_focus(self):
        pass #TODO

    def on_send_to(self):
        dlg = SendTo(self, self.view.selected_objects)
        dlg.exec_()


    def on_reset(self):
        stat, res = query("set_meta", objects=[obj.id for obj in self.view.selected_objects if obj["status"] not in [ARCHIVED, TRASHED, RESET]], data={"status" : RESET} )


    def on_trash(self):
        ret = QMessageBox.question(self,
            "Trash",
            "Do you really want to trash {} selected asset(s)?".format(len(self.view.selected_objects)),
            QMessageBox.Yes | QMessageBox.No
            )
        if ret == QMessageBox.Yes:
            stat, res = query("trash", objects=[obj.id for obj in self.view.selected_objects if obj["status"] not in [ARCHIVED, TRASHED]])


    def on_untrash(self):
        objs = [obj.id for obj in self.view.selected_objects if obj["status"] in [TRASHED]]
        if objs:
            stat, res = query("untrash", objects=objs)


    def on_archive(self):
        ret = QMessageBox.question(self,
            "Archive",
            "Do you really want to move {} selected asset(s) to archive?".format(len(self.view.selected_objects)),
            QMessageBox.Yes | QMessageBox.No
            )
        if ret == QMessageBox.Yes:
            QMessageBox.warning(self,
                "Not available",
                "This feature is not available in this version",
                QMessageBox.Cancel
                )


    def on_choose_columns(self):
        pass #TODO



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


