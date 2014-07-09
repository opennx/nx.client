import time
import datetime

from functools import partial

from firefly_common import *


class SendToButton(QPushButton):
    pass

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
                btn_send = SendToButton(title)
                btn_send.clicked.connect(partial(self.on_send, id_action))
                layout.addWidget(btn_send,1)

            self.restart = QCheckBox('Restart existing actions', self)
            self.restart.setChecked(True)
            layout.addWidget(self.restart,0)

            self.setLayout(layout)
            self.setMinimumWidth(400)

    @property
    def assets(self):
        result = []
        for obj in self.objects:
            if obj.object_type == "asset":
                result.append(obj.id)
            elif obj.object_type == "item" and obj["id_asset"]:
                result.append(obj["id_asset"])
        return result

    def on_send(self, id_action):
        res, status = query("send_to", {"id_action" : id_action, "objects": self.assets, "settings":{}, "restart_existing": self.restart.isChecked() })
        if failed(res):
            QMessageBox.error(self, "Error", "status")
        else:
            self.close()
