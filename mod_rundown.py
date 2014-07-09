import time
import datetime

from functools import partial

from firefly_common import *
from firefly_view import *

from mod_rundown_onair import OnAir
from mod_rundown_model import RundownModel

from dlg_sendto import SendTo


DEFAULT_COLUMNS = ["rundown_symbol", "title", "duration", "rundown_scheduled", "rundown_broadcast", "rundown_status", "mark_in", "mark_out", "id_asset"]


class RundownDate(QLabel):
    pass


def rundown_toolbar(wnd):
    toolbar = QToolBar(wnd)

    action_day_prev = QAction(QIcon(pixlib["back"]), '&Previous day', wnd)        
    action_day_prev.setShortcut('Alt+Left')
    action_day_prev.setStatusTip('Go to previous day')
    action_day_prev.triggered.connect(wnd.on_day_prev)
    toolbar.addAction(action_day_prev)

    action_now = QAction(QIcon(pixlib["now"]), '&Now', wnd)        
    action_now.setShortcut('F1')
    action_now.setStatusTip('Go to now')
    action_now.triggered.connect(wnd.on_now)
    toolbar.addAction(action_now)


    action_calendar = QAction(QIcon(pixlib["calendar"]), '&Calendar', wnd)        
    action_calendar.setShortcut('Ctrl+D')
    action_calendar.setStatusTip('Open calendar')
    action_calendar.triggered.connect(wnd.on_calendar)
    toolbar.addAction(action_calendar)

    action_refresh = QAction(QIcon(pixlib["refresh"]), '&Refresh', wnd)        
    action_refresh.setStatusTip('Refresh rundown')
    action_refresh.triggered.connect(partial(wnd.refresh, True))
    toolbar.addAction(action_refresh)

    action_day_next = QAction(QIcon(pixlib["next"]), '&Next day', wnd)        
    action_day_next.setShortcut('Alt+Right')
    action_day_next.setStatusTip('Go to next day')
    action_day_next.triggered.connect(wnd.on_day_next)
    toolbar.addAction(action_day_next)

    toolbar.addSeparator()

    action_onair = QAction(QIcon(pixlib["onair"]), '&Playout controls', wnd)        
    action_onair.setShortcut('F6')
    action_onair.setStatusTip('Toggle playout controls')
    action_onair.triggered.connect(wnd.on_onair)
    toolbar.addAction(action_onair)

    toolbar.addWidget(ToolBarStretcher(wnd))

    wnd.date_display = RundownDate()
    toolbar.addWidget(wnd.date_display)

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

        if self.selected_objects:
            self.parent().parent().parent().focus(self.selected_objects)
            if len(self.selected_objects) > 1 and tot_dur:
                self.parent().status("{} objects selected. Total duration {}".format(len(self.selected_objects), s2time(tot_dur) ))

        super(NXView, self).selectionChanged(selected, deselected)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            QApplication.processEvents()
            QApplication.setOverrideCursor(Qt.WaitCursor)
            stat, res = query("del_items", params={"items":[obj.id for obj in self.selected_objects]})
            self.parent().status("Delete item: {}".format(res))
            QApplication.restoreOverrideCursor()
            self.parent().refresh()
            return
        NXView.keyPressEvent(self, event)


class Rundown(BaseWidget):
    def __init__(self, parent):
        super(Rundown, self).__init__(parent)
        toolbar = rundown_toolbar(self)
        
        self.current_date = time.strftime("%Y-%m-%d")
        self.id_channel   = 1 # TODO (get default from playout config, overide in setState)
        self.update_header()

        self.current_item = False
        self.cued_item = False

        self.on_air = OnAir(self)
        self.view  = RundownView(self)
        self.model = RundownModel(self)

        self.delegate = MetaEditItemDelegate(self.view)
        self.delegate.settings["base_date"] = datestr2ts(self.current_date)

        self.view.setModel(self.model)
        self.view.setItemDelegate(self.delegate)
        
        self.view.activated.connect(self.on_activate)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)       

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.on_air)
        layout.addWidget(self.view, 1)

        self.setLayout(layout)
        self.subscribe("playout_status", "job_progress")


    def save_state(self):
        state = {}
        state["c"] = self.model.header_data
        state["cw"] = self.view.horizontalHeader().saveState()
        return state

    def load_state(self, state):
        self.model.header_data = state.get("c", False) or DEFAULT_COLUMNS
        self.id_channel = state.get("id_channel", min(config["playout_channels"].keys()))
        self.load(self.id_channel, self.current_date)

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
                self.refresh()

            if data.data["cued_item"] != self.cued_item:
                self.cued_item = data.data["cued_item"]
                self.refresh(full=False)
            
            self.on_air.seismic_handler(data)


        elif data.method == "job_progress":
            for i, obj in enumerate(self.model.object_data):
                if obj["id_asset"] == data.data["id_object"]:
                    if data.data["progress"] == COMPLETED:
                        obj["rundown_status"] = 2
                        obj["rundown_transfer_progress"] = COMPLETED
                    else:
                        obj["rundown_transfer_progress"] = data.data["progress"]
                    index = self.model.index(i, len(self.model.header_data)-1)
                    self.model.dataChanged.emit(index, index)
                    self.update()

    ###########################################################################


    def load(self, id_channel, date, full=True):
        self.model.load(id_channel, date, full=full)

    def refresh(self, full=True):
        self.load(self.id_channel, self.current_date, full=full)

    def update_header(self):
        syy,smm,sdd = [int(i) for i in self.current_date.split("-")]
        t = datetime.date(syy, smm, sdd)

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
        item = self.model.object_data[mi.row()]
        params = {
            "id_channel" : self.id_channel,
            "id_item"    : item.id
            }
        query("cue", params, "play{}".format(self.id_channel))


    def contextMenuEvent(self, event):
        if not self.view.selected_objects: return
        menu = QMenu(self)
        
        menu.addSeparator()
        action_send_to = QAction('&Send to...', self)        
        action_send_to.setStatusTip('Create action for selected asset(s)')
        action_send_to.triggered.connect(self.send_to)
        menu.addAction(action_send_to)
                
        menu.exec_(event.globalPos()) 


    def send_to(self):
        dlg = SendTo(self, self.view.selected_objects)
        dlg.exec_()

    ################################################################
    ## Toolbar actions

    def set_date(self, date):
        self.current_date = date
        self.update_header()
        self.load(self.id_channel, self.current_date)

    def on_day_prev(self):
        syy,smm,sdd = [int(i) for i in self.current_date.split("-")]
        go = time.mktime(time.struct_time([syy,smm,sdd,0,0,0,False,False,False])) - (24*3600)
        self.set_date(time.strftime("%Y-%m-%d",time.localtime(go)))

    def on_day_next(self):
        syy,smm,sdd = [int(i) for i in self.current_date.split("-")]
        go = time.mktime(time.struct_time([syy,smm,sdd,0,0,0,False,False,False])) + (24*3600)
        self.set_date(time.strftime("%Y-%m-%d",time.localtime(go)))

    def on_now(self):
        self.set_date(time.strftime("%Y-%m-%d"))


    def on_calendar(self):
        pass

    def on_scheduler(self):
        scheduler = Scheduler(self, self.id_channel, self.current_date)
        scheduler.exec_()
        self.refresh()

    def on_onair(self):
        if self.on_air.isVisible():
            self.on_air.hide()
        else:
            self.on_air.show()

    ## Toolbar actions
    ################################################################
