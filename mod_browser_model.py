from firefly_view import *
from nx.objects import Asset

DEFAULT_HEADER_DATA = ["title", "duration", "id_folder"]

class BrowserModel(NXViewModel):
    def browse(self, **kwargs):
        start_time = time.time()
        self.beginResetModel()

        self.object_data = []
        
        try:
            self.header_data = config["views"][kwargs["view"]][2]
        except:
            self.header_data =  DEFAULT_HEADER_DATA

        res, data = query("browse", kwargs)
        if success(res) and "asset_data" in data:    
            for adata in data["asset_data"]:
                self.object_data.append(Asset(from_data=adata))

        self.endResetModel()
        self.parent().status("Got %d assets in %.03f seconds." % (len(self.object_data), time.time()-start_time))


    def flags(self,index):
        flags = super(BrowserModel, self).flags(index)
        if index.isValid():
            if self.object_data[index.row()]["id_object"]:
             flags |= Qt.ItemIsEditable
             flags |= Qt.ItemIsDragEnabled # Itemy se daji dragovat
        return flags


    def mimeTypes(self):
        return ["application/nx.asset"]
     
   
    def mimeData(self, indexes):
        data        = [self.object_data[i] for i in set(index.row() for index in indexes if index.isValid())]
        encodedData = json.dumps([a.meta for a in data])
        mimeData = QMimeData()
        mimeData.setData("application/nx.asset", encodedData.encode("ascii"))

        try:
            urls =[QUrl.fromLocalFile(asset.get_file_path()) for asset in data]
            mimeData.setUrls(urls)
        except:
            pass

        return mimeData

    def dropMimeData(self, data, action, row, column, parent):
        #TODO: UPLOAD
        return False


    def setData(self, index, data, role=False):
        tag = self.header_data[index.column()] 
        value = data
        id_object = self.object_data[index.row()].id
        
        res, data = query("set_meta", {"id_object":id_object, "tag":tag, "value":value })

        if success(res):
            self.object_data[index.row()] = Asset(from_data=data)
            self.dataChanged.emit(index, index)
        else:
            QMessageBox.error(self, "Error", "Unable to save")
        return True
   
