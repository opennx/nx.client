from firefly_common import *
from firefly_view import *

from nx.objects import *

from qt_txcalendar import TXCalendar



def scheduler_toolbar(wnd):
    toolbar = QToolBar(wnd)

    action_week_prev = QAction(QIcon(pixlib["back"]), '&Previous week', wnd)        
#    action_week_prev.setShortcut('Alt+Left')
    action_week_prev.setStatusTip('Go to previous week')
    action_week_prev.triggered.connect(wnd.on_week_prev)
    toolbar.addAction(action_week_prev)

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
    action_refresh.setShortcut('F5')
    action_refresh.setStatusTip('Refresh rundown')
    action_refresh.triggered.connect(partial(wnd.refresh, True))
    toolbar.addAction(action_refresh)

    action_week_next = QAction(QIcon(pixlib["next"]), '&Next week', wnd)        
#    action_week_next.setShortcut('Alt+Right')
    action_week_next.setStatusTip('Go to next week')
    action_week_next.triggered.connect(wnd.on_week_next)
    toolbar.addAction(action_day_next)

    return toolbar



class Scheduler(BaseWidget):
    def __init__(self, parent):
        super(Scheduler, self).__init__(parent)
        toolbar = scheduler_toolbar(self)
        self.current_date = time.strftime("%Y-%m-%d")
        self.id_channel   = 1 # TODO (get default from playout config, overide in setState)
        self.update_header()

        self.calendar = TXCalendar(self.current_date)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.on_air)
        layout.addWidget(self.view, 1)

        self.setLayout(layout)

    def update_header(self):
        pass