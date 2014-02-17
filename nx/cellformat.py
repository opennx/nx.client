from nx.common import *
from nx.common.utils import *
from nx.common.metadata import meta_types, fract2float

from nx.colors import *



ROLE_DISPLAY    = 0
ROLE_EDIT       = 1
ROLE_DECORATION = 2
ROLE_FOREGROUND = 3
ROLE_BACKGROUND = 4
ROLE_SORT       = 5


class SuperTags():
    def __init__(self):
        self.tags = {"rundown_symbol":True}

    def keyformat(self, obj, key, role):
        value = None
        ###########################
        ## TODO: PLUGINIZE THIS

        if key == "rundown_symbol":
            if obj.object_type == "event":
                key = "promoted"
            else:
                if role == ROLE_DECORATION:
                    value = "folder_{}".format(obj["id_folder"])
                elif role == ROLE_DISPLAY:
                    value = ""


        ## TODO: PLUGINIZE THIS        
        ###########################

        return key, value


    def __getitem__(self, key):
        return self.tags[key]





super_tags = SuperTags()


class NXCellFormat():
    format_settings = {}

    def _key(self, key, role=ROLE_DISPLAY):
        if not key in self.meta: 
            if not key in super_tags.tags:
                return key, None
            return super_tags.keyformat(self, key, role)
        return key, None
       

    def format_display(self, key):
        key, val = self._key(key)
        if val is not None:
            return val
        elif not key:
            return ""


        if key == "duration":
            if self["video/fps"]:
                return s2tc(self.get_duration(),  fract2float(self["video/fps"]))
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
        elif mtype.class_ in [STAR, BOOLEAN]:      return None
        elif mtype.class_ == DATETIME:
            if "base_date" in self.format_settings:
                return time.strftime("%H:%M",time.localtime(value))
            else:
                return time.strftime("%Y-%m-%d %H:%M",time.localtime(value))
        elif mtype.class_ == FILESIZE:
            for x in ['bytes','KB','MB','GB','TB']:
                if value < 1024.0: return "%3.1f %s" % (value, x)
                value /= 1024.0
        else: return "E %s" %value 


    def format_edit(self, key):
        key, val = self._key(key, ROLE_EDIT)

        if key and meta_types[key].editable and not val:
            return key, meta_types[key].class_, meta_types[key].settings, self[key]
        else:
            return key, "NOEDIT", False, False 


    def format_decoration(self, key):
        key, val = self._key(key, ROLE_DECORATION)
        if val is not None:
            return val
        elif not key:
            return None

        if key == "content_type":
            return ["text", "video", "audio", "image"][self[key]]

        mtype = meta_types[key]
        value = self[key]

        if mtype.class_ == STAR:
            return ["star_disabled", "star_enabled"][int(value)]

        return None


    def format_background(self, key): # Key is unused.... color per row
        if self.object_type == "event":  # and scheduled start
            return RUNDOWN_EVENT_BACKGROUND_COLOR
        return None
        

    def format_foreground(self,key):
        return DEFAULT_TEXT_COLOR

    def format_sort(self, key):
        return self[key]

