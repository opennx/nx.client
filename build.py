import subprocess
import time
import os

qrc = "<RCC>\n <qresource>\n"
for f in os.listdir("images"):
    qrc += "  <file>images/{}</file>\n".format(f)
qrc += " </qresource>\n</RCC>"

f = open(".firefly.qrc","w")
f.write(qrc)
f.close()

p = subprocess.Popen("""c:\Python33\Lib\site-packages\PyQt5\pyrcc5 .firefly.qrc -o firefly_rc.py""", shell=True)
while p.poll() == None:
    time.sleep(.1)



f = "Win32GUI"
f = "Console"

p = subprocess.Popen("""C:\\Python33\\Scripts\\cxfreeze.bat firefly.py --base-name=%s --icon=firefly.ico"""%f, shell=True)
while p.poll() == None:
    time.sleep(.1)
