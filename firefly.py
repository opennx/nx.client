#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, '')

import sys

from firefly_common import *
from firefly_menu import create_menu
from firefly_starter import Firestarter

from mod_browser import Browser
from mod_rundown import Rundown
from mod_detail import Detail
from mod_scheduler import Scheduler

from dlg_system import SystemDialog

class Firefly(QMainWindow):
    def __init__(self, parent):
        super(Firefly, self).__init__()
        settings = ffsettings()
        workspace = settings.value("global/current_workspace", "default")
        workspaces =  list(set(k.split("/")[0] for k in settings.allKeys() if k.split("/")[0] not in ["global", "docks"]))
        self.setDockOptions(QMainWindow.AllowNestedDocks)
        self.setCentralWidget(None)
        create_menu(self, workspaces=workspaces)
        self.parent = parent
        self.status("")
        self.setStyleSheet(base_css)
        self.docks = []
        self.sys_dlg = None
        self.load_workspace(workspace)
        self.show()
        
    def on_close_all(self):
        for dock in self.docks:
            dock.close()

    def load_workspace(self, workspace="default"):
        self.on_close_all()
        self.docks = []
        self.workspace = workspace 
        settings = ffsettings()

        self.workspace_locked = settings.value("%s/locked" % workspace, False)

        if "{}/docks".format(workspace) in settings.allKeys() and settings.value("{}/docks".format(workspace)):
            for object_name in settings.value("{}/docks".format(workspace)):
                dock_data = settings.value("docks/{}".format(object_name))
                widget =   {"browser" : Browser, 
                            "rundown" : Rundown, 
                            "detail" : Detail,
                            "scheduler" : Scheduler,
                            }[dock_data["class"]]

                dock = BaseDock(self, object_name)
                dock.load_state(widget, dock_data)
                self.docks.append(dock)
 
        if "%s/geometry" % workspace in settings.allKeys():
            self.restoreGeometry(settings.value("%s/geometry" % workspace))
        else:
            self.fake_maximize()

        if "%s/state" % workspace in settings.allKeys():
            self.restoreState(settings.value("%s/state" % workspace))

        if self.workspace_locked:
            self.on_workspace_lock(True)
        
        for dock in self.docks:
            dock.show()
        self.setWindowTitle("Firefly - {}".format(self.workspace))


    def on_save_workspace(self):
        self.save_workspace(True)


    def on_save_workspace_as(self):
        text, ok = QInputDialog.getText(self, 'Save workspace',  'Enter workspace name')
        if (not ok) or (text in ["global", "docks"]):
            QMessageBox.error(self, "Error", "Unable to save workspace")
            return
        for dock in self.docks:
            dock.reset_object_name()
        self.save_workspace(full=True, workspace=text)


    def save_workspace(self, full=False, workspace=False):
        if workspace:
            self.workspace = workspace

        settings = ffsettings()

        for dock in self.docks:
            dock.save(settings)

        settings.setValue("global/current_workspace", self.workspace)

        if full:
            settings.setValue("{}/docks".format(self.workspace)    , [str(dock.objectName()) for dock in self.docks if dock.isVisible()])
            settings.setValue("{}/locked".format(self.workspace)   , self.workspace_locked)
            settings.setValue("{}/state".format(self.workspace)    , self.saveState())
            settings.setValue("{}/geometry".format(self.workspace) , self.saveGeometry())

        



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
        pass

    def on_dock_destroyed(self):
        for i, dock in enumerate(self.docks):
            try:
                a = dock.objectName()
            except:
                del(self.docks[i])
        

    def status(self, message, message_type=INFO):
        if message:
            print(message)
        if message_type > DEBUG:
            self.statusBar().showMessage(message)


    ###############################################################################
    ## Global actions

    def on_wnd_browser(self):
        wnd = BaseDock(self)
        wnd.load_state(Browser, {})
        self.docks.append(wnd)
        wnd.show()
        if self.workspace_locked:
            wnd.setAllowedAreas(Qt.NoDockWidgetArea)

    def on_wnd_rundown(self):
        wnd = BaseDock(self)
        wnd.load_state(Rundown, {})
        self.docks.append(wnd)
        wnd.show()
        if self.workspace_locked:
            wnd.setAllowedAreas(Qt.NoDockWidgetArea)

    def on_wnd_scheduler(self):
        wnd = BaseDock(self)
        wnd.load_state(Scheduler, {})
        self.docks.append(wnd)
        wnd.show()
        if self.workspace_locked:
            wnd.setAllowedAreas(Qt.NoDockWidgetArea)


    def on_wnd_detail(self):
        for d in self.docks: # Only one detail instance allowed
            if d.class_ == "detail":
                return
        wnd = BaseDock(self)
        wnd.load_state(Detail, {})
        self.docks.append(wnd)
        wnd.show()
        if self.workspace_locked:
            wnd.setAllowedAreas(Qt.NoDockWidgetArea)



    def on_dlg_system(self):
        self.sys_dlg = SystemDialog(self)
        self.sys_dlg.exec_()
        self.sys_dlg.save_state()
        self.sys_dlg = None


    def on_new_asset(self):
        pass


    def on_logout(self):
        pass


    def on_exit(self):
        self.close()


    def on_debug(self):
        for dock in self.docks:
            print (dock.class_)


    def on_workspace_lock(self, force = False):
        if self.workspace_locked and not force:
            self.workspace_locked = False
            wdgt = BaseDock(self).titleBarWidget()
            for dock in self.docks:
                if dock.isFloating(): 
                    dock.setAllowedAreas(Qt.AllDockWidgetAreas)
                else:
                    dock.setTitleBarWidget(wdgt)
        else:
            for dock in self.docks:
                if dock.isFloating():
                    dock.setAllowedAreas(Qt.NoDockWidgetArea)
                else:
                    dock.setTitleBarWidget(QWidget())
            self.workspace_locked = True


    def on_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()


    def focus(self, objects):
        for d in self.docks:
            if d.class_ == "detail" and objects:
                d.main_widget.focus(objects)
        

    ## Global actions
    ###############################################################################
    ## SEISMIC


    def handle_messaging(self, data):
        if data.method == "playout_status":
            for dock in self.docks:
                if dock.class_ == "rundown" and data.data["id_channel"] == dock.main_widget.id_channel:
                    dock.main_widget.update_status(data)

        elif data.method == "hive_heartbeat":
            if self.sys_dlg:
                self.sys_dlg.update_status(data)


        elif data.method == "rundown_change":
            for dock in self.docks:
                if dock.class_ == "rundown":
                    if [dock.main_widget.id_channel, dock.main_widget.current_date] in data.data["rundowns"] and dock.objectName() != data.data["sender"]:
                        dock.main_widget.refresh()






if __name__ == "__main__":
    app = Firestarter(Firefly)
    app.start()
