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

        
    def getString(self, cat, identifier):
        """
        Calls the pomo getString function to enhance readability.
        """
        return self.pomo.getString(cat, identifier)
        
        
    def initUI(self):      
        """
        Initializes the UI.
        """
        self.setFixedSize(460, 275)
        self.move(250,250)
        self.setWindowTitle(self.getString("main", "app_name"))
        self.setWindowIcon(QtGui.QIcon('/usr/share/icons/pomodorian.png'))
        
        # Initialize our three tabs
        pomoTab = self.initPomoTab()
        statsTab = self.initStatsTab()
        aboutTab = self.initAboutTab()
        
        tabWidget = QtGui.QTabWidget(self)
        tabWidget.resize(459,274)
        
        tabWidget.addTab(pomoTab, self.getString("gui", "tab_pomo"))
        tabWidget.addTab(statsTab, self.getString("gui", "tab_stats"))
        tabWidget.addTab(aboutTab, self.getString("gui", "tab_about"))
        
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
        
        taskBar = QtGui.QComboBox()
        taskBar.setEditable(True)
        taskBarLine = taskBar.lineEdit()
        taskBarLine.setMaxLength(64)
        taskBarLine.setPlaceholderText(self.getString("gui", "input_task"))
        taskBar.setFixedSize(365,30)
        taskBar.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        taskBar.setStyleSheet('font-size: 11pt;')
        
        for taskID, taskName, pomoCount, pomoLast in tasks:
            taskBar.addItem(taskName, None)
        
        self.pomoTaskBar = taskBar
        
        
        mainBtn = QtGui.QPushButton(self.getString("gui", "btn_start"), pomoTab)
        mainBtn.setFixedSize(170, 55)
        mainBtn.setStyleSheet('font-size: 16pt;')

        
        timeBtn = QtGui.QPushButton(
                self.getString("gui", "lbl_regularpomo"), pomoTab)
        timeBtn.setToolTip(self.getString("gui", "ttp_regularpomo"))
        timeBtn.setFixedSize(50, 25)
        timeBtn.setStyleSheet('font-size: 9pt;')

        
        # default time is selected at the start
        timeBtn.setDisabled(True)
        self.pomoButtonActive = timeBtn

        
        longTimeBtn = QtGui.QPushButton(
                self.getString("gui", "lbl_longpomo"), pomoTab)
        longTimeBtn.setToolTip(self.getString("gui", "ttp_longpomo"))
        longTimeBtn.setFixedSize(50, 25)
        longTimeBtn.setStyleSheet('font-size: 9pt;')

        
        pauseBtn = QtGui.QPushButton(
                self.getString("gui", "lbl_shortpause"), pomoTab)
        pauseBtn.setToolTip(self.getString("gui", "ttp_shortpause"))
        pauseBtn.setFixedSize(50, 25)
        pauseBtn.setStyleSheet('font-size: 9pt;')
        
        
        longPauseBtn = QtGui.QPushButton(
                self.getString("gui", "lbl_longpause"), pomoTab)
        longPauseBtn.setToolTip(self.getString("gui", "ttp_longpause"))
        longPauseBtn.setFixedSize(50, 25)
        longPauseBtn.setStyleSheet('font-size: 9pt;')


        # Save button references for later usage.
        self.pomoBtns = dict()
        self.pomoBtns['main'] = mainBtn
        self.pomoBtns['time'] = timeBtn
        self.pomoBtns['longTime'] = longTimeBtn
        self.pomoBtns['pause'] = pauseBtn
        self.pomoBtns['longPause'] = longPauseBtn

        for name, button in self.pomoBtns.items():
            button.connect(button, QtCore.SIGNAL('clicked()'), self.onClicked)
    
        firstRow = QtGui.QHBoxLayout()
        firstRow.addWidget(taskBar)
        
        secondRow = QtGui.QHBoxLayout()
        secondRow.addStretch()
        secondRow.addWidget(pauseBtn)
        secondRow.addWidget(longPauseBtn)
        secondRow.addStretch()
        secondRow.addWidget(timeBtn)
        secondRow.addWidget(longTimeBtn)
        secondRow.addStretch()
        
        thirdRow = QtGui.QHBoxLayout()
        thirdRow.addWidget(mainBtn)
        
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
        
        
        table.setHorizontalHeaderLabels(["",
                self.getString("gui", "lbl_stats_task"),
                self.getString("gui", "lbl_stats_pomos"),
                self.getString("gui", "lbl_stats_last")])
        table.verticalHeader().setVisible(False)
        table.resizeColumnsToContents()
        table.setColumnWidth(1, 278)
        
        self.statsTable = table
        
        allCheck = QtGui.QCheckBox(self.getString("gui", "lbl_stats_all"),
                statsTab)
        
        allCheck.connect(allCheck, QtCore.SIGNAL('clicked()'),
                           self.onClickedStatsAll)

        
        selTimeSpan = QtGui.QComboBox()
        selTimeSpan.insertItem (0, self.getString("gui", "optn_lastweek"), None)
        selTimeSpan.insertItem (0, self.getString("gui", "optn_lastmonth"), None)
        selTimeSpan.insertItem (0, self.getString("gui", "optn_last3months"), None)
        selTimeSpan.insertItem (0, self.getString("gui", "optn_last6months"), None)
        selTimeSpan.insertItem (0, self.getString("gui", "optn_lastyear"), None)
        
        showBtn = QtGui.QPushButton(self.getString("gui", "btn_showdaily"),
                statsTab)
        
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(allCheck)
        hbox.addStretch()
        hbox.addWidget(selTimeSpan)
        hbox.addStretch()
        hbox.addWidget(showBtn)
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
        
        aboutText = QtGui.QLabel(self.getString("gui", "about"))
        
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
            reply = QtGui.QMessageBox.question(self,
                        self.getString("gui", "ask_paused_title"),
                        self.getString("gui", "ask_paused_text"),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                        QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.Yes:
                return True
            else:
                return False

        elif identifier == 'warn_notask':
            QtGui.QMessageBox.warning(self,
                    self.getString("gui", "warn_notask_title"),
                    self.getString("gui", "warn_notask_text"))
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
                self.pomo.startTimer(0, restart=True)
        else:
            event.accept()

            
    def receiveTick(self, timerCount):
        """
        Updates the GUI every second when the timer is running.
        """
        if self.pomo.isTimerRunning():
            timeStr = "{0:0>2}:{1:0>2}".format(
                    math.floor(timerCount / 60), timerCount % 60) 
            self.pomoBtns['main'].setText(timeStr)
            # Show current time in the title.
            #title = timeStr + " - " +  self.getString("main", "app_name")
            #self.window().setWindowTitle(title)
            if timerCount == 0:
                self.playRingtone()
                self.pomo.finishTimer(self.pomoTaskBar.currentText())
                self.resetPomoTab()
            
            
    def resetPomoTab(self):
        """
        Resets the button states in the pomo tab.
        """
        if (self.pomoButtonActive != self.pomoBtns['pause'] and
                self.pomoButtonActive != self.pomoBtns['longPause']):   
            self.pomoTaskBar.setDisabled(False)
            
        self.pomoBtns['main'].setText("start")
        for k,v in self.pomoBtns.items():
            if k != 'main' and v is not self.pomoButtonActive:
                v.setDisabled(False)

        # Also reset the window title.
        #self.window().setWindowTitle(self.getString("main", "app_name"))
            
            
    def addTask(self, taskName):
        """
        Adds a task to the taskbar.
        """
        self.pomoTaskBar.addItem(taskName, None)


    def onClicked(self):
        """
        Main function for catching button clicks in the pomo tab.
        """
        sender = self.sender()
        if sender == self.pomoBtns['main']:
            return self.onClickedPomoMain()
            
        elif (sender == self.pomoBtns['pause'] or
              sender == self.pomoBtns['longPause'] or
              sender == self.pomoBtns['time'] or
              sender == self.pomoBtns['longTime']):
            return self.onClickedPomoTime()

        raise ValueError()

    
    def onClickedPomoMain(self):
        """
        Starts/Stops the timer depending on the state of the button.
        """
        sender = self.sender()

        if self.pomo.isTimerRunning():
            self.pomo.stopTimer()
            # Ask the user whether he wants to reset the running timer.
            if self.promptUser("ask_paused"):
                self.resetPomoTab()
                self.pomo.resetTimer()
            else:
                self.pomo.startTimer(0, restart=True)
        else:
            newText = self.pomoTaskBar.currentText().strip()
            self.pomoTaskBar.setEditText(newText)

            if (newText != "" or self.pomoTaskBar.isEnabled() is False):
                self.pomoTaskBar.setDisabled(True)
                for k,v in self.pomoBtns.items():
                    if k != 'main':
                        v.setDisabled(True)
                timeSpan = int(self.pomoButtonActive.text())
                sender.setText("{0:0>2}:00".format(timeSpan))
                self.pomo.startTimer(timeSpan)
            else:
                self.promptUser("warn_notask")
        
                
    def onClickedPomoTime(self):
        """
        Toggles the state of the timer buttons in the pomo tab.
        """
        sender = self.sender()
        
        if self.pomoBtns['main'].text() == 'start':
            self.pomoButtonActive.setDisabled(False)
            sender.setDisabled(True)
            self.pomoButtonActive = sender
            
            if (sender == self.pomoBtns['pause']
                    or sender == self.pomoBtns['longPause']):
                self.pomoTaskBar.setDisabled(True)
            else:
                self.pomoTaskBar.setDisabled(False)
        

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
        # Kill the thread once it finishes.
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
