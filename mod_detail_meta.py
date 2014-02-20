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

        for obj in objects:

            for tag in sorted(obj.meta):
                try:
                    value = str(obj[tag])
                except:
                    value = obj[tag].encode("utf-8")
                txt += "{0:<25} {1}\n".format(tag, value)
            txt+= "-------------------------------------\n"
            
        self.setText(txt)