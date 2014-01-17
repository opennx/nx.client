from PySide.QtCore import *
from PySide.QtGui  import *


def format(color, style=''):
 _color = QColor()
 _color.setNamedColor(color)
 _format = QTextCharFormat()
 _format.setForeground(_color)
 if 'bold' in style:   _format.setFontWeight(QFont.Bold)
 if 'italic' in style: _format.setFontItalic(True)
 return _format

STYLES = {
    'keyword': format('orange','bold'),
    'operator': format('red'),
    'brace': format('gray'),
    'defclass': format('gray', 'bold'),
    'string': format('orange'),
    'string2': format('orange'),
    'comment': format('green', 'italic'),
    'pybang': format('green', 'italic'),
}

class PythonHL (QSyntaxHighlighter):
 keywords = ['and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'exec', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'print', 'raise', 'return', 'try', 'while', 'with', 'yield', 'True', 'False', 'None' ]
 operators = ['=','==', '!=', '<', '<=', '>', '>=','\+', '-', '\*', '/', '//', '\%', '\*\*','\+=', '-=', '\*=', '/=', '\%=','\^', '\|', '\&', '\~', '>>', '<<' ]
 braces = ['\{', '\}', '\(', '\)', '\[', '\]' ]
 def __init__(self, document):
  QSyntaxHighlighter.__init__(self, document)
  self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
  self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])
  rules = []
  rules += [(r'\b%s\b' % w, 0, STYLES['keyword']) for w in PythonHL.keywords]
  rules += [(r'%s' % o, 0, STYLES['operator'])    for o in PythonHL.operators]
  rules += [(r'%s' % b, 0, STYLES['brace'])       for b in PythonHL.braces]
  rules += [(r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']), (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']), (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']), (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']), (r'#[^\n]*', 0, STYLES['comment']), (r'#![^\n]*', 0, STYLES['pybang']) ]
  self.rules = [(QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]

 def highlightBlock(self, text):
  for expression, nth, format in self.rules:
   index = expression.indexIn(text, 0)
   while index >= 0:
    index = expression.pos(nth)
    length = len(expression.cap(nth))
    self.setFormat(index, length, format)
    index = expression.indexIn(text, index + length)
  self.setCurrentBlockState(0)
  in_multiline = self.match_multiline(text, *self.tri_single)
  if not in_multiline: in_multiline = self.match_multiline(text, *self.tri_double)


 def match_multiline(self, text, delimiter, in_state, style):
  if self.previousBlockState() == in_state:
   start = 0
   add = 0
  else:
   start = delimiter.indexIn(text)
   add = delimiter.matchedLength()
  while start >= 0:
   end = delimiter.indexIn(text, start + add)
   if end >= add:
    length = end - start + add + delimiter.matchedLength()
    self.setCurrentBlockState(0)
   else:
    self.setCurrentBlockState(in_state)
    length = len(text) - start + add
   self.setFormat(start, length, style)
   start = delimiter.indexIn(text, start + length)
  if self.currentBlockState() == in_state:  return True
  else: return False




