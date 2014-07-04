import time
import datetime

from functools import partial

from firefly_common import *



class SendTo(QDialog):
    def __init__(self,  parent, objects=[]):
        super(SendTo, self).__init__(parent)
        self.objects = objects
        self.setModal(True)
        self.setStyleSheet(base_css)

        if len(self.objects) == 1:
            what = self.objects[0]["title"]
        else:
            what = "{} objects".format(len(self.objects))

        self.setWindowTitle("Send {} to...".format(what))

        self.actions = []
        res, data = query("actions", {"assets":self.assets})
        if success(res):

            layout = QVBoxLayout()
            for id_action, title in data:
                btn_send = QPushButton(title)
                btn_send.clicked.connect(partial(self.on_send, id_action))
                layout.addWidget(btn_send,0)

            self.setLayout(layout)
            self.setMinimumWidth(400)

    @property
    def assets(self):
        if self.objects and self.objects[0].object_type == "asset":
            objects = [obj.id for obj in self.objects]
        elif self.objects and self.objects[0].object_type == "item":
            objects = [obj["id_asset"] for obj in self.objects]
        else:
            return []
        return objects

    def on_send(self, id_action):
        res, status = query("send_to", {"id_action" : id_action, "objects": self.assets, "settings":{}, "restart_existing": True })
        if failed(res):
            QMessageBox.error(self, "Error", "status")
        else:
            self.close()
