from firefly_common import *
from firefly_view import *

from nx.objects import *

class RundownModel(NXViewModel):
    def load(self, id_channel, start_time, full=True):
        self.id_channel = id_channel
        self.start_time = start_time

        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.beginResetModel()

        if full:
            self.object_data = []
            res, data = query("rundown",id_channel=id_channel, start_time=start_time)
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
        QApplication.restoreOverrideCursor()



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
            else:
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
            QApplication.processEvents()
            QApplication.setOverrideCursor(Qt.WaitCursor)
            stat, res = query("bin_order", id_bin=to_bin, order=pre_items, sender=self.parent().parent().objectName())
            if success(stat):
                self.parent().status("Bin order changed")
            QApplication.restoreOverrideCursor()
            self.load(self.id_channel, self.start_time)
        return True

