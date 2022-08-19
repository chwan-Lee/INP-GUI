 #-*- coding: utf-8 -*- 
import os
import sys

from package import mainWindow
from PyQt5.QtWidgets import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainWindow.App()
    window.show()
    app.exec_()
