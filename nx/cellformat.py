from nx.common import *
from nx.common.utils import *
from nx.common.metadata import meta_types, fract2float

from nx.colors import *

def shorten(instr):
    output = instr[:100]
    output = output.split("\n")[0]
    if instr != output:
        output += "..."
    return output

class TagFormat(object):
    tag = "none"
    def display(self, obj):
        return None
    
    def decoration(self, obj):
        return None

    def edit(self, obj):
        return None

    def tooltip(self, obj):
        return None

    def statustip(self, obj):
        return self.tooltip(obj)

    def whatsthis(self, obj):
        return self.tooltip(obj)

    def background(self, obj):
        return None

    def foreground(self, obj):
        return DEFAULT_TEXT_COLOR

##########################################################################################

class TagFolder(TagFormat):
    tag = "id_folder"
    def display(self, obj):
        return config["folders"][obj[self.tag]][0]

    def foreground(self, obj):
        return config["folders"][obj[self.tag]][1]


class TagDuration(TagFormat):
    tag = "duration"

    def display(self, obj):
        if obj.object_type not in ["asset", "item"]:
            return ""
        elif obj["video/fps"]:
            return s2tc(obj.get_duration(),  fract2float(obj["video/fps"]))
        else:
            return s2time(obj.get_duration())

class TagFileSize(TagFormat):
    tag = "file/size"

    def display(self, obj):
        value = obj[self.tag]
        if not value:
            return ""
        for x in ['bytes','KB','MB','GB','TB']:
            if value < 1024.0: 
                return "%3.1f %s" % (value, x)
            value /= 1024.0
        return value

class TagContentType(TagFormat):
    tag = "content_type"

    def decoration(self, obj):
        return ["text", "video", "audio", "image"][int(obj[self.tag])]

class TagPromoted(TagFormat):
    tag = "promoted"

    def decoration(self, obj):
        return ["star_disabled", "star_enabled"][int(obj[self.tag])]

class TagRundownSymbol(TagFormat):
    tag = "rundown_symbol"

    def decoration(self, obj):
        if obj.object_type == "event":
            return ["star_disabled", "star_enabled"][int(obj["promoted"])]
        else:
            return "folder_{}".format(obj["id_folder"])

class TagRundownStatus(TagFormat):
    tag = "rundown_status"
    def display(self, obj):
        try:
            return [
                "OFFLINE",
                "NOT SCHEDULED",
                "READY"
                ][obj[self.tag]]
        except:
            return ""

    def foreground(self, obj):
        return [NXColors[ASSET_FG_OFFLINE], 
                NXColors[ASSET_FG_OFFLINE], 
                DEFAULT_TEXT_COLOR
                ][int(obj[self.tag])]


class TagRundownScheduled(TagFormat):
    tag = "rundown_scheduled"
    def display(self, obj):
        return time.strftime("%H:%M", time.localtime(obj[self.tag]))

class TagRundownBroadcast(TagRundownScheduled):
    tag = "rundown_broadcast"



##########################################################################################

format_helpers_list = [
    TagFolder,
    TagDuration,
    TagFileSize,
    TagContentType,
    TagPromoted,
    TagRundownSymbol,
    TagRundownStatus,
    TagRundownScheduled,
    TagRundownBroadcast
    ]

format_helpers = {}
for h in format_helpers_list:
    helper = h()
    format_helpers[h.tag] = helper

##########################################################################################



class NXCellFormat():
    format_settings = {}

    def format_display(self, key):
        if key in format_helpers:
            return format_helpers[key].display(self)

        value = self[key]
        if not key in meta_types:
            return value

        if not value:
            return None

        mtype = meta_types[key]

        if mtype.class_ in [TEXT, BLOB]:         
            return shorten(value)

        elif mtype.class_ in [INTEGER, NUMERIC]:   
            return ["%.3f","%d"][float(value).is_integer()] % value if value else 0

        elif mtype.class_ == BOOLEAN:
             return None

        elif mtype.class_ == DATETIME:
            if "base_date" in self.format_settings:
                return time.strftime("%H:%M",time.localtime(value))
            else:
                return time.strftime("%Y-%m-%d %H:%M",time.localtime(value))

        elif mtype.class_ == TIMECODE:
            if self["video/fps"]:
                return s2tc(value,  fract2float(self["video/fps"]))
            else:
                return s2time(value)

        return value 


    def format_edit(self, key):
        if key in format_helpers:
            res = format_helpers[key].edit(self)
            if res:
                return res
        if key in meta_types and meta_types[key].editable:
            return key, meta_types[key].class_, meta_types[key].settings, self
        return key, "NOEDIT", False, self


    def format_decoration(self, key):
        if key in format_helpers:
            return format_helpers[key].decoration(self)
        return None


    def format_background(self, key, model=False):
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
        

    def format_foreground(self, key):
        if key in format_helpers:
            return format_helpers[key].foreground(self)       

        elif key == "title" and self.object_type == "asset":
            return NXColors[[ASSET_FG_OFFLINE, ASSET_FG_ONLINE, ASSET_FG_CREATING, ASSET_FG_TRASHED, ASSET_FG_RESET][self["status"]]]

        return DEFAULT_TEXT_COLOR


    def format_sort(self, key):
        return self[key]

