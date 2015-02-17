import time
import datetime

from functools import partial

from firefly_common import *
from firefly_view import *

from mod_rundown_onair import OnAir
from mod_rundown_cg import CG
from mod_rundown_model import RundownModel

from dlg_sendto import SendTo
from dlg_event import EventDialog


DEFAULT_COLUMNS = [
    "rundown_symbol",
    "title",
    "identifier/main",
    "duration",
    "run_mode",
    "rundown_scheduled",
    "rundown_broadcast",
    "rundown_difference",
    "rundown_status",
    "mark_in",
    "mark_out",
    "id_asset",
    "id_object"
    ]


ITEM_BUTTONS = [
    {
        "icon"      : "placeholder",
        "title"     : "Placeholder",
        "tooltip"   : "Drag this to rundown to create placeholder",
        "item_role" : "placeholder",
    },

    {
        "icon"      : "talking_head",
        "title"     : "Studio",
        "tooltip"   : "Drag this to rundown to create studio placeholder",
        "item_role" : "studio",
    },

    {
        "icon"      : "mark_in",
        "title"     : "Lead-in",
        "tooltip"   : "Drag this to rundown to create Lead-in",
        "item_role" : "lead_in",
    },

    {
        "icon"      : "mark_out",
        "title"     : "Lead-out",
        "tooltip"   : "Drag this to rundown to create Lead-out",
        "item_role" : "lead_out",
    }

    ]


def get_date():
    class CalendarDialog(QDialog):
        def __init__(self):
            super(CalendarDialog, self).__init__()
            self.setWindowTitle('Calendar')
            self.date = False, False, False
            self.setModal(True)
            self.calendar = QCalendarWidget(self)
            self.calendar.setGridVisible(True)
            self.calendar.setFirstDayOfWeek(1)
            self.calendar.activated[QDate].connect(self.setDate)
            layout = QVBoxLayout()
            layout.addWidget(self.calendar)
            self.setLayout(layout)
            self.show()

        def setDate(self, date):
            self.date = (date.year(), date.month(), date.day())
            self.close()

    cal = CalendarDialog()
    cal.exec_()
    return cal.date



def day_start(ts, start):
    hh, mm = start
    r =  ts - (hh*3600 + mm*60)
    dt = datetime.datetime.fromtimestamp(r).replace(
        hour = hh,
        minute = mm,
        second = 0
        )
    return time.mktime(dt.timetuple())


class RundownDate(QLabel):
    pass

class ItemButton(QToolButton):
    def __init__(self, parent, config):
        super(ItemButton, self).__init__()
        self.button_config = config
        self.pressed.connect(self.startDrag)
        self.setIcon(QIcon(pixlib[self.button_config["icon"]]))
        self.setToolTip(self.button_config["tooltip"])

    def startDrag(self):
        item_data = [{
            "title" : self.button_config["title"],
            "item_role" : self.button_config["item_role"]
            }]
        drag = QDrag(self);
        mimeData = QMimeData()
        mimeData.setData(
           "application/nx.item",
           json.dumps(item_data)
           )
        drag.setMimeData(mimeData)
        if drag.exec_(Qt.CopyAction):
            pass # nejak to rozumne ukonc

