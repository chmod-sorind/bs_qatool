from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import *
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import sys
import re
import telnetlib
import time
import logging
from ui import MyPythonWindow
import xml.etree.ElementTree as ET
from bs_logger import bsLogger


class newTelnetThread(QThread):
    finishedSignal = pyqtSignal()

    def __init__(self, telnetParams, listOfHosts):
        """
        Make a new thread instance with the specified
        telnetParams as the first argument. The telnetParams argument
        will be stored in an instance variable called telnetParams
        which then can be accessed by all other class instance functions
        :param telnetParams: A list of telnet param names
        :type telnetParams: list
        """
        QThread.__init__(self)
        self.telnetParams = telnetParams
        self.listOfHosts = listOfHosts

    def __del__(self):
        self.wait()

    def _run_telnet_connection(self):
        telnetTimeout = 2
        count = self.telnetParams[0]
        rate = self.telnetParams[1]
        port = self.telnetParams[2]
        command = self.telnetParams[3]
        bsLogger.write(logging.info, "Telnet connection params.\n"
                                     "Poll Count: {0}\n"
                                     "Poll Rate: {1} sec\n"
                                     "Port: {2}\nCommand: {3}".
                       format(self.telnetParams[0],
                              self.telnetParams[1],
                              self.telnetParams[2],
                              self.telnetParams[3]))

        for pollNum in range(1, count + 1):
            for ipHost in self.listOfHosts:
                    try:
                        telnet = telnetlib.Telnet(ipHost, port, telnetTimeout)
                        telnet.write((command + '\n').encode('UTF-8'))
                        telnet.close()
                        bsLogger.write(logging.info, ("#{0} Command {1} sent to {2}".format(pollNum, command, ipHost)))
                    except Exception as e:
                        bsLogger.write(logging.warn, "HOST [{0}] {1}".format(ipHost, e))
            if pollNum < count:
                pollRate = int(rate)
                bsLogger.write(logging.info, "Sleeping for {} seconds".format(pollRate))
                while pollRate > 0:
                    minutes, sec = divmod(int(pollRate), 60)
                    countdown = '{:02d}:{:02d}'.format(minutes, sec)
                    print(countdown, end='\r')
                    time.sleep(1)
                    pollRate -= 1

    def run(self):
        self._run_telnet_connection()
        self.finishedSignal.emit()


