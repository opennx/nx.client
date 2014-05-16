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


def shorten(instr):
    output = instr[:100]
    output = output.split("\n")[0]
    if instr != output:
        output += "..."
    return output


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
                if role == ROLE_DECORATION and obj["id_folder"]:
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

        value = self[key]

        if key == "duration":
            if self.object_type not in ["asset", "item"]:
                return ""
            elif self["video/fps"]:
                return s2tc(self.get_duration(),  fract2float(self["video/fps"]))
            else:
                return s2time(self.get_duration())

        elif key in ["mark_in", "mark_out"]:
            if not value:
                return ""
            elif self["video/fps"]:
                return s2tc(value,  fract2float(self["video/fps"]))
            else:
                return s2time(value)

        elif key == "rundown_status":
            try:
                return [
                    "OFFLINE",
                    "NOT SCHEDULED",
                    "READY"
                    ][value]
            except:
                return ""

        elif key == "content_type":
            return ""

        elif key == "id_folder":
            return config["folders"][self[key]][0]




        if not key in meta_types:
            return self[key]

        mtype = meta_types[key]

        if   mtype.class_ in [TEXT, BLOB]:         return shorten(value)
        elif mtype.class_ in [INTEGER, NUMERIC]:   return ["%.3f","%d"][float(value).is_integer()] % value if value else 0
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
        elif mtype.class_ == TIMECODE:
            if self["video/fps"]:
                return s2tc(value,  fract2float(self["video/fps"]))
            else:
                return s2time(value)
        else:
            return value 


    def format_edit(self, key):
        key, val = self._key(key, ROLE_EDIT)

        if key and meta_types[key].editable and not val:
            return key, meta_types[key].class_, meta_types[key].settings, self
        else:
            return key, "NOEDIT", False, self


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


    def format_background(self, key, model=False): # Key is not used.... color per row
        if model and self.object_type == "item":   
            if not self.id:
                return "#111140"
            elif model.parent().cued_item == self.id:
                return "#059005"
            elif model.parent().current_item == self.id:
                return "#900505"

        if self.object_type == "event" and self.model.parent().__class__.__name__ == "Rundown":
            return RUNDOWN_EVENT_BACKGROUND_COLOR
        return None
        

    def format_foreground(self,key):
        if key == "id_folder":
            return config["folders"][self[key]][1]

        elif "rundown_status" in self.meta:
            return [NXColors[ASSET_FG_OFFLINE], 
                    NXColors[ASSET_FG_OFFLINE], 
                    DEFAULT_TEXT_COLOR
                    ][int(self["rundown_status"])]

        elif key == "title" and self.object_type == "asset":
            return NXColors[[ASSET_FG_OFFLINE, ASSET_FG_ONLINE, ASSET_FG_CREATING, ASSET_FG_TRASHED, ASSET_FG_RESET][self["status"]]]

        return DEFAULT_TEXT_COLOR



    def format_sort(self, key):
        return self[key]

