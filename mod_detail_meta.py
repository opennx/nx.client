from firefly_common import *
from firefly_widgets import *



class MetaView(QTableView):
    def __init__(self, parent):
        super(MetaView, self).__init__(parent)
        self.parent = parent

    def load(self, obj):
        pass




class MetaView(QTextEdit):
    def load(self, objects):
        txt = ""

        tags = set([tag for obj in objects for tag in obj.meta])

        for tag in sorted(tags):
            s = set([obj[tag] for obj in objects])
            s = list(s)
            if len(s) == 1:
                try:
                    value = str(s[0])
                except:
                    value = s[0].encode("utf-8")
            else:
                value = ">>>MULTIPLE VALUES<<<"

            txt += "{0:<25} {1}\n".format(tag, value)


            
        self.setText(txt)