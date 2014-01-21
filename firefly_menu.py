from firefly_skin import *

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



    menuWindow = menubar.addMenu('&Window')

    action_wnd_browser = QAction('&Browser', wnd)        
    action_wnd_browser.setShortcut('Ctrl+T')
    action_wnd_browser.setStatusTip('Open new browser window')
    action_wnd_browser.triggered.connect(wnd.on_wnd_browser)
    menuWindow.addAction(action_wnd_browser)    

    action_wnd_rundown = QAction('&Rundown', wnd)        
    action_wnd_rundown.setShortcut('Ctrl+R')
    action_wnd_rundown.setStatusTip('Open new rundown window')
    action_wnd_rundown.triggered.connect(wnd.on_wnd_rundown)
    menuWindow.addAction(action_wnd_rundown)    

    action_wnd_detail = QAction('&Asset Detail', wnd)        
    action_wnd_detail.setShortcut('Ctrl+D')
    action_wnd_detail.setStatusTip('Open asset detail window')
    action_wnd_detail.triggered.connect(wnd.on_wnd_detail)
    menuWindow.addAction(action_wnd_detail)    