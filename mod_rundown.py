import time
import datetime

from functools import partial

from firefly_common import *
from firefly_view import *

from mod_rundown_onair import OnAir
from mod_rundown_model import RundownModel

from dlg_sendto import SendTo


DEFAULT_COLUMNS = ["rundown_symbol", "title", "duration", "run_mode", "rundown_scheduled", "rundown_broadcast", "rundown_status", "mark_in", "mark_out", "id_asset"]

def ts_today():
    return time.mktime(datetime.datetime.combine(datetime.date.today(), datetime.time.min).timetuple()) 


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
            stat, res = query("del_items", items=[obj.id for obj in self.selected_objects])
            if success(stat):
                self.parent().status("Delete item: {}".format(res))
            else:
                self.parent().status("Item deletion failed")
            QApplication.restoreOverrideCursor()
            self.parent().refresh()
            return
        NXView.keyPressEvent(self, event)


class Rundown(BaseWidget):
    def __init__(self, parent):
        super(Rundown, self).__init__(parent)
        toolbar = rundown_toolbar(self)

        self.id_channel   = 1 # TODO (get default from playout config, overide in setState).... also get start time from today + playout_config channel day start
        self.start_time = ts_today()

        self.playout_config = config["playout_channels"][self.id_channel]
        

        dt = datetime.datetime.fromtimestamp(time.time() - 86400).replace(hour = self.playout_config["day_start"][0], minute = self.playout_config["day_start"][1], second = 0)
        self.start_time = time.mktime(dt.timetuple()) 


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
        layout.addWidget(self.mcr)
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
                self.refresh()

            if data.data["cued_item"] != self.cued_item:
                self.cued_item = data.data["cued_item"]
                self.refresh(full=False)
            
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

    ###########################################################################


    def load(self, id_channel, start_time, full=True):
        self.id_channel = id_channel
        self.start_time = start_time
        self.update_header()
        self.model.load(id_channel, start_time, full=full)

    def refresh(self, full=True):
        self.load(self.id_channel, self.start_time, full=full)

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
        if self.mcr and self.mcr.isVisible():
            item = self.model.object_data[mi.row()]
            query("cue", self.mcr.route, id_channel=self.id_channel, id_item=item.id)


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

    def set_date(self, start_time):
        self.start_time = start_time
        self.update_header()
        self.load(self.id_channel, self.start_time)

    def on_day_prev(self):
        self.set_date(self.start_time - (3600*24))

    def on_day_next(self):
        self.set_date(self.start_time + (3600*24))

    def on_now(self):
        self.set_date(ts_today())


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
