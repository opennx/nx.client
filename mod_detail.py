from firefly_common import *
from firefly_widgets import *

from nx.common.metadata import meta_types
from nx.objects import Asset


import copy

class EditForm(QWidget):
    pass

def create_form(parent, tags):
    widget = EditForm(parent)
    widget.inputs = {}
    layout = QFormLayout()
    for tag, conf in tags:
        tagname = meta_types.tag_alias(tag, config.get("language","en-US"))
        
        if meta_types[tag].class_ == TEXT:
            widget.inputs[tag] = NXE_text(widget)

        elif meta_types[tag].class_ == BLOB:
            widget.inputs[tag] = NXE_blob(widget)

        else:
            widget.inputs[tag] = NXE_text(widget)
            widget.inputs[tag].setReadOnly(True)

        layout.addRow(tagname, widget.inputs[tag])

    widget.setLayout(layout)
    return widget


class DetailTabMain(QWidget):
    def __init__(self, parent):
        super(DetailTabMain, self).__init__(parent)
        self.widgets = {}
        self.layout = QVBoxLayout()
        self.form = False
        self.setLayout(self.layout)
        self.id_folder = False

    def load(self, obj):
        if obj["id_folder"] != self.id_folder:
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

            self.form = create_form(self, self.tags)
            self.layout.addWidget(self.form)
            self.id_folder = obj["id_folder"]


        for tag, conf in self.tags:
            self.form.inputs[tag].set_value(obj[tag])




class DetailTabExtended(QWidget):
    def load(self, obj):
        pass

class DetailTabTechnical(QTextEdit):
    def __init__(self, parent):
        super(DetailTabTechnical, self).__init__(parent)
        self.setReadOnly(True)

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
        for tag_group in ["File", "Format", "QC"]:
            for tag in self.tag_groups[tag_group]:
                if not tag in obj.meta:
                    continue
                tag_title = meta_types.tag_alias(tag, config.get("language","en-US"))
                value = obj.format_display(tag) or obj["tag"] or ""
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

    wnd.folder_select = NXE_enum(wnd, fdata)
    wnd.folder_select.currentIndexChanged.connect(wnd.on_folder_changed)
    wnd.folder_select.setEnabled(False)
    toolbar.addWidget(wnd.folder_select)

    toolbar.addWidget(ToolBarStretcher(wnd))
    
    action_revert = QAction(QIcon(pixlib["cancel"]), '&Revert changes', wnd)        
    action_revert.setStatusTip('Revert changes')
    action_revert.triggered.connect(wnd.on_revert)
    toolbar.addAction(action_revert)

    action_apply = QAction(QIcon(pixlib["accept"]), '&Apply changes', wnd)        
    action_apply.setStatusTip('Apply changes')
    action_apply.triggered.connect(wnd.on_apply)
    toolbar.addAction(action_apply)

    return toolbar



class Detail(BaseWidget):
    def __init__(self, parent):
        super(Detail, self).__init__(parent)
        parent.setWindowTitle("Asset detail")
        self.object = False

        self.toolbar = detail_toolbar(self)
        self.detail_tabs = DetailTabs(self)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.detail_tabs)
        self.setLayout(layout)
        self.subscribe("objects_changed")

    def save_state(self):
        state = {}
        return state

    def load_state(self, state):
        pass

    def switch_tabs(self, idx=-1):
        if idx == -1:
            idx = (self.detail_tabs.currentIndex()+1) % self.detail_tabs.count()
        self.detail_tabs.setCurrentIndex(idx)

    def focus(self, objects):
        if len(objects) == 1 and objects[0].object_type in ["asset"]:
            self.folder_select.setEnabled(True)
            self.object = Asset(from_data=copy.copy(objects[0].meta))

            self.detail_tabs.load(self.object)
            self.parent().setWindowTitle("Detail of {}".format(self.object))
            
            self.folder_select.set_value(self.object["id_folder"])

    def on_folder_changed(self):
        self.update_data()
        self.detail_tabs.load(self.object)

    def update_data(self):
        self.object["id_folder"] = self.folder_select.get_value()
        for key, cfg in self.detail_tabs.tab_main.tags:
            self.object[key] = self.detail_tabs.tab_main.form.inputs[key].get_value()
            
                

    def new_asset(self):
        QMessageBox.warning(self,
                "Not available",
                "This feature is not available in preview version",
                QMessageBox.Cancel
                )


    def on_apply(self):
        QMessageBox.warning(self,
                "Not available",
                "This feature is not available in preview version",
                QMessageBox.Cancel
                )
        print (self.object.meta)
        return
        stat, res = query("set_meta", objects=[self.object.id], data={"id_folder":self.folder_select.get_value()})

    def on_revert(self):
        if self.object:
            self.focus([asset_cache[self.object.id]])


    def seismic_handler(self, data):
        if data.method == "objects_changed" and data.data["object_type"] == "asset" and self.object: 
            if self.object.id in data.data["objects"]:
                self.focus([asset_cache[self.object.id]])