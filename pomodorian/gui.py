from PyQt4 import QtGui, QtCore
from pomodorian.utils import *
import sys, math


class PomoWindow(QtGui.QWidget):
    
    def __init__(self, pomo):
        super(PomoWindow, self).__init__()
        
        self.pomo = pomo
        
        self.initUI()
        
    def initUI(self):      
        # window settings
        
        self.setFixedSize(420, 255)
        self.move(250,250)
        self.setWindowTitle('Pomodorian')
        self.setWindowIcon(QtGui.QIcon('/usr/share/icons/pomodorian.png'))

        # pomo Tab
        
        pomoTab = QtGui.QWidget()
        
        pomo_taskEdit = QtGui.QComboBox()
        pomo_taskEdit.setEditable(True)
        pomo_taskEdit.lineEdit().setMaxLength(45)
        pomo_taskEdit.lineEdit().setPlaceholderText("task / activity / project")
        pomo_taskEdit.setFixedSize(354,29)
        pomo_taskEdit.setStyleSheet('font-size: 11pt;')
        
        pomo_btn = QtGui.QPushButton('Start', pomoTab)
        pomo_btn.setToolTip('This is a <b>QPushButton</b> widget')
        pomo_btn.setFixedSize(180,60)
        pomo_btn.setStyleSheet('font-size: 16pt;')
        #pomo_btn.connect(self.startButton)
        pomo_btn.connect(pomo_btn, QtCore.SIGNAL('clicked()'), self.onClicked)
        
        self.pomoBTN = pomo_btn
        
        pomo_checkBox = QtGui.QCheckBox("just one")
        pomo_checkBox2 = QtGui.QCheckBox("double length")
        
        pomo_firstRow = QtGui.QHBoxLayout()
        pomo_firstRow.addWidget(pomo_taskEdit)
        
        pomo_secondRow = QtGui.QHBoxLayout()
        pomo_secondRow.addStretch()
        pomo_secondRow.addWidget(pomo_checkBox)
        pomo_secondRow.addWidget(pomo_checkBox2)
        pomo_secondRow.addStretch()
        
        pomo_thirdRow = QtGui.QHBoxLayout()
        pomo_thirdRow.addWidget(pomo_btn)
        
        pomo_vbox = QtGui.QVBoxLayout()
        pomo_vbox.addStretch(0.05)
        pomo_vbox.addLayout(pomo_firstRow)
        pomo_vbox.addStretch(0.25)
        pomo_vbox.addLayout(pomo_secondRow)
        pomo_vbox.addStretch(0.25)
        pomo_vbox.addLayout(pomo_thirdRow)
        pomo_vbox.addStretch(0.33)
        
        pomoTab.setLayout(pomo_vbox) 

        # stats tab
        
        statsTab = QtGui.QWidget()
        
        stats_table = QtGui.QTableWidget(5,5)
        stats_table.setShowGrid(True)
        
        for i in range(0,3):
            stats_checkBox = QtGui.QCheckBox()
            stats_checkWidget = QtGui.QWidget()
            stats_checkLayout = QtGui.QHBoxLayout(stats_checkWidget)
            stats_checkLayout.addWidget(stats_checkBox)
            stats_checkLayout.setAlignment(QtCore.Qt.AlignCenter)
            stats_checkLayout.setContentsMargins(0,0,0,0)
            stats_checkWidget.setLayout(stats_checkLayout)
            stats_table.setCellWidget(i,0, stats_checkWidget)
        
        item = QtGui.QTableWidgetItem()
        item.setText("test")
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        
        stats_table.setItem(0,1,item)
        stats_table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        
        
        stats_table.setHorizontalHeaderLabels(["", "name", "pomos", "hours", "last"])
        stats_table.verticalHeader().setVisible(False)
        stats_table.resizeColumnsToContents()
        
        
        stats_hbox = QtGui.QHBoxLayout()
        stats_hbox.addWidget(stats_table)
        
        
        statsTab.setLayout(stats_hbox) 
        
        # about tab
        
        aboutTab = QtGui.QWidget()
        
        aboutText = QtGui.QLabel("Blabla")
        
        about_vbox = QtGui.QVBoxLayout()
        about_hbox = QtGui.QHBoxLayout()
        
        about_hbox.addStretch()
        about_hbox.addWidget(aboutText)
        about_hbox.addStretch()
        
        about_vbox.addStretch()
        about_vbox.addLayout(about_hbox)
        about_vbox.addStretch()
        
        aboutTab.setLayout(about_vbox) 
        
        # init tab Widget
        
        tabWidget = QtGui.QTabWidget(self)
        tabWidget.resize(419,254)
        
        tabWidget.addTab(pomoTab, "pomo")
        tabWidget.addTab(statsTab, "stats")
        tabWidget.addTab(aboutTab, "about")
        
        self.show()
        
    def keyPressEvent(self, e):
        
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            
    def sendTick(self, val):
        if self.pomoBTN.text() is not 'Start':
            newVal = 25*60 - val
            newVal = "{0:0>2}:{1:0>2}".format(math.floor(newVal/60),newVal % 60)
            self.pomoBTN.setText(newVal)
            
    def onClicked(self):
        sender = self.sender()
        
        if sender.text() == 'Start':
            sender.setText("25:00")
            self.pomo.startTimer()
        else:
            self.pomo.stopTimer()
            reply = QtGui.QMessageBox.question(self, 'Timer paused',
            "Do you really want to reset the running timer?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            
            if reply == QtGui.QMessageBox.Yes:
                sender.setText("Start")
                self.pomo.resetTimer()
            else:
                self.pomo.startTimer()
        

def initGUI(pomo):
    app = QtGui.QApplication(sys.argv)
    pomoGUI = PomoWindow(pomo)
    pomo.setGUI(pomoGUI)
    sys.exit(app.exec_())
