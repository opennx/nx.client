import time
import datetime

from firefly_common import *
from firefly_view import *



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
        self.id_channel   = False # TODO (get default from playout config, overide in setState)
        self.update_header()

        self.rundown_view = NXView(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.rundown_view, 1)

        self.setLayout(layout)


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
        self.parent.setWindowTitle("Rundown %s" % t)
        self.date_display.setText("<font %s>%s</font>" % (s, t))

    ################################################################
    ## Navigation


    def set_date(self, date):
        self.current_date = date
        self.update_header()
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
        pass