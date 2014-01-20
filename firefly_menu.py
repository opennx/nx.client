from firefly_skin import *

def create_menu(wnd):
    menubar = wnd.menuBar()
    
    menuFile = menubar.addMenu('&File')

    action_new_browser = QAction('&New browser', wnd)        
    action_new_browser.setShortcut('Ctrl+N')
    action_new_browser.setStatusTip('Open new browser window')
    #action_quit.triggered.connect(wnd.on_new_browser)
    menuFile.addAction(action_new_browser)
    
    

    menuFile.addSeparator()

    action_logout = QAction('L&ogout', wnd)        
    action_logout.setStatusTip('Log out user')
    #action_quit.triggered.connect(wnd.on_logout)
    menuFile.addAction(action_logout)

    action_exit = QAction('E&xit', wnd)        
    action_exit.setShortcut('Alt+F4')
    action_exit.setStatusTip('Quit Firefly NX')
    #action_quit.triggered.connect(wnd.on_quit)
    menuFile.addAction(action_exit)
     

    menuEdit = menubar.addMenu('&Edit')
    
    