from firefly_common import *


class Rundown(QWidget):
    def __init__(self, parent):
        super(Rundown, self).__init__(parent)
        self.parent = parent
        self.setStyleSheet("background-color: #cc00cc;")

    def getState(self):
        state = {}
        state["window_class"] = "rundown"
        return state


    def setState(self, state):
        pass