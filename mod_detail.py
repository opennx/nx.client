import copy

from firefly_common import *
from firefly_widgets import *

from nx.common.metadata import meta_types
from nx.objects import Asset


from dlg_ingest import IngestDialog

class DetailTabMain(QWidget):
    def __init__(self, parent):
        super(DetailTabMain, self).__init__(parent)
        self.tags = []
        self.widgets = {}
        self.layout = QVBoxLayout()
        self.form = False
        self.id_folder = False
        self.status = -1

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setContentsMargins(0,0,0,0)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        mwidget = QWidget()
        mwidget.setLayout(self.layout)
        self.scroll_area.setWidget(mwidget)

        scroll_layout = QVBoxLayout()
        scroll_layout.addWidget(self.scroll_area)
        self.setLayout(scroll_layout)


    def load(self, obj, **kwargs):
        id_folder = kwargs.get("id_folder", obj["id_folder"])
        if id_folder != self.id_folder:
            if id_folder == 0:
                self.tags = []
            else:
                self.tags = config["folders"][id_folder][2]

            if self.form:
                # SRSLY. I've no idea what I'm doing here
                self.layout.removeWidget(self.form)
                self.form.deleteLater()
                QApplication.processEvents()
                self.form.destroy()
                QApplication.processEvents()
                self.form = None
            for i in reversed(range(self.layout.count())): 
                self.layout.itemAt(i).widget().deleteLater()

            self.form = MetaEditor(self, self.tags)
            self.layout.addWidget(self.form)
            self.id_folder = id_folder
            self.status = obj["status"]

        for tag, conf in self.tags:
            self.form[tag] = obj[tag]
            obj[tag] = self.form[tag]
        
        if self.form:
            enabled = has_right("asset_edit", id_folder)
            self.form.setEnabled(enabled)


class MetaList(QTextEdit):
    def __init__(self, parent):
        super(MetaList, self).__init__(parent)
        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.setCurrentFont(fixed_font)
        self.setReadOnly(True)
        self.setStyleSheet("border:0;")


class DetailTabExtended(MetaList):
    def load(self, obj, **kwargs):
        self.tag_groups = {
                "core" :  [],
                "other"  : [],
            }
        if not obj["id_folder"]:
            return
        for tag in sorted(meta_types):
            if meta_types[tag].namespace in ["a", "i", "e", "b", "o"]:
                self.tag_groups["core"].append(tag)
            elif meta_types[tag].namespace in ("fmt", "qc"):
                continue
            elif tag not in [r[0] for r in config["folders"][obj["id_folder"]][2]]:
                self.tag_groups["other"].append(tag)

        data = ""
        for tag_group in ["core", "other"]:
            for tag in self.tag_groups[tag_group]:
                if not tag in obj.meta:
                    continue
                tag_title = meta_types.tag_alias(tag, config.get("language","en-US"))
                value = obj.format_display(tag) or obj["tag"] or ""
                if value:
                    data += "{:<40}: {}\n".format(tag_title, value)
            data += "\n\n"

        self.setText(data)



class DetailTabTechnical(MetaList):
    def load(self, obj, **kwargs):        
        self.tag_groups = {
                "File" : [],
                "Format"  : [],
                "QC"   : []
            }

        for tag in sorted(meta_types):
            if tag.startswith("file") or tag in ["id_storage", "path", "origin"]:
                self.tag_groups["File"].append(tag)
            elif meta_types[tag].namespace == "fmt":
                self.tag_groups["Format"].append(tag)
            elif meta_types[tag].namespace == "qc" and not tag.startswith("qc/"):
                self.tag_groups["QC"].append(tag)

        data = ""
        if not obj["id_folder"]:
            return
        for tag_group in ["File", "Format", "QC"]:
            for tag in self.tag_groups[tag_group]:
                if not tag in obj.meta:
                    continue
                tag_title = meta_types.tag_alias(tag, config.get("language","en-US"))
                value = obj.format_display(tag) or obj["tag"] or ""
                if value:
                    data += "{:<40}: {}\n".format(tag_title, value)
            data += "\n\n"

        self.setText(data)





class DetailTabJobs(QWidget):
    def load(self, obj, **kwargs):
        pass

class DetailTabUsage(QWidget):
    def load(self, obj, **kwargs):
        pass


