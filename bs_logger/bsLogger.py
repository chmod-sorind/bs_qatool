# bsLogger.py
import logging
import PyQt5
from ui import MyPythonWindow

logFile = MyPythonWindow.Ui_MainWindow


def write(log_level, msg):
    logging.basicConfig(format='%(asctime)s(%(levelname)s) %(message)s',
                        datefmt='[%Y-%m-%dT%H:%M:%S]',
                        filename=logFile, level=logging.DEBUG)
    log_level(msg)
