from functools import partial

from firefly_common import *
from firefly_view import *

from nx.objects import *



ITEM_ROLES = {
    "placeholder" : [["title", "Studio"], ["duration", 300], ["article", ""]],
    "studio" : [["title", "Placeholder"], ["duration", 3600] ],
}


class PlaceholderDialog(QDialog):
    def __init__(self,  parent, item_role):
        super(PlaceholderDialog, self).__init__(parent)
        self.setWindowTitle("Rundown placeholder")

        self.ok = False

        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.addWidget(ToolBarStretcher(toolbar))

        action_accept = QAction(QIcon(pixlib["accept"]), 'Accept changes', self)
        action_accept.setShortcut('Ctrl+S')
        action_accept.triggered.connect(self.on_accept)
        toolbar.addAction(action_accept)

        keys =  [[key, {"default":default}] for key, default in ITEM_ROLES[item_role]]
        self.form = MetaEditor(parent, keys)

        layout = QVBoxLayout()
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.form, 1)
        self.setLayout(layout)

        self.setModal(True)
        self.setStyleSheet(base_css)
        self.setMinimumWidth(400)

    @property
    def meta(self):
        return self.form.meta

    def on_accept(self):
        self.ok = True
        self.close()



class SubclipSelectDialog(QDialog):
    def __init__(self,  parent, asset):
        super(SubclipSelectDialog, self).__init__(parent)
        self.setModal(True)
        self.setStyleSheet(base_css)
        self.setWindowTitle("Select {} subclip to use".format(asset))
        self.ok = False

        layout = QVBoxLayout()

        btn = QPushButton("Entire clip")
        btn.clicked.connect(partial(self.on_submit, "", [asset["mark_in"],asset["mark_out"]]))
        layout.addWidget(btn)

        subclips = asset.meta.get("subclips", {})
        for subclip in sorted(subclips):
            marks = subclips[subclip]
            btn = QPushButton(subclip)
            btn.clicked.connect(partial(self.on_submit, subclip, marks))
            layout.addWidget(btn)

        self.setLayout(layout)


    def on_submit(self, clip, marks):
        self.marks = [float(mark) for mark in marks]
        self.clip = clip
        self.ok = True
        self.close()



class RundownModel(NXViewModel):
    def load(self, id_channel, start_time):
        self.id_channel = id_channel
        self.start_time = start_time
        dbg_start_time = time.time()

        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.WaitCursor)

        self.event_ids = [] # helper for auto refresh

        res, data = query("rundown", handler=self.handle_load, id_channel=id_channel, start_time=start_time)
        if not (success(res) and data):
            QApplication.restoreOverrideCursor()
            return

        data_len = 0
        for edata in data["data"]:
            data_len += 1
            data_len += max(1, len(edata["items"]))

        if data_len != len(self.object_data):
            self.beginResetModel()
            reset = True
            self.object_data = []
        else:
            reset = False

        row = 0
        current_bin = False
        changed_rows = []
        required_assets = []
        for edata in data["data"]:
            evt = Event(from_data=edata["event_meta"])
            evt.bin = Bin(from_data=edata["bin_meta"])
            current_bin = evt.bin.id
            self.event_ids.append(evt.id)
            event_asset = evt["id_asset"]

            evt["rundown_bin"] = current_bin
            evt["rundown_row"] = row
            if reset:
                self.object_data.append(evt)
            elif self.object_data[row].meta != evt.meta:
                self.object_data[row] = evt
                changed_rows.append(row)
            row += 1

            if not edata["items"]:
                dummy = Dummy("(no item)")
                dummy["rundown_bin"] = current_bin
                dummy["rundown_row"] = row
                if reset:
                    self.object_data.append(dummy)
                elif self.object_data[row] != dummy:
                    self.object_data[row] = dummy
                    changed_rows.append(row)
                row += 1


            for i_data in edata["items"]:
                item = Item(from_data=i_data)
                id_asset = item["id_asset"]

                if id_asset:
                    if not id_asset in asset_cache:
                        asset_cache[id_asset] = Asset()
                        required_assets.append(id_asset)
                    elif asset_cache[id_asset]["mtime"] != item["asset_mtime"]:
                        required_assets.append(id_asset)

                item._asset = asset_cache[item["id_asset"]]
                item["rundown_bin"] = current_bin
                item["rundown_row"] = row
                item["rundown_event_asset"] = event_asset
                if reset:
                    self.object_data.append(item)
                elif self.object_data[row] != item:
                    self.object_data[row] = item
                    changed_rows.append(row)
                row += 1

        if required_assets:
            self.parent().parent().parent().update_assets(required_assets)

        if reset:
            self.endResetModel()
        else:
            for row in changed_rows:
                self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.header_data)-1))

        QApplication.restoreOverrideCursor()
        self.parent().status("Rundown loaded in {:.03f}".format(time.time()-dbg_start_time))


    def refresh_assets(self, assets):
        for row in range(len(self.object_data)):
            if self.object_data[row].object_type == "item" and self.object_data[row]["id_asset"] in assets:
                self.object_data[row]._asset = asset_cache[self.object_data[row]["id_asset"]]
                self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.header_data)-1))

    def refresh_items(self, items):
        for row, obj in enumerate(self.object_data):
            if self.object_data[row].id in items and self.object_data[row].object_type == "item":
                self.dataChanged.emit(self.index(row, 0), self.index(row, len(self.header_data)-1))
                break


    def handle_load(self,msg):
        self.parent().status("Loading rundown. {:0.0%}".format(msg["progress"]))
        QApplication.processEvents()



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

        encodedAData = json.dumps([i.asset.meta for i in data])
        mimeData.setData("application/nx.asset", encodedAData)

        try:
            urls =[QUrl.fromLocalFile(item.asset.file_path) for item in data]
            mimeData.setUrls(urls)
        except:
            pass
        return mimeData

    def dropMimeData(self, data, action, row, column, parent):
        if action == Qt.IgnoreAction:
            return True

        if not has_right("rundown_edit", self.id_channel):
            QMessageBox.warning(self.parent(), "Error", "You are not allowed to modify this rundown")
            return False

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
                    if not obj.get("id_object", False) and obj.get("item_role", False) in ITEM_ROLES:
                        dlg = PlaceholderDialog(self.parent(), obj["item_role"])
                        dlg.exec_()
                        if not dlg.ok:
                            return
                        for key in dlg.meta:
                            obj[key] = dlg.meta[key]

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
                pre_items.append({"object_type" : ITEM, "id_object" : obj.id, "params" : obj.meta})
                dbg.append(obj.id)

            elif data.hasFormat("application/nx.asset"):
                mark_in = mark_out = False

                params = {}

                if obj["subclips"]:
                    dlg = SubclipSelectDialog(self.parent(), obj)
                    dlg.exec_()
                    if dlg.ok:
                        mark_in, mark_out = dlg.marks
                        if dlg.clip:
                            params["title"] = "{} ({})".format(obj["title"], dlg.clip)
                else:
                    mark_in  = obj["mark_in"]
                    mark_out = obj["mark_out"]

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
            QApplication.restoreOverrideCursor()
            if success(stat):
                self.parent().status("Bin order changed")
            else:
                QMessageBox.critical(self.parent(), "Error {}".format(stat), res)
            self.load(self.id_channel, self.start_time)
        return True

