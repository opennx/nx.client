from functools import partial

from firefly_common import *
from firefly_widgets import *




class CGPlugin(QWidget):
    def __init__(self, parent, data):
        super(CGPlugin, self).__init__(parent)
        self._parent = parent
        self.buttons = []
        self.widgets = []
        button_layout = QHBoxLayout()
        layout = QFormLayout()

        self.id_plugin = data["id"]

        for i, slot in enumerate(data.get("slots",[])):
            slot_type = slot["slot_type"]
            id_slot = slot["id"]

            if slot_type == "button":
                self.buttons.append(QPushButton(slot["title"]))
                self.buttons[-1].clicked.connect(
                    partial(
                        self.execute, 
                        id_slot=id_slot
                        )
                    )
                button_layout.addWidget(self.buttons[-1])
                continue


            if slot_type == "text":
                self.widgets.append(NXE_text(self))
                signal = self.widgets[-1].textChanged
            
            elif slot_type == "select":
                self.widgets.append(NXE_select(self, slot["data"]))
                signal = self.widgets[-1].currentIndexChanged
            else:
                continue

            if slot.get("value", False):
                self.widgets[-1].set_value(slot["value"])

            signal.connect(
                partial(
                    self.execute, 
                    id_slot=id_slot
                    )
                )
            self.widgets[-1].id_slot = id_slot
            layout.addRow(slot["title"], self.widgets[-1])

        if self.buttons:
            layout.addRow("", button_layout)
        self.setLayout(layout)


    def execute(self, id_slot):
        value = False
        for widget in self.widgets:
            if widget.id_slot == id_slot:
                value = widget.get_value()
                break

        self._parent.execute(
            id_plugin=self.id_plugin,
            id_slot=id_slot,
            value=value
            )




class CG(QTabWidget):
    def __init__(self, parent):
        super(CG, self).__init__(parent)
        self.setStyleSheet(base_css)   
        self.plugins = []
        self.id_channel = False
        self.load_plugins(self.parent().id_channel)
        
    def load_plugins(self, id_channel):
        for idx in reversed(range(self.count())):
            widget = self.widget(idx)
            self.removeTab(idx)
            widget.deleteLater()

        self.id_channel = id_channel
        stat, plugins = query("cg_list", self.parent().mcr.route, id_channel=id_channel)
        if not success(stat):
            print ("Unable to load CG plugins")
            return

        for plugin in plugins:
            self.plugins.append(CGPlugin(self, plugin))
            self.addTab(self.plugins[-1], plugin["title"])



    def execute(self, id_plugin, id_slot, value=False):
        stat, res = query(
            "cg_exec", 
            self.parent().mcr.route, 
            id_channel=self.id_channel, 
            id_plugin=id_plugin, 
            id_slot=id_slot, 
            value=value
            )