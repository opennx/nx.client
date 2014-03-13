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



class OnAir(QWidget):
    def __init__(self, parent):
        super(OnAir, self).__init__(parent)
        self.parent = parent

        self.pos = 0
        self.dur = 0
        self.current  = "(loading)"
        self.cued     = "(loading)"
        self.request_time = 0


        self.parent.setWindowTitle("On air ctrl")


        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
        QProgressBar{background: #3d3d3d; border:0; border-radius:0; height: 4px}
        QProgressBar::chunk{background:qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,  stop: 0 #009fbc, stop: 1 #00a5c3);}
        """)
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

        
        

        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.progress_bar,0)
        layout.addLayout(btns_layout,0)
        self.setLayout(layout)

        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.update_display)
        self.display_timer.start(80)


    def on_take(self, evt=False):
        query("take", {"id_channel":self.parent.id_channel}, "play1")


    def on_freeze(self, evt=False):
        query("freeze", {"id_channel":self.parent.id_channel}, "play1")

    
    def on_retake(self, evt=False):
        query("retake", {"id_channel":self.parent.id_channel}, "play1")

        
    def on_abort(self, evt=False):
        query("abort", {"id_channel":self.parent.id_channel}, "play1")

            




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

        if self.dur !=  status["duration"]:
            self.dur = status["duration"]
            self.progress_bar.setMaximum(int(self.dur * 25))

        if self.current != status["current_title"]:
            self.current = status["current_title"]
        
        if self.cued    != status["cued_title"]:
            self.cued    != status["cued_title"]



    def update_display(self):
        self.progress_bar.setValue(int(self.pos * 25))