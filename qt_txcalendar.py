import time
import math
from qt_common import *

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


class TXEvent(object):
    def __init__(self, start):
        self.start = start


class TXVerticalBar(QWidget):
    def __init__(self, parent):      
        super(TXVerticalBar, self).__init__(parent)
        self.setMouseTracking(True)

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

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        pass
            



class TXDayWidget(TXVerticalBar):  
    def __init__(self, parent, start_time):      
        super(TXDayWidget, self).__init__(parent)
        self.setMinimumWidth(140)
        self.start_time = start_time

      
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


    def mouseMoveEvent(self, evt):
        tc = (evt.y()/self.min_size*60) + self.start_time
        
    #    print (time.strftime("%Y-%m-%d %H:%M", time.localtime(tc)))
        



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


class TXCalendar(QWidget):
    def __init__(self, parent, view_start):
        super(TXCalendar, self).__init__(parent)
        self.week_start = 0     # Monday is a first day of week
        self.day_start = (6,00) # Broadcast starts at 6:00 AM
        self.num_days = 7

        self.start_time = datestr2ts(view_start, *self.day_start)

        self.parent = parent

        self.days = []
        self.events = []

        cols_layout = QHBoxLayout()
        cols_layout.addWidget(TXClockBar(self, self.day_start), 0)

        for i in range(self.num_days):
            self.days.append(TXDayWidget(self, self.start_time+(i*DAY)))
            cols_layout.addWidget(self.days[-1], 1)        
        
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(cols_layout)
        self.scroll_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

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




if __name__ == "__main__":
    import sys
    class DemoWnd(QMainWindow):
        def __init__(self):
            super(DemoWnd, self).__init__()
            self.setStyleSheet(base_css)
            self.calendar = TXCalendar(self, time.strftime("%Y-%m-%d"))
            self.setCentralWidget(self.calendar)
            self.show()

    app = QApplication(sys.argv)
    wnd = DemoWnd()
    app.exec_()
