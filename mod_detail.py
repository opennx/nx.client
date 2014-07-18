from firefly_common import *
from firefly_widgets import *
from nx.common.metadata import meta_types


class DetailTabMain(QWidget):
    def load(self, obj):
        pass

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
        self.tab_jobs = DetailTabUsage(self)
        self.tab_usage = DetailTabJobs(self)

        self.addTab(self.tab_main, "Main")
        self.addTab(self.tab_extended, "Extended")
        self.addTab(self.tab_technical, "Technical")
        self.addTab(self.tab_jobs, "Jobs")
        self.addTab(self.tab_usage, "Usage")

    def load(self, obj):
        tabs = [
                self.tab_main,
                self.tab_extended,
                self.tab_technical,
                self.tab_jobs,
                self.tab_usage
                ]
        for tab  in tabs:
            tab.load(obj)




class Detail(BaseWidget):
    def __init__(self, parent):
        super(Detail, self).__init__(parent)
        parent.setWindowTitle("Asset detail")

        self.detail_tabs = DetailTabs(self)

        layout = QVBoxLayout()
        layout.addWidget(self.detail_tabs)
        self.setLayout(layout)

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
        if len(objects) == 1 and objects[0].object_type in ["asset", "item"]:
            self.detail_tabs.load(objects[0])
            self.parent().setWindowTitle("Detail of {}".format(objects[0]))
            self.setFocus(True)

    def new_asset(self):
        pass