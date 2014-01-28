import uuid

from nx.common import *
from nx.common.metadata import meta_types
from nx.connection import *

from qt_common import *



def ffsettings():
    return QSettings(".ffstate", QSettings.IniFormat)

def get_pix(name):
    return QPixmap(os.path.join("images","%s.png" % name))

class Pixlib(dict):
    def __getitem__(self, key):
        if not key in self:
            self[key] = get_pix(key)
        return self.get(key, None)


class BaseDock(QDockWidget):
    def __init__(self, parent, object_name=False):
        super(BaseDock, self).__init__(parent)

        if object_name:
            self.setObjectName(object_name)
        else:
            self.setObjectName(str(uuid.uuid1()))

        self.parent = parent
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setFloating(True)

    def closeEvent(self, evt):
        self.deleteLater()
        self.parent.on_dock_closed(self)

    def setState(self, main_widget, state):
        self.main_widget = main_widget(self)
        self.setWidget(self.main_widget)
        self.main_widget.setState(state)
        self.init_size = state.get("size",False)

    def getState(self):
        state = self.main_widget.getState() 
        #state = {"class":"browser"}
        size = self.size()
        state.update({"object_name": self.objectName(), "size" : (size.width(),size.height())})
        return state

    def status(self, message, message_type=INFO):
        self.parent.status(message, message_type)



class BaseWidget(QWidget):
    def status(self, message, message_type=INFO):
        self.parent.status(message, message_type)

    def getState(self):
        pass

    def setState(self):
        pass



pixlib = Pixlib()
