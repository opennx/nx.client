from firefly_common import *


class Detail(QWidget):
    def __init__(self, parent):
        super(Detail, self).__init__(parent)
        self.parent = parent
        self.setStyleSheet("background-color: #0000cc;")

    def getState(self):
        state = {}
        state["window_class"] = "detail"
        return state


    def setState(self, state):
        pass