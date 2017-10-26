from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *

try:
    from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
    from PyQt5.QtMultimediaWidgets import QVideoWidget
    has_multimedia = True
except ImportError:
    print ("Video playback support disabled")
    has_multimedia = False


Signal = pyqtSignal
Slot = pyqtSlot
Property = pyqtProperty


try:
    base_css = open("skin.css").read()
except:
    base_css = ""
