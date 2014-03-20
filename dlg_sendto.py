import time
import datetime

from firefly_common import *



class SendTo(QDialog):
    def __init__(self,  parent, objects=[]):
        super(SendTo, self).__init__()
        self.parent = parent
        self.objects = objects
        self.setModal(True)
        self.setStyleSheet(base_css)

        btn_send = QPushButton("Send to playout")
        btn_send.clicked.connect(self.on_send)

        layout = QVBoxLayout()
        layout.addWidget(btn_send,0)
        self.setLayout(layout)
        self.resize(400,600)

    def on_send(self):
        if self.objects and self.objects[0].object_type == "asset":
            objects = [obj.id for obj in self.objects]
        elif self.objects and self.objects[0].object_type == "item":
            objects = [obj["id_asset"] for obj in self.objects]
        else:
            return
        query("send_to", {"id_action" : 1, "objects": objects, "settings":{}, "restart_existing": True })
