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


class BaseDock(QDockWidget):
    def __init__(self, parent, object_name=False):
        super(BaseDock, self).__init__(parent)

        if object_name:
            self.setObjectName(object_name)
        else:
            self.reset_object_name()

        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFloating(True)

    def reset_object_name(self):
        self.setObjectName(str(uuid.uuid1()))

    def closeEvent(self, evt):
        self.deleteLater()
        self.parent().on_dock_closed(self)

    @property 
    def class_(self):
        return self.main_widget.__class__.__name__.lower()

    def load_state(self, main_widget, state):
        self.main_widget = main_widget(self)
        self.setWidget(self.main_widget)
        self.main_widget.load_state(state)

    def save(self, settings=False):
        if not settings:
            settings = ffsettings()
        settings.setValue("docks/{}".format(self.objectName()), self.save_state())

    def save_state(self):
        return self.main_widget.save_state()

    def status(self, message, message_type=INFO):
        self.parent().status(message, message_type)



class BaseWidget(QWidget):
    def status(self, message, message_type=INFO):
        self.parent().status(message, message_type)

    def save_state(self):
        pass

    def load_state(self):
        pass


class ToolBarStretcher(QWidget):
    def __init__(self, parent):
        super(ToolBarStretcher, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

