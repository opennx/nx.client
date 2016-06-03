import uuid
import socket
import pickle
import pprint

from nx import *

from qt_common import *
from firefly_rc import *
from default_state import DEFAULT_STATE

#
# Settings and utils
#

def p(*args):
    l = pprint.pprint(*args)

def ffsettings():
    sfile = "state.{}.{}.nxsettings".format(socket.gethostname(), config["site_name"])
    if not os.path.exists(sfile):
        f = open(sfile, "w")
        f.write(DEFAULT_STATE)
        f.close()
    return QSettings(sfile, QSettings.IniFormat)

#
# Icons
#

def get_pix(name):
    if not name:
        return None
    if name.startswith("folder_"):
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


#
# Cache
#

class AssetCache():
    def __init__(self):
        self.data = {}
        self.cache_time = 0

    def __getitem__(self, key):
        if key == 0:
            return Asset()
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.cache_time = time.time()

    def __contains__(self, key):
        return key in self.data

    def keys(self):
        return self.data.keys()

    @property
    def local_file(self):
        return "state.{}.{}.nxcache".format(socket.gethostname(), config["site_name"])

    def save(self):
        f = open(self.local_file, "wb")
        pickle.dump([time.time(), [asset.meta for asset in self.data.values()]], f)
        f.close()

    def load(self):
        if os.path.exists(self.local_file):
            start_time = time.time()
            try:
                f = open(self.local_file, "rb")
                self.cache_time, _data = pickle.load(f)
                f.close()
                for meta in _data:
                    self.data[meta["id_object"]] = Asset(from_data=meta)
            except:
                pass
            else:
                logging.info("{} cached assets loaded in {:.02f} seconds.".format(len(self.data), time.time() - start_time))
                return
        self.data = {}

asset_cache = AssetCache()

#
# Auth
#

def has_right(key, val=True):
    """Don't worry. It's also validated server-side"""
    if str(config["rights"].get("is_admin", False)).lower() == "true":
        return True
    key = "can/{}".format(key)
    if not key in config["rights"]:
        return False
    tval = config["rights"][key]
    if tval is True:
        return True
    if val is True:
        return True
    return tval and type(tval) == list and val in tval

#
# QT Helpers
#

class BaseWidget(QWidget):
    def __init__(self, parent):
        super(BaseWidget, self).__init__(parent)
        self.setContentsMargins(3,5,3,3)

    def save_state(self):
        pass

    def load_state(self):
        pass

    def status(self, message, message_type=INFO):
        #DEPRECATED
        print ("Deprecated status call:", message)

    def subscribe(self, *methods):
        self.parent().subscribe(self.seismic_handler, *methods)

    def closeEvent(self, event):
        self.parent().unsubscribe(self.seismic_handler)

    def seismic_handler(self, data):
        pass

    def refresh(self):
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
        if state.get("is_floating", True):
            self.setFloating(True)

        if not "object_name" in state:
            if self.class_ in ["browser", "detail"]:
                self.resize(600,600)
            elif self.class_ == "rundown":
                self.resize(800,600)


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
        # DEPRECATED. USE LOGGING INSTEAS
        self.parent().status(message, message_type)



class ToolBarStretcher(QWidget):
    def __init__(self, parent):
        super(ToolBarStretcher, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
