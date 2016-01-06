import subprocess
import time
import os

def build():
    qrc = "<RCC>\n <qresource>\n"
    for f in os.listdir("images"):
        qrc += "  <file>images/{}</file>\n".format(f)
    qrc += " </qresource>\n</RCC>"

    f = open(".firefly.qrc","w")
    f.write(qrc)
    f.close()

    p = subprocess.Popen("""c:\Python34\Lib\site-packages\PyQt5\pyrcc5 .firefly.qrc -o firefly_rc.py""", shell=True)
    while p.poll() == None:
        time.sleep(.1)

    #f = "Win32GUI"
    f = "Console"

    p = subprocess.Popen("""python C:\\Python34\\Scripts\\cxfreeze firefly.py --base-name=%s --icon=firefly.ico"""%f, shell=True)
    while p.poll() == None:
        time.sleep(.1)

build()



import zipfile

FILE_LIST = [
    ("dist/_bz2.pyd", "_bz2.pyd"),
    ("dist/_ctypes.pyd", "_ctypes.pyd"),
    ("dist/_elementtree.pyd", "_elementtree.pyd"),
    ("dist/_hashlib.pyd", "_hashlib.pyd"),
    ("dist/_lzma.pyd", "_lzma.pyd"),
    ("dist/_socket.pyd", "_socket.pyd"),
    ("dist/_ssl.pyd", "_ssl.pyd"),
    ("dist/firefly.exe", "firefly.exe"),
    ("dist/icudt49.dll", "icudt49.dll"),
    ("dist/icuin49.dll", "icuin49.dll"),
    ("dist/icuuc49.dll", "icuuc49.dll"),
    ("dist/imageformats", "imageformats"),
    ("dist/LIBEAY32.dll", "LIBEAY32.dll"),
    ("dist/libGLESv2.dll", "libGLESv2.dll"),
    ("dist/mediaservice", "mediaservice"),
    ("dist/platforms", "platforms"),
    ("dist/pyexpat.pyd", "pyexpat.pyd"),
    ("dist/PyQt5.QtCore.pyd", "PyQt5.QtCore.pyd"),
    ("dist/PyQt5.QtGui.pyd", "PyQt5.QtGui.pyd"),
    ("dist/PyQt5.QtMultimedia.pyd", "PyQt5.QtMultimedia.pyd"),
    ("dist/PyQt5.QtMultimediaWidgets.pyd", "PyQt5.QtMultimediaWidgets.pyd"),
    ("dist/PyQt5.QtNetwork.pyd", "PyQt5.QtNetwork.pyd"),
    ("dist/PyQt5.QtWidgets.pyd", "PyQt5.QtWidgets.pyd"),
    ("dist/python34.dll", "python34.dll"),
    ("dist/Qt5Core.dll", "Qt5Core.dll"),
    ("dist/Qt5Gui.dll", "Qt5Gui.dll"),
    ("dist/Qt5Multimedia.dll", "Qt5Multimedia.dll"),
    ("dist/Qt5MultimediaWidgets.dll", "Qt5MultimediaWidgets.dll"),
    ("dist/Qt5Network.dll", "Qt5Network.dll"),
    ("dist/Qt5OpenGL.dll", "Qt5OpenGL.dll"),
    ("dist/Qt5Widgets.dll", "Qt5Widgets.dll"),
    ("dist/select.pyd", "select.pyd"),
    ("dist/sip.pyd", "sip.pyd"),
    ("dist/skin.css", "skin.css"),
    ("dist/SSLEAY32.dll", "SSLEAY32.dll"),
    ("dist/unicodedata.pyd", "unicodedata.pyd"),

    ("dist/imageformats/qgif.dll", "imageformats/qgif.dll"),
    ("dist/imageformats/qico.dll", "imageformats/qico.dll"),
    ("dist/imageformats/qjpeg.dll", "imageformats/qjpeg.dll"),
    ("dist/imageformats/qmng.dll", "imageformats/qmng.dll"),
    ("dist/imageformats/qsvg.dll", "imageformats/qsvg.dll"),
    ("dist/imageformats/qtga.dll", "imageformats/qtga.dll"),
    ("dist/imageformats/qtiff.dll", "imageformats/qtiff.dll"),
    ("dist/imageformats/qwbmp.dll", "imageformats/qwbmp.dll"),

    ("dist/mediaservice/dsengine.dll", "mediaservice/dsengine.dll"),
    ("dist/mediaservice/qtmedia_audioengine.dll", "mediaservice/qtmedia_audioengine.dll"),
    ("dist/mediaservice/wmfengine.dll", "mediaservice/wmfengine.dll"),

    ("dist/platforms/qminimal.dll", "platforms/qminimal.dll"),
    ("dist/platforms/qoffscreen.dll", "platforms/qoffscreen.dll"),
    ("dist/platforms/qwindows.dll", "platforms/qwindows.dll"),

    ("local_settings.default", "local_settings.json")
    ]


with zipfile.ZipFile('firefly-latest.zip', 'w') as arch:
    for path, a in FILE_LIST:
        print (a)
        arch.write(path, a, zipfile.ZIP_DEFLATED)
    arch.close()
