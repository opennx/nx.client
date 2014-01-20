#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nx.common import *

from nx.common.nxobject import NXObject, AssetBase
from nx.common.metadata import meta_types, fract2float
from nx.common.utils import *

from nx.connection import *

from nx.colors import *

__all__ = ["Asset"]


class Asset(NXObject, AssetBase):

    def format_display(self, key):
        if not key in self.meta: 
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
        elif mtype.class_ == DATETIME:             return time.strftime("%Y-%m-%d %H:%M",time.localtime(value))
        elif mtype.class_ == FILESIZE:
            for x in ['bytes','KB','MB','GB','TB']:
                if value < 1024.0: return "%3.1f %s" % (value, x)
                value /= 1024.0
        else: return "E %s" %value 


    def format_foreground(self,key):
        if key == "title":
            return NXColors[[ASSET_FG_OFFLINE, ASSET_FG_ONLINE, ASSET_FG_CREATING, ASSET_FG_TRASHED, ASSET_FG_RESET][self["status"]]]
        return "#c0c0c0"

    def format_edit(self, key):
        if key in meta_types and meta_types[key].editable:
            return key, meta_types[key].class_, meta_types[key].settings, self[key]
        else:
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

        return value
        
        if mtype.class_   in [INTEGER, NUMERIC, DATE, TIME, DATETIME, DURATION, STATUS, STATE, FILESIZE, PART, BOOLEAN, STAR]: return value #FIXME
        elif mtype.class_ in [TEXT, BLOB]: return value
        elif mtype.class_ in [SELECT, ISELECT, LIST, COMBO, FOLDER]: return unaccent(self.format_display(key))
        
        return ""


    def format_decoration(self, key):
        if key == "content_type":
            return ["text", "video-camera", "volume-up", "picture-o"][self[key]]

        return None