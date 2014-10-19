import copy

from firefly_common import *
from firefly_widgets import *

from nx.common.metadata import meta_types
from nx.objects import Asset


class DetailTabMain(QWidget):
    def __init__(self, parent):
        super(DetailTabMain, self).__init__(parent)
        self.tags = []
        self.widgets = {}
        self.layout = QVBoxLayout()
        self.form = False
        self.id_folder = False


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


    def load(self, obj):
        if obj["id_folder"] != self.id_folder:
            if obj["id_folder"] == 0:
                self.tags = []
            else:
                self.tags = config["folders"][obj["id_folder"]][2]

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
            self.id_folder = obj["id_folder"]

        for tag, conf in self.tags:
            self.form[tag] = obj[tag]




class DetailTabExtended(QTextEdit):
    def __init__(self, parent):
        super(DetailTabExtended, self).__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("border:0;")

    def load(self, obj):

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



class DetailTabTechnical(QTextEdit):
    def __init__(self, parent):
        super(DetailTabTechnical, self).__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("border:0;")

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

    def load(self, obj):
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
    def load(self, obj):
        pass

class DetailTabUsage(QWidget):
    def load(self, obj):
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

    def load(self, obj):
        tabs = [
                self.tab_main,
                self.tab_extended,
                self.tab_technical,
#                self.tab_jobs,
#                self.tab_usage
                ]
        for tab  in tabs:
            tab.load(obj)



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

    wnd.action_approve = QAction(QIcon(pixlib["qc_approved"]),'Approve', wnd)        
    wnd.action_approve.setShortcut('Y')
    wnd.action_approve.triggered.connect(wnd.on_approve)
    wnd.action_approve.setEnabled(False)
    toolbar.addAction(wnd.action_approve)

    wnd.action_qc_reset = QAction(QIcon(pixlib["qc_new"]),'QC Reset', wnd)        
    wnd.action_qc_reset.setShortcut('T')
    wnd.action_qc_reset.triggered.connect(wnd.on_qc_reset)
    wnd.action_qc_reset.setEnabled(False)
    toolbar.addAction(wnd.action_qc_reset)

    wnd.action_reject = QAction(QIcon(pixlib["qc_rejected"]),'Reject', wnd)        
    wnd.action_reject.setShortcut('U')
    wnd.action_reject.triggered.connect(wnd.on_reject)
    wnd.action_reject.setEnabled(False)
    toolbar.addAction(wnd.action_reject)

    toolbar.addWidget(ToolBarStretcher(wnd))
    
    action_revert = QAction(QIcon(pixlib["cancel"]), '&Revert changes', wnd)        
    action_revert.setStatusTip('Revert changes')
    action_revert.triggered.connect(wnd.on_revert)
    toolbar.addAction(action_revert)

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

            if self.form and self.object and not silent:
                for tag in self.form.inputs:
                    if str(self.form[tag]).strip() != str(self.object[tag]).strip().replace("\r",""):
                        reply = QMessageBox.question(self, "Save changes?", "{} has been changed. Save changes?".format(
                            self.object, 
                            json.dumps(self.form[tag]), 
                            json.dumps(self.object[tag])),
                            QMessageBox.Yes|QMessageBox.No);
                        if reply == QMessageBox.Yes:
                            self.on_apply()
                        break

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
            
            self.action_approve.setEnabled(True)
            self.action_qc_reset.setEnabled(True)
            self.action_reject.setEnabled(True)

            self._is_loading = False
            if self._load_queue:
                self.focus(self._load_queue)



    def on_folder_changed(self):
        self.update_data()
        self.detail_tabs.load(self.object)

    def update_data(self):
        self.object["id_folder"] = self.folder_select.get_value()
        for key, cfg in self.detail_tabs.tab_main.tags:
            self.object[key] = self.form.inputs[key].get_value()
            
                

    def new_asset(self):
        new_asset = Asset()
        if self.object and self.object["id_folder"]:
            new_asset["id_folder"] = self.object["id_folder"]
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
        stat, res = query("set_meta", objects=[self.object.id], data=data)
        if not success(stat):
            QMessageBox.critical(self, "Error", res)

    def on_revert(self):
        if self.object:
            self.focus([asset_cache[self.object.id]], silent=False)

    def on_approve(self):
        res, data = query("set_meta", objects=[self.object.id], data={"qc/state" : 4} )

    def on_qc_reset(self):
        res, data = query("set_meta", objects=[self.object.id], data={"qc/state" : 0} )

    def on_reject(self):
        res, data = query("set_meta", objects=[self.object.id], data={"qc/state" : 3} )

    def seismic_handler(self, data):
        if data.method == "objects_changed" and data.data["object_type"] == "asset" and self.object: 
            if self.object.id in data.data["objects"]:
                self.focus([asset_cache[self.object.id]], silent=True)


