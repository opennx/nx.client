import math
import datetime

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
SAFE_OVR = 5 # Do not warn if overflow < 5 mins

def suggested_duration(dur):
    adur = int(dur) + 360
    g = adur % 300
    if g > 150:
        r =  adur-g + 300
    else:
        r =  adur -g
    return r


CLOCKBAR_WIDTH = 45


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
        self.setMinimumWidth(CLOCKBAR_WIDTH)
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
        








import re
def text_shorten(text, font, target_width):
    fm = QFontMetrics(font)
    r = r"[A-Za-z]([AEIOUaeiou])"
    text = text[::-1]
    while fm.width(text) > target_width:
        text, n = re.subn(r, r"\0", text, 1)
        if n == 0:
            return
    return text[::-1]













class TXDayWidget(TXVerticalBar):  
    def __init__(self, parent, start_time):      
        super(TXDayWidget, self).__init__(parent)
        self.setMinimumWidth(120)
        self.start_time = start_time
        self.setAcceptDrops(True)
        self.cursor_time = 0
        self.dragging = False
        self.drag_outside = False


    @property 
    def id_channel(self):
        return self.calendar.id_channel

    @property
    def calendar(self):
        return self.parent().parent().parent().parent()

    def ts2pos(self, ts):
        ts -= self.start_time
        return ts*self.sec_size


    def is_ts_today(self, ts):
        return ts >= self.start_time and ts < self.start_time + (3600*24)

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

        for i,event in enumerate(self.calendar.events):
            if not self.is_ts_today(event["start"]):
                continue
            try:
                end = self.calendar.events[i+1]["start"]
            except IndexError:
                end = self.start_time + (3600*24)

            self.drawBlock(qp, event, end=end)

        if self.calendar.dragging and self.dragging:
            self.draw_dragging(qp)
            

    def drawBlock(self, qp, event, end):
        if type(self.calendar.dragging) == Event and self.calendar.dragging.id == event.id:
            if not self.drag_outside:
                return

        TEXT_SIZE = 9
        base_t = self.ts2pos(event["start"])
        base_h = self.min_size * (event["duration"] / 60) 
        evt_h = self.ts2pos(end) - base_t
        
        # Event block (Gradient one)        
        erect = QRect(0,base_t,self.width(),evt_h) # EventRectangle Muhehe!
        gradient = QLinearGradient(erect.topLeft(), erect.bottomLeft())
        gradient.setColorAt(.0, QColor(40,80,120,210))
        gradient.setColorAt(1, QColor(0,0,0, 0))
        qp.fillRect(erect, gradient)


        lcolor = QColor("#909090")
        erect = QRect(0, base_t, self.width(), 2)
        qp.fillRect(erect, lcolor)
        if base_h:
            if base_h > evt_h + (SAFE_OVR * self.min_size):
                lcolor = QColor("#e01010")
            erect = QRect(0, base_t, 2, min(base_h, evt_h))  
            qp.fillRect(erect, lcolor)


        qp.setPen(QColor("#e0e0e0"))
        font = QFont("Sans", TEXT_SIZE)
        if evt_h > TEXT_SIZE + 15:
            text = text_shorten(event["title"], font, self.width()-10)
            qp.drawText(6, base_t + TEXT_SIZE + 9, text)




    def draw_dragging(self, qp):
        if type(self.calendar.dragging) == Asset:
            exp_dur = suggested_duration(self.calendar.dragging.get_duration())
        elif type(self.calendar.dragging) == Event:
            exp_dur = self.calendar.dragging["duration"]
        else: 
            return

        base_t = self.ts2pos(self.cursor_time)
        base_h = self.min_size * max(5, (exp_dur / 60))

        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor(200,200,200,128))
        qp.drawRect(0, base_t, self.width(), base_h)

       # self.status("Start time: {} End time: {}".format(
       #         time.strftime("%H:%M", time.localtime(self.cursor_time)), 
       #         time.strftime("%H:%M", time.localtime(self.cursor_time + exp_dur))
       #         ))
        



    def mouseMoveEvent(self, e):
        mx = e.x()
        my = e.y()
        tc = (my/self.min_size*60) + self.start_time
        for i, event in enumerate(self.calendar.events):
            try:
                end = self.calendar.events[i+1]["start"]
            except IndexError:
                end = self.start_time + (3600*24)

            if end >= tc > event["start"]:
                self.setToolTip("<b>{title}</b><br>Start: {start}".format(**event.meta))
                break
        else:
            return

        if e.buttons() != Qt.LeftButton:
            return
        
        encodedData = json.dumps([event.meta])
        mimeData = QMimeData()
        mimeData.setData("application/nx.event", encodedData.encode("ascii"))

        drag = QDrag(self)
        drag.targetChanged.connect(self.dragTargetChanged)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos() - self.rect().topLeft())
        self.calendar.drag_source = self
        dropAction = drag.exec_(Qt.MoveAction)  

    def dragTargetChanged(self, evt):
        if type(evt) == TXDayWidget:
            self.drag_outside = False
        else:
            self.drag_outside = True
            self.calendar.drag_source.update()


    def dragEnterEvent(self, evt):
        if evt.mimeData().hasFormat('application/nx.asset'):
            d = evt.mimeData().data("application/nx.asset").data()
            d = json.loads(d.decode("ascii"))
            if len(d) != 1:
                evt.ignore()
                return
            asset = Asset(from_data=d[0])

            if not eval(self.calendar.playout_config["scheduler_accepts"]):
                evt.ignore()
                return

            self.calendar.dragging = asset
            evt.accept()

        elif evt.mimeData().hasFormat('application/nx.event'):
            d = evt.mimeData().data("application/nx.event").data()
            d = json.loads(d.decode("ascii"))
            if len(d) != 1:
                evt.ignore()
                return
            event = Event(from_data=d[0])
            self.calendar.dragging = event
            evt.accept()

        else:
            evt.ignore()

        if self.calendar.drag_source:
            self.calendar.drag_source.drag_outside = False
            self.calendar.drag_source.update()


    def dragMoveEvent(self, evt):
        self.dragging= True
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
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if type(self.calendar.dragging) == Asset:
            self.status("Creating event from {} at time {}".format(self.calendar.dragging, time.strftime("%Y-%m-%d %H:%M", time.localtime(self.cursor_time))))
            query("event_from_asset", {
                    "id_asset" : self.calendar.dragging.id,
                    "id_channel" : self.id_channel,
                    "timestamp" : self.cursor_time
                })
        elif type(self.calendar.dragging) == Event:
            print ("Dropping event")
            event = self.calendar.dragging
            event["start"] = self.cursor_time
            result, data = query("set_day_events", 
                        {   
                            "id_channel" : self.id_channel,
                            "events" : [event.meta]
                        })

        self.calendar.drag_source = False
        self.calendar.dragging = False
        self.calendar.load()
        for day in self.calendar.days:
            day.update()
        QApplication.restoreOverrideCursor()



