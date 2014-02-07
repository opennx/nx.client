 #!/usr/bin/env python
 # -*- coding: utf-8 -*-

from nx.common import *
from nx.common.nxobject import NXObject
from nx.common.metadata import meta_types

from nx.cellformat import NXCellFormat


class Item(NXObject, NXCellFormat):
    object_type = "item"

class Bin(NXObject, NXCellFormat):
    object_type = "bin"

class Event(NXObject, NXCellFormat):
    object_type = "event"