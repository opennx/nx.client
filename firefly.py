#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, '')

import sys
from pprint import pprint

from version_info import VERSION_INFO

from firefly_common import *
from firefly_menu import create_menu
from firefly_starter import Firestarter

from dlg_system import SystemDialog

from mod_browser import Browser
from mod_preview import Preview
from mod_detail import Detail
from mod_rundown import Rundown
from mod_scheduler import Scheduler

from nx.objects import Asset

class Firefly(QMainWindow):
    def __init__(self, parent):
        super(Firefly, self).__init__()
        self.setWindowTitle("{} - {}".format(config["site_name"], VERSION_INFO))
        self.setWindowIcon(QIcon(":/images/firefly.ico"))
        self.parent = parent

        self.subscribers = {}
        self.docks = []
        
        create_menu(self)
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.North)
        self.setDockNestingEnabled(True)
        self.setStyleSheet(base_css)

        settings = ffsettings() 

        self.on_change_channel(1) # todo: Load default from settings
        self.workspace_locked = settings.value("main_window/locked", False)

        for dock_key in settings.allKeys():
            if not dock_key.startswith("docks/"):
                continue
            dock_data = settings.value(dock_key)
            parent.splash_message("Loading {} {}".format(dock_data["class"], dock_data["object_name"]))
            self.create_dock(dock_data["class"], state=dock_data, show=False)

        if settings.contains("main_window/pos"):
            self.move(settings.value("main_window/pos")) 

        if settings.contains("main_window/size"):
            self.resize(settings.value("main_window/size"))
            self.size_helper = self.size()

        if settings.contains("main_window/state"):
            self.restoreState(settings.value("main_window/state"))

        if self.workspace_locked:
            self.lock_workspace()
        else:
            self.unlock_workspace()

        if not settings.contains("main_window/pos") or (settings.contains("main_window/maximized") and int(settings.value("main_window/maximized"))):
            self.showMaximized()
        else:
            self.show()

        for dock in self.docks:                
            dock.show()

        self.status("Ready")

            

    def resizeEvent(self, evt):
        if not self.isMaximized():
            self.size_helper = evt.size()
    

    def create_dock(self, widget_class, state={}, show=True, one_instance=False):
        widget = {
                "browser"   : Browser,
                "scheduler" : Scheduler,
                "rundown"   : Rundown,
                "preview"   : Preview,
                "detail"    : Detail
                }[widget_class]

        create = True
        if one_instance:
            for dock in self.docks:
                if dock.class_ == widget_class:                
                    if dock.class_ == "detail":
                        if dock.hasFocus():
                            dock.main_widget.switch_tabs()
                        else:
                            dock.main_widget.switch_tabs(0)
                    dock.raise_()
                    dock.setFocus()
                    return dock

        # Create new dock
        QApplication.processEvents()
        QApplication.setOverrideCursor(Qt.WaitCursor)

        self.docks.append(BaseDock(self, widget, state))
        if self.workspace_locked:
            self.docks[-1].setAllowedAreas(Qt.NoDockWidgetArea)
        else:
            self.docks[-1].setAllowedAreas(Qt.AllDockWidgetAreas)
        if show:
            self.docks[-1].setFloating(True)
            self.docks[-1].show()

        qr = self.docks[-1].frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.docks[-1].move(qr.topLeft())

        # populate dock with asset data from cache
        self.push_asset_data(self.docks[-1])

        QApplication.restoreOverrideCursor()
        return self.docks[-1]



    def lock_workspace(self):
        for dock in self.docks:
            if dock.isFloating():
                dock.setAllowedAreas(Qt.NoDockWidgetArea)
            else:
                dock.setTitleBarWidget(QWidget())
        self.workspace_locked = True
          
    def unlock_workspace(self):
        wdgt = QDockWidget().titleBarWidget()
        for dock in self.docks:
            dock.setAllowedAreas(Qt.AllDockWidgetAreas)
            if not dock.isFloating():
                dock.setTitleBarWidget(wdgt)
        self.workspace_locked = False

    def status(self, message, message_type=INFO):
        if message_type > DEBUG:
            self.statusBar().showMessage(message)


    def closeEvent(self, event):
        settings = ffsettings() 
 
        settings.remove("main_window")
        settings.setValue("main_window/state", self.saveState())

        settings.setValue("main_window/pos", self.pos())
        settings.setValue("main_window/size", self.size_helper)
        settings.setValue("main_window/maximized", int(self.isMaximized()))
        settings.setValue("main_window/locked", int(self.workspace_locked))

        settings.remove("docks")
        for dock in self.docks:
            dock.save()

    def on_dock_destroyed(self):
        for i, dock in enumerate(self.docks):
            try:
                a = dock.objectName()
            except:
                del(self.docks[i])

    def focus(self, objects):
        for d in self.docks:
            if d.class_ in ["preview", "detail", "scheduler"] and objects:
                d.main_widget.focus(objects)

    def focus_rundown(self, id_channel, date):
        dock = self.create_dock("rundown", state={}, show=True, one_instance=True)
        dock.main_widget.load(id_channel, date)

    def on_search(self):
        for d in self.docks:
            if d.class_ == "browser":
                d.main_widget.search_box.setFocus()
                d.main_widget.search_box.selectAll()

    def on_now(self):
        dock = self.create_dock("rundown", state={}, show=True, one_instance=True)
        dock.main_widget.on_now()

    ###############################################################################
    ## Menu actions
    ## FILE

    def on_new_asset(self):
        dock = self.create_dock("detail", state={}, show=True, one_instance=True)
        dock.main_widget.new_asset()

    def on_dlg_system(self):
        self.sys_dlg = SystemDialog(self)
        self.sys_dlg.exec_()

    def on_logout(self):
        pass

    def on_exit(self):
        self.close()

    ## EDIT
    def on_debug(self):
        for subscriber in self.subscribers:
            print (subscriber, " --> ", self.subscribers[subscriber]) 

    ## VIEW
    def on_wnd_browser(self):
        self.create_dock("browser")

    def on_wnd_preview(self):
        self.create_dock("preview", one_instance=True)

    def on_wnd_scheduler(self):
        self.create_dock("scheduler", one_instance=True)

    def on_wnd_rundown(self):
        self.create_dock("rundown", one_instance=True)


    def on_lock_workspace(self):
        if self.workspace_locked:
            self.unlock_workspace()
        else:
            self.lock_workspace()

    def on_refresh(self):
        for dock in self.docks:
            dock.main_widget.refresh()

    def on_change_channel(self, id_channel):
        self.id_channel = id_channel
        for action in self.menu_channel.actions():
            if action.id_channel == id_channel:
                action.setChecked(True)
        for d in self.docks:
            if d.class_ in ["rundown", "scheduler"]:
                d.main_widget.set_channel



    ## Menu actions
    ###############################################################################
    ## SEISMIC

    def subscribe(self, handler, *methods):
        self.subscribers[handler] = methods

    def unsubscribe(self, handler):
        del self.subscribers[handler]

    def handle_messaging(self, data):
        if data.method == "objects_changed" and data.data["object_type"] == "asset": 
            aids = [aid for aid in data.data["objects"] if aid in asset_cache.keys()]
            if not aids:
                return
            self.status ("{} has been changed by {}".format(asset_cache[aids[0]], data.data.get("user", "anonymous"))  )
            self.update_assets(aids)

        for subscriber in self.subscribers:
            if data.method in self.subscribers[subscriber]:
                subscriber(data)

    ## SEISMIC
    ###############################################################################
    ## Asset caching

    def update_assets(self, asset_ids=[]):
        # Call this if you want to update asset cache
        res, adata = query("get_assets", handler=self.update_assets_handler , asset_ids=asset_ids )
        for dock in self.docks:
            self.push_asset_data(dock)
 
    def update_assets_handler(self, data):
        # Handler for asset data comming from get_assets query
        a = Asset(from_data=data)
        asset_cache[a.id] = a

    def push_asset_data(self, dock):
        # Push all cached data to newly created docks
        if dock.class_ in ["rundown", "browser"]:
            dock.main_widget.model.refresh_assets(asset_cache.keys())



if __name__ == "__main__":
    app = Firestarter(Firefly)
    app.start() 