class HeaderWidget(QLabel):
    def __init__(self, *args):
        super(HeaderWidget, self).__init__(*args)
        self.setStyleSheet("background-color:#161616; text-align:center; qproperty-alignment: AlignCenter; font-size:14px; min-height:24px")
        self.setMinimumWidth(120)


class TXCalendar(QWidget):
    def __init__(self, parent, id_channel, view_start):
        super(TXCalendar, self).__init__(parent)
        self.view_start = view_start
        self.first_weekday = 0     # Monday is a first day of week
        self.num_days = 7

        self.id_channel = id_channel
        self.append_condition = False
        self.playout_config = config["playout_channels"][self.id_channel]
        self.day_start = self.playout_config["day_start"]
        self.start_time = datestr2ts(view_start, *self.day_start)

        self.days = []
        self.events = []
        self.dragging = False
        self.drag_source = False
        
        header_layout = QHBoxLayout()
        header_layout.addSpacing(CLOCKBAR_WIDTH+ 15)
        self.headers = []
        for i in range(self.num_days):
            self.headers.append(HeaderWidget())
            header_layout.addWidget(self.headers[-1])        
        header_layout.addSpacing(20)

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
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.zoom = QSlider(Qt.Horizontal)
        self.zoom.setMinimum(0)
        self.zoom.setMaximum(6000)
        self.zoom.valueChanged.connect(self.on_zoom)

        layout = QVBoxLayout()
        layout.addLayout(header_layout)
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



    def load(self):
        res, data = query("scheduler", {
            "id_channel" : self.id_channel,
            "date" : self.view_start,
            })
        self.events = []
        for event_data in data["data"]:
            e = Event(from_data=event_data)
            self.events.append(e)


        # t = datetime.date(syy, smm, sdd)

        # if t < datetime.date.today():
        #     s = " color='red'"
        # elif t > datetime.date.today():
        #     s = " color='green'"
        # else:
        #     s = ""

        # t = t.strftime("%A %Y-%m-%d")
        # self.parent().setWindowTitle("Week {} schedule {}".format(t))

        # self.date_display.setText("<font{}>{}</font>".format(s, t))
        
        for i, header in enumerate(self.headers):
            d = time.strftime("%a %x", time.localtime(self.start_time+(i*DAY))).upper()
            header.setText(d)


















