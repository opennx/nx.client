import time
import datetime

from firefly_common import *


def event_toolbar(wnd):
    toolbar = QToolBar(wnd)
    toolbar.setMovable(False)
    toolbar.setFloatable(False)

    action_add_event = QAction(QIcon(pixlib["add"]), 'Add reprise', wnd)
    action_add_event.setShortcut('+')
    action_add_event.triggered.connect(wnd.on_add_reprise)
    toolbar.addAction(action_add_event)

    action_remove_event = QAction(QIcon(pixlib["remove"]), 'Remove selected reprise', wnd)
    action_remove_event.setShortcut('-')
    action_remove_event.triggered.connect(wnd.on_remove_reprise)
    toolbar.addAction(action_remove_event)

    toolbar.addSeparator()

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
        self.setWindowTitle("Scheduler")
        self.kwargs = kwargs

        self.setStyleSheet(base_css)


        self.toolbar = event_toolbar(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5)

        layout.addWidget(self.toolbar, 1)
        layout.addWidget(QWidget(), 2)

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
        query("event_from_asset", {
                    "id_asset" : self.kwargs["id_asset"],
                    "id_channel" : self.kwargs["id_channel"],
                    "timestamp" : self.kwargs["timestamp"]
                })
        self.close()



    def on_add_reprise(self):
        pass

    def on_remove_reprise(self):
        pass