def rundown_toolbar(wnd):

    action_find = QAction('Search rundown', wnd)
    action_find.setShortcut('Ctrl+F')
    action_find.triggered.connect(wnd.on_find)
    wnd.addAction(action_find)

    action_find_next = QAction('Search rundown', wnd)
    action_find_next.setShortcut('F3')
    action_find_next.triggered.connect(wnd.on_find_next)
    wnd.addAction(action_find_next)

    toolbar = QToolBar(wnd)

    action_day_prev = QAction(QIcon(pixlib["back"]), '&Previous day', wnd)
    action_day_prev.setShortcut('Alt+Left')
    action_day_prev.setStatusTip('Go to previous day')
    action_day_prev.triggered.connect(wnd.on_day_prev)
    toolbar.addAction(action_day_prev)

    action_now = QAction(QIcon(pixlib["now"]), '&Now', wnd)
    action_now.setStatusTip('Go to now')
    action_now.triggered.connect(wnd.on_now)
    toolbar.addAction(action_now)

    action_calendar = QAction(QIcon(pixlib["calendar"]), '&Calendar', wnd)
    action_calendar.setShortcut('Ctrl+D')
    action_calendar.setStatusTip('Open calendar')
    action_calendar.triggered.connect(wnd.on_calendar)
    toolbar.addAction(action_calendar)

    action_refresh = QAction(QIcon(pixlib["refresh"]), '&Refresh', wnd)
    action_refresh.setStatusTip('Refresh rundown')
    action_refresh.triggered.connect(wnd.refresh)
    toolbar.addAction(action_refresh)

    action_day_next = QAction(QIcon(pixlib["next"]), '&Next day', wnd)
    action_day_next.setShortcut('Alt+Right')
    action_day_next.setStatusTip('Go to next day')
    action_day_next.triggered.connect(wnd.on_day_next)
    toolbar.addAction(action_day_next)

    toolbar.addSeparator()

    action_toggle_mcr = QAction(QIcon(pixlib["onair"]), '&Playout controls', wnd)
    action_toggle_mcr.setStatusTip('Toggle playout controls')
    action_toggle_mcr.triggered.connect(wnd.on_toggle_mcr)
    toolbar.addAction(action_toggle_mcr)

    action_toggle_cg = QAction(QIcon(pixlib["cg"]), '&CG controls', wnd)
    action_toggle_cg.setShortcut('F4')
    action_toggle_cg.setStatusTip('Toggle CG controls')
    action_toggle_cg.triggered.connect(wnd.on_toggle_cg)
    toolbar.addAction(action_toggle_cg)


    action_toggle_tools = QAction(QIcon(pixlib["tools"]), '&Rundown tools', wnd)
    action_toggle_tools.setStatusTip('Toggle rundown tools')
    action_toggle_tools.triggered.connect(wnd.on_toggle_tools)
    toolbar.addAction(action_toggle_tools)

    toolbar.addWidget(ToolBarStretcher(wnd))

    wnd.date_display = RundownDate()
    toolbar.addWidget(wnd.date_display)

    return toolbar



def items_toolbar(wnd):
    toolbar = QToolBar(wnd)
    for btn_config in ITEM_BUTTONS:
        toolbar.addWidget(ItemButton(wnd, btn_config))
    return toolbar


