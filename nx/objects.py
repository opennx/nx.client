#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nx.common import *

from nx.common.nxobject import NXObject, AssetBase
from nx.common.metadata import meta_types, fract2float
from nx.common.utils import *

from nx.connection import *

from nx.cellformat import NXCellFormat, super_tags
from nx.colors import *

__all__ = ["Asset", "Item", "Bin", "Event", "Dummy"]


class Asset(NXObject, AssetBase, NXCellFormat):
    def format_foreground(self,key):
        if key == "title":
            return NXColors[[ASSET_FG_OFFLINE, ASSET_FG_ONLINE, ASSET_FG_CREATING, ASSET_FG_TRASHED, ASSET_FG_RESET][self["status"]]]
        return DEFAULT_TEXT_COLOR
        

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


class Dummy(NXCellFormat):
    object_type = "dummy"
    id = False
    def __init__(self, title=""):
        self.meta = {"title":title}
    def __getitem__(self, key):
        return self.meta.get(key,"")
    def __setitem__(self, key, value):
        self.meta[key] = value


class Item(NXObject, NXCellFormat):
    object_type = "item"
    asset = False
    def __getitem__(self, key):
        key = key.lower().strip()
        if key == "id_object":
            return self.id
        if not key in self.meta:
            if self.get_asset():
                return self.get_asset()[key]
            else:
                return False
        return self.meta[key]

    def get_asset(self):
        if (not self.asset) and self["id_asset"]:
            self.asset = Asset(self["id_asset"])
        return self.asset


class Bin(NXObject, NXCellFormat):
    object_type = "bin"

class Event(NXObject, NXCellFormat):
    object_type = "event"