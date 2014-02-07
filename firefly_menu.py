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
    action_wnd_browser.triggered.connect(wnd.on_wnd_browser)
    menuWindow.addAction(action_wnd_browser)    

    action_wnd_detail = QAction('&Asset Detail', wnd)        
    action_wnd_detail.setShortcut('Ctrl+D')
    action_wnd_detail.setStatusTip('Open asset detail window')
    action_wnd_detail.triggered.connect(wnd.on_wnd_detail)
    menuWindow.addAction(action_wnd_detail)    

    menuWindow.addSeparator()

    action_wnd_rundown = QAction('&Rundown', wnd)        
    action_wnd_rundown.setShortcut('Ctrl+R')
    action_wnd_rundown.setStatusTip('Open rundown window')
    action_wnd_rundown.triggered.connect(wnd.on_wnd_rundown)
    menuWindow.addAction(action_wnd_rundown)    

    action_wnd_onair = QAction('&OnAir controls', wnd)        
    #action_wnd_onair.setShortcut('Ctrl+R')
    action_wnd_onair.setStatusTip('Open OnAir window')
    #action_wnd_onair.triggered.connect(wnd.on_wnd_rundown)
    menuWindow.addAction(action_wnd_onair)    



    menuWorkspace = menubar.addMenu('&Workspace')

    action_workspace_lock = QAction('&Lock', wnd)        
    action_workspace_lock.setShortcut('Ctrl+L')
    action_workspace_lock.setStatusTip('Lock workspace')
    action_workspace_lock.triggered.connect(wnd.on_workspace_lock)
    menuWorkspace.addAction(action_workspace_lock)   

    action_fullscreen = QAction('&Full screen', wnd)        
    action_fullscreen.setShortcut('F11')
    action_fullscreen.setStatusTip('Toggle fullscreen')
    action_fullscreen.triggered.connect(wnd.on_fullscreen)
    menuWorkspace.addAction(action_fullscreen)    