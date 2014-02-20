#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, unicode_literals

import sys

from firefly_common import *
from firefly_menu import create_menu
from firefly_starter import Firestarter

from mod_browser import Browser
from mod_rundown import Rundown
from mod_detail  import Detail


class Firefly(QMainWindow):
    def __init__(self, parent):
        super(Firefly, self).__init__()
        self.setWindowTitle("Firefly")
        self.setDockOptions(QMainWindow.AllowNestedDocks)
        self.setCentralWidget(None)
        create_menu(self)
        self.parent = parent
        self.status("")
        self.setStyleSheet(base_css)
        self.docks = []
        self.show()
        self.load_workspace()


    def load_workspace(self, workspace="default"):
        self.workspace = workspace
        settings = ffsettings()


        self.workspace_locked = settings.value("%s/locked" % workspace, False)

        if "%s/docks" % workspace in settings.allKeys():
            docks_data = json.loads(settings.value("%s/docks" % workspace))
            for dock_data in docks_data:
                widget = {"browser" : Browser, "rundown" : Rundown, "detail" : Detail}[dock_data["class"]]
                dock = BaseDock(self, dock_data["object_name"])
                dock.setState(widget, dock_data)
                self.docks.append(dock)

        if "%s/geometry" % workspace in settings.allKeys():
            self.restoreGeometry(settings.value("%s/geometry" % workspace))
        else:
            self.fake_maximize()

        if "%s/state" % workspace in settings.allKeys():
            self.restoreState(settings.value("%s/state" % workspace))

        if self.workspace_locked:
            self.on_workspace_lock(True)


    def save_workspace(self,workspace=False):
        if not workspace:
            workspace = self.workspace

        settings = ffsettings()
        docks = []
        for dock in self.docks:
            docks.append(dock.getState())

        settings.setValue("%s/locked"   % self.workspace, self.workspace_locked)
        settings.setValue("%s/docks"    % self.workspace, json.dumps(docks))
        settings.setValue("%s/state"    % self.workspace, self.saveState())
        settings.setValue("%s/geometry" % self.workspace, self.saveGeometry())



    def fake_maximize(self):
        geo = self.parent.desktop().availableGeometry()
        self.move(geo.topLeft())
        tw = geo.width()
        th = geo.height()
        fw = self.frameGeometry().width()
        fh = self.frameGeometry().height()
        tw -= fw - self.geometry().width()
        th -= fh - self.geometry().height()
        self.resize(tw, th)
            

    def changeEvent(self, evt):
        if self.isMaximized():
            self.showNormal()
            self.fake_maximize()


    def closeEvent(self, evt):
        self.save_workspace()
        evt.accept()


    def on_dock_closed(self, dock):
        for i,w in enumerate(self.docks):
            if w == dock:
                del (self.docks[i])


    def status(self, message, message_type=INFO):
        print(message)
        if message_type > DEBUG:
            self.statusBar().showMessage(message)


    ###############################################################################
    ## Global actions

    def on_wnd_browser(self):
        wnd = BaseDock(self)
        wnd.setState(Browser, {})
        self.docks.append(wnd)
        wnd.show()


    def on_wnd_rundown(self):
        wnd = BaseDock(self)
        wnd.setState(Rundown, {})
        self.docks.append(wnd)
        wnd.show()


    def on_wnd_detail(self):
        for d in self.docks: # Only one detail instance allowed
            if d.getState()["class"] == "detail":
                return
        wnd = BaseDock(self)
        wnd.setState(Detail, {})
        self.docks.append(wnd)
        wnd.show()

    def on_wnd_onair(self):
        pass


    def on_new_asset(self):
        pass


    def on_logout(self):
        pass


    def on_exit(self):
        self.close()


    def on_debug(self):
        self.load_workspace()


    def on_workspace_lock(self, force = False):
        if self.workspace_locked and not force:
            self.workspace_locked = False
            wdgt = BaseDock(self).titleBarWidget()
            for dock in self.docks:
                if not dock.isFloating():
                    dock.setTitleBarWidget(wdgt)
        else:
            for dock in self.docks:
                if not dock.isFloating():
                    dock.setTitleBarWidget(QWidget())
            self.workspace_locked = True


    def on_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()


    ## Global actions
    ###############################################################################
    ## SEISMIC


    def focus(self, objects):
        for d in self.docks:
            if d.getState()["class"] == "detail" and objects:
                d.main_widget.focus(objects)
        


    def handle_messaging(self, data):
        if data.method == "rundown_change":
            for dock in self.docks:
                if dock.getState()["class"] == "rundown":
                    if [dock.main_widget.id_channel, dock.main_widget.current_date] in data.data["rundowns"] and dock.objectName() != data.data["sender"]:
                        dock.main_widget.refresh()




if __name__ == "__main__":
    app = Firestarter(Firefly)
    app.start()