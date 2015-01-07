from firefly_common import *
from firefly_widgets import *

ERR = "** ERROR **"


class BatchDialog(QDialog):
    def __init__(self,  parent, objects):
        super(BatchDialog, self).__init__(parent)
        self.objects = sorted(objects, key=lambda obj: obj.id)
        self.values = {}
        self.setWindowTitle("Batch modify: {} assets".format(len(self.objects)))
        
        self.key = QLineEdit("title")
        self.exp = QLineEdit()
        self.ident = QLineEdit("title", self)
        self.preview = NXE_blob(self)
        self.preview.setMinimumSize(740, 400)
        self.btn_submit = QPushButton("Submit")
        self.btn_submit.clicked.connect(self.on_submit)

        layout = QFormLayout()
        
        layout.addRow("Key", self.key)
        layout.addRow("Expression", self.exp)
        layout.addRow("Ident", self.ident)
        layout.addRow("Preview", self.preview)
        layout.addRow("", self.btn_submit)

        self.exp.textChanged.connect(self.on_change)

        self.setLayout(layout)
        self.setModal(True)

        self.on_change()
        self.resize(800, 400)


    def on_change(self):
        self.preview.clear()
        txt = ""
        for asset in self.objects:
            if self.exp.text():
                try:
                    value = eval(self.exp.text())
                except:
                    value = ERR
            else:
                value = ERR
            self.values[asset.id] = value


            txt += "{:<50}{}\n".format(asset[self.ident.text()], value)
        self.preview.setText(txt)


    def on_submit(self):
        key = self.key.text()
        for asset in self.objects:
            value = self.values[asset.id]
            if value == ERR:
                continue
            stat, res = query("set_meta", objects=[asset.id], data={key : value} )
            if not success(stat):
                QMessageBox.critical(self, "Error", res)
        self.close()



if __name__ == "__main__":
    config["site_name"] = "nxtv"
    asset_cache.load()
    objs = []
    for i, aid in enumerate(asset_cache.keys()):
        if i > 15:
            break
        objs.append(asset_cache[aid])

    app = QApplication(sys.argv)
    dlg = BatchDialog(None, objects=objs)
    dlg.exec_()