class RundownView(NXView):
    def __init__(self, parent):
        super(RundownView, self).__init__(parent)
        self.delegate = MetaEditItemDelegate(self)
        self.setItemDelegate(self.delegate)

        self.activated.connect(self.on_activate)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)


    def selectionChanged(self, selected, deselected):
        rows = []
        self.selected_objects = []
        tot_dur = 0

        for idx in self.selectionModel().selectedIndexes():
            row = idx.row()
            if row in rows:
                continue
            rows.append(row)
            obj = self.model().object_data[row]
            self.selected_objects.append(obj)
            if obj.object_type in ["asset", "item"]:
                tot_dur += obj.get_duration()

        if self.selected_objects and self.focus_enabled:
            self.parent().parent().parent().focus(self.selected_objects)
            if len(self.selected_objects) == 1 and self.selected_objects[0].object_type == "item" and self.selected_objects[0]["id_asset"]:
                asset = self.selected_objects[0].asset
                times = len([obj for obj in self.model().object_data if obj.object_type == "item" and obj["id_asset"] == asset.id])
                self.parent().status("{} is scheduled {}x in this rundown".format(asset, times))
            if len(self.selected_objects) > 1 and tot_dur:
                self.parent().status("{} objects selected. Total duration {}".format(len(self.selected_objects), s2time(tot_dur) ))

        super(NXView, self).selectionChanged(selected, deselected)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.on_delete()
        NXView.keyPressEvent(self, event)


    ###################################################
    ## Rundown actions

    def contextMenuEvent(self, event):
        obj_set = list(set([itm.object_type for itm in self.selected_objects]))
        menu = QMenu(self)

        if len(obj_set) > 0:

            action_focus = QAction('&Focus', self)
            action_focus.setStatusTip('Focus selected object')
            action_focus.triggered.connect(self.on_focus)
            menu.addAction(action_focus)

            menu.addSeparator()


        if len(obj_set) == 1:
            if obj_set[0] == "item" and self.selected_objects[0]["id_asset"]:

                mode_menu = menu.addMenu("Run mode")

                action_mode_auto = QAction('&Auto', self)
                action_mode_auto.setStatusTip('Set run mode to auto')
                action_mode_auto.triggered.connect(partial(self.on_set_mode, 0))
                mode_menu.addAction(action_mode_auto)

                action_mode_manual = QAction('&Manual', self)
                action_mode_manual.setStatusTip('Set run mode to manual')
                action_mode_manual.triggered.connect(partial(self.on_set_mode, 1))
                mode_menu.addAction(action_mode_manual)

            elif obj_set[0] == "event" and len(self.selected_objects) == 1:
                print (self.selected_objects[0]["run_mode"])

                mode_menu = menu.addMenu("Run mode")

                action_mode_auto = QAction('&Auto', self)
                action_mode_auto.setStatusTip('Set run mode to auto')
                action_mode_auto.setCheckable(True)
                action_mode_auto.setChecked(self.selected_objects[0]["run_mode"] == 0)
                action_mode_auto.triggered.connect(partial(self.on_set_mode, 0))
                mode_menu.addAction(action_mode_auto)

                action_mode_manual = QAction('&Manual', self)
                action_mode_manual.setStatusTip('Set run mode to manual')
                action_mode_manual.setCheckable(True)
                action_mode_manual.setChecked(self.selected_objects[0]["run_mode"] == 1)
                action_mode_manual.triggered.connect(partial(self.on_set_mode, 1))
                mode_menu.addAction(action_mode_manual)

                action_mode_soft = QAction('&Soft', self)
                action_mode_soft.setStatusTip('Set run mode to soft')
                action_mode_soft.setCheckable(True)
                action_mode_soft.setChecked(self.selected_objects[0]["run_mode"] == 2)
                action_mode_soft.triggered.connect(partial(self.on_set_mode, 2))
                mode_menu.addAction(action_mode_soft)

                action_mode_hard = QAction('&Hard', self)
                action_mode_hard.setStatusTip('Set run mode to hard')
                action_mode_hard.setCheckable(True)
                action_mode_hard.setChecked(self.selected_objects[0]["run_mode"] == 3)
                action_mode_hard.triggered.connect(partial(self.on_set_mode, 3))
                mode_menu.addAction(action_mode_hard)


        if "item" in obj_set:
            action_send_to = QAction('&Send to...', self)
            action_send_to.setStatusTip('Create action for selected asset(s)')
            action_send_to.triggered.connect(self.on_send_to)
            menu.addAction(action_send_to)


        if "event" in obj_set:
            action_solve = QAction('Solve', self)
            action_solve.setStatusTip('Solve selected event')
            action_solve.triggered.connect(self.on_solve_event)
            menu.addAction(action_solve)




        if len(obj_set) > 0:
            menu.addSeparator()

            action_delete = QAction('&Delete', self)
            action_delete.setStatusTip('Delete selected object')
            action_delete.triggered.connect(self.on_delete)
            menu.addAction(action_delete)

            if len(obj_set) == 1 and "event" in obj_set:
                action_edit = QAction('&Edit', self)
                action_edit.setStatusTip('Edit selected event')
                action_edit.triggered.connect(self.on_edit_event)
                menu.addAction(action_edit)

        menu.addSeparator()

        action_columns = QAction('Choose columns', self)
        action_columns.setStatusTip('Choose header columns')
        action_columns.triggered.connect(self.on_choose_columns)
        menu.addAction(action_columns)

        menu.exec_(event.globalPos())


    def on_set_mode(self, mode):
        if not self.parent().can_edit:
            QMessageBox.warning(self, "Error", "You are not allowed to modify this rundown")
            return
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        stat, res = query("set_meta", object_type=self.selected_objects[0].object_type, objects=[obj.id for obj in self.selected_objects], data={"run_mode":mode})
        QApplication.restoreOverrideCursor()
        if not success(stat):
            QMessageBox.critical(self, "Error", res)
        self.parent().refresh()
        self.selectionModel().clear()
        return

    def on_focus(self):
        pass

    def on_delete(self):

        items = list(set([obj.id for obj in self.selected_objects if obj.object_type == "item"]))
        events  = list(set([obj.id for obj in self.selected_objects if obj.object_type == "event"]))

        if items and not self.parent().can_edit:
            QMessageBox.warning(self, "Error", "You are not allowed to modify this rundown items")
            return
        elif events and not self.parent().can_schedule:
            QMessageBox.warning(self, "Error", "You are not allowed to modify this rundown blocks")
            return


        if events or len(items) > 10:
            ret = QMessageBox.question(self,
                "Delete",
                "Do you REALLY want to delete {} items and {} events?\nThis operation CANNOT be undone".format(len(items), len(events)),
                QMessageBox.Yes | QMessageBox.No
                )

            if ret != QMessageBox.Yes:
                return

        if items:
            QApplication.processEvents()
            QApplication.setOverrideCursor(Qt.WaitCursor)
            stat, res = query("del_items", items=items)
            QApplication.restoreOverrideCursor()
            if success(stat):
                self.parent().status("Delete item: {}".format(res))
            else:
                QMessageBox.critical(self, "Error", res)

        if events:
            QApplication.processEvents()
            QApplication.setOverrideCursor(Qt.WaitCursor)
            print ("DEL", events)
            stat, res = query("set_events", delete=events)
            QApplication.restoreOverrideCursor()
            if success(stat):
                self.parent().status("Delete event: {}".format(res))
            else:
                QMessageBox.critical(self, "Error", res)

        self.parent().refresh()
        self.selectionModel().clear()


    def on_send_to(self):
        objs = set([obj for obj in self.selected_objects if obj.object_type == "item"])
        if not objs:
            QMessageBox.warning(self, "Warning", "No rundown item selected")
            return
        dlg = SendTo(self, objs)
        dlg.exec_()


    def on_edit_event(self):
        objs = [obj for obj in self.selected_objects if obj.object_type == "event"]
        dlg = EventDialog(self, event=objs[0])
        if dlg.exec_() == QDialog.Accepted:
            self.refresh()


    def on_solve_event(self):
        if not self.parent().can_edit:
            QMessageBox.warning(self, QMessageBox.warning, "Error", "You are not allowed to modify this rundown")
            return

        ret = QMessageBox.question(self,
            "Solve event",
            "Do you really want to (re)solve {}?\nThis operation cannot be undone.".format(self.selected_objects[0]),
            QMessageBox.Yes | QMessageBox.No
            )

        if ret == QMessageBox.Yes:
            QApplication.processEvents()
            QApplication.setOverrideCursor(Qt.WaitCursor)
            stat, res = query("dramatica",
                handler=self.parent().handle_message,
                id_channel=self.parent().id_channel,
                date=time.strftime("%Y-%m-%d", time.localtime(self.parent().start_time)),
                id_event =self.selected_objects[0].id,
                solve=True
                )
            QApplication.restoreOverrideCursor()
            if not success(stat):
                QMessageBox.critical(self, "Error", res)
            self.parent().refresh()


    def on_choose_columns(self):
        pass
        #TODO




    def on_activate(self, mi):
        self.parent().on_activate(mi)








