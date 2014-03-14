import time
import datetime

from firefly_common import *
from firefly_view import *

from nx.objects import *

from dlg_scheduler import Scheduler
from mod_rundown_onair import OnAir



class RundownModel(NXViewModel):
    def load(self, id_channel, date, full=True):
        self.id_channel = id_channel
        self.date = date

        self.beginResetModel()

        if full:
            self.object_data = []
            self.header_data = ["rundown_symbol", "title", "rundown_staus", "id_object", "id_magic", "id_asset"]

            res, data = query("rundown",{"id_channel":id_channel,"date":date})
            if success(res) and data: 
                row = 0
                current_bin = False
                for edata in data["data"]:
                    evt = Event(from_data=edata["event_meta"])
                    evt.bin = Bin(from_data=edata["bin_meta"])
                    current_bin = evt.bin.id

                    evt["rundown_bin"] = current_bin
                    evt["rundown_row"] = row
                    self.object_data.append(evt)
                    row += 1

                    if not edata["items"]:
                        dummy = Dummy("(no item)")
                        dummy["rundown_bin"] = current_bin
                        dummy["rundown_row"] = row
                        self.object_data.append(dummy)                    
                        row += 1

                    for idata, adata in edata["items"]:
                        item = Item(from_data=idata)
                        item.asset = Asset(from_data=adata)
                        item["rundown_bin"] = current_bin
                        item["rundown_row"] = row
                        self.object_data.append(item)
                        row += 1
        
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
        
        drop_objects = []
        
        if data.hasFormat("application/nx.item"):
            iformat = ITEM
            d = data.data("application/nx.item").data()
            items = json.loads(d.decode("ascii"))
            if not items or items[0].get("rundown_row","") in [row, row-1]:
                return False
            for obj in items:
                drop_objects.append(Item(from_data=obj))
            
        elif data.hasFormat("application/nx.asset"):
            iformat = ASSET
            d = data.data("application/nx.asset").data()
            items = json.loads(d.decode("ascii"))
            for obj in items:
                drop_objects.append(Asset(from_data=obj))

        else:
            return False
        


        pre_items = []
        dbg = []
        i = row-1   
        to_bin = self.object_data[i]["rundown_bin"]
        
        while i >= 1:
            if self.object_data[i].object_type != "item" or self.object_data[i]["rundown_bin"] != to_bin: break
            p_item = self.object_data[i].id
            
            if not p_item in [item.id for item in drop_objects]: 
                pre_items.append({"object_type" : ITEM, "id_object" : p_item, "params" : {}})
                dbg.append(self.object_data[i].id)
            i-=1
        pre_items.reverse()
     
        
        for obj in drop_objects: 
            if data.hasFormat("application/nx.item"):  
                pre_items.append({"object_type" : ITEM, "id_object" : obj.id, "params" : {}})
                dbg.append(obj.id)

            elif data.hasFormat("application/nx.asset"): 
                mark_in = mark_out = False

               # subclips = json.loads(item[1].get("Subclips","[]"))
               # if subclips:
               #     print "Requesting subclip for item %s" %item[0][0]
               #     mark_in, mark_out = SelectSubclip(subclips)
               # elif item[0][0] == -1:
               #  
               #     print "Requesting live item duration"
               #     mark_in = 0
               #     mark_out = GetTc("Enter live item duration")
               #     if not mark_out: return False
               #
               # else:
                mark_in  = obj["mark_in"]
                mark_out = obj["mark_out"]
                
                params = {} 
                if mark_in:  params["mark_in"]  = mark_in
                if mark_out: params["mark_out"] = mark_out
                
                pre_items.append({"object_type" : ASSET, "id_object" : obj.id, "params" : params}) 

        i = row
        while i < len(self.object_data):
            if self.object_data[i].object_type != "item" or self.object_data[i]["rundown_bin"] != to_bin: break
            p_item = self.object_data[i].id

            if not p_item in [item.id for item in drop_objects]: 
                pre_items.append({"object_type" : ITEM, "id_object" : p_item, "params" : {}})
                dbg.append(self.object_data[i].id)
            i+=1
        
        if pre_items:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                query("bin_order",params={"id_bin":to_bin, "order":pre_items, "sender":self.parent.parent.objectName() })
            except:
                return False
            self.load(self.id_channel, self.date)
            QApplication.restoreOverrideCursor()
        return True




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

    action_onair = QAction(QIcon(pixlib["onair"]), '&Playout controls', parent)        
    action_onair.setShortcut('F6')
    action_onair.setStatusTip('Toggle playout controls')
    action_onair.triggered.connect(parent.on_onair)
    toolbar.addAction(action_onair)

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
        self.current_item = False
        self.cued_item = False
        self.column_widths = {}

        self.on_air = OnAir(self)
        self.view  = NXView(self)
        self.model = RundownModel(self)


        self.delegate = MetaEditItemDelegate(self.view)
        self.delegate.settings["base_date"] = datestr2ts(self.current_date)

        self.view.setModel(self.model)
        self.view.setItemDelegate(self.delegate)
        
        self.view.activated.connect(self.on_activate)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)       
        self.view.selectionChanged = self.selectionChanged
        self.view.keyPressEvent = self.view_keyPressEvent



        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.on_air)
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
        
    def load(self, id_channel, date, full=True):
        if full and self.model.header_data:
            self.saveColumnWidths()
        self.model.load(id_channel, date, full=full)
        if full:
            self.loadColumnWidths()

    def refresh(self, full=True):
        self.load(self.id_channel, self.current_date, full=full)

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

        item = self.model.object_data[mi.row()]
        print (item)

        params = {
            "id_channel" : self.id_channel,
            "id_item"    : item.id
            }

        query("cue", params, "play1")



    def view_keyPressEvent(self, event):
        print (event.key())
        if event.key() == Qt.Key_Delete:
            print (query("del_items",params={"items":[obj.id for obj in self.view.selected_objects]}))
            return
        NXView.keyPressEvent(self.view, event)



    def update_status(self, data):
        if data.data["current_item"] != self.current_item:
            self.current_item = data.data["current_item"]
            self.refresh()

        if data.data["cued_item"] != self.cued_item:
            self.cued_item = data.data["cued_item"]
            self.refresh(full=False)
        
        self.on_air.update_status(data)


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

    def on_onair(self):
        if self.on_air.isVisible():
            self.on_air.hide()
        else:
            self.on_air.show()



    def selectionChanged(self, selected, deselected):     
        rows = []
        self.view.selected_objects = []

        tot_dur = 0

        for idx in self.view.selectionModel().selectedIndexes():
            #row      =  self.sort_model.mapToSource(idx).row()
            row = idx.row()
            if row in rows: 
                continue
            rows.append(row)
            obj = self.model.object_data[row]
            self.view.selected_objects.append(obj)
            if obj.object_type in ["asset", "item"]:
                tot_dur += obj.get_duration()

        if self.view.selected_objects:
            self.parent.parent.focus(self.view.selected_objects)
            if len(self.view.selected_objects) > 1 and tot_dur:
                self.status("{} objects selected. Total duration {}".format(len(self.view.selected_objects), s2time(tot_dur) ))

        super(NXView, self.view).selectionChanged(selected, deselected)

