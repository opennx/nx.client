from firefly_common import *
from firefly_widgets import *
from nx.common.metadata import fract2float
from functools import partial

def proxy_path(id_asset):
    host = config.get("media_host", False) or config["hive_host"]
    port = config.get("media_port", False) or config["hive_port"]
    url = "http://{}:{}/proxy/{:04d}/{:d}.mp4".format(host, port, int(id_asset/1000), id_asset)
    print (url)
    return QUrl(url)


def navigation_toolbar(wnd):
    action_goto_in = QAction('Go to IN', wnd)        
    action_goto_in.setShortcut('Q')
    action_goto_in.triggered.connect(wnd.on_goto_in)
    wnd.addAction(action_goto_in)

    action_goto_out = QAction('Go to OUT', wnd)        
    action_goto_out.setShortcut('W')
    action_goto_out.triggered.connect(wnd.on_goto_out)
    wnd.addAction(action_goto_out)

    action_shuttle_left = QAction('Shuttle left', wnd)        
    action_shuttle_left.setShortcut('J')
    action_shuttle_left.triggered.connect(wnd.on_shuttle_left)
    wnd.addAction(action_shuttle_left)

    action_shuttle_pause = QAction('Shuttle right', wnd)        
    action_shuttle_pause.setShortcut('K')
    action_shuttle_pause.triggered.connect(wnd.on_play)
    wnd.addAction(action_shuttle_pause)

    action_shuttle_right = QAction('Shuttle right', wnd)        
    action_shuttle_right.setShortcut('L')
    action_shuttle_right.triggered.connect(wnd.on_shuttle_right)
    wnd.addAction(action_shuttle_right)

    action_frame_prev5 = QAction('Previous 5 frames', wnd)        
    action_frame_prev5.setShortcut('1')
    action_frame_prev5.triggered.connect(partial(wnd.on_frame_step, -5))
    wnd.addAction(action_frame_prev5)

    action_frame_next5 = QAction('Next 5 frames', wnd)        
    action_frame_next5.setShortcut('2')
    action_frame_next5.triggered.connect(partial(wnd.on_frame_step, 5))
    wnd.addAction(action_frame_next5)


    ################################################################

    toolbar = QToolBar(wnd)
    toolbar.setStyleSheet("background-color:transparent;")

    toolbar.addWidget(ToolBarStretcher(wnd))

    action_clear_in = QAction(QIcon(pixlib["clear_in"]), 'Clear IN', wnd)        
    action_clear_in.setShortcut('d')
    action_clear_in.setStatusTip('Clear IN')
    action_clear_in.triggered.connect(wnd.on_clear_in)
    toolbar.addAction(action_clear_in)

    action_mark_in = QAction(QIcon(pixlib["mark_in"]), 'Mark IN', wnd)        
    action_mark_in.setShortcut('E')
    action_mark_in.setStatusTip('Mark IN')
    action_mark_in.triggered.connect(wnd.on_mark_in)
    toolbar.addAction(action_mark_in)

    action_frame_prev = QAction(QIcon(pixlib["frame_prev"]), 'Previous frame', wnd)        
    action_frame_prev.setShortcut('3')
    action_frame_prev.setStatusTip('Go to previous frame')
    action_frame_prev.triggered.connect(partial(wnd.on_frame_step, -1))
    toolbar.addAction(action_frame_prev)

    wnd.action_play = QAction(QIcon(pixlib["play"]), 'Play/Pause', wnd)        
    wnd.action_play.setShortcut('Space')
    wnd.action_play.setStatusTip('Play/Pause')
    wnd.action_play.triggered.connect(wnd.on_play)
    toolbar.addAction(wnd.action_play)

    action_frame_next = QAction(QIcon(pixlib["frame_next"]), 'Next frame', wnd)        
    action_frame_next.setShortcut('4')
    action_frame_next.setStatusTip('Go to next frame')
    action_frame_next.triggered.connect(partial(wnd.on_frame_step, 1))
    toolbar.addAction(action_frame_next)

    action_mark_out = QAction(QIcon(pixlib["mark_out"]), 'Mark OUT', wnd)        
    action_mark_out.setShortcut('R')
    action_mark_out.setStatusTip('Mark OUT')
    action_mark_out.triggered.connect(wnd.on_mark_out)
    toolbar.addAction(action_mark_out)

    action_clear_out = QAction(QIcon(pixlib["clear_out"]), 'Clear OUT', wnd)        
    action_clear_out.setShortcut('f')
    action_clear_out.setStatusTip('Clear OUT')
    action_clear_out.triggered.connect(wnd.on_clear_out)
    toolbar.addAction(action_clear_out)

    toolbar.addWidget(ToolBarStretcher(wnd))
    return toolbar


