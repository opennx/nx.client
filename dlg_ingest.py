from firefly_common import *
from firefly_widgets import *




class IngestDialog(QDialog):
    def __init__(self,  parent, asset=False):
        super(IngestDialog, self).__init__(parent)
        self.asset = asset
        if asset:
            self.setWindowTitle("{} ingest".format(self.asset))
        else:
            self.setWindowTitle("Scheduled ingests")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ingest is not supported on this system"))

        self.setLayout(layout)

        self.setModal(True)
        self.resize(400, 300)

