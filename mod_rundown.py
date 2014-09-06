import time
import datetime

from functools import partial

from firefly_common import *
from firefly_view import *

from mod_rundown_onair import OnAir
from mod_rundown_model import RundownModel

from dlg_sendto import SendTo


DEFAULT_COLUMNS = ["rundown_symbol", "title", "duration", "run_mode", "rundown_scheduled", "rundown_broadcast", "rundown_status", "mark_in", "mark_out", "id_asset", "id_object"]

def day_start(ts, start):
    hh, mm = start
    r =  ts - (hh*3600 + mm*60)
    dt = datetime.datetime.fromtimestamp(r).replace(
        hour = hh, 
        minute = mm, 
        second = 0
        )
    return time.mktime(dt.timetuple()) 


class RundownDate(QLabel):
    pass




class LeadInButton(QToolButton):
    def __init__(self, parent):
        super(LeadInButton, self).__init__() 
        self.pressed.connect(self.startDrag)
        self.setIcon(QIcon(pixlib["mark_in"]))
        self.setToolTip("Drag this to rundown to create Lead-in.")

    def startDrag(self):
        drag = QDrag(self);
        mimeData = QMimeData()
        mimeData.setData(
           "application/nx.item",
           '[{"item_role":"lead_in", "title":"Lead in"}]'
           )
        drag.setMimeData(mimeData)
        if drag.exec_(Qt.CopyAction):
            pass # nejak to rozumne ukoncit


class LeadOutButton(QToolButton):
    def __init__(self, parent):
        super(LeadOutButton, self).__init__() 
        self.pressed.connect(self.startDrag)
        self.setIcon(QIcon(pixlib["mark_out"]))
        self.setToolTip("Drag this to rundown to create Lead-out.")

    def startDrag(self):
        drag = QDrag(self);
        mimeData = QMimeData()
        mimeData.setData(
           "application/nx.item",
           '[{"item_role":"lead_out", "title":"Lead out"}]'
           )
        drag.setMimeData(mimeData)
        if drag.exec_(Qt.CopyAction):
            pass # nejak to rozumne ukoncit



def rundown_toolbar(wnd):
    toolbar = QToolBar(wnd)

    action_day_prev = QAction(QIcon(pixlib["back"]), '&Previous day', wnd)        
    action_day_prev.setShortcut('Alt+Left')
    action_day_prev.setStatusTip('Go to previous day')
    action_day_prev.triggered.connect(wnd.on_day_prev)
    toolbar.addAction(action_day_prev)

    action_now = QAction(QIcon(pixlib["now"]), '&Now', wnd)        
    action_now.setStatusTip('Go to now')
    action_now.triggered.connect(wnd.on_now)
    toolbar.addAction(action_now)

#    action_calendar = QAction(QIcon(pixlib["calendar"]), '&Calendar', wnd)        
#    action_calendar.setShortcut('Ctrl+D')
#    action_calendar.setStatusTip('Open calendar')
#    action_calendar.triggered.connect(wnd.on_calendar)
#    toolbar.addAction(action_calendar)

    action_refresh = QAction(QIcon(pixlib["refresh"]), '&Refresh', wnd)        
    action_refresh.setStatusTip('Refresh rundown')
    action_refresh.triggered.connect(wnd.refresh)
    toolbar.addAction(action_refresh)

    action_day_next = QAction(QIcon(pixlib["next"]), '&Next day', wnd)        
    action_day_next.setShortcut('Alt+Right')
    action_day_next.setStatusTip('Go to next day')
    action_day_next.triggered.connect(wnd.on_day_next)
    toolbar.addAction(action_day_next)

    toolbar.addSeparator()

    action_toggle_run_mode = QAction(QIcon(pixlib["run_mode"]), '&Toggle run mode', wnd)        
    action_toggle_run_mode.setStatusTip('Toggle item run mode')
    action_toggle_run_mode.triggered.connect(wnd.on_toggle_run_mode)
    toolbar.addAction(action_toggle_run_mode)

    action_toggle_mcr = QAction(QIcon(pixlib["onair"]), '&Playout controls', wnd)        
    action_toggle_mcr.setStatusTip('Toggle playout controls')
    action_toggle_mcr.triggered.connect(wnd.on_toggle_mcr)
    toolbar.addAction(action_toggle_mcr)

    toolbar.addWidget(ToolBarStretcher(wnd))

    wnd.date_display = RundownDate()
    toolbar.addWidget(wnd.date_display)

    return toolbar



def items_toolbar(wnd):
    toolbar = QToolBar(wnd)
    toolbar.addWidget(LeadInButton(wnd))
    toolbar.addWidget(LeadOutButton(wnd))
    return toolbar