def scheduler_toolbar(wnd):
    toolbar = QToolBar(wnd)

    action_week_prev = QAction(QIcon(pixlib["back"]), '&Previous week', wnd)        
    #action_week_prev.setShortcut('Alt+Left')
    action_week_prev.setStatusTip('Go to previous week')
    #action_week_prev.triggered.connect(wnd.on_week_prev)
    toolbar.addAction(action_week_prev)

    action_now = QAction(QIcon(pixlib["now"]), '&Now', wnd)        
    action_now.setShortcut('F1')
    action_now.setStatusTip('Go to now')
    #action_now.triggered.connect(wnd.on_now)
    toolbar.addAction(action_now)

    action_calendar = QAction(QIcon(pixlib["calendar"]), '&Calendar', wnd)        
    #action_calendar.setShortcut('Ctrl+D')
    action_calendar.setStatusTip('Open calendar')
    #action_calendar.triggered.connect(wnd.on_calendar)
    toolbar.addAction(action_calendar)

    action_refresh = QAction(QIcon(pixlib["refresh"]), '&Refresh', wnd)        
    action_refresh.setShortcut('F5')
    action_refresh.setStatusTip('Refresh rundown')
    #action_refresh.triggered.connect(partial(wnd.refresh, True))
    toolbar.addAction(action_refresh)

    action_week_next = QAction(QIcon(pixlib["next"]), '&Next week', wnd)        
    #action_week_next.setShortcut('Alt+Right')
    action_week_next.setStatusTip('Go to next week')
    #action_week_next.triggered.connect(wnd.on_week_next)
    toolbar.addAction(action_week_next)

    return toolbar




class Scheduler(BaseWidget):
    def __init__(self, parent):
        super(Scheduler, self).__init__(parent)
        toolbar = scheduler_toolbar(self)
        self.parent().setWindowTitle("Scheduler")

        #TODO: Get rid of this madness
        self.current_date = time.strftime("%Y-%m-%d")

        dt = datetime.datetime.strptime(self.current_date, '%Y-%m-%d')
        self.week_start = dt - datetime.timedelta(days = dt.weekday())

        self.view_start = self.week_start.strftime("%Y-%m-%d")
        self.id_channel   = 1 # TODO (get default from playout config, overide in setState)
        self.update_header()

        self.calendar = TXCalendar(self, self.id_channel, self.view_start)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.calendar, 1)

        self.setLayout(layout)

        self.calendar.load()



    def update_header(self):
        pass

    def save_state(self):
        state = {}
        state["class"] = "scheduler"
        return state

    def load_state(self, state):
        pass