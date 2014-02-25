import time
import datetime

from firefly_common import *
from firefly_view import *

from nx.objects import Event


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
  








def scheduler_toolbar(parent):
    toolbar = QToolBar(parent)
    toolbar.setMovable(False)
    toolbar.setFloatable(False)
  
    action_add_event = QAction(QIcon(pixlib["add"]), 'Add event', parent)
    action_add_event.setShortcut('+')
    action_add_event.triggered.connect(parent.on_add_event)        
    toolbar.addAction(action_add_event)
  
    action_remove_event = QAction(QIcon(pixlib["remove"]), 'Remove selected event', parent)
    action_remove_event.setShortcut('-')
    action_remove_event.triggered.connect(parent.on_remove_event)        
    toolbar.addAction(action_remove_event)
    
    toolbar.addSeparator()
  
    action_accept = QAction(QIcon(pixlib["accept"]), 'Accept changes', parent)
    action_accept.setShortcut('ESC')
    action_accept.triggered.connect(parent.on_accept)        
    toolbar.addAction(action_accept)
  
    action_cancel = QAction(QIcon(pixlib["cancel"]), 'Cancel', parent)
    action_cancel.setShortcut('Alt+F4')
    action_cancel.triggered.connect(parent.on_cancel)        
    toolbar.addAction(action_cancel)

    return toolbar
  



class Scheduler(QDialog):
    def __init__(self,  parent, current_date):
        super(Scheduler, self).__init__()
        self.parent = parent
        self.setModal(True)
        self.setStyleSheet(base_css)

        self.current_date = current_date
        self.id_channel   = 1

        self.toolbar = scheduler_toolbar(self)
        
        self.model = SchedulerModel(self)
        self.model.header_data = ["promoted", "start", "title", "description"]

        self.view = NXView(self)
        self.view.setModel(self.model)

        self.delegate = MetaEditItemDelegate(self.view)
        self.delegate.settings["base_date"] = datestr2ts(self.current_date)

        self.view.setItemDelegate(self.delegate)
        self.view.activated.connect(self.on_activate)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5)

        layout.addWidget(self.toolbar, 1)
        layout.addWidget(self.view,2) 

        self.setLayout(layout) 

        self.load_state()
        self.model.load(self.id_channel, self.current_date)




    def closeEvent(self, event):
        self.save_state()
        event.accept()



    def load_state(self):
        settings = ffsettings()
        if "global/scheduler_geometry" in settings.allKeys():
            self.restoreGeometry(settings.value("global/scheduler_geometry"))

        if "global/scheduler_column_widths" in settings.allKeys():
            col_widths = settings.value("global/scheduler_column_widths")
            for id_column in range(self.model.columnCount(False)):
                col_tag = self.model.header_data[id_column]
                w = col_widths.get(col_tag,False)
                if w:
                    self.view.setColumnWidth(id_column, w) 
                else: 
                    self.view.resizeColumnToContents(id_column)



    def save_state(self):
        settings = ffsettings()
        settings.setValue("global/scheduler_geometry", self.saveGeometry())
        col_widths = {}
        for id_column in range(self.model.columnCount(False)):
            col_widths[self.model.header_data[id_column]] = self.view.columnWidth(id_column)
        settings.setValue("global/scheduler_column_widths", col_widths)


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

        #print self.model.deleted



    def on_accept(self):
        events = []
        for evt in self.model.object_data:
            events.append(evt.meta)

        delete = self.model.deleted.keys()

        result, data = query("set_day_events",{"date":self.current_date, "id_channel":self.id_channel, "events":events, "delete":delete })

        #self.model.load(self.id_channel, self.current_date)
        self.close()

    def on_cancel(self):
        self.close()