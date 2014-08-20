#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nx.common import *
from nx.common.metadata import meta_types, fract2float
from nx.connection import *

from nx.common.base_objects import BaseAsset, BaseItem, BaseBin, BaseEvent
from nx.common.utils import *

from nx.cellformat import NXCellFormat
from nx.colors import *

__all__ = ["Asset", "Item", "Bin", "Event", "Dummy"]


class Asset(BaseAsset, NXCellFormat):
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


class EmptyAsset():
    def __init__(self):
        self.meta = {}
    def __getitem__(self, key):
        return ""


class Item(BaseItem, NXCellFormat):
    def get_asset(self):
        if not self.asset:
            if self.meta.get("id_asset", 0) > 0:
                self.asset = Asset(self["id_asset"])
            else:
                self.asset = EmptyAsset()

        return self.asset


class Bin(BaseBin, NXCellFormat):
    pass

class Event(BaseEvent, NXCellFormat):
    pass