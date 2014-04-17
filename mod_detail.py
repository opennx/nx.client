from firefly_common import *
from firefly_widgets import *

from mod_detail_video import VideoPlayer
from mod_detail_meta import MetaView




class Detail(BaseWidget):
    def __init__(self, parent):
        super(Detail, self).__init__(parent)
        self.parent = parent
        
        self.parent.setWindowTitle("Asset detail")

        self.tabs = QTabWidget()

        self.video = VideoPlayer(self)
        self.meta  = MetaView(self)

        self.tabs.addTab(self.video, "Preview")
        self.tabs.addTab(self.meta, "Metadata")

        layout = QVBoxLayout()
        layout.setContentsMargins(2,2,2,2)
        layout.addWidget(self.tabs)


        action_toggle_view = QAction('Toggle view', parent)        
        action_toggle_view.setShortcut('F3')
        action_toggle_view.triggered.connect(self.toggle_view)
        self.addAction(action_toggle_view)

        self.setLayout(layout)

    def save_state(self):
        state = {}
        state["class"] = "detail"
        return state

    def load_state(self, state):
        pass


    def toggle_view(self):
        self.tabs.setCurrentIndex(int(not self.tabs.currentIndex()))

    def focus(self, objects):
        if self.tabs.currentIndex() == 1:
            self.meta.load(objects)
        else:
            if len(objects) == 1 and objects[0].object_type in ["asset", "item"]:
                self.video.load(objects[0])
            else:
                self.video.unload()