class DetailTabs(QTabWidget):
    def __init__(self, parent):
        super(DetailTabs, self).__init__()
        self.setStyleSheet(base_css)   
        
        self.tab_main = DetailTabMain(self)
        self.tab_extended = DetailTabExtended(self)
        self.tab_technical = DetailTabTechnical(self)
#        self.tab_jobs = DetailTabUsage(self)
#        self.tab_usage = DetailTabJobs(self)

        self.addTab(self.tab_main, "Main")
        self.addTab(self.tab_extended, "Extended")
        self.addTab(self.tab_technical, "Technical")
#        self.addTab(self.tab_jobs, "Jobs")
#        self.addTab(self.tab_usage, "Usage")

    def load(self, obj, **kwargs):
        tabs = [
                self.tab_main,
                self.tab_extended,
                self.tab_technical,
#                self.tab_jobs,
#                self.tab_usage
                ]
        for tab  in tabs:
            tab.load(obj, **kwargs)



def detail_toolbar(wnd):
    toolbar = QToolBar(wnd)

    fdata = []
    for id_folder in sorted(config["folders"].keys()):
        fdata.append([id_folder, config["folders"][id_folder][0]])

    wnd.folder_select = NXE_select(wnd, fdata)
    wnd.folder_select.currentIndexChanged.connect(wnd.on_folder_changed)
    wnd.folder_select.setEnabled(False)
    toolbar.addWidget(wnd.folder_select)

    toolbar.addSeparator()

    wnd.duration =  NXE_timecode(wnd)
    toolbar.addWidget(wnd.duration)

    toolbar.addSeparator()

    wnd.action_approve = QAction(QIcon(pixlib["qc_approved"]),'Approve', wnd)        
    wnd.action_approve.setShortcut('Y')
    wnd.action_approve.triggered.connect(partial(wnd.on_set_qc, 4))
    wnd.action_approve.setEnabled(False)
    toolbar.addAction(wnd.action_approve)

    wnd.action_qc_reset = QAction(QIcon(pixlib["qc_new"]),'QC Reset', wnd)        
    wnd.action_qc_reset.setShortcut('T')
    wnd.action_qc_reset.triggered.connect(partial(wnd.on_set_qc, 0))
    wnd.action_qc_reset.setEnabled(False)
    toolbar.addAction(wnd.action_qc_reset)

    wnd.action_reject = QAction(QIcon(pixlib["qc_rejected"]),'Reject', wnd)        
    wnd.action_reject.setShortcut('U')
    wnd.action_reject.triggered.connect(partial(wnd.on_set_qc, 3))
    wnd.action_reject.setEnabled(False)
    toolbar.addAction(wnd.action_reject)

    toolbar.addSeparator()

    wnd.action_ingest = QAction(QIcon(pixlib["record"]),'Ingest', wnd)        
    wnd.action_ingest.setShortcut('CTRL+7')
    wnd.action_ingest.triggered.connect(wnd.on_ingest)
    wnd.action_ingest.setEnabled(False)
    toolbar.addAction(wnd.action_ingest)

    toolbar.addWidget(ToolBarStretcher(wnd))
 
### Does not work with cache.... FIX LATER   
#    action_revert = QAction(QIcon(pixlib["cancel"]), '&Revert changes', wnd)        
#    action_revert.setStatusTip('Revert changes')
#    action_revert.triggered.connect(wnd.on_revert)
#    toolbar.addAction(action_revert)

    action_apply = QAction(QIcon(pixlib["accept"]), '&Apply changes', wnd)        
    action_apply.setShortcut('Ctrl+S')
    action_apply.setStatusTip('Apply changes')
    action_apply.triggered.connect(wnd.on_apply)
    toolbar.addAction(action_apply)

    return toolbar



