import time
import datetime

from firefly_common import *
from firefly_view import *

from nx.objects import *

from dlg_scheduler import Scheduler




class RundownModel(NXViewModel):
    def load(self, id_channel, date):
        self.beginResetModel()
        self.object_data = []
        self.header_data = ["rundown_symbol", "title"]

        res, data = query("rundown",{"id_channel":id_channel,"date":date})
        if success(res) and data: 
            
            for edata in data["data"]:
                evt = Event(from_data=edata["event_meta"])
                evt.bin = Bin(from_data=edata["bin_meta"])

                self.object_data.append(evt)

                if not edata["items"]:
                    self.object_data.append(Dummy("(no item)"))                    

                for idata, adata in edata["items"]:
                    item = Item(from_data=idata)
                    item.asset = Asset(from_data=adata)

                    self.object_data.append(item)
        
        self.endResetModel()


    def flags(self,index):
        flags = super(RundownModel, self).flags(index) 
        if index.isValid():
            obj = self.object_data[index.row()]
            if obj.id and obj.object_type == "item":
                flags |= Qt.ItemIsDragEnabled # Itemy se daji dragovat
        else:
            flags = Qt.ItemIsDropEnabled # Dropovat se da jen mezi rowy
        return flags


    def mimeTypes(self):
        return ["application/nx.asset", "application/nx.item"]
     
   
    def mimeData(self, indexes):
        mimeData = QMimeData()

        data         = [self.object_data[i] for i in set(index.row() for index in indexes if index.isValid())]
        encodedIData = json.dumps([i.meta for i in data])
        mimeData.setData("application/nx.item", encodedIData)

        encodedAData = json.dumps([i.get_asset().meta for i in data])
        mimeData.setData("application/nx.asset", encodedAData)

        try:
            urls =[QUrl.fromLocalFile(item.get_asset().get_file_path()) for item in data]
            mimeData.setUrls(urls)
        except:
            pass
        return mimeData


   
    def dropMimeData(self, data, action, row, column, parent):
        if action == Qt.IgnoreAction:
            return True

        if row < 1:
            return False
        
        
        if data.hasFormat("application/nx.item"):
            print "Dropped item"

        elif data.hasFormat("application/nx.asset"):
            print "Dropped asset"            


        return False





class RundownDate(QLabel):
    pass


def rundown_toolbar(parent):
    toolbar = QToolBar(parent)

    action_day_prev = QAction(QIcon(pixlib["back"]), '&Previous day', parent)        
    action_day_prev.setShortcut('Alt+Left')
    action_day_prev.setStatusTip('Go to previous day')
    action_day_prev.triggered.connect(parent.on_day_prev)
    toolbar.addAction(action_day_prev)

    action_now = QAction(QIcon(pixlib["now"]), '&Now', parent)        
    action_now.setShortcut('F1')
    action_now.setStatusTip('Go to now')
    action_now.triggered.connect(parent.on_now)
    toolbar.addAction(action_now)


    action_calendar = QAction(QIcon(pixlib["calendar"]), '&Calendar', parent)        
    action_calendar.setShortcut('Ctrl+D')
    action_calendar.setStatusTip('Open calendar')
    action_calendar.triggered.connect(parent.on_calendar)
    toolbar.addAction(action_calendar)

    action_refresh = QAction(QIcon(pixlib["refresh"]), '&Refresh', parent)        
    action_refresh.setShortcut('F5')
    action_refresh.setStatusTip('Refresh rundown')
    action_refresh.triggered.connect(parent.refresh)
    toolbar.addAction(action_refresh)

    action_day_next = QAction(QIcon(pixlib["next"]), '&Next day', parent)        
    action_day_next.setShortcut('Alt+Right')
    action_day_next.setStatusTip('Go to next day')
    action_day_next.triggered.connect(parent.on_day_next)
    toolbar.addAction(action_day_next)

    toolbar.addSeparator()

    action_scheduler = QAction(QIcon(pixlib["clock"]), '&Scheduler', parent)        
    action_scheduler.setShortcut('F7')
    action_scheduler.setStatusTip('Open scheduler')
    action_scheduler.triggered.connect(parent.on_scheduler)
    toolbar.addAction(action_scheduler)


    toolbar.addWidget(ToolBarStretcher(parent))

    parent.date_display = RundownDate()
    toolbar.addWidget(parent.date_display)

    return toolbar


