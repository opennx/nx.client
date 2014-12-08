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
        return None

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
        elif obj["id_folder"]:
            return "folder_{}".format(obj["id_folder"])
        elif obj["item_role"] == "lead_in":
            return "mark_in"
        elif obj["item_role"] == "lead_out":
            return "mark_out"

class TagRundownStatus(TagFormat):
    tag = "rundown_status"
    def display(self, obj):
        if obj.object_type != "item" :
            return ""

        if obj["rundown_transfer_progress"] and float(obj["rundown_transfer_progress"]) > -1:
            return "{:0.2f}%".format(float(obj["rundown_transfer_progress"]))

        return {
            -2 : "PART AIRED",
            -1 : "AIRED",
             0 : "OFFLINE",
             1 : "NOT SCHEDULED",
             2 : "READY"
        }.get(int(obj[self.tag]), "UNKNOWN")

    def foreground(self, obj):
        if obj["rundown_transfer_progress"] and int(obj["rundown_transfer_progress"]) > -1:
            return NXColors[ASSET_FG_CREATING]

        if obj.object_type == "item":
            return [NXColors[ASSET_FG_OFFLINE], 
                    NXColors[ASSET_FG_OFFLINE], 
                    DEFAULT_TEXT_COLOR
                    ][int(obj[self.tag])]
            


class TagRundownScheduled(TagFormat):
    tag = "rundown_scheduled"
    def display(self, obj):
        if obj[self.tag]:
            return time.strftime("%H:%M:%S", time.localtime(obj[self.tag]))

class TagRundownBroadcast(TagRundownScheduled):
    tag = "rundown_broadcast"


class TagRundownDifference(TagFormat):
    tag = "rundown_difference"
    def display(self, obj):
        if obj["rundown_broadcast"] and obj["rundown_scheduled"]:
            diff = obj["rundown_broadcast"] - obj["rundown_scheduled"]
            if -30 <= diff < 120:
                return None
            return s2time(abs(diff), show_fracs=False)

    def foreground(self, obj):
        if obj["rundown_broadcast"] and obj["rundown_scheduled"]:
            diff = obj["rundown_broadcast"] - obj["rundown_scheduled"]
            return ["#ff0000", "#00ff00"][diff >= 0]


class TagRunMode(TagFormat):
    tag = "run_mode"
    def display(self, obj):
        if obj[self.tag] == 1:
            return "MANUAL"
        if obj[self.tag] == 2:
            return "SOFT"
        elif obj[self.tag] == 3:
            return "HARD"
        return "AUTO"


class TagState(TagFormat):
    tag = "qc/state"
    def decoration(self, obj):
        return {
            0 : "qc_new",
            1 : "qc_failed",
            2 : "qc_passed",
            3 : "qc_rejected",
            4 : "qc_approved"
        }[int(obj.meta.get(self.tag, 0))]

    def foreground(self, obj):
        return {
            0 : None,
            1 : "#cc0000",
            2 : "#cccc00",
            3 : "#cc0000",
            4 : "#00cc00"
        }[int(obj.meta.get(self.tag, 0))]


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
    TagRundownBroadcast,
    TagRundownDifference,
    TagRunMode,
    TagState
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

        elif mtype.class_ in [CS_ENUM, CS_SELECT]:
            if not value:
                return ""
            cs = {key : val for key, val in config["cs"].get(mtype.settings, [])}
            label = cs.get(value, False)
            #value, label =  {key : val for key, val in cs } .get(value, ("No CS value",False))
            return label or value

        elif mtype.class_ == [ENUM, SELECT]:
            return value # FIXME
            #return mtype.settings.get()[1] or mtype.settings[0]

        return value 


    def format_edit(self, key):
        #if key in format_helpers:
        #    res = format_helpers[key].edit(self)
        #    if res:
        #        return res
        if key in meta_types:# and meta_types[key].editable:
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
            elif not self["id_asset"]:
                return "#121240"

        if self.object_type == "event" and self.model.parent().__class__.__name__ == "Rundown":
            return RUNDOWN_EVENT_BACKGROUND_COLOR
        return None
        

    def format_foreground(self, key):
        if key in format_helpers:
            val = format_helpers[key].foreground(self)       
            if val is not None:
                return val

        if self.object_type == "item" and self["rundown_status"] == -1:
            return "#404040"

        elif key == "title" and self.object_type == "asset":
            return NXColors[[ASSET_FG_OFFLINE, ASSET_FG_ONLINE, ASSET_FG_CREATING, ASSET_FG_TRASHED, ASSET_FG_ARCHIVED][self["status"]]]

        return DEFAULT_TEXT_COLOR


    def format_sort(self, key):
        return self[key]

