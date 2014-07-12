import re
import math
import datetime

from nx.objects import *
from nx.common.utils import *

from firefly_common import *
from firefly_view import *

from dlg_event import EventDialog


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

CLOCKBAR_WIDTH = 45



def suggested_duration(dur):
    adur = int(dur) + 360
    g = adur % 300
    if g > 150:
        r =  adur-g + 300
    else:
        r =  adur -g
    return r

def text_shorten(text, font, target_width):
    fm = QFontMetrics(font)
    exps =  [r"\W|_", r"[a-z]([aeiou])", r"[a-z]", r"."]
    r = exps.pop(0)
    text = text[::-1]
    while fm.width(text) > target_width:
        text, n = re.subn(r, "", text, 1)
        if n == 0:
            r = exps.pop(0)
    return text[::-1]








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
    def __init__(self, parent):
        super(TXClockBar, self).__init__(parent)
        self.setMinimumWidth(CLOCKBAR_WIDTH)
        self.day_start = 0

    def drawWidget(self, qp):
        if not self.day_start:
            return 
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
    def __init__(self, parent):      
        super(TXDayWidget, self).__init__(parent)
        self.setMinimumWidth(120)
        self.start_time = 0
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

    def round_ts(self, ts):
        base = 300
        return int(base * round(float(ts)/base))


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

        drop_ts = self.round_ts(self.cursor_time - self.calendar.drag_offset)

        base_t = self.ts2pos(drop_ts) 
        base_h = self.sec_size * max(300, exp_dur)

        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor(200,200,200,128))
        qp.drawRect(0, base_t, self.width(), base_h)

        self.status("Start time: {} End time: {}".format(
                time.strftime("%H:%M", time.localtime(drop_ts)), 
                time.strftime("%H:%M", time.localtime(drop_ts + max(300, exp_dur)))
                ))
        

    def mouseMoveEvent(self, e):
        mx = e.x()
        my = e.y()
        ts = (my/self.min_size*60) + self.start_time
        for i, event in enumerate(self.calendar.events):
            try:
                end = self.calendar.events[i+1]["start"]
            except IndexError:
                end = self.start_time + (3600*24)

            if end >= ts > event["start"] >= self.start_time:
                self.setToolTip("<b>{title}</b><br>Start: {start}".format(
                    title=event["title"],
                    start=time.strftime("%H:%M",time.localtime(event["start"]))
                    ))
                break
        else:
            return

        if e.buttons() != Qt.LeftButton:
            return
        
        self.calendar.drag_offset = ts - event["start"]
        print(self.calendar.drag_offset, event["duration"])
        if self.calendar.drag_offset > event["duration"]:
            self.calendar.drag_offset = event["duration"]

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
            self.calendar.drag_offset = 20/self.sec_size   #### TODO: SOMETHING MORE CLEVER
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
        cursor_time = (self.my / self.min_size*60) + self.start_time
        if self.round_ts(cursor_time) != self.round_ts(self.cursor_time):
            self.cursor_time = cursor_time
            self.update()

    def dragLeaveEvent(self, evt):
        self.dragging = False
        self.update()

    def dropEvent(self, evt):
        drop_tc = max(self.start_time, self.round_ts(self.cursor_time - self.calendar.drag_offset))
        if type(self.calendar.dragging) == Asset:

            if evt.keyboardModifiers() & Qt.ControlModifier:
                self.status("Creating event from {} at time {}".format(self.calendar.dragging, time.strftime("%Y-%m-%d %H:%M", time.localtime(self.cursor_time))))
                dlg = EventDialog(self,
                        id_asset=self.calendar.dragging.id,
                        id_channel=self.id_channel,
                        timestamp=drop_tc
                    )
                dlg.exec_()
            else:
                query("set_events", {
                        "id_channel" : self.id_channel,

                        "events" : [{
                            "id_asset" : self.calendar.dragging.id,
                            "start" : drop_tc
                            # TODO: If Alt modifier is pressed add id_event of original event here
                            }]
                    })

        elif type(self.calendar.dragging) == Event:
            event = self.calendar.dragging
            event["start"] = drop_tc
            result, data = query("set_events", 
                        {   
                            "id_channel" : self.id_channel,
                            "events" : [event.meta]
                        })


        self.calendar.drag_source = False
        self.calendar.dragging = False
        self.calendar.refresh()
        for day in self.calendar.days:
            day.update()




