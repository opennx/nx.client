from skin   import *
from nebula_utils  import *
from time import *
from syntaxhl import *



class NTimeCode(QLineEdit):
 def __init__(self, parent, default=0):
  super(NTimeCode,self).__init__(parent)
  self.setInputMask("99:99:99.99")
  if default:  self.SetSeconds(default)
  else:        self.setText("00:00:00.00")
  self.setCursorPosition(0)
  self.default = default
  
 def SetSeconds(self,seconds):
  try:    self.setText(s2time(seconds))
  except: self.setText("00:00:00.00")

 def GetSeconds(self):
  try:
   hh,mm,ss = self.text().split(":")
   hh = int(hh)
   mm = int(mm)
   ss = float(ss)
   secs = (hh*3600) + (mm*60) + ss
  except:
   secs = self.default
  return secs



class NDateTime(QLineEdit):
 def __init__(self, parent, default=0):
  super(NDateTime,self).__init__(parent)
  self.setInputMask("9999-99-99 99:99:99")
  self.SetTimestamp(default)
  self.default = default
  
 def SetTimestamp(self, timestamp):
  if timestamp: self.setText (strftime("%Y-%m-%d %H:%M:%S",localtime(timestamp)))
  else:         self.setText (strftime("%Y-%m-%d %H:%M:%S"))
  
 def GetTimestamp(self):
  try:
   t = strptime (self.text(), "%Y-%m-%d %H:%M:%S")
   return mktime(t)
  except:
   print "Wrong time format"
   return self.default


class NDate(QLineEdit):
 def __init__(self, parent, default=0):
  super(NDate,self).__init__(parent)
  self.setInputMask("9999-99-99")
  self.SetTimestamp(default)
  self.default = default
  
 def SetTimestamp(self, timestamp):
  if timestamp: self.setText (strftime("%Y-%m-%d",localtime(timestamp)))
  else:         self.setText (strftime("%Y-%m-%d"))
  
 def GetTimestamp(self):
  try:
   t = strptime (self.text(), "%Y-%m-%d")
   return mktime(t)
  except:
   print "Wrong time format"
   return self.default



class NOption(QComboBox):
 def __init__(self, parent, data, default=False):
  super(NOption,self).__init__(parent)
  self.SetData(data,default)
  self.default = default
  
 def SetData(self, data, default=False):
  self.cdata = []
  for i,j in enumerate(sorted(data)):
   self.addItem(data[j])
   self.cdata.append(j)
   if default == j: self.setCurrentIndex(i)   
  if not default:
   self.setCurrentIndex(0)

 def GetValue(self):
  return self.cdata[self.currentIndex()]





class wndTextEdit(QDialog):    
 def __init__(self, index, default,syntax=False):
  super(wndTextEdit, self).__init__()
  self.setWindowTitle('Text editor: Press ESC to discard, Alt+F4 to Save and close')
  self.setModal(True)
  self.setStyleSheet(base_css)
  
  self.edit = QTextEdit(self)
  if syntax == "python": hl = PythonHL(self.edit)
  self.edit.setStyleSheet("font: 9pt \"Courier\";")
  
  self.default = default
  self.setText(default)
  
  self.index = index
  
  layout = QVBoxLayout()
  layout.addWidget(self.edit)
  
  self.setLayout(layout)
  self.resize(640,640)
  self.show()
  self.raise_()
  self.edit.activateWindow()
  self.edit.setFocus()
    
 def closeEvent(self,evt):
  print self.index.model().setData(self.index,self.toPlainText())
    
 def setText(self,text):
  self.edit.setText(text)

 def toPlainText(self):
  return self.edit.toPlainText()



########################################################################


class NItemDelegate(QStyledItemDelegate):
 def __init__(self, parent = None):
  super(NItemDelegate, self).__init__(parent)
  self.parent = parent

 def createEditor(self, parent, styleOption, index):
  self.parent.is_editing = True  
  try:col,method,default_value = index.model().data(index, Qt.EditRole)
  except: return None
  
  if default_value == "None": default_value = ""
  
  if method == "datetime":
   editor = NDateTime(parent)
   if not default_value: editor.default = int(time())
   else: editor.default = int(default_value)
   editor.editingFinished.connect(self.commitAndCloseEditor)
   
  elif method == "date":
   editor = NDate(parent)
   if not default_value: editor.default = int(time())
   else: editor.default = int(default_value)
   editor.editingFinished.connect(self.commitAndCloseEditor)
  
  elif method == "clock":
   editor = QLineEdit(parent)
   editor.setInputMask("99:99")
   editor.default = strftime("%H:%M",localtime(default_value))
   editor.editingFinished.connect(self.commitAndCloseEditor)
   
  elif method[0] == "option":
   editor = NOption(parent,method[1],default_value)
   
  elif method == "text":
   editor = QLineEdit(parent)
   editor.default = default_value
   editor.editingFinished.connect(self.commitAndCloseEditor)
   
  elif method == "blob":
   self.parent.text_editor = wndTextEdit(index, default_value)
   return None
  
  elif method[0] == "script":
   self.parent.text_editor = wndTextEdit(index, default_value,method[1])
   return None

  else:
   editor = None
  return editor

 #######################################################################
 
 def commitAndCloseEditor(self):
  editor = self.sender()
  self.commitData.emit(editor)
  self.closeEditor.emit(editor, QAbstractItemDelegate.NoHint)
  self.parent.is_editing = False
  self.parent.editor_closed_at = time()

 #######################################################################
 
 def setEditorData(self, editor, index):
  if isinstance(editor,NDateTime) or isinstance(editor, NDate):
   editor.SetTimestamp(editor.default)
 
  elif isinstance(editor, QLineEdit) or isinstance(editor, QTextEdit) or isinstance(editor, wndTextEdit):
   editor.setText(editor.default)

 #######################################################################
 
 def setModelData(self, editor, model, index):
  if isinstance(editor,NDateTime) or isinstance(editor,NDate):
   val = editor.GetTimestamp()
   if val != editor.default: 
    model.setData(index, val)
    
  elif isinstance(editor, QLineEdit):
   if editor.text() != editor.default: 
    model.setData(index, editor.text())
    
  elif isinstance(editor, QTextEdit) or isinstance(editor, wndTextEdit):
   if editor.toPlainText() != editor.default:
    model.setData(index, editor.toPlainText()) 
     
  elif isinstance(editor, NOption):
   if editor.GetValue() != editor.default: 
    model.setData(index, editor.GetValue()) 
    
  elif editor == "boolean":
   model.setData(index, str(int(not bool(int(model.data(index,Qt.DisplayRole)))))) 
