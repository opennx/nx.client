from PySide.QtCore import *
from PySide.QtGui  import *

base_css = """

QMainWindow, QDialog{
 background-color:#242424;
 color: #cccccc;
} 

QStatusBar{
 background-color:#242424;
 color: #cccccc;
} 


QToolBar{
 background-color:#242424;
 color: #cccccc;
} 

QTableView{
 background-color: #161616;
 border:0px;
 }  
 
QLineEdit{
 background-color: #161616;
 border:1px solid #646464;
 color: #d3d3d3;
 height: 24px;
}

QTextEdit{
 background-color: #161616;
 border:1px solid #646464;
 color: #d3d3d3;
}


QComboBox {
 background-color: #161616;
 border:1px solid #646464;
 color: #d3d3d3;
 height: 24px;
}

QComboBox::drop-down {
 border-width:1px;
}



QTableView {
 background-color: #1a1a1a;
 alternate-background-color: #242424;
 selection-background-color: rgba(160, 160, 160, 160);
 color : #f9f9f9; 
}




QLabel {
 color: #d3d3d3;
}


QHeaderView {
 background-color: #161616;
}

QHeaderView::section {
 background-color: #161616;
 color: #cccccc;
 font-weight: bold;
 border: 1px solid black;
 padding: 3px;
}


QTableCornerButton::section{
 background-color: #242424;

}



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
