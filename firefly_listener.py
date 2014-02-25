import json
import socket

from qt_common import *

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
            except (socket.error):
                pass
            else:
                try:
                    message = SeismicMessage(json.loads(data.decode('ascii')))
                    if message.site_name == self.site_name:
                        message.address = addr
                        self.signal.sig.emit(message)
                except:
                    print ("Malformed seismic message detected:")
                    print (data)
        print ("Listener halted")
        self.halted = True

    def halt(self):
        self._halt = True
      
    def add_handler(self, handler):
        self.signal.sig.connect(handler)


