from firefly_view import *
from nx.objects import Asset

DEFAULT_HEADER_DATA = ["title", "duration", "id_folder"]

class BrowserModel(NXViewModel):
    def browse(self, **kwargs):
        start_time = time.time()
        self.beginResetModel()
        try:
            self.header_data = config["views"][kwargs["view"]][2]
        except:
            self.header_data =  DEFAULT_HEADER_DATA

        res, data = query("browse", **kwargs)
        to_update = []
        if success(res) and "result" in data:
            asset_ids = data["result"]
            for id_asset, mtime in asset_ids:
                if not (id_asset in asset_cache and asset_cache[id_asset]["mtime"] == mtime):
                    to_update.append(id_asset)
            if to_update:
                self.parent().parent().parent().update_assets(to_update)
                # res, data = query("get_assets", asset_ids=to_update)
                # if success(res):
                #     for id_asset in data:
                #         try:
                #             asset_cache[int(id_asset)] = Asset(from_data=data[id_asset])
                #         except:
                #             print(id_asset)
            self.object_data = [asset_cache[id_asset] for id_asset, mtime in asset_ids]

        self.endResetModel()
        self.parent().status("Got {} assets in {:.03f} seconds. ({} updated)".format(len(self.object_data), time.time()-start_time, len(to_update)))

    def refresh_assets(self, assets):
        for i in range(len(self.object_data)):
            if self.object_data[i].id in assets:
                self.object_data[i] = asset_cache[self.object_data[i].id]
                self.dataChanged.emit(self.index(i, 0), self.index(i, len(self.header_data)-1))

    def flags(self,index):
        flags = super(BrowserModel, self).flags(index)
        if index.isValid():
            if self.object_data[index.row()]["id_object"]:
                flags |= Qt.ItemIsEditable
                flags |= Qt.ItemIsDragEnabled
        return flags


    def mimeTypes(self):
        return ["application/nx.asset"]
     
   
    def mimeData(self, indexes):
        data        = [self.object_data[i] for i in set(index.row() for index in indexes if index.isValid())]
        encodedData = json.dumps([a.meta for a in data])
        mimeData = QMimeData()
        mimeData.setData("application/nx.asset", encodedData.encode("ascii"))
        try:
            urls =[QUrl.fromLocalFile(asset.get_file_path()) for asset in data if asset.get_file_path()]
            mimeData.setUrls(urls)
        except:
            pass
        return mimeData

    def setData(self, index, data, role=False):
        tag = self.header_data[index.column()] 
        value = data
        id_object = self.object_data[index.row()].id
        res, data = query("set_meta", objects=[id_object], data={tag: value})
        if success(res):
            self.object_data[index.row()] = Asset(from_data=data)
            self.dataChanged.emit(index, index)
        else:
            QMessageBox.error(self, "Error", "Unable to save")
        return True

   
    def dropMimeData(self, data, action, row, column, parent):
        #TODO: UPLOAD
        return False
