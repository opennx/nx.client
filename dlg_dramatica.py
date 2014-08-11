import time
import datetime

from firefly_common import *

class DramaticaDialog(QDialog):
    def __init__(self,  parent, **kwargs):
        super(DramaticaDialog, self).__init__(parent)
        self.setWindowTitle("Dramatica")
        self.setModal(True)
        self.result = False

        self.chk_clear = QCheckBox()
        self.chk_aptpl = QCheckBox()
        self.chk_solve = QCheckBox()

        self.btn_ok = QPushButton("OK")
        self.btn_ok.clicked.connect(self.on_ok)


        layout = QFormLayout()
        layout.addRow("Clear rundown",  self.chk_clear)
        layout.addRow("Apply template", self.chk_aptpl)
        layout.addRow("Solve rundown",  self.chk_solve)
        layout.addRow("", self.btn_ok)

        self.setLayout(layout)
        self.resize(300,150)
        self.show()

    def on_ok(self):
        self.result = True
        self.close()

