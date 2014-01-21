#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid

from nx.common import *
from nx.common.metadata import meta_types
from nx.connection import *

from firefly_widgets import *



def get_pix(name):
    return QPixmap(os.path.join("images","%s.png" % name))

class Pixlib(dict):
    def __getitem__(self, key):
        if not key in self:
            self[key] = get_pix(key)
        return self.get(key, None)

pixlib = Pixlib()


def ffsettings():
    return QSettings(".ffstate", QSettings.IniFormat)




class BaseDock(QDockWidget):
    def __init__(self, parent, object_name=False):
        super(BaseDock, self).__init__(parent)

        if object_name:
            self.setObjectName(object_name)
        else:
            self.setObjectName(str(uuid.uuid1()))

        self.parent = parent
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setStyleSheet(base_css)
        self.setFloating(True)

    def setState(self, main_widget, state):
        self.main_widget = main_widget(self)
        self.setWidget(self.main_widget)
        self.main_widget.setState(state)


    def getState(self):
        state = self.main_widget.getState() 
        state.update({"object_name": self.objectName()})
        return state


    def closeEvent(self, evt):
        self.deleteLater()
        self.parent.on_window_closed(self)





class SeismicMessage(object):
    def __init__(self, packet):
        self.timestamp, self.site_name, self.host, self.method, self.data = packet

class SeismicSignal(QObject):
    sig = Signal(SeismicMessage)

class SeismicListener(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.parent = parent
        self._halt = False
        self.halted = True
        self.signal = SeismicSignal()
        
    def listen(self, site_name, addr, port):
        self.site_name = site_name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0",port))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
        status = self.sock.setsockopt(socket.IPPROTO_IP,socket.IP_ADD_MEMBERSHIP,socket.inet_aton(addr) + socket.inet_aton("0.0.0.0"));
        self.sock.settimeout(1)
        self.start() 
    
    def run(self):
        self.halted = False
        while not self._halt:
            try:
                data, addr = self.sock.recvfrom(1024)
            except socket.error, e:
                pass
            else:
              #  try:
                    message = SeismicMessage(json.loads(data))
                    #print message
                    if message.site_name == self.site_name:
                        message.address = addr
                        self.signal.sig.emit(message)
              #  except:
              #      print ("Malformed seismic message detected:")
              #      print (data)
        print "Listener halted"
        self.halted = True

    def halt(self):
        self._halt = True
      
    def add_handler(self,handler):
        self.signal.connect(handler)







class Firestarter(QApplication):
    def __init__(self):
        super(Firestarter, self).__init__(sys.argv)

        self.splash = QSplashScreen(pixlib['splash'])
        self.splash.show()
        self.listener = SeismicListener()

        self.tasks = [
                      self.load_site_settings,
                      self.load_meta_types,
                      self.load_storages,
                      self.init_listener
                     ]

        for task in self.tasks:
            task()

        self.splash_message("Loading user workspace...")

    def splash_message(self, msg):
        self.splash.showMessage(msg,alignment=Qt.AlignBottom|Qt.AlignLeft, color=Qt.white)


    def load_site_settings(self):
        self.splash_message("Loading site settings")
        ret_code, result = query("site_settings")
        if ret_code < 300:
            config.update(result)
        else:
            critical_error("Unable to load site settings")

    def load_meta_types(self):
        self.splash_message("Loading metadata types")
        if not meta_types.load():
            critical_error("Unable to load meta types")            

    def load_storages(self):
        pass

    def init_listener(self):
        self.splash_message("Initializing seismic listener")
        self.listener.listen(config["site_name"], config["seismic_addr"], int(config["seismic_port"]))




    def start(self):
        self.splash.hide()
        self.exec_()
        self.on_exit()


    def on_exit(self):
        self.listener.halt()
        i = 0
        while not self.listener.halted and i < 30:
            time.sleep(.1)
