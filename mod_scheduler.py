import math

from firefly_common import *
from firefly_view import *

from nx.objects import *
from nx.common.utils import *


COLOR_CALENDAR_BACKGROUND = QColor("#161616")
COLOR_DAY_BACKGROUND = QColor("#323232")

TIME_PENS = [
        (60 , QPen( QColor("#999999"), 2 , Qt.SolidLine )),
        (15 , QPen( QColor("#999999"), 1 , Qt.SolidLine )),
        (5  , QPen( QColor("#444444"), 1 , Qt.SolidLine ))
    ]

DAY = 3600*24
MIN_PER_DAY = (60 * 24)


def suggested_duration(dur):
    adur = int(dur) + 360
    g = adur % 300
    if g > 150:
        r =  adur-g + 300
    else:
        r =  adur -g
    return r


class TXEvent(object):
    def __init__(self, parent, start, obj):
        self.parent = parent
        self.start = start
        self.base_dur = base_dur
        self.obj = obj

    @property
    def start_pos(self):
        return self.parent.ts2pos(start)

    @property
    def end_pos(self):
        return self.parent.ts2pos(start + self.obj.get_duration())


class TXVerticalBar(QWidget):
    def __init__(self, parent):      
        super(TXVerticalBar, self).__init__(parent)
        self.setMouseTracking(True)

    def status(self, message, message_type=INFO):
        self.parent().status(message, message_type)

    @property
    def resolution(self):
        if self.min_size > 2:
            return 5
        elif self.min_size > 1:
            return 15
        else:
            return 60

    @property
    def min_size(self):
        return self.height() / MIN_PER_DAY

    @property
    def sec_size(self):
        return self.min_size / 60

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        pass


class TXClockBar(TXVerticalBar):
    def __init__(self, parent, day_start):
        super(TXClockBar, self).__init__(parent)
        self.setMinimumWidth(45)
        self.day_start = day_start

    def drawWidget(self, qp):
        qp.setPen(Qt.NoPen)       
        qp.setBrush(COLOR_CALENDAR_BACKGROUND)
        qp.drawRect(0, 0, self.width(), self.height())

        qp.setPen(TIME_PENS[0][1])
        font = QFont('Serif', 9, QFont.Light)
        qp.setFont(font)

        for i in range(0, MIN_PER_DAY, self.resolution):
            if i % 60:
                continue
            y = i * self.min_size
            tc = (self.day_start[0]*60 + self.day_start[1]) + i
            qp.drawLine(0, y, self.width(), y)
            qp.drawText(5, y+15, s2time(tc*60, False, False))
        



























class TXDayWidget(TXVerticalBar):  
    def __init__(self, parent, start_time):      
        super(TXDayWidget, self).__init__(parent)
        self.setMinimumWidth(140)
        self.start_time = start_time
        self.setAcceptDrops(True)
        self.dragging = False
        self.cursor_time = 0

    def ts2pos(self, ts):
        ts -= self.start_time
        return ts*self.sec_size

    def drawWidget(self, qp):
        qp.setPen(Qt.NoPen)       
        qp.setBrush(COLOR_DAY_BACKGROUND)
        qp.drawRect(0, 0, self.width(), self.height())

        for i in range(0, MIN_PER_DAY, self.resolution):
            for pen in TIME_PENS:
                if i % pen[0] == 0:
                    qp.setPen(pen[1])
                    break 
            else:
                continue
            y = i * self.min_size
            qp.drawLine(0, y, self.width(), y)    

        if self.dragging:
            self.drawGrabbed(qp)
            

    def drawGrabbed(self, qp):
        exp_dur = suggested_duration(self.dragging.get_duration())
        base_t = self.ts2pos(self.cursor_time)
        base_h = self.min_size * (exp_dur / 60)

        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor(200,200,200,128))
        qp.drawRect(0, base_t, self.width(), base_h)

        self.status("Start time: {} End time: {}".format(
                time.strftime("%H:%M", time.localtime(self.cursor_time)), 
                time.strftime("%H:%M", time.localtime(self.cursor_time + exp_dur))
                ))
            


    def drawBlock(self, qp, start_time, asset):
        pass


    def dragEnterEvent(self, evt):
        if evt.mimeData().hasFormat('application/nx.asset'):
            d = evt.mimeData().data("application/nx.asset").data()
            d = json.loads(d.decode("ascii"))
            if len(d) != 1:
                evt.ignore()
                return

            self.dragging = Asset(from_data=d[0])
            evt.accept()
        else:
            evt.ignore()


    def dragMoveEvent(self, evt):
        self.mx = evt.pos().x()
        self.my = evt.pos().y()
        self.cursor_time_prec = (self.my/self.min_size*60) + self.start_time
        cursor_time = self.cursor_time_prec + (300 - (self.cursor_time_prec % 300)) # Round to nearest 5 min up
        if cursor_time != self.cursor_time:
            self.cursor_time = cursor_time
            self.update()

    def dragLeaveEvent(self, evt):
        self.dragging = False
        self.update()

    def dropEvent(self, evt):
        self.status("Creating event from {} at time {}".format(self.dragging, time.strftime("%Y-%m-%d %H:%M", time.localtime(self.cursor_time))))
        query("event_from_asset", {
                "id_asset" : self.dragging.id,
                "id_channel" : 1,
                "timestamp" : self.cursor_time
            })

        self.dragging = False
        self.update()




