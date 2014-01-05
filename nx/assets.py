from assets_common import *

from PySide.QtCore import *
from PySide.QtGui  import *

from utils import *

class Asset(AssetPrototype):
    def __init__(self, id_asset=False, json=False):
        if json:
            self.meta = json
            self.id_asset = self["id_asset"]
        elif id_asset:
            pass


    def format_display(self, key):
        if not key in self.meta: 
            return ""

        if key == "duration":
            if self["fps"]:
                return s2tc(self.get_duration(), self["fps"])
            else:
                return s2time(self.get_duration())
        if key == "content_type":
            return ""


        if not key in meta_types:
            return self[key]

        mtype = meta_types[key]
        value = self[key]

        if   mtype.class_ in [TEXT, BLOB]:         return value
        elif mtype.class_ in [INTEGER, NUMERIC]:   return ["%.3f","%d"][float(value).is_integer()] % value
        elif mtype.class_ == DATE:                 return time.strftime("%Y-%m-%d",time.localtime(value))
        elif mtype.class_ == TIME:                 return time.strftime("%H:%M",time.localtime(value))
        elif mtype.class_ == DATETIME:             return time.strftime("%Y-%m-%d %H:%M",time.localtime(value))
        elif mtype.class_ == FILESIZE:
            for x in ['bytes','KB','MB','GB','TB']:
                if value < 1024.0: return "%3.1f %s" % (value, x)
                value /= 1024.0
        else: return "E %s" %value


    def format_foreground(self,key):
        if key == "title":
            return QBrush([Qt.red, QColor("#c0c0c0"), Qt.yellow, Qt.black, Qt.black][self["status"]])
        return QColor("#c0c0c0")


    def format_edit(self, key):
        if key in meta_types and meta_types[key].editable:
            return key, meta_types[key].class_, meta_types[key].settings, self[key]
        else:
            print "%s is not editable"
            return key, "NOEDIT", False, False 


    def format_sort(self, key):
        if not key in self.meta: 
            return ""
        if not key in meta_types:
            return self[key]
        if key == "content_type":
            return self[key]
        mtype = meta_types[key]
        value = self[key]

        if mtype.class_   in [INTEGER, NUMERIC, DATE, TIME, DATETIME, DURATION, STATUS, STATE, FILESIZE, PART, BOOLEAN, STAR]: return value
        elif mtype.class_ in [TEXT, BLOB]: return unaccent(value)
        elif mtype.class_ in [SELECT, ISELECT, LIST, COMBO, FOLDER]: return unaccent(self.format_sort(key))
        
        return ""
        #REGION, REGIONS, 


    def format_decoration(self, key):
        if key == "content_type":
            return ["text", "video-camera", "volume-up", "picture-o"][self[key]]

        return None