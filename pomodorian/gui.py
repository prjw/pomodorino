from PyQt4 import QtGui, QtCore
from pomodorian.utils import *
import sys, math


class PomoWindow(QtGui.QWidget):
    
    def __init__(self, pomo):
        super(PomoWindow, self).__init__()
        
        self.pomo = pomo
        
        self.initUI()
        
        
    def initPomoTab(self):
        pomoTab = QtGui.QWidget()
        
        taskEdit = QtGui.QComboBox()
        taskEdit.setEditable(True)
        taskEdit.lineEdit().setMaxLength(45)
        taskEdit.lineEdit().setPlaceholderText("task / activity / project")
        taskEdit.setFixedSize(354,29)
        taskEdit.setStyleSheet('font-size: 11pt;')
        self.pomoTaskEdit = taskEdit
        
        
        mainButton = QtGui.QPushButton('Start', pomoTab)
        mainButton.setToolTip('This is a <b>QPushButton</b> widget')
        mainButton.setFixedSize(180,60)
        mainButton.setStyleSheet('font-size: 16pt;')

        
        timeButton = QtGui.QPushButton('25', pomoTab)
        timeButton.setToolTip('Standard one-size-fits-all Pomodoro')
        timeButton.setFixedSize(50, 25)
        timeButton.setStyleSheet('font-size: 9pt;')
        
        # default time is selected at the start
        timeButton.setDisabled(True)
        self.pomoButtonActive = timeButton
        
        doubleTimeButton = QtGui.QPushButton('50', pomoTab)
        doubleTimeButton.setToolTip('Double length Pomodoro (counts as two)')
        doubleTimeButton.setFixedSize(50, 25)
        doubleTimeButton.setStyleSheet('font-size: 9pt;')
        
        pauseButton = QtGui.QPushButton('5', pomoTab)
        pauseButton.setToolTip('Short pause')
        pauseButton.setFixedSize(50, 25)
        pauseButton.setStyleSheet('font-size: 9pt;')
        
        
        doublePauseButton = QtGui.QPushButton('10', pomoTab)
        doublePauseButton.setToolTip('Long pause')
        doublePauseButton.setFixedSize(50, 25)
        doublePauseButton.setStyleSheet('font-size: 9pt;')


        mainButton.connect(mainButton, QtCore.SIGNAL('clicked()'), self.onClickedPomoMain)
        timeButton.connect(timeButton, QtCore.SIGNAL('clicked()'), self.onClickedPomoTime)
        pauseButton.connect(pauseButton, QtCore.SIGNAL('clicked()'), self.onClickedPomoTime)
        doubleTimeButton.connect(doubleTimeButton, QtCore.SIGNAL('clicked()'), self.onClickedPomoTime)
        doublePauseButton.connect(doublePauseButton, QtCore.SIGNAL('clicked()'), self.onClickedPomoTime)
        
        
        # save button references for usage in other methods
        self.pomoButtons = dict()
        self.pomoButtons['main'] = mainButton
        self.pomoButtons['time'] = timeButton
        self.pomoButtons['doubleTime'] = doubleTimeButton
        self.pomoButtons['pause'] = pauseButton
        self.pomoButtons['doublePause'] = doublePauseButton
        

    
        firstRow = QtGui.QHBoxLayout()
        firstRow.addWidget(taskEdit)
        
        secondRow = QtGui.QHBoxLayout()
        secondRow.addStretch()
        secondRow.addWidget(pauseButton)
        secondRow.addWidget(doublePauseButton)
        secondRow.addStretch()
        secondRow.addWidget(timeButton)
        secondRow.addWidget(doubleTimeButton)
        secondRow.addStretch()
        
        thirdRow = QtGui.QHBoxLayout()
        thirdRow.addWidget(mainButton)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(0.05)
        vbox.addLayout(firstRow)
        vbox.addStretch(0.25)
        vbox.addLayout(secondRow)
        vbox.addStretch(0.25)
        vbox.addLayout(thirdRow)
        vbox.addStretch(0.33)
        
        pomoTab.setLayout(vbox) 
        
        return pomoTab
        
    def initStatsTab(self):
        statsTab = QtGui.QWidget()
        
        table = QtGui.QTableWidget(5,5)
        table.setShowGrid(True)
        
        for i in range(0,3):
            checkBox = QtGui.QCheckBox()
            checkWidget = QtGui.QWidget()
            checkLayout = QtGui.QHBoxLayout(checkWidget)
            checkLayout.addWidget(checkBox)
            checkLayout.setAlignment(QtCore.Qt.AlignCenter)
            checkLayout.setContentsMargins(0,0,0,0)
            checkWidget.setLayout(checkLayout)
            table.setCellWidget(i,0, checkWidget)
        
        item = QtGui.QTableWidgetItem()
        item.setText("test")
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        
        table.setItem(0,1,item)
        table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        
        
        table.setHorizontalHeaderLabels(["", "name", "pomos", "hours", "last"])
        table.verticalHeader().setVisible(False)
        table.resizeColumnsToContents()
        
        
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(table)
        
        
        statsTab.setLayout(hbox)
        
        return statsTab 
        
        
        
    def initAboutTab(self):
        aboutTab = QtGui.QWidget()
        
        aboutText = QtGui.QLabel("Blabla")
        
        vbox = QtGui.QVBoxLayout()
        hbox = QtGui.QHBoxLayout()
        
        hbox.addStretch()
        hbox.addWidget(aboutText)
        hbox.addStretch()
        
        vbox.addStretch()
        vbox.addLayout(hbox)
        vbox.addStretch()
        
        aboutTab.setLayout(vbox) 
        
        return aboutTab
        
        
        
    def initUI(self):      
        self.setFixedSize(420, 255)
        self.move(250,250)
        self.setWindowTitle('Pomodorian')
        self.setWindowIcon(QtGui.QIcon('/usr/share/icons/pomodorian.png'))
        
        pomoTab = self.initPomoTab()
        statsTab = self.initStatsTab()
        aboutTab = self.initAboutTab()
        
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
        if self.pomoButtons['main'].text() != 'Start':
            newVal = int(self.pomoButtonActive.text())*60 - val
            newVal = "{0:0>2}:{1:0>2}".format(math.floor(newVal/60),newVal % 60)
            self.pomoButtons['main'].setText(newVal)
            if newVal == '00:00':
                self.pomo.finishTimer(int(self.pomoButtonActive.text()))
                self.resetPomoTab()
                    
            
    def resetPomoTab(self):
        self.pomoTaskEdit.setDisabled(False)
        self.pomoButtons['main'].setText("Start")
        for k,v in self.pomoButtons.items():
            if k != 'main' and v is not self.pomoButtonActive:
                v.setDisabled(False)
            
            
            
    def onClickedPomoMain(self):
        sender = self.sender()
        
        if sender.text() == 'Start':
            self.pomoTaskEdit.setDisabled(True)
            for k,v in self.pomoButtons.items():
                if k != 'main':
                    v.setDisabled(True)
            sender.setText("{0:0>2}:00".format(int(self.pomoButtonActive.text())))
            self.pomo.startTimer()
            
        else:
            self.pomo.stopTimer()
            reply = QtGui.QMessageBox.question(self, 'Timer paused',
            "Do you really want to reset the running timer?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            
            if reply == QtGui.QMessageBox.Yes:
                self.resetPomoTab()
                self.pomo.resetTimer()
            else:
                self.pomo.startTimer()
                
                
                
    def onClickedPomoTime(self):
        sender = self.sender()
        
        if self.pomoButtons['main'].text() == 'Start':
            self.pomoButtonActive.setDisabled(False)
            sender.setDisabled(True)
            self.pomoButtonActive = sender
        



def initGUI(pomo):
    app = QtGui.QApplication(sys.argv)
    pomoGUI = PomoWindow(pomo)
    pomo.setGUI(pomoGUI)
    sys.exit(app.exec_())
