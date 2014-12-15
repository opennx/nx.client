from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *

from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget

Signal = pyqtSignal
Slot = pyqtSlot
Property = pyqtProperty 


try:
    base_css = open("skin.css").read()
except:
    base_css = ""