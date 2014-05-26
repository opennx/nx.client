import math

from firefly_common import *
from firefly_widgets import *


class OnAirButton(QPushButton):
    def __init__(self, title, parent=None, on_click=False):
        super(OnAirButton, self).__init__(parent)
        self.setText(title)
        
        if title == "Freeze":
            bg_col = "qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,  stop: 0 #c01616, stop: 1 #941010);"
            self.setToolTip("Pause/unpause current clip")
        elif title == "Take":
            bg_col = "qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,  stop: 0 #16c316, stop: 1 #109410);"
            self.setToolTip("Start cued clip")
        else:
            bg_col = "qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,  stop: 0 #787878, stop: 1 #565656);"
        self.setStyleSheet("OnAirButton{font-size:16px; font-weight: bold; font-family: Arial; color: #eeeeee; border:  1px raised #323232;  width:80px; height:30px; background: %s }  OnAirButton:pressed {border-style: inset;} "%bg_col)
        
        if on_click:
            self.clicked.connect(on_click)

class OnAirLabel(QLabel):
    def __init__(self,head, default, parent=None, tcolor="#eeeeee"):
        super(OnAirLabel,self).__init__(parent)
        self.head = head 
        self.setStyleSheet("background-color: #161616; padding:5px; margin:3px; font:16px; font-weight: bold; color : {};".format(tcolor))
        self.setMinimumWidth(160)
    
    def set_text(self,text):
       self.setText("%s: %s"%(self.head,text))
 



class OnAir(QWidget):
    def __init__(self, parent):
        super(OnAir, self).__init__(parent)

        self.pos = 0
        self.dur = 0
        self.current  = "(loading)"
        self.cued     = "(loading)"
        self.request_time = 0
        self.local_request_time = time.time()

        self.fps = 25.0

        self.parent().setWindowTitle("On air ctrl")

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)

        self.btn_take    = OnAirButton(u"Take",   self, self.on_take)
        self.btn_freeze  = OnAirButton(u"Freeze", self, self.on_freeze)
        self.btn_retake  = OnAirButton(u"Retake", self, self.on_retake)
        self.btn_abort   = OnAirButton(u"Abort",  self, self.on_abort)
        
        btns_layout = QHBoxLayout()
        
        btns_layout.addStretch(1)
        btns_layout.addWidget(self.btn_take ,0)
        btns_layout.addWidget(self.btn_freeze ,0)
        btns_layout.addWidget(self.btn_retake,0)
        btns_layout.addWidget(self.btn_abort,0)
        btns_layout.addStretch(1)

        self.display_clock   = OnAirLabel("CLK", "--:--:--:--")
        self.display_pos     = OnAirLabel("POS", "--:--:--:--")
      
        self.display_current = OnAirLabel("CUR","(no clip)", tcolor="#cc0000")
        self.display_cued    = OnAirLabel("NXT","(no clip)", tcolor="#00cc00")
       
        self.display_rem     = OnAirLabel("REM","(unknown)")
        self.display_dur     = OnAirLabel("DUR", "--:--:--:--")
        
        info_layout = QGridLayout()    
        info_layout.setContentsMargins(0,0,0,0)
        info_layout.setSpacing(2)

        info_layout.addWidget(self.display_clock,   0, 0)    
        info_layout.addWidget(self.display_pos,     1, 0)  

        info_layout.addWidget(self.display_current, 0, 1)          
        info_layout.addWidget(self.display_cued,    1, 1)

        info_layout.addWidget(self.display_rem,     0, 2)
        info_layout.addWidget(self.display_dur,     1, 2)

        info_layout.setColumnStretch(1,1)

        layout = QVBoxLayout()
        layout.addLayout(info_layout,0)
        layout.addStretch(1)
        layout.addWidget(self.progress_bar,0)
        layout.addLayout(btns_layout,0)
        self.setLayout(layout)

        self.display_timer = QTimer(self)
        self.display_timer.timeout.connect(self.update_display)
        self.display_timer.start(40)

    @property
    def route(self):
        return "play{}".format(self.parent.id_channel)

    def on_take(self, evt=False):
        query("take", {"id_channel":self.parent().id_channel}, self.route)

    def on_freeze(self, evt=False):
        query("freeze", {"id_channel":self.parent().id_channel}, self.route)

    def on_retake(self, evt=False):
        query("retake", {"id_channel":self.parent().id_channel}, self.route)

    def on_abort(self, evt=False):
        query("abort", {"id_channel":self.parent().id_channel}, self.route)

    def getState(self):
        state = {}
        state["class"] = "onair"
        return state

    def setState(self, state):
        pass


    def update_status(self, data):
        status = data.data
        self.pos = status["position"]
        self.request_time = status["request_time"]
        self.local_request_time = time.time()

        if self.dur !=  status["duration"]:
            self.dur = status["duration"]
            self.progress_bar.setMaximum(int(self.dur * self.fps))
            self.display_dur.set_text(f2tc(self.dur, self.fps))

        if self.current != status["current_title"]:
            self.current = status["current_title"]
            self.display_current.set_text(self.current)
        
        if self.cued != status["cued_title"]:
            self.cued = status["cued_title"]
            self.display_cued.set_text(self.cued)


    def update_display(self):
        try:
            adv = time.time() - self.local_request_time
            rtime = self.request_time+adv
            rpos = self.pos + (adv*self.fps)

            clock = time.strftime("%H:%M:%S:{:02d}", time.localtime(rtime)).format(int(25*(rtime-math.floor(rtime))))
            self.display_clock.set_text(clock)
        
            self.progress_bar.setValue(int(rpos*self.fps))
            self.display_pos.set_text(f2tc(min(self.dur, rpos), self.fps))
            self.display_rem.set_text(f2tc(max(0,self.dur - rpos), self.fps))
        except:
            pass