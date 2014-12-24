import time
import datetime

from firefly_common import *
from firefly_widgets import *

from nx.objects import Event


def event_toolbar(wnd):
    toolbar = QToolBar(wnd)
    toolbar.setMovable(False)
    toolbar.setFloatable(False)

    wnd.action_toggle_promoted = QAction('Toggle promoted', wnd)
    wnd.action_toggle_promoted.setShortcut('*')
    wnd.action_toggle_promoted.triggered.connect(wnd.on_toggle_promoted)
    toolbar.addAction(wnd.action_toggle_promoted)

    toolbar.addWidget(ToolBarStretcher(toolbar))

    action_accept = QAction(QIcon(pixlib["accept"]), 'Accept changes', wnd)
    action_accept.setShortcut('Ctrl+S')
    action_accept.triggered.connect(wnd.on_accept)
    toolbar.addAction(action_accept)

    action_cancel = QAction(QIcon(pixlib["cancel"]), 'Cancel', wnd)
    action_cancel.setShortcut('ESC')
    action_cancel.triggered.connect(wnd.on_cancel)
    toolbar.addAction(action_cancel)

    return toolbar



class EventForm(QWidget):
    def __init__(self, parent, event):
        super(EventForm, self).__init__(parent)

        layout = QFormLayout()
        self.data = {}

        for key, title, widget in [
            ("start", "Start", NXE_datetime),
            ("title", "Title", NXE_text),
            ("title/subtitle", "Subtitle", NXE_text),
            ("description", "Description", NXE_blob)
            ]: # TODO: load title and widget from metatypes somehow

            self.data[key] = widget(self)
            if event[key]:
                self.data[key].set_value(event[key])

            layout.addRow(title, self.data[key])

        self.setLayout(layout)

    def keys(self):
        return self.data.keys()

    def __getitem__(self, key):
        if not key in self.keys():
            return False

        return self.data[key].get_value()



class EventDialog(QDialog):
    def __init__(self,  parent, **kwargs):
        super(EventDialog, self).__init__(parent)
        self.setWindowTitle("Scheduler")
        self.kwargs = kwargs
        self.setStyleSheet(base_css)

        self.toolbar = event_toolbar(self)

        self.event = kwargs.get("event", Event())

        for key in ["start", "id_channel"]:
            if kwargs.get(key, False):
                self.event[key] = kwargs[key]

        if "asset" in self.kwargs:
            asset = self.kwargs["asset"]
            self.form.title.set_value(asset["title"])
            self.form.description.set_value(asset["description"])

        self.on_toggle_promoted(value=self.event["promoted"])

        self.form = EventForm(self, self.event)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5)

        layout.addWidget(self.toolbar, 1)
        layout.addWidget(self.form, 2)

        self.setLayout(layout)
        self.load_state()
        self.setModal(True)



    def load_state(self):
        settings = ffsettings()
        if "dialogs/event_g" in settings.allKeys():
            self.restoreGeometry(settings.value("dialogs/event_g"))
        else:
            self.resize(800,400)

    def save_state(self):
        settings = ffsettings()
        settings.setValue("dialogs/event_g", self.saveGeometry())

    def on_cancel(self):
        self.close()

    def closeEvent(self, event):
         self.save_state()
         event.accept()



    def on_accept(self):
        for key in self.form.keys():
            value = self.form[key]
            if value:
                self.event[key] = self.form[key]

        stat, res = query("set_events",
                id_channel=self.event["id_channel"],
                events=[self.event.meta]
                    )

        self.close()


    def on_toggle_promoted(self, **kwargs):
        if not "value" in kwargs:
            print (self.event["promoted"], not self.event["promoted"])
            self.event["promoted"] = not bool(self.event["promoted"])
        else:
            self.event["promoted"] = bool(kwargs.get("value"))

        self.action_toggle_promoted.setIcon(
            [
                QIcon(pixlib["star_disabled"]),
                QIcon(pixlib["star_enabled"])
            ][bool(self.event["promoted"])]
            )