class MyApp(QtWidgets.QMainWindow, MyPythonWindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyApp, self).__init__(parent)
        self.setupUi(self)

        # Button Functionality.
        self.buttonRemoveItemFromList.clicked.connect(self.buttonRemoveChecked)
        self.buttonStopTelnet.clicked.connect(self.stopTelnetThreading)
        self.checkBoxCheckAll.stateChanged.connect(self.CheckUncheckAll)

        # Host List View.
        self.model = QStandardItemModel(self.treeView)
        self.treeView.setModel(self.model)
        self.model.setColumnCount(2)
        self.model.setHeaderData(0, Qt.Horizontal, "Host IP")
        self.model.setHeaderData(1, Qt.Horizontal, "Host Port")
        self.treeView.setColumnWidth(0, 250)
        self.treeView.setColumnWidth(1, 50)

    @QtCore.pyqtSlot()
    def on_buttonAddItemToList_clicked(self):
        # ToDo: Make key ENTER add items to the list.
        _getTextFromLineEditHost = self.lineEditHost.text()
        _getTextFromLineEditPort = self.lineEditAddPort.text()
        if _getTextFromLineEditHost:
            ip_regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
            ip_pattern = re.compile(ip_regex)
            if ip_pattern.match(_getTextFromLineEditHost):
                ip_item = QStandardItem()
                port_item = QStandardItem()
                ip_item.setText(_getTextFromLineEditHost)
                port_item.setText(_getTextFromLineEditPort)
                ip_item.setAccessibleText(_getTextFromLineEditHost)
                port_item.setAccessibleText(_getTextFromLineEditPort)
                ip_item.setCheckable(True)
                if _getTextFromLineEditPort:
                    port_regex = r"\d{1,5}"
                    port_pattern = re.compile(port_regex)
                    if port_pattern.match(_getTextFromLineEditPort):
                        self.model.appendRow([ip_item, port_item])
                        self.lineEditHost.clear()
                        self.lineEditAddPort.clear()
                    else:
                        self.lineEditAddPort.setStyleSheet("background-color: rgb(255, 0, 0)")
                        QtCore.QTimer.singleShot(200, lambda: self.lineEditAddPort.setStyleSheet("background-color: rgb(255, 255, 255)"))
                        QtCore.QTimer.singleShot(500, lambda: self.lineEditAddPort.setStyleSheet("background-color: rgb(255, 0, 0)"))
                        QtCore.QTimer.singleShot(700, lambda: self.lineEditAddPort.setStyleSheet("background-color: rgb(255, 255, 255)"))
                        #QMessageBox.warning(self, 'Warning!', "<i>{}</i> doesn't look like a port!".format(_getTextFromLineEditPort))
                else:
                    self.model.appendRow([ip_item, QStandardItem('2323')])
                    self.lineEditHost.clear()
            else:
                self.lineEditHost.setStyleSheet("background-color: rgb(255, 0, 0)")
                QtCore.QTimer.singleShot(200, lambda: self.lineEditHost.setStyleSheet("background-color: rgb(255, 255, 255)"))
                QtCore.QTimer.singleShot(500, lambda: self.lineEditHost.setStyleSheet("background-color: rgb(255, 0, 0)"))
                QtCore.QTimer.singleShot(700, lambda: self.lineEditHost.setStyleSheet("background-color: rgb(255, 255, 255)"))
                #QMessageBox.warning(self, 'Warning!', "<i>{}</i> doesn't look like an IP address!".format(_getTextFromLineEditHost))
        else:
            self.statusBar().showMessage('Nothing to add')

    def CheckUncheckAll(self):
        for index in range(self.model.rowCount()):
            item = self.model.item(index)
            if self.checkBoxCheckAll.isChecked():
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

    def buttonRemoveChecked(self):
        try:
            for index in range(self.model.rowCount()):
                item = self.model.item(index)
                if item.checkState() == QtCore.Qt.Checked:
                    self.model.removeRow(index)
        except AttributeError as error:
            print(error)
            pass

    def buttonClicked(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')
        print(sender.text() + ' was pressed')

    @QtCore.pyqtSlot()
    def on_buttonCancel_clicked(self):
        self.statusBar().showMessage('Aplication will now exit.')
        time.sleep(1)
        bsLogger.write(logging.info, 'Application exited.')
        quit()


    @QtCore.pyqtSlot()
    def on_buttonStartTelnet_clicked(self):
        _com = str(self.lineEditCommand.text())
        _port = str(self.lineEditPort.text())
        _count = int(self.countBox.text())
        _rate = float(self.frequencyBox.text())
        telnetParams_list = [_count, _rate, _port, _com]

        ipHosts_list = []
        for index in range(self.model.rowCount()):
            ipItem = self.model.item(index)
            ipItemText = ipItem.accessibleText()
            if ipItem.checkState() == QtCore.Qt.Checked:
                ipHosts_list.append(ipItemText)

        if _port and _com:
            self.get_thread = newTelnetThread(telnetParams_list, ipHosts_list)
            self.get_thread.start()
            self.buttonStopTelnet.setEnabled(True)
            self.get_thread.finishedSignal.connect(self.stopTelnetThreading)
            self.buttonStopTelnet.clicked.connect(self.get_thread.terminate)
            self.buttonStartTelnet.setEnabled(False)
        else:
            QMessageBox.critical(self, 'Connection Failiure!', "Target Port OR Telnet Command values are missing.")

    def stopTelnetThreading(self):
        self.buttonStopTelnet.setEnabled(False)
        self.buttonStartTelnet.setEnabled(True)
        bsLogger.write(logging.info, 'Telnet connections have been interrupted!')

    @QtCore.pyqtSlot()
    def on_buttonLoadConigFile_clicked(self):
        fileName = QFileDialog.getOpenFileName(self, 'Load Ip List...')
        if fileName[0]:
            tree = ET.parse(fileName[0])
            root = tree.getroot()
            ip_items = []
            port_items = []
            for child_0 in root:
                if child_0.tag == 'HostPortList':
                    for child_1 in child_0:
                        for child_2 in child_1:
                            if child_2.tag == 'ip':
                                ip_items.append(child_2.text)
                            elif child_2.tag == 'port':
                                port_items.append(child_2.text)
                elif child_0.tag == 'ConnectionParams':
                    for child_3 in child_0:
                        if child_3.tag == 'count':
                            self.countBox.setValue(int(child_3.text))
                        if child_3.tag == 'rate':
                            self.frequencyBox.setValue(float(child_3.text))
                        if child_3.tag == 'command':
                            self.lineEditCommand.setText(child_3.text)
                        if child_3.tag == 'port':
                            self.lineEditPort.setText(child_3.text)
            no_ip_items = len(ip_items)
            no_port_items = len(port_items)
            if no_ip_items == no_port_items:
                pass
            else:
                raise Exception('exception')
            i = 0
            while i < no_ip_items:
                ip_item = QStandardItem()
                ip_item.setText(ip_items[i])
                ip_item.setAccessibleText(ip_items[i])
                ip_item.setCheckable(True)
                port_item = QStandardItem()
                port_item.setText(port_items[i])
                port_item.setAccessibleText(port_items[i])
                self.model.appendRow([ip_item, port_item])
                i += 1
        self.statusBar().showMessage("{} loaded...".format(fileName[0]))

    @QtCore.pyqtSlot()
    def on_buttonSaveConfigToFile_clicked(self):
        print('buttonSaveConfigToFile was pressed')
    #     fileName = QFileDialog.getOpenFileName(self, 'Open Config file...')
    #     self.statusBar().showMessage("{} loaded...".format(fileName[0]))
    #     tree = ET.parse(fileName[0])
    #     root = tree.getroot()
    #     for node in root:
    #         if node.tag == 'count':
    #             x = node.attrib
    #             for item in x.items():
    #                 count = int(item[1])
    #         if node.tag == 'rate':
    #             x = node.attrib
    #             for item in x.items():
    #                 rate = float(item[1])
    #         if node.tag == 'port':
    #             x = node.attrib
    #             for item in x.items():
    #                 port = item[1]
    #         if node.tag == 'command':
    #             x = node.attrib
    #             for item in x.items():
    #                 command = item[1]
    #     self.countBox.setValue(count)
    #     self.frequencyBox.setValue(rate)
    #     self.lineEditCommand.setText(command)
    #     self.lineEditPort.setText(port)


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = MyApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
