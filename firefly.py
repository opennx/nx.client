#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, unicode_literals

from firefly_common import *
from firefly_menu import create_menu

from mod_browser import Browser
from mod_rundown import Rundown
from mod_detail import Detail


class Firefly(QMainWindow):
    def __init__(self, parent):
        super(Firefly, self).__init__()
        self.setWindowTitle("Firefly NX")
        self.setStyleSheet(base_css)
        self.setDockOptions(QMainWindow.AllowNestedDocks)
        self.setCentralWidget(None)
 
        create_menu(self)

        self.status("Ready")

        self.windows = []
        self.show()
        self.load_workspace()
        


    def load_workspace(self, workspace="default"):
        for i,w in enumerate(self.windows):
            w.close()
            w.destroy()
            del (self.windows[i])

        self.workspace = workspace
        settings = ffsettings()

        if "%s/windows" % workspace in settings.allKeys():
            windows = json.loads(settings.value("%s/windows" % workspace))
            if windows:
                for window in windows:
                    widg = {"browser" : Browser, "rundown" : Rundown, "detail" : Detail}[window["window_class"]]
                    wnd = BaseDock(self, window["object_name"])
                    wnd.setState(widg, window)
                    self.windows.append(wnd)


        for w in self.windows:
            w.show()

        if "%s/geometry" % workspace in settings.allKeys():
            self.restoreGeometry(settings.value("%s/geometry" % workspace))
        else:
            self.resize(800,600)
            self.setWindowState(Qt.WindowMaximized)

        if "%s/state" % workspace in settings.allKeys():
            self.restoreState(settings.value("%s/state" % workspace))

 

    def closeEvent(self, evt):
        settings = ffsettings()

        windows = []
        for window in self.windows:
            windows.append(window.getState())

        settings.setValue("%s/windows" % self.workspace, json.dumps(windows))
        settings.setValue("%s/state" % self.workspace, self.saveState())
        settings.setValue("%s/geometry" % self.workspace, self.saveGeometry())

        for window in self.windows:
            window.close()

        evt.accept()

    def status(self, msg):
        self.statusBar().showMessage(msg)

    def on_window_closed(self, wnd):
        for i,w in enumerate(self.windows):
            if w == wnd:
                del (self.windows[i])

    ###############################################################################
    ## Global actions

    def on_wnd_browser(self):
        wnd = BaseDock(self)
        wnd.setState(Browser, {})
        self.windows.append(wnd)
        wnd.show()

    def on_wnd_rundown(self):
        wnd = BaseDock(self)
        wnd.setState(Rundown, {})
        self.windows.append(wnd)
        wnd.show()

    def on_wnd_detail(self):
        for w in self.windows: # Only one detail instance allowed
            if w.getState()["window_class"] == "detail":
                return

        wnd = BaseDock(self)
        wnd.setState(Rundown, {})
        self.windows.append(wnd)
        wnd.show()


    def on_new_asset(self):
        pass

    def on_logout(self):
        pass

    def on_exit(self):
        self.close()


    def on_debug(self):
        self.load_workspace()



if __name__ == "__main__":
    app = Firestarter()
    wnd = Firefly(app)
    app.start()