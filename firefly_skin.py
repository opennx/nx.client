try:
    from PyQt5.QtCore import *
    from PyQt5.QtGui  import *

    from PyQt5.QtWidgets import QApplication, QSplashScreen, QMainWindow, QWidget, \
                                QTableView, QStyledItemDelegate, QAbstractItemView, \
                                QLineEdit, QComboBox, QDialog, QTabWidget, QAction, QDockWidget, QVBoxLayout, QHBoxLayout
except:
    from PySide.QtCore import *
    from PySide.QtGui  import *




base_css = """

QMainWindow, QDialog, QDockWidget, QLineEdit, QTextEdit, QComboBox, QLabel {
    background-color : #242424;
    color : #F8F8F2;
    } 

QStatusBar, QToolBar {
    background-color : #161616;
    color : #F8F8F2;
    }


QTableView {
    border : 0;
    background-color: #1a1a1a;
    alternate-background-color: #242424;
    selection-background-color: rgba(160, 160, 160, 160);
    color : #c0c0c0; 
    }


QLineEdit, QTextEdit, QComboBox {
    border : 1px solid #646464;
    }

QLineEdit, QComboBox {
    height: 24px;
    }

QComboBox::drop-down {
    border-width:1px;
    }



QLabel {
    color: #c0c0c0;
    }




QHeaderView {
    background-color: #161616;
    }

QHeaderView::section {
    background-color: #161616;
    color: #c0c0c0;
    font-weight: bold;
    border: 1px solid black;
    padding: 3px;
    }

QTableCornerButton::section{
    background-color: #242424;
    }


/**********************************************************************/


QTabWidget {
    border : 0;
    }

 QTabWidget::pane { /* The tab widget frame */
    border-top: 0;
    padding-bottom: 3px;
    }

 QTabWidget::tab-bar {
    left: 5px; /* move to the right by 5px */
    color : #c0c0c0; 
    }

 QTabBar::tab {
    background: #161616;
    color : #c0c0c0; 
    /*font-weight: bold;*/

    border: 1px solid #242424;
    border-bottom-color: #161616;
    padding : 6px;
    min-width: 12ex;
    }

 QTabBar::tab:selected, QTabBar::tab:hover {
    background: #161616;
    color : #f0f0f0; 
    }

 QTabBar::tab:selected {
    border-bottom: 2px solid #729fcf;
    }

/*
QTabBar::close-button {
    image: url(close.png)
    subcontrol-position: left;
    }
QTabBar::close-button:hover {
    image: url(close-hover.png)
    }
*/


/**********************************************************************/

QScrollBar:horizontal {
    border: 2px solid #242424;
    background: #161616;
    height: 15px;
    margin:0;
    }

QScrollBar:vertical {
    margin:0;
    margin-top: 23px;
    border: 2px solid #242424;
    background: #161616;
    width: 15px;
    }

QScrollBar::handle:horizontal {
    background: gray;
    min-width: 15px;
    }

QScrollBar::handle:vertical {
    background: gray;
    min-height: 15 px;
 }
 
QScrollBar::add-line:horizontal, QScrollBar::add-line:vertical { background: none; }
QScrollBar::sub-line:horizontal, QScrollBar::sub-line:vertical { background: none; }
QScrollBar:left-arrow:horizontal, QScrollBar::right-arrow:horizontal,QScrollBar:left-arrow:vertical, QScrollBar::right-arrow:vertical { background: none; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal,QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }


QPushButton{
    color: #8EB0C1;
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #505050,  stop: 1 #404040);
    border:1px solid #646464;
    width: 45px;
    height: 24px;
    font-size: 12px;
    }

QPushButton:hover{
    color : #fff;
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #505050,  stop: 1 #545454);
    }
"""