class HeaderWidget(QLabel):
    def __init__(self, *args):
        super(HeaderWidget, self).__init__(*args)
        self.setStyleSheet("background-color:#161616; text-align:center; qproperty-alignment: AlignCenter; font-size:14px; min-height:24px")
        self.setMinimumWidth(120)

    def set_rundown(self, id_channel, date):
        self.id_channel = id_channel
        self.date = date
        t = time.strftime("%a %Y-%m-%d", time.localtime(date))
        if date < time.time() - (3600*24):
            self.setText("<font color='red'>{}</font>".format(t))
        elif date > time.time():
            self.setText("<font color='green'>{}</font>".format(t))
        else:
            self.setText(t)


    def mouseDoubleClickEvent(self, event):
        self.parent().parent().parent().parent().focus_rundown(self.id_channel, self.date) # Please kill me


class TXCalendar(QWidget):
    def __init__(self, parent):
        super(TXCalendar, self).__init__(parent)
        self.id_channel = 0
        self.num_days = 7

        self.events = []
        self.dragging = False
        self.drag_offset = 0
        self.drag_source = False
        self.append_condition = False
        
        header_layout = QHBoxLayout()
        header_layout.addSpacing(CLOCKBAR_WIDTH+ 15)

        self.headers = []
        for i in range(self.num_days):
            self.headers.append(HeaderWidget())
            header_layout.addWidget(self.headers[-1])        
        header_layout.addSpacing(20)


        cols_layout = QHBoxLayout()

        self.clock_bar = TXClockBar(self)
        cols_layout.addWidget(self.clock_bar, 0)

        self.days = []
        for i in range(self.num_days):
            self.days.append(TXDayWidget(self))
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


    def refresh(self):
        self.load()

    def load(self, id_channel=False, ts=False):
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.WaitCursor)

        if id_channel:
            self.id_channel = id_channel
            self.playout_config = config["playout_channels"][self.id_channel]
            self.day_start = self.playout_config["day_start"]

        if ts:
            self.ts = ts    
            dt = datetime.datetime.fromtimestamp(ts)

            self.week_start = dt - datetime.timedelta(days = dt.weekday())
            self.week_start = self.week_start.replace(hour = self.day_start[0], minute = self.day_start[1], second = 0)
            
            self.start_time = time.mktime(self.week_start.timetuple()) 
            self.end_time = self.start_time + (3600*24*7)


        self.events = []

        res, data = query("get_events", {
            "id_channel" : self.id_channel,
            "start_time" : self.start_time,
            "end_time" : self.end_time,
            "extend"   : True
            })

        for event_data in data["events"]:
            e = Event(from_data=event_data)
            self.events.append(e)

        self.clock_bar.day_start = self.day_start
        self.clock_bar.update()

        for i, day_widget in enumerate(self.days):
            day_widget.start_time = self.start_time+(i*DAY)
            day_widget.update()

        for i, header in enumerate(self.headers):
            d = time.strftime("%a %x", time.localtime(self.start_time+(i*DAY))).upper()
            header.set_rundown(self.id_channel, self.start_time+(i*DAY))

        QApplication.restoreOverrideCursor()




def scheduler_toolbar(wnd):
    toolbar = QToolBar(wnd)

    action_week_prev = QAction(QIcon(pixlib["back"]), '&Previous week', wnd)        
    action_week_prev.setStatusTip('Go to previous week')
    action_week_prev.triggered.connect(wnd.on_week_prev)
    toolbar.addAction(action_week_prev)

    action_refresh = QAction(QIcon(pixlib["refresh"]), '&Refresh', wnd)        
    action_refresh.setStatusTip('Refresh scheduler')
    action_refresh.triggered.connect(wnd.refresh)
    toolbar.addAction(action_refresh)

    action_week_next = QAction(QIcon(pixlib["next"]), '&Next week', wnd)        
    action_week_next.setShortcut('Alt+Right')
    action_week_next.setStatusTip('Go to next week')
    action_week_next.triggered.connect(wnd.on_week_next)
    toolbar.addAction(action_week_next)

    return toolbar


class Scheduler(BaseWidget):
    def __init__(self, parent):
        super(Scheduler, self).__init__(parent)
        toolbar = scheduler_toolbar(self)
        self.parent().setWindowTitle("Scheduler")

        self.id_channel   = 1 # TODO (get default from playout config, overide in setState)

        self.calendar = TXCalendar(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.calendar, 1)

        self.setLayout(layout)
        self.calendar.load(self.id_channel, time.time())


    def save_state(self):
        state = {}
        return state

    def load_state(self, state):
        pass

    def refresh(self):
        self.calendar.refresh()

    def on_week_prev(self):
        self.calendar.load(self.calendar.id_channel, self.calendar.start_time-(3600*24*7))
    
    def on_week_next(self):
        self.calendar.load(self.calendar.id_channel, self.calendar.start_time+(3600*24*7))
        