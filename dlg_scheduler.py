import time
import datetime

from firefly_common import *
from firefly_view import *

from nx.objects import Event

DEFAULT_COLUMNS =  ["promoted", "start", "title", "description"]

class SchedulerModel(NXViewModel):        
    def load(self, id_channel, date):
        self.beginResetModel()
        res, data = query("get_day_events",{"id_channel":id_channel,"date":date})
        if res and data: 
            self.object_data = [Event(from_data=d) for d in sorted(data["events"], key=lambda k: k["start"])]
            for o in self.object_data:
                o.format_settings = {"base_date":date}
        else:
            self.object_data = []
        self.deleted = {}
        self.endResetModel()
 
    def refresh(self):
        self.beginResetModel()
        data = sorted(self.object_data, key=lambda k: k["start"])
        self.object_data = data
        self.endResetModel()
      
    def flags(self,index):
        flags = super(SchedulerModel, self).flags(index)
        if index.isValid():
            flags |= Qt.ItemIsEditable
        return flags
  

def scheduler_toolbar(wnd):
    toolbar = QToolBar(wnd)
    toolbar.setMovable(False)
    toolbar.setFloatable(False)
  
    action_add_event = QAction(QIcon(pixlib["add"]), 'Add event', wnd)
    action_add_event.setShortcut('+')
    action_add_event.triggered.connect(wnd.on_add_event)
    toolbar.addAction(action_add_event)
  
    action_remove_event = QAction(QIcon(pixlib["remove"]), 'Remove selected event', wnd)
    action_remove_event.setShortcut('-')
    action_remove_event.triggered.connect(wnd.on_remove_event)
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
  


class Scheduler(QDialog):
    def __init__(self,  parent, id_channel, current_date):
        super(Scheduler, self).__init__(parent)
        self.setModal(True)
        self.setStyleSheet(base_css)
        self.setWindowTitle("Scheduler")

        self.id_channel = id_channel
        self.current_date = current_date

        self.model = SchedulerModel(self)
        self.view = NXView(self)
        self.view.setModel(self.model)

        self.delegate = MetaEditItemDelegate(self.view)
        self.delegate.settings["base_date"] = datestr2ts(self.current_date)

        self.view.setItemDelegate(self.delegate)
        self.view.activated.connect(self.on_activate)
        
        self.toolbar = scheduler_toolbar(self)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5)

        layout.addWidget(self.toolbar, 1)
        layout.addWidget(self.view, 2) 

        self.setLayout(layout) 

        self.load_state()



    def closeEvent(self, event):
        self.save_state()
        event.accept()


    def load_state(self):
        settings = ffsettings()
        if "global/scheduler_g" in settings.allKeys():
            self.restoreGeometry(settings.value("global/scheduler_g"))

        if "global/scheduler_c" in settings.allKeys():
            self.model.header_data = settings.value("global/scheduler_c") or DEFAULT_COLUMNS

        self.model.load(self.id_channel, self.current_date)

        if "global/scheduler_cw" in settings.allKeys():
            self.view.horizontalHeader().restoreState(settings.value("global/scheduler_cw"))
        else:
            for id_column in range(self.model.columnCount(False)):
                self.view.resizeColumnToContents(id_column)

        self.model.load(self.parent().id_channel, self.parent().current_date)


    def save_state(self):
        settings = ffsettings()
        settings.setValue("global/scheduler_g", self.saveGeometry())
        settings.setValue("global/scheduler_c", self.model.header_data)
        settings.setValue("global/scheduler_cw", self.view.horizontalHeader().saveState())


    def on_activate(self,mi):
        self.view.do_edit(mi)


    def on_add_event(self):
        try:
            start = self.model.object_data[-1]["start"] + 3600
        except:
            start = datestr2ts(self.current_date, 7, 0)

        self.model.object_data.append(Event(from_data={"start" : start, "title" : "New event"}))
        self.model.object_data[-1].format_settings = {"base_date" : datestr2ts(self.current_date)}
        self.model.refresh()

        index = self.model.index(len(self.model.object_data)-1, 1, QModelIndex())
        self.view.edit(index)


    def on_remove_event(self):
        rtd = []
        for idx in self.view.selectionModel().selectedIndexes():
            if not idx.row() in rtd: rtd.append(idx.row())
            id_event = self.model.object_data[idx.row()]["id_object"]
            if id_event and id_event not in self.model.deleted.keys(): 
                self.model.deleted[id_event] = self.model.object_data[idx.row()]["title"]
        rtd.sort()
        for i in reversed(rtd):
            del(self.model.object_data[i])
        self.model.refresh()


    def on_accept(self):
        events = []
        for evt in self.model.object_data:
            events.append(evt.meta)

        delete = list(self.model.deleted.keys())
        result, data = query("set_day_events", 
                                {   
                                    "date" : self.current_date, 
                                    "id_channel" : self.id_channel,
                                    "events" : events,
                                    "delete" : delete 
                                })
        self.close()

    def on_cancel(self):
        self.close()