class Rundown(BaseWidget):
    def __init__(self, parent):
        super(Rundown, self).__init__(parent)
        self.parent = parent

        toolbar = rundown_toolbar(self)
        
        self.current_date = time.strftime("%Y-%m-%d")
        self.id_channel   = 1 # TODO (get default from playout config, overide in setState)
        self.column_widths = {}


        self.view = NXView(self)
        self.model = RundownModel(self)


        self.delegate = MetaEditItemDelegate(self.view)
        self.delegate.settings["base_date"] = datestr2ts(self.current_date)

        self.view.setModel(self.model)
        self.view.setItemDelegate(self.delegate)
        
        self.view.activated.connect(self.on_activate)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)        

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.view, 1)

        self.setLayout(layout)




    def getState(self):
        state = {}
        state["class"] = "rundown"
        self.saveColumnWidths()
        state["column_widths"] = self.column_widths
        return state

    def setState(self, state):
        self.column_widths = state.get("column_widths", {})
        self.load(self.id_channel, self.current_date)

    def loadColumnWidths(self):
        for id_column in range(self.model.columnCount(False)):
            col_tag = self.model.header_data[id_column]
            w = self.column_widths.get(col_tag,False)
            if w:
                self.view.setColumnWidth(id_column, w)
            else: 
                self.view.resizeColumnToContents(id_column)

    def saveColumnWidths(self):
        for id_column in range(self.model.columnCount(False)):
            self.column_widths[self.model.header_data[id_column]] = self.view.columnWidth(id_column)
        
    def load(self, id_channel, date):
        if self.model.header_data:
            self.saveColumnWidths()
        self.model.load(id_channel, date)
        self.loadColumnWidths()

    def refresh(self):
        self.load(self.id_channel, self.current_date)

    def update_header(self):
        syy,smm,sdd = [int(i) for i in self.current_date.split("-")]
        t = datetime.date(syy, smm, sdd)

        if t < datetime.date.today():
            s = " color='red'"
        elif t > datetime.date.today():
            s = " color='green'"
        else:
            s = ""

        t = t.strftime("%A %Y-%m-%d")
        self.parent.setWindowTitle("Rundown {}".format(t))
        self.date_display.setText("<font{}>{}</font>".format(s, t))

    ################################################################
    ## 

    def on_activate(self, mi):
        pass




    ################################################################
    ## Navigation

    def set_date(self, date):
        self.current_date = date
        self.update_header()
        self.load(self.id_channel, self.current_date)

    def on_day_prev(self):
        syy,smm,sdd = [int(i) for i in self.current_date.split("-")]
        go = time.mktime(time.struct_time([syy,smm,sdd,0,0,0,False,False,False])) - (24*3600)
        self.set_date(time.strftime("%Y-%m-%d",time.localtime(go)))

    def on_day_next(self):
        syy,smm,sdd = [int(i) for i in self.current_date.split("-")]
        go = time.mktime(time.struct_time([syy,smm,sdd,0,0,0,False,False,False])) + (24*3600)
        self.set_date(time.strftime("%Y-%m-%d",time.localtime(go)))

    def on_now(self):
        self.set_date(time.strftime("%Y-%m-%d"))

    ## Navigation
    ################################################################

    def on_calendar(self):
        pass

    def on_scheduler(self):
        scheduler = Scheduler(self, self.current_date)
        scheduler.exec_()
        self.refresh()