class RundownView(NXView):
    def selectionChanged(self, selected, deselected):     
        rows = []
        self.selected_objects = []
        tot_dur = 0

        for idx in self.selectionModel().selectedIndexes():
            row = idx.row()
            if row in rows: 
                continue
            rows.append(row)
            obj = self.model().object_data[row]
            self.selected_objects.append(obj)
            if obj.object_type in ["asset", "item"]:
                tot_dur += obj.get_duration()

        if self.selected_objects and self.focus_enabled:
            self.parent().parent().parent().focus(self.selected_objects)
            if len(self.selected_objects) > 1 and tot_dur:
                self.parent().status("{} objects selected. Total duration {}".format(len(self.selected_objects), s2time(tot_dur) ))

        super(NXView, self).selectionChanged(selected, deselected)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:

            if self.id_channel not in config["rights"].get("can/rundown_edit", []):
                QMessageBox.warning(self, "Error", "You are not allowed to modify this rundown")

            QApplication.processEvents()
            QApplication.setOverrideCursor(Qt.WaitCursor)
            stat, res = query("del_items", items=[obj.id for obj in self.selected_objects])
            QApplication.restoreOverrideCursor()
            if success(stat):
                self.parent().status("Delete item: {}".format(res))
            else:
                QMessageBox.critical(self, "Error", res)
            self.parent().refresh()
            return
        NXView.keyPressEvent(self, event)


class Rundown(BaseWidget):
    def __init__(self, parent):
        super(Rundown, self).__init__(parent)
        toolbar = rundown_toolbar(self)
        self.items_toolbar = items_toolbar(self)

        self.id_channel   = self.parent().parent().id_channel
        self.playout_config = config["playout_channels"][self.id_channel]

        self.start_time = day_start (time.time(), self.playout_config["day_start"])

        self.update_header()

        self.current_item = False
        self.cued_item = False

        if "user is allowed to use MCR": #TODO
            self.mcr = OnAir(self)
        else:
            self.mcr = False

        self.view  = RundownView(self)
        self.model = RundownModel(self)

        self.delegate = MetaEditItemDelegate(self.view)
        #self.delegate.settings["base_date"] = datestr2ts(self.current_date)

        self.view.setModel(self.model)
        self.view.setItemDelegate(self.delegate)
        
        self.view.activated.connect(self.on_activate)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)       

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.items_toolbar, 0)
        layout.addWidget(self.mcr)
        layout.addWidget(self.view, 1)

        self.setLayout(layout)
 


    def save_state(self):
        state = {}
        state["c"] = self.model.header_data
        state["cw"] = self.view.horizontalHeader().saveState()
        return state

    def load_state(self, state):
        self.model.header_data = state.get("c", False) or DEFAULT_COLUMNS
        self.id_channel = state.get("id_channel", min(config["playout_channels"].keys()))
        self.load(self.id_channel, self.start_time)

        cw = state.get("cw", False)
        if cw:
            self.view.horizontalHeader().restoreState(cw)
        else:
            for id_column in range(self.model.columnCount(False)):
                self.view.resizeColumnToContents(id_column)

    def seismic_handler(self, data):
        if data.method == "playout_status": 
            if data.data["id_channel"] != self.id_channel:
                return
            
            if data.data["current_item"] != self.current_item:
                self.current_item = data.data["current_item"]
                self.model.refresh_items([self.current_item])

                
            if data.data["cued_item"] != self.cued_item:
                self.cued_item = data.data["cued_item"]
                self.refresh()

            if self.mcr:
                self.mcr.seismic_handler(data)


        elif data.method == "job_progress":
            for i, obj in enumerate(self.model.object_data):
                if obj["id_asset"] == data.data["id_object"]:
                    if data.data["progress"] == COMPLETED:
                        obj["rundown_status"] = 2
                        obj["rundown_transfer_progress"] = COMPLETED
                    else:
                        obj["rundown_transfer_progress"] = data.data["progress"]
                    self.model.dataChanged.emit(self.model.index(i, 0), self.model.index(i, len(self.model.header_data)-1))
                    self.update()

        elif data.method == "objects_changed" and data.data["object_type"] == "event":
            my_name =self.parent().objectName()
