from mod_scheduler_model import *


class EmptyEventButton(QToolButton):
    def __init__(self, parent):
        super(EmptyEventButton, self).__init__()
        self.pressed.connect(self.startDrag)
        self.setIcon(QIcon(pixlib["empty_event"]))
        self.setToolTip("Drag this to scheduler to create empty event.")

    def startDrag(self):
        drag = QDrag(self);
        mimeData = QMimeData()
        mimeData.setData(
           "application/nx.event",
           '[{"id_object":0, "title":"Empty event"}]'.encode("ascii")  # Empty event
           )
        drag.setMimeData(mimeData)
        if drag.exec_(Qt.CopyAction):
            pass # nejak to rozumne ukoncit


def scheduler_toolbar(wnd):
    toolbar = QToolBar(wnd)

    action_week_prev = QAction(QIcon(pixlib["back"]), '&Previous week', wnd)
    action_week_prev.setStatusTip('Go to previous week')
    action_week_prev.triggered.connect(wnd.on_week_prev)
    toolbar.addAction(action_week_prev)

    action_refresh = QAction(QIcon(pixlib["refresh"]), '&Refresh', wnd)
    action_refresh.setStatusTip('Refresh scheduler')
    action_refresh.triggered.connect(wnd.refresh)
    toolbar.addAction(action_refresh)

    action_week_next = QAction(QIcon(pixlib["next"]), '&Next week', wnd)
    action_week_next.setStatusTip('Go to next week')
    action_week_next.triggered.connect(wnd.on_week_next)
    toolbar.addAction(action_week_next)

    toolbar.addSeparator()

    wnd.action_show_runs = QAction(QIcon(pixlib["repeat"]), '&Show runs', wnd)
    wnd.action_show_runs.setStatusTip('Show runs')
    wnd.action_show_runs.setCheckable(True)
    toolbar.addAction(wnd.action_show_runs)

    toolbar.addSeparator()

    toolbar.addWidget(EmptyEventButton(wnd))

    toolbar.addWidget(ToolBarStretcher(wnd))

    wnd.channel_display = ChannelDisplay()
    toolbar.addWidget(wnd.channel_display)

    return toolbar


class Scheduler(BaseWidget):
    def __init__(self, parent):
        super(Scheduler, self).__init__(parent)
        toolbar = scheduler_toolbar(self)
        self.parent().setWindowTitle("Scheduler")
        self.id_channel = False

        self.calendar = TXCalendar(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.calendar, 1)

        self.setLayout(layout)
        self.set_channel(self.parent().parent().id_channel)


    def update_header(self):
        date = datetime.date.fromtimestamp(self.calendar.start_time)
        week_no = date.isocalendar()[1]
        header = "Week {} - {}".format(week_no, config["playout_channels"][self.id_channel]["title"])
        self.channel_display.setText(header)

    def set_channel(self, id_channel):
        if self.id_channel != id_channel:
            self.id_channel = id_channel
            self.calendar.load(self.id_channel, self.calendar.start_time)
            self.update_header()

    def save_state(self):
        state = {}
        return state

    def load_state(self, state):
        pass

    def refresh(self):
        self.calendar.refresh()

    def on_week_prev(self):
        self.calendar.load(self.calendar.id_channel, self.calendar.start_time-(3600*24*7))
        self.update_header()

    def on_week_next(self):
        self.calendar.load(self.calendar.id_channel, self.calendar.start_time+(3600*24*7))
        self.update_header()

    def focus(self, objects):
        if self.action_show_runs.isChecked():
            asset_ids = [obj.id for obj in objects if obj.object_type == "asset"]
            if not asset_ids:
                return
            res, data = query("get_runs", id_channel=self.id_channel, asset_ids=asset_ids )
            if success(res):
                self.calendar.focus_data = data["data"]
                self.calendar.update()


    def seismic_handler(self, data):
       if data.method == "objects_changed" and data.data["object_type"] == "event":
            my_name = self.parent().objectName()
#            print (data.data)
#            print (my_name)
#            for id_event in data.data["objects"]:#
#                if data.data["sender"] != my_name and id_event in self.model.event_ids :
#                    self.refresh()
#                    break
        # TODO!