class Rundown(BaseWidget):
    def __init__(self, parent):
        super(Rundown, self).__init__(parent)
        self.id_channel   = self.parent().parent().id_channel
        self.playout_config = config["playout_channels"][self.id_channel]

        self.current_item = False
        self.cued_item = False

        self.last_search = ""

        self.view  = RundownView(self)
        self.model = RundownModel(self)

        self.view.setModel(self.model)

        self.mcr = OnAir(self)
        self.cg = CG(self)

        toolbar = rundown_toolbar(self)
        self.items_toolbar = items_toolbar(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(2)
        layout.addWidget(toolbar, 0)
        layout.addWidget(self.items_toolbar, 0)
        layout.addWidget(self.mcr)
        layout.addWidget(self.cg)
        layout.addWidget(self.view, 1)

        self.setLayout(layout)

        self.start_time = day_start (time.time(), self.playout_config["day_start"])
        self.update_header()

    @property
    def can_edit(self):
        return has_right("rundown_edit", self.id_channel)

    @property
    def can_schedule(self):
        return has_right("scheduler_edit", self.id_channel)


    def save_state(self):
        state = {}
        state["c"] = self.model.header_data
        state["cw"] = self.view.horizontalHeader().saveState()
        state["mcr"] = self.mcr.isVisible()
        state["cg"] = self.cg.isVisible()
        state["items_toolbar"] = self.items_toolbar.isVisible()
        return state

    def load_state(self, state):
        self.model.header_data = state.get("c", False) or DEFAULT_COLUMNS
        self.id_channel = state.get("id_channel", min(config["playout_channels"].keys()))
        self.load(self.id_channel, self.start_time)

        cw = state.get("cw", False)
        if cw:
            self.view.horizontalHeader().restoreState(cw)
        else:
            for id_column in range(self.model.columnCount(False)):
                self.view.resizeColumnToContents(id_column)

        if state.get("mcr", False) and has_right("mcr", self.id_channel):
            self.mcr.show()
        else:
            self.mcr.hide()

        if state.get("cg", False) and has_right("cg", self.id_channel):
            self.cg.show()
        else:
            self.cg.hide()


        if state.get("items_toolbar", False):
            self.items_toolbar.show()
        else:
            self.items_toolbar.hide()

    def seismic_handler(self, data):
        if data.method == "playout_status":
            if data.data["id_channel"] != self.id_channel:
                return

            if data.data["current_item"] != self.current_item:
                self.current_item = data.data["current_item"]
                self.model.refresh_items([self.current_item])

            if data.data["cued_item"] != self.cued_item:
                self.cued_item = data.data["cued_item"]
                self.refresh()

            if self.mcr:
                self.mcr.seismic_handler(data)

        elif data.method == "job_progress":
            if data.data["id_action"] == config["playout_channels"][self.id_channel].get("send_action", False):
                for i, obj in enumerate(self.model.object_data):
                    if obj["id_asset"] == data.data["id_object"]:
                        if data.data["progress"] == COMPLETED:
                            obj["rundown_status"] = 2
                            obj["rundown_transfer_progress"] = COMPLETED
                        else:
                            obj["rundown_transfer_progress"] = data.data["progress"]
                        self.model.dataChanged.emit(self.model.index(i, 0), self.model.index(i, len(self.model.header_data)-1))
                        self.update()

        elif data.method == "objects_changed" and data.data["object_type"] == "event":
            my_name = self.parent().objectName()

            for id_event in data.data["objects"]:#
                if data.data.get("sender", False) != my_name and id_event in self.model.event_ids :
                    self.refresh()
                    break

    ###########################################################################

    def load(self, id_channel, start_time, event=False):
        self.id_channel = id_channel
        self.start_time = start_time
        self.update_header()
        self.model.load(id_channel, start_time)
        if not event:
            return

        for i, r in enumerate(self.model.object_data):
            if event.id == r.id and r.object_type=="event":
                self.view.scrollTo(self.model.index(i, 0, QModelIndex()), QAbstractItemView.PositionAtTop  )
                break

    def refresh(self):
        selection = []
        for idx in self.view.selectionModel().selectedIndexes():
            if self.model.object_data[idx.row()].id:
                selection.append([self.model.object_data[idx.row()].object_type, self.model.object_data[idx.row()].id])

        self.load(self.id_channel, self.start_time)

        item_selection = QItemSelection()
        for i, row in enumerate(self.model.object_data):
            if [row.object_type, row.id] in selection:
               i1 = self.model.index(i, 0, QModelIndex())
               i2 = self.model.index(i, len(self.model.header_data)-1, QModelIndex())
               item_selection.select(i1,i2)
        self.view.focus_enabled = False
        self.view.selectionModel().select(item_selection, QItemSelectionModel.ClearAndSelect)
        self.view.focus_enabled = True

    def update_header(self):
        t = datetime.date.fromtimestamp(self.start_time)

        if t < datetime.date.today():
            s = " color='red'"
        elif t > datetime.date.today():
            s = " color='green'"
        else:
            s = ""

        t = t.strftime("%A %Y-%m-%d")
        self.parent().setWindowTitle("Rundown {}".format(t))
        self.date_display.setText("<font{}>{}</font>".format(s, t))


    ################################################################
    ## Toolbar actions

    def set_channel(self, id_channel):
        if self.id_channel != id_channel:
            self.id_channel = id_channel
            self.refresh()
            if self.cg:
                self.cg.load_plugins(id_channel)

            if self.mcr:
                can_mcr = has_right("mcr", self.id_channel)
                self.mcr.btn_take.setEnabled(can_mcr)
                self.mcr.btn_freeze.setEnabled(can_mcr)
                self.mcr.btn_retake.setEnabled(can_mcr)
                self.mcr.btn_abort.setEnabled(can_mcr)


    def set_date(self, start_time):
        self.start_time = start_time
        self.update_header()
        self.load(self.id_channel, self.start_time)

    def on_day_prev(self):
        self.set_date(self.start_time - (3600*24))

    def on_day_next(self):
        self.set_date(self.start_time + (3600*24))

    def on_now(self):
        if not (self.start_time+86400 > time.time() > self.start_time):
            self.set_date(day_start (time.time(), self.playout_config["day_start"]))

        for i,r in enumerate(self.model.object_data):
            if self.current_item == r.id and r.object_type=="item":
                self.view.scrollTo(self.model.index(i, 0, QModelIndex()), QAbstractItemView.PositionAtTop  )
                break


    def on_calendar(self):
        y, m, d = get_date()
        if not y:
            return
        hh, mm = self.playout_config["day_start"]
        dt = datetime.datetime(y,m,d,hh,mm)
        self.set_date(time.mktime(dt.timetuple()))


    def on_toggle_mcr(self):
        if self.mcr:
            if self.mcr.isVisible():
                self.mcr.hide()
            else:
                self.mcr.show()


    def on_toggle_cg(self):
        if self.cg and has_right("cg", self.id_channel):
            if self.cg.isVisible():
                self.cg.hide()
            else:
                self.cg.show()


    def on_toggle_tools(self):
        if self.items_toolbar.isVisible():
            self.items_toolbar.hide()
        else:
            self.items_toolbar.show()


    def on_activate(self, mi):
        obj = self.model.object_data[mi.row()]
        can_mcr = has_right("mcr", self.id_channel)
        if obj.object_type == "item" and self.mcr and self.mcr.isVisible() and can_mcr:
            stat, res = query("cue", self.mcr.route, id_channel=self.id_channel, id_item=obj.id)
            if not success(stat):
                QMessageBox.critical(self, "Error", res)
            self.view.clearSelection()
        elif obj.object_type == "event" and has_right("scheduler_edit", self.id_channel):
            if self.model.header_data[mi.column()] == "rundown_symbol":
                obj["promoted"] = not obj["promoted"]
                stat, res = query("set_events",
                    id_channel=obj["id_channel"],
                    events=[obj.meta]
                    )
                self.refresh()
            else:
                self.view.on_edit_event()


    def on_find(self):
        text, result = QInputDialog.getText(self, "Rundown search", "Enter your blabla:", text=self.last_search)
        if result and text:
            self.do_find(text)
        else:
            self.last_search = ""

    def on_find_next(self):
        if self.last_search:
            self.do_find(self.last_search)
        else:
            self.on_find()

    def do_find(self, search_string, start_row=-1):
        self.last_search = search_string
        search_string = search_string.lower()

        if start_row == -1:
            for idx in self.view.selectionModel().selectedIndexes():
                if idx.row() > start_row:
                    start_row = idx.row()

        start_row += 1

        for i, row in enumerate(self.model.object_data[start_row:]):
            for key in ["title", "identifier/main"]:
                if str(row[key]).lower().find(search_string) > -1:
                    selection = QItemSelection()
                    i1 = self.model.index(i + start_row, 0, QModelIndex())
                    i2 = self.model.index(i + start_row, len(self.model.header_data)-1, QModelIndex())
                    self.view.scrollTo(i1 , QAbstractItemView.PositionAtTop  )
                    selection.select(i1, i2)
                    self.view.selectionModel().select(selection, QItemSelectionModel.ClearAndSelect)
                    break
            else:
                continue
            break
        else:
            self.status("Not found: {}".format(self.last_search))
            self.view.clearSelection()


    ## Toolbar actions
    ################################################################

    def handle_message(self, msg):
        self.status(msg.get("message",""))
        QApplication.processEvents()
