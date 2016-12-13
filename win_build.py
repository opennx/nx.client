#!/usr/bin/env python3
#
# Requirements:
#  - pywin32
#  - pyinstaller

import os
import sys
import subprocess
import time
import shutil

import_error_message = "'{}' module is not installed. Exiting"
python_path = os.path.dirname(sys.executable)


#
# Check prerequisites
#

try:
    from nxtools import *
except ImportError:
    print(import_error_message.format("nxtools"))
    sys.exit(-1)

try:
    import requests
except:
    critical_error(import_error_message.format("requests"))

try:
    import PyQt5
except:
    critical_error(import_error_message.format("PyQT5"))

if PYTHON_VERSION < 3:
    critical_error("Python 3 is required")

if PLATFORM != "windows":
    critical_error("This script must be run under windows")

#
# Create resources
#

TARGET_DIR = "dist/firefly/"


def build_resources():
    logging.info("Building resources")
    qrc = "<RCC>\n <qresource>\n"
    for f in os.listdir("images"):
        qrc += "  <file>images/{}</file>\n".format(f)
    qrc += " </qresource>\n</RCC>"

    f = open(".firefly.qrc","w")
    f.write(qrc)
    f.close()
    pyrcc_path = os.path.join(python_path, "lib", "site-packages", "PyQt5", "pyrcc5")
    proc = subprocess.Popen([pyrcc_path, ".firefly.qrc", "-o", "firefly_rc.py"])
    while proc.poll() == None:
        time.sleep(.1)

def build_exe():
    shutil.copy("firefly.spec.template", "firefly.spec")
    os.system("pyinstaller.exe -y firefly.spec")

def copy_deps():
    shutil.copy("local_settings.json", TARGET_DIR)
    shutil.copy("local_settings.default", TARGET_DIR)
    shutil.copy("skin.css", TARGET_DIR)


if __name__ == "__main__":
    #build_resources()
    build_exe()
    copy_deps()