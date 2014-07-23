from functools import partial
from qt_common import *

class SendToButton(QPushButton):
    pass

class SiteSelect(QDialog):
    def __init__(self,  parent, sites=[]):
        super(SiteSelect, self).__init__(parent)
        self.sites = sites
        self.setModal(True)
        self.setStyleSheet(base_css)
        self.setWindowTitle("Multiple sites are cofigured")

        layout = QVBoxLayout()
        for i, site in enumerate(sites):
            btn_site = SendToButton(site["site_name"])
            btn_site.clicked.connect(partial(self.on_select, i))
            layout.addWidget(btn_site, 1)

            self.setLayout(layout)
            self.setMinimumWidth(400)

    def on_select(self, id_site):
        self.close()
        self.setResult(id_site)