#            print (data.data)
#            print (my_name)
            for id_event in data.data["objects"]:#  
                if data.data.get("sender", False) != my_name and id_event in self.model.event_ids :
                    self.refresh()
                    break


    ###########################################################################


    def load(self, id_channel, start_time, event=False):
        self.id_channel = id_channel
        self.start_time = start_time
        self.update_header()
        self.model.load(id_channel, start_time)
        if not event:
            return

        for i, r in enumerate(self.model.object_data):
            if event.id == r.id and r.object_type=="event":
                self.view.scrollTo(self.model.index(i, 0, QModelIndex()), QAbstractItemView.PositionAtTop  )
                break


    def refresh(self):
        selection = []
        for idx in self.view.selectionModel().selectedIndexes():
            selection.append([self.model.object_data[idx.row()].object_type, self.model.object_data[idx.row()].id]) 

        self.load(self.id_channel, self.start_time)

        item_selection = QItemSelection()
        for i, row in enumerate(self.model.object_data):
            if [row.object_type, row.id] in selection:
               i1 = self.model.index(i, 0, QModelIndex())
               i2 = self.model.index(i, len(self.model.header_data)-1, QModelIndex())
               item_selection.select(i1,i2)
        self.view.focus_enabled = False
        self.view.selectionModel().select(item_selection, QItemSelectionModel.ClearAndSelect)
        self.view.focus_enabled = True

    def update_header(self):
        t = datetime.date.fromtimestamp(self.start_time)

        if t < datetime.date.today():
            s = " color='red'"
        elif t > datetime.date.today():
            s = " color='green'"
        else:
            s = ""

        t = t.strftime("%A %Y-%m-%d")
        self.parent().setWindowTitle("Rundown {}".format(t))
        self.date_display.setText("<font{}>{}</font>".format(s, t))

    ################################################################


    def on_activate(self, mi):
        obj = self.model.object_data[mi.row()]
        can_mcr = self.id_channel in config["rights"].get("can/mcr", [])
        if obj.object_type == "item" and self.mcr and self.mcr.isVisible() and can_mcr:    
            stat, res = query("cue", self.mcr.route, id_channel=self.id_channel, id_item=obj.id)
            if not success(stat):
                QMessageBox.critical(self, "Error", res)
        elif obj.object_type == "event":
            self.on_edit_event()


    def contextMenuEvent(self, event):
        if not self.view.selected_objects:
            return

        obj_set = list(set([itm.object_type for itm in self.view.selected_objects]))
        if len(obj_set) != 1:
            return

        menu = QMenu(self)
        if obj_set[0] == "item":
            
            action_send_to = QAction('&Send to...', self)        
            action_send_to.setStatusTip('Create action for selected asset(s)')
            action_send_to.triggered.connect(self.on_send_to)
            menu.addAction(action_send_to)
        
        
        elif obj_set[0] == "event" and len(self.view.selected_objects) == 1:    
            action_edit = QAction('&Edit', self)        
            action_edit.setStatusTip('Edit selected event')
            action_edit.triggered.connect(self.on_edit_event)
            menu.addAction(action_edit)
        
            menu.addSeparator()

            action_solve = QAction('Solve', self)        
            action_solve.setStatusTip('Solve selected event')
            action_solve.triggered.connect(self.on_solve_event)
            menu.addAction(action_solve)
        else:
            return

        menu.exec_(event.globalPos()) 



    def on_send_to(self):
        dlg = SendTo(self, self.view.selected_objects)
        dlg.exec_()


    def on_edit_event(self):
        pass

    def on_solve_event(self):
        if self.id_channel not in config["rights"].get("can/rundown_edit", []):
            QMessageBox.warning(self, QMessageBox.warning, "Error", "You are not allowed to modify this rundown")

        ret = QMessageBox.question(self,
            "Solve event",
            "Do you really want to (re)solve {}?\nThis operation cannot be undone.".format(self.view.selected_objects[0]),
            QMessageBox.Yes | QMessageBox.No
            )

        if ret == QMessageBox.Yes:
            QApplication.processEvents()
            QApplication.setOverrideCursor(Qt.WaitCursor)
            stat, res = query("dramatica", 
                handler=self.handle_message, 
                id_channel=self.id_channel, 
                date=time.strftime("%Y-%m-%d", time.localtime(self.start_time)),
                id_event =self.view.selected_objects[0].id,
                solve=True
                )
            QApplication.restoreOverrideCursor()
            if not success(stat):
                QMessageBox.critical(self, "Error", res)
            self.refresh()



    ################################################################
    ## Toolbar actions

    def set_channel(self):
        if self.id_channel != id_channel:
            self.id_channel = id_channel
            self.refresh()

    def set_date(self, start_time):
        self.start_time = start_time
        self.update_header()
        self.load(self.id_channel, self.start_time)

    def on_day_prev(self):
        self.set_date(self.start_time - (3600*24))

    def on_day_next(self):
        self.set_date(self.start_time + (3600*24))

    def on_now(self):
        if not (self.start_time+86400 > time.time() > self.start_time):
            self.set_date(day_start (time.time(), self.playout_config["day_start"]))

        for i,r in enumerate(self.model.object_data):
            if self.current_item == r.id and r.object_type=="item":
                self.view.scrollTo(self.model.index(i, 0, QModelIndex()), QAbstractItemView.PositionAtCenter  )
                break


    def on_calendar(self):
        pass

    def on_toggle_mcr(self):
        if self.mcr:
            if self.mcr.isVisible():
                self.mcr.hide()
            else:
                self.mcr.show()

    def on_toggle_run_mode(self):
        obj = self.view.selected_objects[0]
        print (obj)


    ## Toolbar actions
    ################################################################

    def handle_message(self, msg):
        self.status(msg.get("message",""))
        QApplication.processEvents()
