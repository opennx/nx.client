from firefly_common import config, has_right
from functools import partial
from qt_common import *


def about_dialog(parent):
    QMessageBox.about(parent, "About Firefly",
    "Firefly is free software; "
    "you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; "
    "either version 3 of the License, or (at your option) any later version.\n\n"
#    "For more information visit project homepage at http://opennx.eu"
    )


def create_menu(wnd):
    menubar = wnd.menuBar()

    menu_file = menubar.addMenu('&File')
    action_new_asset = QAction('&New asset', wnd)
    action_new_asset.setShortcut('Ctrl+N')
    action_new_asset.setStatusTip('Create new asset from template')
    action_new_asset.triggered.connect(wnd.on_new_asset)
    if not has_right("asset_create"):
        action_new_asset.setEnabled(False)
    menu_file.addAction(action_new_asset)

    action_clone_asset = QAction('&Clone asset', wnd)
    action_clone_asset.setShortcut('Ctrl+Shift+N')
    action_clone_asset.setStatusTip('Create new asset from current blabla')
    action_clone_asset.triggered.connect(wnd.on_clone_asset)
    if not has_right("asset_create"):
        action_clone_asset.setEnabled(False)
    menu_file.addAction(action_clone_asset)


    menu_file.addSeparator()

    action_dlg_system = QAction('&System manager', wnd)
    action_dlg_system.setShortcut('Shift+ESC')
    action_dlg_system.setStatusTip('Open system manager')
    action_dlg_system.triggered.connect(wnd.on_dlg_system)
    if not has_right("service_control"):
        action_dlg_system.setEnabled(False)
    menu_file.addAction(action_dlg_system)

    action_send_message = QAction('Send &message', wnd)
    action_send_message.setStatusTip('Send message to other users')
    action_send_message.triggered.connect(wnd.on_send_message)
    menu_file.addAction(action_send_message)

    menu_file.addSeparator()

    action_logout = QAction('L&ogout', wnd)
    action_logout.setStatusTip('Log out user')
    action_logout.triggered.connect(wnd.on_logout)
    menu_file.addAction(action_logout)

    action_exit = QAction('E&xit', wnd)
    action_exit.setShortcut('Alt+F4')
    action_exit.setStatusTip('Quit Firefly NX')
    action_exit.triggered.connect(wnd.on_exit)
    menu_file.addAction(action_exit)



    menu_navigate = menubar.addMenu('&Navigate')

    action_search = QAction('Search assets', wnd)
    action_search.setShortcut('ESC')
    action_search.setStatusTip('Focus asset search bar')
    action_search.triggered.connect(wnd.on_search)
    menu_navigate.addAction(action_search)

    action_now = QAction('Now', wnd)
    action_now.setShortcut('F1')
    action_now.setStatusTip('Open current position in rundown')
    action_now.triggered.connect(wnd.on_now)
    if not (has_right("rundown_view") or has_right("rundown_edit")):
        action_now.setEnabled(False)
    menu_navigate.addAction(action_now)



    wnd.menu_channel = menubar.addMenu('&Channel')
    ag = QActionGroup(wnd, exclusive=True)

    for id_channel in sorted(config["playout_channels"]):
        a = ag.addAction(QAction(config["playout_channels"][id_channel]["title"], wnd, checkable=True))
        a.id_channel = id_channel
        a.triggered.connect(partial(wnd.on_change_channel, id_channel))
        wnd.menu_channel.addAction(a)


    menu_window = menubar.addMenu('&Window')

    action_wnd_browser = QAction('&Browser', wnd)
    action_wnd_browser.setShortcut('Ctrl+T')
    action_wnd_browser.setStatusTip('Open new browser window')
    action_wnd_browser.triggered.connect(partial(wnd.create_dock, widget_class="browser"))
    menu_window.addAction(action_wnd_browser)

    action_wnd_preview = QAction('&Preview', wnd)
    action_wnd_preview.setStatusTip('Open preview window')
    action_wnd_preview.triggered.connect(partial(wnd.create_dock, widget_class="preview", one_instance=True))
    menu_window.addAction(action_wnd_preview)

    action_wnd_detail = QAction('&Object detail', wnd)
    action_wnd_detail.setShortcut('F8')
    action_wnd_detail.setStatusTip('Open detail/editor window')
    action_wnd_detail.triggered.connect(partial(wnd.create_dock, widget_class="detail", one_instance=True))
    menu_window.addAction(action_wnd_detail)

    action_wnd_scheduler = QAction('&Scheduler', wnd)
    action_wnd_scheduler.setShortcut('F7')
    action_wnd_scheduler.setStatusTip('Open scheduler window')
    action_wnd_scheduler.triggered.connect(partial(wnd.create_dock, widget_class="scheduler", one_instance=True))
    if not (has_right("scheduler_view") or has_right("scheduler_edit")):
        action_wnd_scheduler.setEnabled(False)
    menu_window.addAction(action_wnd_scheduler)


    action_wnd_rundown = QAction('&Rundown', wnd)
    action_wnd_rundown.setStatusTip('Open rundown window')
    action_wnd_rundown.triggered.connect(partial(wnd.create_dock, widget_class="rundown", one_instance=True))
    if not (has_right("rundown_view") or has_right("rundown_edit")):
        action_wnd_rundown.setEnabled(False)
    menu_window.addAction(action_wnd_rundown)

    menu_window.addSeparator()

    action_refresh = QAction('&Refresh', wnd)
    action_refresh.setShortcut('F5')
    action_refresh.setStatusTip('Refresh views')
    action_refresh.triggered.connect(wnd.on_refresh)
    menu_window.addAction(action_refresh)

    action_lock_workspace = QAction('&Lock workspace', wnd)
    action_lock_workspace.setShortcut('Ctrl+L')
    action_lock_workspace.setStatusTip('Lock widgets position')
    action_lock_workspace.triggered.connect(wnd.on_lock_workspace)
    menu_window.addAction(action_lock_workspace)

    menu_help = menubar.addMenu('Help')
    action_about = QAction('&About', wnd)
    action_about.setStatusTip('About Firefly')
    action_about.triggered.connect(partial(about_dialog, wnd))
    menu_help.addAction(action_about)
