import uuid
import socket

from nx.common import *
from nx.common.metadata import meta_types
from nx.connection import *

from qt_common import *
from firefly_rc import *


def ffsettings():
    return QSettings(".state.%s.nxsettings" % socket.gethostname(), QSettings.IniFormat)

def get_pix(name):
    if not name:
        return None

    elif name.startswith("folder_"):
            id_folder = int(name.lstrip("folder_"))
            icn = QPixmap(12, 12)
            icn.fill(QColor(config["folders"][id_folder][1]))
            return icn

    return QPixmap(":/images/{}.png".format(name))

class Pixlib(dict):
    def __getitem__(self, key):
        if not key in self:
            self[key] = get_pix(key)
        return self.get(key, None)

pixlib = Pixlib()







class BaseWidget(QWidget):
    def __init__(self, parent):
        super(BaseWidget, self).__init__(parent)
        self.setContentsMargins(3,5,3,3)

    def save_state(self):
        pass

    def load_state(self):
        pass

    def status(self, message, message_type=INFO):
        self.parent().status(message, message_type)

    def subscribe(self, *methods):
        self.parent().subscribe(self.seismic_handler, *methods)

    def closeEvent(self, event):
        self.parent().unsubscribe(self.seismic_handler)

    def seismic_handler(self, data):
        pass


class BaseDock(QDockWidget):
    def __init__(self, parent, main_widget, state={}):
        super(BaseDock, self).__init__(parent)
        if "object_name" in state:
            self.setObjectName(state["object_name"])
        else:
            self.reset_object_name()
        self.destroyed.connect(parent.on_dock_destroyed)
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.main_widget = main_widget(self)
        self.setWidget(self.main_widget)
        self.main_widget.load_state(state)
        if state.get("is_floating", False):
            self.setFloating(True)


    def reset_object_name(self):
        self.setObjectName(str(uuid.uuid1()))

    def closeEvent(self, evt):
        self.save()
        self.deleteLater()

    @property 
    def class_(self):
        return self.main_widget.__class__.__name__.lower()

    def save(self, settings=False):
        if not settings:
            settings = ffsettings()
        state = self.main_widget.save_state()
        state["class"] = self.class_
        state["object_name"] = self.objectName()
        state["is_floating"] = self.isFloating()
        settings.setValue("docks/{}".format(self.objectName()), state)

    def status(self, message, message_type=INFO):
        self.parent().status(message, message_type)

    def subscribe(self, handler,  *methods):
        self.parent().subscribe(handler, *methods)




class ToolBarStretcher(QWidget):
    def __init__(self, parent):
        super(ToolBarStretcher, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)