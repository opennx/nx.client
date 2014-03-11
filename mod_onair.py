from firefly_common import *
from firefly_widgets import *






class OnAir(BaseWidget):
    def __init__(self, parent):
        super(OnAir, self).__init__(parent)
        self.parent = parent
        
        self.parent.setWindowTitle("On air ctrl")

        layout = QVBoxLayout()


        self.setLayout(layout)






    def getState(self):
        state = {}
        state["class"] = "onair"
        return state

    def setState(self, state):
        pass


    def update_status(self, data):
        pass
