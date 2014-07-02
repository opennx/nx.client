from firefly_common import *
from firefly_widgets import *


class Detail(BaseWidget):
    def __init__(self, parent):
        super(Detail, self).__init__(parent)
        parent.setWindowTitle("Asset editor")


    def save_state(self):
        state = {}
        return state

    def load_state(self, state):
        pass


    ###############################################   

    def focus(self, objects):
        if len(objects) == 1 and objects[0].object_type in ["asset", "item"]:
            pass

    def new_asset(self):
        pass