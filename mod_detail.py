from firefly_common import *
from firefly_widgets import *

from mod_detail_video import VideoPreview
from mod_detail_meta import MetaView









def navigation_toolbar(parent):
    toolbar = QToolBar(parent)
    toolbar.setStyleSheet("background-color:transparent;")

    ################################
    ## Hidden actions

    action_toggle_view = QAction('Toggle view', parent)        
    action_toggle_view.setShortcut('F3')
    action_toggle_view.triggered.connect(parent.toggle_view)
    parent.addAction(action_toggle_view)



    action_goto_in = QAction('Go to IN', parent)        
    action_goto_in.setShortcut('Q')
    action_goto_in.triggered.connect(parent.on_goto_in)
    parent.addAction(action_goto_in)

    action_goto_out = QAction('Go to OUT', parent)        
    action_goto_out.setShortcut('W')
    action_goto_out.triggered.connect(parent.on_goto_out)
    parent.addAction(action_goto_out)



    action_shuttle_left = QAction('Shuttle left', parent)        
    action_shuttle_left.setShortcut('J')
    action_shuttle_left.triggered.connect(parent.on_shuttle_left)
    parent.addAction(action_shuttle_left)

    action_shuttle_pause = QAction('Shuttle right', parent)        
    action_shuttle_pause.setShortcut('K')
    action_shuttle_pause.triggered.connect(parent.on_play)
    parent.addAction(action_shuttle_pause)

    action_shuttle_right = QAction('Shuttle right', parent)        
    action_shuttle_right.setShortcut('L')
    action_shuttle_right.triggered.connect(parent.on_shuttle_right)
    parent.addAction(action_shuttle_right)

    ## Hidden actions
    ################################
    ## Visible actions

    toolbar.addWidget(ToolBarStretcher(parent))

    action_clear_in = QAction(QIcon(pixlib["clear_in"]), 'Clear IN', parent)        
    action_clear_in.setShortcut('d')
    action_clear_in.setStatusTip('Clear IN')
    action_clear_in.triggered.connect(parent.on_clear_in)
    toolbar.addAction(action_clear_in)

    action_mark_in = QAction(QIcon(pixlib["mark_in"]), 'Mark IN', parent)        
    action_mark_in.setShortcut('E')
    action_mark_in.setStatusTip('Mark IN')
    action_mark_in.triggered.connect(parent.on_mark_in)
    toolbar.addAction(action_mark_in)


    action_frame_prev = QAction(QIcon(pixlib["frame_prev"]), 'Previous frame', parent)        
    action_frame_prev.setShortcut('Left')
    action_frame_prev.setStatusTip('Go to previous frame')
    action_frame_prev.triggered.connect(parent.on_frame_prev)
    toolbar.addAction(action_frame_prev)

    parent.action_frame_prev = QAction(QIcon(pixlib["play"]), 'Play/Pause', parent)        
    parent.action_frame_prev.setShortcut('Space')
    parent.action_frame_prev.setStatusTip('Play/Pause')
    parent.action_frame_prev.triggered.connect(parent.on_play)
    toolbar.addAction(parent.action_frame_prev)

    action_frame_next = QAction(QIcon(pixlib["frame_next"]), 'Next frame', parent)        
    action_frame_next.setShortcut('Right')
    action_frame_next.setStatusTip('Go to next frame')
    action_frame_next.triggered.connect(parent.on_frame_next)
    toolbar.addAction(action_frame_next)


    action_mark_out = QAction(QIcon(pixlib["mark_out"]), 'Mark OUT', parent)        
    action_mark_out.setShortcut('R')
    action_mark_out.setStatusTip('Mark OUT')
    action_mark_out.triggered.connect(parent.on_mark_out)
    toolbar.addAction(action_mark_out)

    action_clear_out = QAction(QIcon(pixlib["clear_out"]), 'Clear OUT', parent)        
    action_clear_out.setShortcut('f')
    action_clear_out.setStatusTip('Clear OUT')
    action_clear_out.triggered.connect(parent.on_clear_out)
    toolbar.addAction(action_clear_out)


    ## Visible actions
    ################################

    toolbar.addWidget(ToolBarStretcher(parent))
    return toolbar



class Detail(BaseWidget):
    def __init__(self, parent):
        super(Detail, self).__init__(parent)
        self.parent = parent
        
        self.parent.setWindowTitle("Asset detail")


        self.tabs = QTabWidget()

        ####################################
        ## Video preview

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
        self.buttons = navigation_toolbar(self)

        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)
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

        video_preview = QWidget()
        video_preview.setLayout(layout)

        
        ## Video preview
        ####################################

        self.meta = MetaView(self)


        self.tabs.addTab(video_preview, "Preview")
        self.tabs.addTab(self.meta, "Metadata")


        layout = QVBoxLayout()
        layout.setContentsMargins(2,2,2,2)
        layout.addWidget(self.tabs)
        self.setLayout(layout)





    def getState(self):
        state = {}
        state["class"] = "detail"
        return state


    def setState(self, state):
        pass


    def toggle_view(self):
        self.tabs.setCurrentIndex(int(not self.tabs.currentIndex()))

    def focus(self, objects):
        if self.tabs.currentIndex() == 1:
            self.meta.load(objects)
        else:
            print ("OPEN VIDEO PREVIEW")


    ###############################################
    ## navigation

    def on_frame_prev(self):
        self.status("on_frame_prev")

    def on_frame_next(self):
        self.status("on_frame_next")

    def on_play(self):
        self.status("on_play")

    def on_shuttle_left(self):
        self.status("on_shuttle_left")

    def on_shuttle_right(self):
        self.status("on_shuttle_right")

    def on_mark_in(self):
        self.status("on_mark_in")

    def on_mark_out(self):
        self.status("on_mark_out")

    def on_clear_in(self):
        self.status("on_clear_in")

    def on_clear_out(self):
        self.status("on_clear_out")

    def on_goto_in(self):
        self.status("on_goto_in")

    def on_goto_out(self):
        self.status("on_goto_out")
