try:
    from PyQt5.QtCore import *
    from PyQt5.QtGui  import *
    from PyQt5.QtWidgets import *

    Signal = pyqtSignal
    Slot = pyqtSlot
    Property = pyqtProperty 

except:
    from PySide.QtCore import *
    from PySide.QtGui  import *


try:
    base_css = open("skin.css").read()
except:
    base_css = ""