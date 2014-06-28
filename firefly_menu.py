from functools import partial
from qt_common import *

def create_menu(wnd):
    menubar = wnd.menuBar()


    menuFile = menubar.addMenu('&File')

    action_new_asset = QAction('&New asset', wnd)        
    action_new_asset.setShortcut('Ctrl+N')
    action_new_asset.setStatusTip('Create new asset from template')
    action_new_asset.triggered.connect(wnd.on_new_asset)
    menuFile.addAction(action_new_asset)

    menuFile.addSeparator()

    action_dlg_system = QAction('&System manager', wnd)        
    action_dlg_system.setShortcut('Shift+ESC')
    action_dlg_system.setStatusTip('Open system manager')
    action_dlg_system.triggered.connect(wnd.on_dlg_system)
    menuFile.addAction(action_dlg_system)

    menuFile.addSeparator()

    action_logout = QAction('L&ogout', wnd)        
    action_logout.setStatusTip('Log out user')
    action_logout.triggered.connect(wnd.on_logout)
    menuFile.addAction(action_logout)

    action_exit = QAction('E&xit', wnd)        
    action_exit.setShortcut('Alt+F4')
    action_exit.setStatusTip('Quit Firefly NX')
    action_exit.triggered.connect(wnd.on_exit)
    menuFile.addAction(action_exit)
     


    menuEdit = menubar.addMenu('&Edit')

    action_debug = QAction('Debug', wnd)        
    action_debug.setShortcut('F9')
    action_debug.setStatusTip('Show debug dump')
    action_debug.triggered.connect(wnd.on_debug)
    menuEdit.addAction(action_debug)



    menuWindow = menubar.addMenu('&View')

    action_wnd_browser = QAction('&Browser', wnd)        
    action_wnd_browser.setShortcut('Ctrl+T')
    action_wnd_browser.setStatusTip('Open new browser window')
    action_wnd_browser.triggered.connect(partial(wnd.create_dock, widget_class="browser"))
    menuWindow.addAction(action_wnd_browser)    

    action_wnd_preview = QAction('&Preview', wnd)        
    action_wnd_preview.setShortcut('Ctrl+D')
    action_wnd_preview.setStatusTip('Open preview window')
    action_wnd_preview.triggered.connect(partial(wnd.create_dock, widget_class="preview", one_instance=True))
    menuWindow.addAction(action_wnd_preview)    

    action_wnd_scheduler = QAction('&Scheduler', wnd)        
    action_wnd_scheduler.setShortcut('F7')
    action_wnd_scheduler.setStatusTip('Open scheduler window')
    action_wnd_scheduler.triggered.connect(partial(wnd.create_dock, widget_class="scheduler", one_instance=True))
    menuWindow.addAction(action_wnd_scheduler)    

    action_wnd_rundown = QAction('&Rundown', wnd)        
    action_wnd_rundown.setShortcut('F8')
    action_wnd_rundown.setStatusTip('Open rundown window')
    action_wnd_rundown.triggered.connect(partial(wnd.create_dock, widget_class="rundown", one_instance=True))
    menuWindow.addAction(action_wnd_rundown)

    menuWindow.addSeparator()

    action_lock_workspace = QAction('&Lock workspace', wnd)        
    action_lock_workspace.setShortcut('Ctrl+L')
    action_lock_workspace.setStatusTip('Lock widgets position')
    action_lock_workspace.triggered.connect(wnd.on_lock_workspace)
    menuWindow.addAction(action_lock_workspace)


#    action_wnd_detail = QAction('&Asset Detail', wnd)        
#    action_wnd_detail.setShortcut('Ctrl+D')
#    action_wnd_detail.setStatusTip('Open asset detail window')
#    action_wnd_detail.triggered.connect(wnd.on_wnd_detail)
#    menuWindow.addAction(action_wnd_detail)