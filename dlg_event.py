import time
import datetime

from firefly_common import *
from firefly_widgets import *


class RunsModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(RunsModel, self).__init__(parent)
        self.object_data = ["13456"]

    def rowCount(self ,parent):
        return len(self.object_data)

class RunsView(QListView):
    pass




def event_toolbar(wnd):
    toolbar = QToolBar(wnd)
    toolbar.setMovable(False)
    toolbar.setFloatable(False)

    action_add_run = QAction(QIcon(pixlib["add"]), 'Add run', wnd)
    action_add_run.setShortcut('+')
    action_add_run.triggered.connect(wnd.on_add_run)
    toolbar.addAction(action_add_run)

    action_remove_event = QAction(QIcon(pixlib["remove"]), 'Remove selected run', wnd)
    action_remove_event.setShortcut('-')
    action_remove_event.triggered.connect(wnd.on_remove_run)
    toolbar.addAction(action_remove_event)

    toolbar.addWidget(ToolBarStretcher(toolbar))

    action_accept = QAction(QIcon(pixlib["accept"]), 'Accept changes', wnd)
    action_accept.setShortcut('ESC')
    action_accept.triggered.connect(wnd.on_accept)
    toolbar.addAction(action_accept)

    action_cancel = QAction(QIcon(pixlib["cancel"]), 'Cancel', wnd)
    action_cancel.setShortcut('Alt+F4')
    action_cancel.triggered.connect(wnd.on_cancel)
    toolbar.addAction(action_cancel)

    return toolbar



class EventDialog(QDialog):
    def __init__(self,  parent, **kwargs):
        super(EventDialog, self).__init__(parent)
        self.setStyleSheet(base_css)
        self.setWindowTitle("New event")
        self.kwargs = kwargs

        self.event_meta = [
            ["title", True],
            ["title/subtitle", False],
            ["description", False]
            ]

        self.toolbar = event_toolbar(self)
        self.meta_editor = MetaEditor(self, self.event_meta)

        self.id_channel = self.kwargs.get("id_channel", False)
        self.id_event = False
        self.base_ts = False

        if "event" in self.kwargs:
            event = self.kwargs["event"]
            self.setWindowTitle(event.__repr__())

            for tag, conf in self.event_meta:
                if event[tag]:
                    self.meta_editor[tag] = event[tag]

            self.base_ts  = event["start"]
            self.id_asset = event.meta.get("id_asset", False)
            self.id_event = event.id
            
        elif "asset" in self.kwargs:
            asset = self.kwargs["asset"]
            self.id_asset = asset.id

            for tag, conf in self.event_meta:
                if asset[tag]:
                    self.meta_editor[tag] = asset[tag]

            self.setWindowTitle("New event ({})".format(asset["title"]))

        if "timestamp" in self.kwargs:
            self.base_ts = self.kwargs["timestamp"]

        self.runs_model = RunsModel(self)
        self.runs_view = RunsView(self)
        self.runs_view.setModel(self.runs_model)


        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5)

        layout.addWidget(self.toolbar, 1)
        layout.addWidget(self.meta_editor, 2)
        layout.addWidget(self.runs_view, 2)

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
        self.setResult(QDialog.Rejected)

    def closeEvent(self, event):
         self.save_state()
         event.accept()






    def on_accept(self):
        events = []
        for run in self.runs_model.object_data:

            data = {}
            if "event" in self.kwargs:
                data["id_object"] = self.kwargs["event"].id
            elif "asset" in self.kwargs:
                data["id_asset"] = self.kwargs["asset"].id

            for tag, conf in self.event_meta:
                if self.meta_editor[tag]:
                    data[tag] = self.meta_editor[tag]

            data["start"] = self.form.timestamp.get_value()
            data["id_channel"] = self.id_channel
            events.append(data)


        stat, res = query("set_events", events=events)
        self.setResult(QDialog.Accepted)
        self.close()



    def on_add_run(self):
        pass


    def on_remove_run(self):
        pass