class Detail(BaseWidget):
    def __init__(self, parent):
        super(Detail, self).__init__(parent)
        parent.setWindowTitle("Asset detail")
        self.object = False

        self._is_loading = self._load_queue = False

        self.toolbar = detail_toolbar(self)
        self.detail_tabs = DetailTabs(self)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.detail_tabs)
        self.setLayout(layout)

    @property 
    def form(self):
        return self.detail_tabs.tab_main.form

    def save_state(self):
        state = {}
        return state

    def load_state(self, state):
        pass

    def switch_tabs(self, idx=-1):
        if idx == -1:
            idx = (self.detail_tabs.currentIndex()+1) % self.detail_tabs.count()
        self.detail_tabs.setCurrentIndex(idx)

    def focus(self, objects, silent=False):
        if len(objects) == 1 and objects[0].object_type in ["asset"]:

            if self._is_loading:
                self._load_queue = objects
                return
            else:
                self._load_queue = False
                self._is_loading = True  

            ###############################################
            ## Save changes?

            changed = False
            if self.form and self.object and not silent:
               changed = (self.object["id_folder"] != self.folder_select.get_value()) or self.form.changed

            if changed:
                reply = QMessageBox.question(
                        self, 
                        "Save changes?", 
                        "{} has been changed.\n\nSave changes?".format(self.object),
                        QMessageBox.Yes | QMessageBox.No
                        )

                if reply == QMessageBox.Yes:
                    self.on_apply()

            ## Save changes?
            ###############################################


            self.folder_select.setEnabled(True)
            if not self.object or self.object.id != objects[0].id:
                self.object = Asset(from_data=objects[0].meta)
                self.parent().setWindowTitle("Detail of {}".format(self.object))
            else:
                for tag in set(list(objects[0].meta.keys()) + list(self.detail_tabs.tab_main.form.inputs.keys())):
                    if self.form and tag in self.form.inputs:
                        if self.form[tag] != self.object[tag]:
                            self.object[tag] = self.form[tag]
                            continue
                    self.object[tag] = objects[0][tag]

            self.detail_tabs.load(self.object)
            self.folder_select.set_value(self.object["id_folder"])

            if self.object.object_type in ["asset", "item"]:
                self.duration.set_value(self.object.duration)
                self.duration.show()
                if self.object["status"] == OFFLINE:
                    self.duration.setEnabled(True)
                else:
                    self.duration.setEnabled(False)
    
            enabled = (self.object.id == 0) or has_right("asset_edit", self.object["id_folder"])
            self.folder_select.setEnabled(enabled)
            self.action_approve.setEnabled(enabled)
            self.action_qc_reset.setEnabled(enabled)
            self.action_reject.setEnabled(enabled)
            self.action_ingest.setEnabled(enabled)

            self._is_loading = False
            if self._load_queue:
                self.focus(self._load_queue)


    def on_folder_changed(self):
        self.detail_tabs.load(self.object, id_folder=self.folder_select.get_value())
       

    def new_asset(self):
        new_asset = Asset()
        print ("status:", new_asset["status"])
        if self.object and self.object["id_folder"]:
            new_asset["id_folder"] = self.object["id_folder"]
        else:
            new_asset["id_folder"] = 0
        self.object = False
        self.duration.set_value(0)
        self.focus([new_asset])


    def clone_asset(self):
        new_asset = Asset()
        if self.object and self.object["id_folder"]:
            new_asset["id_folder"] = self.object["id_folder"]
            for key in self.form.inputs:
                new_asset[key] = self.form[key]
                if self.duration.isEnabled():
                   new_asset["duration"] = self.duration.get_value()
        else:
            new_asset["id_folder"] = 0
        self.object = False
        self.focus([new_asset])


    def on_apply(self):
        if not self.form:
            return 
        data = {"id_folder":self.folder_select.get_value()}
        for key in self.form.inputs:
            data[key] = self.form[key]
        if self.duration.isEnabled():
            data["duration"] = self.duration.get_value()
        stat, res = query("set_meta", objects=[self.object.id], data=data)
        if not success(stat):
            QMessageBox.critical(self, "Error", res)
        else:
            if not self.object.id:
                obj = Asset(from_data=res)
                asset_cache[obj.id] = obj
                self.focus([obj], silent=True)
        self.form.reset_changes()
        self.parent().setWindowTitle("Detail of {}".format(self.object))


    def on_revert(self):
        if self.object:
            self.focus([asset_cache[self.object.id]], silent=True)


    def on_set_qc(self, state):
        stat, res = query("set_meta", objects=[self.object.id], data={"qc/state" : state} )
        if not success(stat):
            QMessageBox.critical(self, "Error", res)


    def on_ingest(self):
        dlg = IngestDialog(self, self.object)
        dlg.exec_()



    def seismic_handler(self, data):
        if data.method == "objects_changed" and data.data["object_type"] == "asset" and self.object: 
            if self.object.id in data.data["objects"] and self.object.id:
                self.focus([asset_cache[self.object.id]], silent=True)