class VideoWidget(QVideoWidget):
    def __init__(self, parent):
        super(VideoWidget,self).__init__(parent)
        self.setMinimumWidth(512)
        self.setMinimumHeight(288)
        self.pix = pixlib["thumb_video"]

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        qp.setPen(Qt.NoPen)       
        qp.setBrush(QColor("#000000"))
        qp.drawRect(0, 0, self.width(), self.height())
        x, y = int(self.width()/2), int(self.height()/2)
        x -= int(self.pix.width()/2)
        y -= int(self.pix.height()/2)
        qp.drawPixmap(x, y, self.pix)

    def load_thumb(self, id_asset, content_type):
        self.pix = pixlib[{
            VIDEO: "thumb_video",
            AUDIO: "thumb_audio",
            IMAGE: "thumb_image",
            TEXT : "thumb_text"
            }[content_type]]


class VideoPlayer(QWidget):
    def __init__(self, parent):
        super(VideoPlayer, self).__init__(parent)

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

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = VideoWidget(self)
        self.current_id = False

        self.timeline = QSlider(Qt.Horizontal)
        self.timeline.setRange(0, 0)
        self.timeline.sliderMoved.connect(self.set_position)

        self.buttons = navigation_toolbar(self)

        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.din  , 0, 0)
        layout.addWidget(QWidget() , 0, 1)
        layout.addWidget(self.dout , 0, 2)
        
        layout.addWidget(self.video_widget ,1, 0, 1, -1)
        layout.addWidget(self.timeline     ,2, 0, 1, -1)
        
        layout.addWidget(self.dpos,    3,0)
        layout.addWidget(self.buttons, 3,1)
        layout.addWidget(self.ddur,    3,2)
        
        layout.setRowStretch(1,2)
        
        layout.setColumnStretch(0,0)
        layout.setColumnStretch(1,1)
        layout.setColumnStretch(2,0)

        self.setLayout(layout)

        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setNotifyInterval(40)
        self.media_player.stateChanged.connect(self.media_state_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.error.connect(self.handle_error)


    def status(self, message, message_type=INFO):
        self.parent().parent().parent().status(message, message_type)

    def media_state_changed(self, state):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.action_play.setIcon(QIcon(pixlib["pause"]))
        else:
            self.action_play.setIcon(QIcon(pixlib["play"]))

    def position_changed(self, position):
        self.timeline.setValue(position)
        if self.fps:
            self.dpos.setText(s2tc(position/1000.0, self.fps))
        else:
            self.dpos.setText(s2time(position/1000.0))

    def duration_changed(self, duration):
        self.timeline.setRange(0, duration)
        if self.fps:
            dstring = s2tc(duration/1000.0, self.fps)
        else:
            dstring = s2tc(duration/1000.0)

        self.ddur.setText(dstring)
        print ("DUR", dstring)

    def get_position(self):
        return self.media_player.position()

    def set_position(self, position):
        self.media_player.setPosition(position)

    def handle_error(self):
        self.status(self.media_player.errorString(), ERROR)

    ###############################################
    ## loading


    def load(self, obj):
        self.status("")
        id_asset = obj.id
        
        id_asset = obj.id if obj.object_type == "asset" else obj["id_asset"]
        if not id_asset:
            self.unload()
            return    

        try:
            if int(id_asset) < 1 or id_asset == self.current_id:
                return
        except:
            return
            
        self.current_object = obj
        self.current_id = id_asset      
        
        try:
            self.fps = fract2float(self.current_object["video/fps"])
        except:
            self.fps = 0
        
        self.video_widget.load_thumb(id_asset, obj["content_type"])

        self.unload()
        self.action_play.setIcon(QIcon(pixlib["play"]))



    def unload(self):
        if self.media_player.state() in [QMediaPlayer.PlayingState,QMediaPlayer.PausedState]:
            self.media_player.stop()


    ###############################################
    ## navigation

    def on_frame_step(self, frames):
        fps = self.fps or 25.0 # default
        toffset = (frames / fps) * 1000
        self.media_player.pause()
        self.set_position(self.media_player.position()+toffset)


    def on_play(self):
        if not self.current_id:
            return

        if self.media_player.state() == QMediaPlayer.StoppedState:
            self.status("Loading. Please wait...")
            self.media_player.setMedia(QMediaContent(proxy_path(self.current_id)))
            self.media_player.play()
            self.media_player.setPlaybackRate(1.0)
            self.status("Playing")

        elif self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.status("Paused")
        else:
            self.media_player.play()
            self.media_player.setPlaybackRate(1.0)
            self.status("Playing")


    def on_shuttle_left(self):
        old_rate = self.media_player.playbackRate()
        new_rate = min(-.5, old_rate - 0.5)
        self.media_player.play()
        self.media_player.setPlaybackRate(new_rate)
        self.status("Playing {}x".format(self.media_player.playbackRate()))

    def on_shuttle_right(self):
        old_rate = self.media_player.playbackRate()
        new_rate = max(.5, old_rate + 0.5)
        self.media_player.play()
        self.media_player.setPlaybackRate(new_rate)
        self.status("Playing {}x".format(self.media_player.playbackRate()))

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
