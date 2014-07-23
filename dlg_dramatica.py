import time
import datetime

from firefly_common import *

class DramaticaDialog(QDialog):
    def __init__(self,  parent, **kwargs):
        super(DramaticaDialog, self).__init__(parent)
        self.setModal(True)
        self.setStyleSheet(base_css)