import sys
import datetime
import math
import wave
import threading

from PyQt4 import QtGui, QtCore
import alsaaudio



class PomoWindow(QtGui.QWidget):
    
    def __init__(self, pomo):
        """
        Makes necessary variable initializations and calls other init methods.
        """
        super(PomoWindow, self).__init__()
        self.pomo = pomo
        self.initUI()
        self.initAudio()
        
        
    def initUI(self):      
        """
        Initializes the UI.
        """
        self.setFixedSize(460, 275)
        self.move(250,250)
        self.setWindowTitle(self.pomo.getString("general", "app_name"))
        self.setWindowIcon(QtGui.QIcon('/usr/share/icons/pomodorian.png'))
        
        # Initialize our three tabs
        pomoTab = self.initPomoTab()
        statsTab = self.initStatsTab()
        aboutTab = self.initAboutTab()
        
        tabWidget = QtGui.QTabWidget(self)
        tabWidget.resize(459,274)
        
        tabWidget.addTab(pomoTab, self.pomo.getString("guitext", "tab_pomo"))
        tabWidget.addTab(statsTab, self.pomo.getString("guitext", "tab_stats"))
        tabWidget.addTab(aboutTab, self.pomo.getString("guitext", "tab_about"))
        
        # Show the window
        self.show()
        
        
    def initAudio(self):
        """
        Detects the audio device and buffers our ringtone
        """
        # Detect a ALSA audio device
        # TODO: WinSound
        
        self.audioDevice = alsaaudio.PCM()
        
        ring = wave.open("data/ring.wav", 'rb')
        self.audioDevice.setchannels(ring.getnchannels())
        self.audioDevice.setrate(ring.getframerate())
        
        # 8bit is unsigned in wav files
        if ring.getsampwidth() == 1:
            self.audioDevice.setformat(alsaaudio.PCM_FORMAT_U8)
        # Otherwise we assume signed data, little endian
        elif ring.getsampwidth() == 2:
            self.audioDevice.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        elif ring.getsampwidth() == 3:
            self.audioDevice.setformat(alsaaudio.PCM_FORMAT_S24_LE)
        elif ring.getsampwidth() == 4:
            self.audioDevice.setformat(alsaaudio.PCM_FORMAT_S32_LE)
        else:
            raise ValueError('Unsupported format')

        self.audioDevice.setperiodsize(320)
        
        # Read the audio data of the ringtone.
        self.audioData = list()
        buf = ring.readframes(320)
        while buf:
            self.audioData.append(buf)
            buf = ring.readframes(320)
                
        
        
    def initPomoTab(self):
        """
        Creates the layout of the pomodoro tab
        """
        pomoTab = QtGui.QWidget()
        
        tasks = self.pomo.getAllTasks()
        
        taskEdit = QtGui.QComboBox()
        taskEdit.setEditable(True)
        taskEdit.lineEdit().setMaxLength(64)
        taskEdit.lineEdit().setPlaceholderText(self.pomo.getString("guitext",
                                               "input_task"))
        taskEdit.setFixedSize(365,30)
        taskEdit.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        taskEdit.setStyleSheet('font-size: 11pt;')
        
        for taskID, taskName, pomoCount, pomoLast in tasks:
            taskEdit.addItem(taskName, None)
        
        self.pomoTaskEdit = taskEdit
        
        
        mainButton = QtGui.QPushButton(self.pomo.getString("guitext",
                                       "btn_start"), pomoTab)
        mainButton.setFixedSize(170, 55)
        mainButton.setStyleSheet('font-size: 16pt;')

        
        timeButton = QtGui.QPushButton(self.pomo.getString("guitext",
                                       "lbl_regularpomo"), pomoTab)
        timeButton.setToolTip(self.pomo.getString("guitext",
                            "ttp_regularpomo"))
        timeButton.setFixedSize(50, 25)
        timeButton.setStyleSheet('font-size: 9pt;')

        
        # default time is selected at the start
        timeButton.setDisabled(True)
        self.pomoButtonActive = timeButton

        
        doubleTimeButton = QtGui.QPushButton(self.pomo.getString("guitext",
                                             "lbl_longpomo"), pomoTab)
        doubleTimeButton.setToolTip(self.pomo.getString("guitext",
                                    "ttp_longpomo"))
        doubleTimeButton.setFixedSize(50, 25)
        doubleTimeButton.setStyleSheet('font-size: 9pt;')

        
        pauseButton = QtGui.QPushButton(self.pomo.getString("guitext",
                                        "lbl_shortpause"), pomoTab)
        pauseButton.setToolTip(self.pomo.getString("guitext",
                               "ttp_shortpause"))
        pauseButton.setFixedSize(50, 25)
        pauseButton.setStyleSheet('font-size: 9pt;')
        
        
        doublePauseButton = QtGui.QPushButton(self.pomo.getString("guitext",
                                              "lbl_longpause"), pomoTab)
        doublePauseButton.setToolTip(self.pomo.getString("guitext",
                                     "ttp_longpause"))
        doublePauseButton.setFixedSize(50, 25)
        doublePauseButton.setStyleSheet('font-size: 9pt;')


        mainButton.connect(mainButton, QtCore.SIGNAL('clicked()'),
                           self.onClickedPomoMain)
        timeButton.connect(timeButton, QtCore.SIGNAL('clicked()'),
                           self.onClickedPomoTime)
        pauseButton.connect(pauseButton, QtCore.SIGNAL('clicked()'),
                            self.onClickedPomoTime)
        doubleTimeButton.connect(doubleTimeButton, QtCore.SIGNAL('clicked()'),
                                 self.onClickedPomoTime)
        doublePauseButton.connect(doublePauseButton, QtCore.SIGNAL('clicked()'),
                                  self.onClickedPomoTime)
        
        
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
        """
        Creates the layout of the statistics tab
        """
        statsTab = QtGui.QWidget()

        tasks = self.pomo.getAllTasks()
        
        table = QtGui.QTableWidget(len(tasks),4)
        table.setShowGrid(True)
        
        for taskID, taskName, pomoCount, pomoLast in tasks:
            checkBox = QtGui.QCheckBox()
            checkWidget = QtGui.QWidget()
            checkLayout = QtGui.QHBoxLayout(checkWidget)
            checkLayout.addWidget(checkBox)
            checkLayout.setAlignment(QtCore.Qt.AlignCenter)
            checkLayout.setContentsMargins(0, 0, 0, 0)
            checkWidget.setLayout(checkLayout)
            table.setCellWidget(taskID - 1 , 0, checkWidget)
            
            
            item = QtGui.QTableWidgetItem()
            item.setText(taskName)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            table.setItem(taskID - 1 , 1, item)
            
            item = QtGui.QTableWidgetItem()
            item.setText(str(pomoCount) + "  (" +
                         str(round((pomoCount * 25) / 60, 1))+"h)")
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            table.setItem(taskID - 1 , 2, item)
            
            
            pomoLastDate = datetime.datetime.fromtimestamp(pomoLast)
            item = QtGui.QTableWidgetItem()
            item.setText(pomoLastDate.strftime("%x"))
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            table.setItem(taskID - 1 , 3, item)
        
        
        table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        
        
        table.setHorizontalHeaderLabels(["", self.pomo.getString("guitext",
                                                        "lbl_stats_task"),
                                        self.pomo.getString("guitext",
                                                        "lbl_stats_pomos"),
                                        self.pomo.getString("guitext",
                                                        "lbl_stats_last")])
        table.verticalHeader().setVisible(False)
        table.resizeColumnsToContents()
        table.setColumnWidth(1, 278)
        
        self.statsTable = table
        
        mainButton = QtGui.QCheckBox(self.pomo.getString("guitext",
                                     "lbl_stats_all"), statsTab)
        
        mainButton.connect(mainButton, QtCore.SIGNAL('clicked()'),
                           self.onClickedStatsAll)

        
        mainButton2 = QtGui.QComboBox()
        mainButton2.insertItem (0, self.pomo.getString("guitext",
                                "optn_lastweek"), None)
        mainButton2.insertItem (0, self.pomo.getString("guitext",
                                "optn_lastmonth"), None)
        mainButton2.insertItem (0, self.pomo.getString("guitext",
                                "optn_last3months"), None)
        mainButton2.insertItem (0, self.pomo.getString("guitext",
                                "optn_last6months"), None)
        mainButton2.insertItem (0, self.pomo.getString("guitext",
                                "optn_lastyear"), None)
        
        mainButton3 = QtGui.QPushButton(self.pomo.getString("guitext",
                                        "btn_showdaily"), statsTab)
        
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(mainButton)
        hbox.addStretch()
        hbox.addWidget(mainButton2)
        hbox.addStretch()
        hbox.addWidget(mainButton3)
        hbox.addStretch()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(table)
        vbox.addLayout(hbox)
        
        
        statsTab.setLayout(vbox)
        return statsTab 

        
    def initAboutTab(self):
        """
        Creates the layout of the about tab
        """
        aboutTab = QtGui.QWidget()
        
        aboutText = QtGui.QLabel(self.pomo.getString("guitext", "about"))
        
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


    def promptUser(self, identifier):
        if identifier == 'ask_paused':
            reply = QtGui.QMessageBox.question(self, self.pomo.getString(
            "guitext", "ask_paused_title"), self.pomo.getString("guitext",
            "ask_paused_text"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
            QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.Yes:
                return True
            else:
                return False

        elif identifier == 'warn_notask':
            QtGui.QMessageBox.warning(self, self.pomo.getString(
            "guitext", "warn_notask_title"), self.pomo.getString(
            "guitext", "warn_notask_text"))
            return

        raise KeyError
        

        
    def closeEvent(self, event):
        """
        Prevents accidental shutdowns by asking the user.
        """
        if self.pomo.isTimerRunning():
            self.pomo.stopTimer()
            
            if self.promptUser("ask_paused"):
                event.accept()
            else:
                event.ignore()
                self.pomo.startTimer()
        else:
            event.accept()

            
    def receiveTick(self, val):
        """
        
        """
        if self.pomoButtons['main'].text() != 'start':
            newVal = int(self.pomoButtonActive.text()) * 60 - val
            newVal = "{0:0>2}:{1:0>2}".format(math.floor(newVal / 60),
                                              newVal % 60)
            self.pomoButtons['main'].setText(newVal)
            if newVal == '00:00':
                self.playRingtone()
                self.pomo.finishTimer(int(self.pomoButtonActive.text()),
                                      self.pomoTaskEdit.currentText())
                self.resetPomoTab()
            
            
    def resetPomoTab(self):
        """
        
        """
        if (self.pomoButtonActive != self.pomoButtons['pause'] and
        self.pomoButtonActive != self.pomoButtons['doublePause']):
            self.pomoTaskEdit.setDisabled(False)
            
        self.pomoButtons['main'].setText("start")
        for k,v in self.pomoButtons.items():
            if k != 'main' and v is not self.pomoButtonActive:
                v.setDisabled(False)
            
            
    def addTask(self, taskName):
        """

        """
        self.pomoTaskEdit.addItem(taskName, None)
            
            
    def onClickedPomoMain(self):
        """
        Starts/Stops the timer depending on the state of the button.
        """
        sender = self.sender()
        
        if sender.text() == 'start':
            if (self.pomoTaskEdit.currentText() != '' or
            self.pomoTaskEdit.isEnabled() is False):
                self.pomoTaskEdit.setDisabled(True)
                self.pomoTaskEdit.setEditText(
                    self.pomoTaskEdit.currentText().strip())
                for k,v in self.pomoButtons.items():
                    if k != 'main':
                        v.setDisabled(True)
                sender.setText("{0:0>2}:00".format(int(
                    self.pomoButtonActive.text())))
                self.pomo.startTimer()
            else:
                self.promptUser("warn_notask")
            
        else:
            self.pomo.stopTimer()
            
            if self.promptUser("ask_paused"):
                self.resetPomoTab()
                self.pomo.resetTimer()
            else:
                self.pomo.startTimer()
                
                
    def onClickedPomoTime(self):
        """
        Toggles the state of the timer buttons in the pomo tab.
        """
        sender = self.sender()
        
        if self.pomoButtons['main'].text() == 'start':
            self.pomoButtonActive.setDisabled(False)
            sender.setDisabled(True)
            self.pomoButtonActive = sender
            
            if (sender == self.pomoButtons['pause']
            or sender == self.pomoButtons['doublePause']):
                self.pomoTaskEdit.setDisabled(True)
            else:
                self.pomoTaskEdit.setDisabled(False)
        

    def onClickedStatsAll(self):
        """
        (Un)Checks all the checkboxes in the stats tab.
        """
        sender = self.sender()
        state = sender.isChecked()
        
        for i in range(0, self.statsTable.rowCount()):
            item = self.statsTable.cellWidget(i, 0)
            checkbox = item.layout().itemAt(0).widget()
            checkbox.setChecked(state)
        
        
    def playRingtone(self):
        """
        Creates a thread for playing the ringtone.
        """
        t = threading.Thread(target=self.playRingThread)
        # Kill the thread when it finishes.
        t.daemon = True
        t.start()
        

    def playRingThread(self):
        """
        Plays the Ringtone.
        """
        for data in self.audioData:
            self.audioDevice.write(data)


def initGUI(pomo):
    app = QtGui.QApplication(sys.argv)
    pomoGUI = PomoWindow(pomo)
    pomo.setGUI(pomoGUI)
    sys.exit(app.exec_())
