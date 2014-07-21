import time
import datetime

from firefly_common import *
from firefly_widgets import *


def event_toolbar(wnd):
    toolbar = QToolBar(wnd)
    toolbar.setMovable(False)
    toolbar.setFloatable(False)

    # action_add_event = QAction(QIcon(pixlib["add"]), 'Add reprise', wnd)
    # action_add_event.setShortcut('+')
    # action_add_event.triggered.connect(wnd.on_add_reprise)
    # toolbar.addAction(action_add_event)

    # action_remove_event = QAction(QIcon(pixlib["remove"]), 'Remove selected reprise', wnd)
    # action_remove_event.setShortcut('-')
    # action_remove_event.triggered.connect(wnd.on_remove_reprise)
    # toolbar.addAction(action_remove_event)

    # toolbar.addSeparator()

    action_accept = QAction(QIcon(pixlib["accept"]), 'Accept changes', wnd)
    action_accept.setShortcut('ESC')
    action_accept.triggered.connect(wnd.on_accept)
    toolbar.addAction(action_accept)

    action_cancel = QAction(QIcon(pixlib["cancel"]), 'Cancel', wnd)
    action_cancel.setShortcut('Alt+F4')
    action_cancel.triggered.connect(wnd.on_cancel)
    toolbar.addAction(action_cancel)

    return toolbar



class EventForm(QWidget):
    def __init__(self, parent):
        super(EventForm, self).__init__(parent)

        self.timestamp  = NXE_datetime(self)
        self.title = NXE_text(self)
        self.description = NXE_blob(self)

        layout = QFormLayout()
        layout.addRow("Event start", self.timestamp)
        layout.addRow("Title", self.title)
        layout.addRow("Description", self.description)

        self.setLayout(layout)





class EventDialog(QDialog):
    def __init__(self,  parent, **kwargs):
        super(EventDialog, self).__init__(parent)
        self.setWindowTitle("Scheduler")
        self.kwargs = kwargs
        self.setStyleSheet(base_css)

        self.toolbar = event_toolbar(self)
        self.form = EventForm(self)

        if "event" in self.kwargs:
            event = self.kwargs["event"]
            self.form.title.set_value(event["title"])
            self.form.description.set_value(event["description"])
            self.form.timestamp.set_value(event["start"])
            
        elif "asset" in self.kwargs:
            asset = self.kwargs["asset"]
            self.form.title.set_value(asset["title"])
            self.form.description.set_value(asset["description"])

        if "timestamp" in self.kwargs:
          self.form.timestamp.set_value(self.kwargs["timestamp"])


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
        timestamp = self.form.timestamp.get_value()
        title = self.form.title.get_value().strip()
        description = self.form.description.get_value().strip()

        if timestamp < time.time():
            QMessageBox.warning(self, "Error", "Event start cannot be in the past")
            return
        elif not title:
            QMessageBox.warning(self, "Error", "You must specify event title")
            return

        
        id_channel = self.kwargs.get("id_channel", False)

        data = {}
        if "event" in self.kwargs:
            data["id_event"] = self.kwargs["event"].id
        elif "asset" in self.kwargs:
            data["id_asset"] = self.kwargs["asset"].id


        data["start"] = self.form.timestamp.get_value()
        data["title"] = self.form.title.get_value()
        data["description"] = self.form.description.get_value()

        stat, res = query("set_events", 
                id_channel=id_channel,
                events=[data]
                    )

        self.close()



    def on_add_reprise(self):
        pass

    def on_remove_reprise(self):
        pass
