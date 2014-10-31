from firefly_common import *

def prompter_toolbar(wnd):
    toolbar = QToolBar(wnd)

    action_refresh = QAction(QIcon(pixlib["refresh"]), '&Refresh', wnd)        
    action_refresh.setStatusTip('Refresh scheduler')
    action_refresh.triggered.connect(wnd.refresh)
    toolbar.addAction(action_refresh)

    toolbar.addSeparator()

    wnd.action_show_runs = QAction(QIcon(pixlib["repeat"]), '&Mirror', wnd)        
    wnd.action_show_runs.setStatusTip('Mirror image')
    wnd.action_show_runs.setCheckable(True)
    #action_show_runs.triggered.connect(wnd.on_show_runs)
    toolbar.addAction(wnd.action_show_runs)


    toolbar.addWidget(ToolBarStretcher(wnd))

    toolbar.addWidget(EmptyEventButton(wnd))

    return toolbar


class Teleprompter(BaseWidget):
    def __init__(self, parent):
        super(Teleprompter, self).__init__(parent)
        toolbar = prompter_toolbar(self)
        self.parent().setWindowTitle("Teleprompter")

        self.id_channel = self.parent().parent().id_channel

        self.calendar = QWidget()

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.calendar, 1)

        self.setLayout(layout)

    def set_channel(self):
        if self.id_channel != id_channel:
            self.id_channel = id_channel
            self.refresh()

    def save_state(self):
        state = {}
        return state

    def load_state(self, state):
        pass

    def refresh(self):
        pass



    def seismic_handler(self, data):
        pass
#       if data.method == "objects_changed" and data.data["object_type"] == "event":
#            my_name =self.parent().objectName()
#            print (data.data)
#            print (my_name)
#            for id_event in data.data["objects"]:#  
#                if data.data["sender"] != my_name and id_event in self.model.event_ids :
#                    self.refresh()
#                    break
        # TODO!