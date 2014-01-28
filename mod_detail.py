from firefly_common import *
from firefly_widgets import *


class VideoPreview(QWidget):
    def __init__(self, parent):
        super(VideoPreview, self).__init__(parent)
        self.setStyleSheet("background-color : #000000; border: 1px solid green;")




class Detail(BaseWidget):
    def __init__(self, parent):
        super(Detail, self).__init__(parent)
        self.parent = parent
        
        self.parent.setWindowTitle("Asset detail")

        self.ddur  = NXE_timecode(self)
        self.dpos  = NXE_timecode(self)
        self.din   = NXE_timecode(self)
        self.dout  = NXE_timecode(self)

        self.ddur.setEnabled(False)
        self.dpos.setEnabled(False)

        self.ddur.setStatusTip("Duration")
        self.dpos.setStatusTip("Position")
        self.din.setStatusTip ("Mark In")
        self.dout.setStatusTip("Mark Out")


        self.video = VideoPreview(self)

        self.timeline = QWidget()
        self.buttons = QWidget()

        layout = QGridLayout()
        layout.addWidget(self.din  , 0, 0)
        layout.addWidget(QWidget() , 0, 1)
        layout.addWidget(self.dout , 0, 2)
        
        layout.addWidget(self.video    ,1, 0, 1, -1)
        layout.addWidget(self.timeline ,2, 0, 1, -1)
        
        layout.addWidget(self.dpos,    3,0)
        layout.addWidget(self.buttons, 3,1)
        layout.addWidget(self.ddur,    3,2)
        
        layout.setRowStretch(1,2)
        
        layout.setColumnStretch(0,0)
        layout.setColumnStretch(1,1)
        layout.setColumnStretch(2,0)

        self.setLayout(layout)




    def getState(self):
        state = {}
        state["class"] = "detail"
        return state


    def setState(self, state):
        pass

