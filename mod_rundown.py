import time
import datetime

from firefly_common import *
from firefly_view import *

from nx.objects import Item, Bin, Event

from dlg_scheduler import Scheduler



class RundownModel(NXViewModel):
    def load(self, id_channel, date):
        self.beginResetModel()
        self.object_data = []

        res, data = query("rundown",{"id_channel":id_channel,"date":date})
        if success(res) and data: 
            
            for edata in data["data"]:
                evt = Event(from_data=edata["event_meta"])
                evt.bin = Bin(from_data=edata["bin_meta"])

                self.object_data.append(evt)

                for idata, adata in edata["items"]:
                    item = Item(from_data=idata)
                    item.asset = Asset(from_data=adata)

                    self.object_data.append(item)
        
        self.endResetModel()



class RundownDate(QLabel):
    pass


def rundown_toolbar(parent):
    toolbar = QToolBar(parent)

    action_day_prev = QAction(QIcon(pixlib["back"]), '&Previous day', parent)        
    action_day_prev.setShortcut('Alt+Left')
    action_day_prev.setStatusTip('Go to previous day')
    action_day_prev.triggered.connect(parent.on_day_prev)
    toolbar.addAction(action_day_prev)

    action_now = QAction(QIcon(pixlib["now"]), '&Now', parent)        
    action_now.setShortcut('F1')
    action_now.setStatusTip('Go to now')
    action_now.triggered.connect(parent.on_now)
    toolbar.addAction(action_now)


    action_calendar = QAction(QIcon(pixlib["calendar"]), '&Calendar', parent)        
    action_calendar.setShortcut('Ctrl+D')
    action_calendar.setStatusTip('Open calendar')
    action_calendar.triggered.connect(parent.on_calendar)
    toolbar.addAction(action_calendar)

    action_day_next = QAction(QIcon(pixlib["next"]), '&Next day', parent)        
    action_day_next.setShortcut('Alt+Right')
    action_day_next.setStatusTip('Go to next day')
    action_day_next.triggered.connect(parent.on_day_next)
    toolbar.addAction(action_day_next)

    toolbar.addSeparator()

    action_scheduler = QAction(QIcon(pixlib["clock"]), '&Scheduler', parent)        
    action_scheduler.setShortcut('F7')
    action_scheduler.setStatusTip('Open scheduler')
    action_scheduler.triggered.connect(parent.on_scheduler)
    toolbar.addAction(action_scheduler)


    toolbar.addWidget(ToolBarStretcher(parent))

    parent.date_display = RundownDate()
    toolbar.addWidget(parent.date_display)

    return toolbar




class Rundown(BaseWidget):
    def __init__(self, parent):
        super(Rundown, self).__init__(parent)
        self.parent = parent

        toolbar = rundown_toolbar(self)
        
        self.current_date = time.strftime("%Y-%m-%d")
        self.id_channel   = 1 # TODO (get default from playout config, overide in setState)


        self.view = NXView(self)
        self.model = RundownModel(self)
        self.model.header_data = ["rundown_symbol","title"]

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
        layout.addWidget(self.view, 1)

        self.setLayout(layout)

        self.model.load(self.id_channel, self.current_date)


    def getState(self):
        state = {}
        state["class"] = "rundown"
        return state

    def setState(self, state):
        pass


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
        self.parent.setWindowTitle("Rundown {}".format(t))
        self.date_display.setText("<font{}>{}</font>".format(s, t))

    ################################################################
    ## 

    def on_activate(self, mi):
        pass




    ################################################################
    ## Navigation


    def set_date(self, date):
        self.current_date = date
        self.update_header()
        self.model.load(self.id_channel, self.current_date)
        #TODO: refresh

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


    ## Navigation
    ################################################################

    def on_calendar(self):
        pass

    def on_scheduler(self):
        scheduler = Scheduler(self, self.current_date)
        scheduler.exec_()