class TXCalendar(QWidget):
    def __init__(self, parent, view_start):
        super(TXCalendar, self).__init__(parent)
        self.week_start = 0     # Monday is a first day of week
        self.day_start = (6,00) # Broadcast starts at 6:00 AM
        self.num_days = 7

        self.start_time = datestr2ts(view_start, *self.day_start)

        self.days = []
        self.events = []

        cols_layout = QHBoxLayout()
        cols_layout.addWidget(TXClockBar(self, self.day_start), 0)

        for i in range(self.num_days):
            self.days.append(TXDayWidget(self, self.start_time+(i*DAY)))
            cols_layout.addWidget(self.days[-1], 1)        
        
        self.scroll_widget = QWidget()
        self.scroll_widget.status = self.status
        self.scroll_widget.setLayout(cols_layout)
        self.scroll_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setContentsMargins(0,0,0,0)

        self.zoom = QSlider(Qt.Horizontal)
        self.zoom.setMinimum(0)
        self.zoom.setMaximum(6000)
        self.zoom.valueChanged.connect(self.on_zoom)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area,1)
        layout.addWidget(self.zoom,0)
        self.setLayout(layout)
        self.setMinimumHeight(600)
    
    def on_zoom(self):
        self.scroll_widget.setMinimumHeight(self.zoom.value())


    def resizeEvent(self, evt):
        self.zoom.setMinimum(self.scroll_area.height())

    def status(self, message, message_type=INFO):
        self.parent().status(message, message_type)
























def scheduler_toolbar(wnd):
    toolbar = QToolBar(wnd)

    action_week_prev = QAction(QIcon(pixlib["back"]), '&Previous week', wnd)        
#    action_week_prev.setShortcut('Alt+Left')
    action_week_prev.setStatusTip('Go to previous week')
#    action_week_prev.triggered.connect(wnd.on_week_prev)
    toolbar.addAction(action_week_prev)

    action_now = QAction(QIcon(pixlib["now"]), '&Now', wnd)        
    action_now.setShortcut('F1')
    action_now.setStatusTip('Go to now')
#    action_now.triggered.connect(wnd.on_now)
    toolbar.addAction(action_now)

    action_calendar = QAction(QIcon(pixlib["calendar"]), '&Calendar', wnd)        
#    action_calendar.setShortcut('Ctrl+D')
    action_calendar.setStatusTip('Open calendar')
#    action_calendar.triggered.connect(wnd.on_calendar)
    toolbar.addAction(action_calendar)

    action_refresh = QAction(QIcon(pixlib["refresh"]), '&Refresh', wnd)        
    action_refresh.setShortcut('F5')
    action_refresh.setStatusTip('Refresh rundown')
#    action_refresh.triggered.connect(partial(wnd.refresh, True))
    toolbar.addAction(action_refresh)

    action_week_next = QAction(QIcon(pixlib["next"]), '&Next week', wnd)        
#    action_week_next.setShortcut('Alt+Right')
    action_week_next.setStatusTip('Go to next week')
#    action_week_next.triggered.connect(wnd.on_week_next)
    toolbar.addAction(action_week_next)

    return toolbar



class Scheduler(BaseWidget):
    def __init__(self, parent):
        super(Scheduler, self).__init__(parent)
        toolbar = scheduler_toolbar(self)
        self.current_date = time.strftime("%Y-%m-%d")
        self.id_channel   = 1 # TODO (get default from playout config, overide in setState)
        self.update_header()

        self.calendar = TXCalendar(self, self.current_date)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.calendar, 1)

        self.setLayout(layout)

    def update_header(self):
        pass

    def save_state(self):
        state = {}
        state["class"] = "scheduler"
        return state

    def load_state(self, state):
        pass