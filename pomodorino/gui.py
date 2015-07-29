import sys
import datetime
import calendar
import math
import wave
import threading
import time
import random

from PyQt4 import QtGui, QtCore
import matplotlib
# Workaround since matplotlib defaults to Qt5Agg
matplotlib.use("Qt4Agg")
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import alsaaudio


class PomoWindow(QtGui.QWidget):
    def __init__(self, pomo):
        """
        Makes necessary variable initializations and calls other init methods.
        """
        super(PomoWindow, self).__init__()
        self.pomo = pomo
        # Enhance readability
        self.getString = self.pomo.getString
        self.initUI()
        self.initAudio()
        self.timerActive = False
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)

    def initUI(self):      
        """
        Initializes the UI.
        """
        # Set some general window settings.
        self.setFixedSize(480, 310)
        self.move(250,250)
        self.setWindowTitle(self.getString("app_name"))
        self.setWindowIcon(QtGui.QIcon('/usr/share/icons/pomodorino.png'))
        self.trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon('/usr/share/icons/pomodorino.png'), self)
        self.trayIcon.setVisible(True)
        self.trayIcon.activated.connect(self.trayClick)

        # Add a minimal context menu for the tray icon.
        #trayMenu = QtGui.QMenu(self)
        #trayMenu.addAction("Quit", self.close)
        #self.trayIcon.setContextMenu(trayMenu)
        
        # Initialize and display the tabs
        pomoTab = self.initPomoTab()
        tasksTab = self.initTasksTab()
        activityTab = self.initActivityTab()
        
        tabWidget = QtGui.QTabWidget(self)
        tabWidget.resize(479,309)
        
        tabWidget.addTab(pomoTab, self.getString("tab_pomo"))
        tabWidget.addTab(tasksTab, self.getString("tab_tasks"))
        tabWidget.addTab(activityTab, self.getString("tab_activity"))

        self.show()
        
    def initAudio(self):
        """
        Detects an ALSA audio device and buffers our ringtone.
        """
        # Detect an ALSA audio device
        self.audioDevice = alsaaudio.PCM()

        # Open the ringtone and set some audio settings.
        ring = wave.open("/usr/share/pomodorino/ring.wav", 'rb')
        self.audioDevice.setchannels(ring.getnchannels())
        self.audioDevice.setrate(ring.getframerate())
        self.audioDevice.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.audioDevice.setperiodsize(320)
        
        # Read the audio data of the ringtone.
        self.audioData = list()
        buf = ring.readframes(320)
        while buf:
            self.audioData.append(buf)
            buf = ring.readframes(320)

    def closeEvent(self, event):
        """
        Prevents accidental shutdowns by asking the user.
        """
        if self.timerActive:
            self.stopTimer()
            
            if self.promptUser("ask_paused"):
                event.accept()
            else:
                event.ignore()
                self.startTimer(0, restart=True)
        else:
            event.accept()

    def changeEvent(self, event):
        """
        Catches the minimizing event and restores the window state.
        """
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                if self.trayIcon.isSystemTrayAvailable():
                    # Restore window state so that the window won't be 
                    # hidden when the user clicks on the tray icon.
                    self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized)
                    self.setVisible(False)
        event.accept()

    def setTitle(self, title):
        """
        Sets the window title.
        """
        if title is None:
            title = self.getString("app_name")
        else:
            title += " - " + self.getString("app_name")

        self.window().setWindowTitle(title)

    def startTimer(self, timeSpan, restart=False):
        """
        Starts the timer.
        """
        if restart is False:
            self.timerType = timeSpan
            self.timerCount = timeSpan * 60
        self.timerActive = True
        self.timer.start(1000)

    def stopTimer(self):
        """
        Stops the timer.
        """
        self.timerActive = False
        self.timer.stop()

    def resetTimer(self):
        """
        Resets the timer.
        """
        self.stopTimer()
        self.timerCount = 0

    def finishTimer(self, task):
        """
        Is called once the timer finished.
        """
        self.resetTimer()
        # Define the regular length of a pomodoro. Mainly for debugging reasons
        POMO_CONST = 25
        pomos = math.floor(self.timerType / POMO_CONST)
        self.setVisible(True)
        if pomos >= 1 and task != '':
            newTask = self.pomo.pomoData.addPomo(task, pomos)
            if newTask == True:
                self.pomoTaskBar.addItem(taskName, None)
            self.fillActivityTab()
            self.updateTasksTab()

    def trayClick(self, reason):
        """
        Is called when the user clicks on the tray icon.
        """
        if reason == 2 or reason == 3:
            if self.isVisible():
                self.setVisible(False)
            else:
                self.setVisible(True)

    ##############
    ## Pomo Tab ##
    ##############
        
    def initPomoTab(self):
        """
        Creates the layout of the pomodoro tab
        """
        pomoTab = QtGui.QWidget()

        # Create a combobox with a lineedit for task selection.
        taskBar = QtGui.QComboBox()
        taskBar.setEditable(True)
        taskBarLine = taskBar.lineEdit()
        taskBarLine.setMaxLength(64)
        taskBarLine.setPlaceholderText(self.getString("input_task"))
        taskBar.setFixedSize(375,32)
        taskBar.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        taskBar.setStyleSheet('font-size: 11pt;')
        taskBar.addItem("", None)
        self.pomoTaskBar = taskBar

        # Add all the task names.
        tasks = self.pomo.pomoData.tasks
        for taskID, taskName, pomoCount, pomoLast in tasks:
            taskBar.addItem(taskName, None)
        
        # Create the main button.
        mainBtn = QtGui.QPushButton(self.getString("btn_start"), pomoTab)
        mainBtn.setFixedSize(180, 60)
        mainBtn.setStyleSheet('font-size: 17pt;')

        # Create the 25 min button.
        timeBtn = QtGui.QPushButton(self.getString("lbl_regularpomo"), pomoTab)
        timeBtn.setToolTip(self.getString("ttp_regularpomo"))
        timeBtn.setFixedSize(50, 25)
        timeBtn.setStyleSheet('font-size: 9pt;')
        
        # Create the 50 min button.
        longTimeBtn = QtGui.QPushButton(self.getString("lbl_longpomo"), pomoTab)
        longTimeBtn.setToolTip(self.getString("ttp_longpomo"))
        longTimeBtn.setFixedSize(50, 25)
        longTimeBtn.setStyleSheet('font-size: 9pt;')

        # Create the 5 min button.
        pauseBtn = QtGui.QPushButton(self.getString("lbl_shortpause"), pomoTab)
        pauseBtn.setToolTip(self.getString("ttp_shortpause"))
        pauseBtn.setFixedSize(50, 25)
        pauseBtn.setStyleSheet('font-size: 9pt;')

        # Create the 10 min button.
        longPauseBtn = QtGui.QPushButton(self.getString("lbl_longpause"), pomoTab)
        longPauseBtn.setToolTip(self.getString("ttp_longpause"))
        longPauseBtn.setFixedSize(50, 25)
        longPauseBtn.setStyleSheet('font-size: 9pt;')
        
        # Select 25 min button as default on startup.
        timeBtn.setDisabled(True)
        self.pomoButtonActive = timeBtn

        # Save button references for later usage.
        self.pomoBtns = dict()
        self.pomoBtns['main'] = mainBtn
        self.pomoBtns['time'] = timeBtn
        self.pomoBtns['longTime'] = longTimeBtn
        self.pomoBtns['pause'] = pauseBtn
        self.pomoBtns['longPause'] = longPauseBtn

        # Connect the buttons to the handler function.
        for name, button in self.pomoBtns.items():
            button.clicked.connect(self.onClicked)

        # Create and set the layout.
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
        vbox.addStretch()
        vbox.addLayout(firstRow)
        vbox.addStretch()
        vbox.addLayout(secondRow)
        vbox.addStretch()
        vbox.addLayout(thirdRow)
        vbox.addStretch()
        
        pomoTab.setLayout(vbox) 
        
        return pomoTab

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

        if self.timerActive:
            self.stopTimer()
            # Ask the user whether he wants to reset the running timer.
            if self.promptUser("ask_paused"):
                self.resetPomoTab()
                self.resetTimer()
            else:
                self.startTimer(0, restart=True)
        else:
            newText = self.pomoTaskBar.currentText().strip()
            self.pomoTaskBar.setEditText(newText)

            if newText != "" or self.pomoTaskBar.isEnabled() is False:
                self.pomoTaskBar.setDisabled(True)
                for k,v in self.pomoBtns.items():
                    if k != 'main':
                        v.setDisabled(True)
                timeSpan = int(self.pomoButtonActive.text())
                title = "{0:0>2}:00".format(timeSpan)
                sender.setText(title)
                self.setTitle(title)
                self.startTimer(timeSpan)
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
            
            if sender == self.pomoBtns['pause'] or sender == self.pomoBtns['longPause']:
                self.pomoTaskBar.setDisabled(True)
            else:
                self.pomoTaskBar.setDisabled(False)

    def resetPomoTab(self):
        """
        Resets the button states in the pomo tab.
        """
        if self.pomoButtonActive != self.pomoBtns['pause'] and self.pomoButtonActive != self.pomoBtns['longPause']:   
            self.pomoTaskBar.setDisabled(False)
            
        self.pomoBtns['main'].setText("start")
        for k,v in self.pomoBtns.items():
            if k != 'main' and v is not self.pomoButtonActive:
                v.setDisabled(False)

        # Also reset the window title.
        self.setTitle(None)
            
    def tick(self):
        """
        Updates the GUI every second when the timer is running.
        """
        self.timerCount -= 1
        
        timeStr = "{0:0>2}:{1:0>2}".format(math.floor(self.timerCount / 60), self.timerCount % 60) 
        self.pomoBtns['main'].setText(timeStr)
        # Show current time in the title.
        self.setTitle(timeStr)
            
        # Timer finished?
        if self.timerCount == 0:
            self.playRingtone()
            self.finishTimer(self.pomoTaskBar.currentText())
            self.resetPomoTab()

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
            
    ###############
    ## tasks tab ##
    ###############
    
    def initTasksTab(self):
        """
        Creates the layout of the tasks tab.
        """
        tasksTab = QtGui.QWidget()

        self.tasksTable = self.fillTasksTable()
        self.tasksVBox = QtGui.QVBoxLayout()
        self.tasksVBox.addWidget(self.tasksTable)
        self.tasksTable.sortItems(0)
        
        tasksTab.setLayout(self.tasksVBox)
        return tasksTab

    def fillTasksTable(self):
        """
        Fills the table in the tasks tab.
        """
        tasks = self.pomo.pomoData.tasks
        self.taskTableSelChange = False

        # Create a table with three columns.
        table = QtGui.QTableWidget(len(tasks),3)
        table.itemSelectionChanged.connect(self.taskListSelectionChanged)
        table.itemClicked.connect(self.taskListClick)
        table.setShowGrid(True)
        table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        table.setFocusPolicy(QtCore.Qt.NoFocus)
        table.setHorizontalHeaderLabels([self.getString("lbl_stats_task"), self.getString("lbl_stats_pomos"), self.getString("lbl_stats_last")])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setHighlightSections(False)
        
        # Create a context menu for the table.
        def ctMenuEvent(event):
            self.taskTableSelChange = False
            menu = QtGui.QMenu(table)
            rnAct = menu.addAction("Rename", self.renameTask)
            dlAct = menu.addAction("Delete", self.deleteTask)
            menu.popup(QtGui.QCursor.pos())
            if self.timerActive and self.pomoTaskBar.currentText() == self.tasksTable.selectedItems()[0].text():
                    rnAct.setEnabled(False)
                    dlAct.setEnabled(False)

        table.contextMenuEvent = ctMenuEvent
        
        # Columwidth depends on the existence of a scrollbar.
        if len(tasks) <= 7:
            table.setColumnWidth(0, 345)
        else:
            table.setColumnWidth(0, 329)
        table.setColumnWidth(1, 48)
        table.setColumnWidth(2, 60)
        
        # There must be a row counter since the taskID can be different.
        rowCount = 0

        # Fill the table rows.
        for taskID, taskName, pomoCount, pomoLast in tasks:
            # First column: taskName
            item = QtGui.QTableWidgetItem()
            item.setText(taskName)
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            table.setItem(rowCount, 0, item)

            # Second column: pomoCount
            item = QtGui.QTableWidgetItem()
            item.setText(str(pomoCount))
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            item.setToolTip("~" + str(round((pomoCount * 25) / 60, 1)) + "h")
            table.setItem(rowCount, 1, item)
            
            # Third column: pomoLast
            pomoLastDate = datetime.datetime.fromtimestamp(pomoLast)
            item = QtGui.QTableWidgetItem()
            item.setText(pomoLastDate.strftime("%x"))
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            table.setItem(rowCount, 2, item)

            rowCount += 1
        return table

    def updateTasksTab(self):
        """
        Updates the pomodoro statistics in the tasks tab.
        """
        self.tasksVBox.removeWidget(self.tasksTable)
        self.tasksTable.close()
        self.tasksTable = self.fillTasksTable()
        self.tasksVBox.insertWidget(0, self.tasksTable)

    def taskListSelectionChanged(self):
        """
        Sets a flag when the selection in the task table was changed.
        """
        if self.tasksTable.selectedItems() != []:
            self.taskTableSelChange = True

    def taskListClick(self, item):
        """
        Detects when an item in the task table was clicked and clears selection if necessary.
        """
        if self.taskTableSelChange == False:
            self.tasksTable.clearSelection()
        self.taskTableSelChange = False
        
    def deleteTask(self):
        """
        Deletes a task by the users request.
        """
        taskName = self.tasksTable.selectedItems()[0].text()
        okay = self.promptUser("ask_taskdel", additional=taskName)
        if okay:
            # Delete entry from GUI
            pbID = self.pomoTaskBar.findText(taskName)
            self.pomoTaskBar.removeItem(pbID)
        
            stID = self.activitySelTask.findText(taskName)
            self.activitySelTask.removeItem(stID)

            rownum = self.tasksTable.row(self.tasksTable.selectedItems()[0])
            self.tasksTable.removeRow(rownum)
            
            if self.tasksTable.rowCount() <= 7:
                self.tasksTable.setColumnWidth(0, 345)
            
            # Delete entry from db and cache
            taskID = self.pomo.pomoData.getTaskID(taskName)
            self.pomo.pomoData.delTask(taskID)

    def renameTask(self, warn=""):
        """
        Renames a task by the users request.
        """
        oldname = self.tasksTable.selectedItems()[0].text()
        name, okay = QtGui.QInputDialog.getText(self, self.getString("lbl_rename_task"), warn, text=oldname)
        if okay and name != '' and name != oldname:
            try:
                self.pomo.pomoData.getTaskID(name)
                self.renameTask(self.getString("lbl_rename_taken"))
            except KeyError:
                # Update entry in GUI
                self.tasksTable.selectedItems()[0].setText(name)
                
                pbID = self.pomoTaskBar.findText(oldname)
                self.pomoTaskBar.setItemText(pbID, name)

                stID = self.activitySelTask.findText(oldname)
                self.activitySelTask.setItemText(stID, name)
                
                # Update entry in db and cache
                tID = self.pomo.pomoData.getTaskID(oldname)
                self.pomo.pomoData.renameTask(tID, name)

    ##################
    ## activity tab ##
    ##################

    def initActivityTab(self):
        """
        Creates the layout of the activity tab and prepares the graph.
        """
        activityTab = QtGui.QWidget()
        
        # Get the background color of the window to make the graph fit in.
        color = self.palette().color(QtGui.QPalette.Background)
        
        # Create a fixed-size canvas for the graph.
        self.figure = plt.figure(facecolor=color.name(), tight_layout=False)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFixedSize(460,236)

        # Set default values for some attributes used in fillActivityTab
        self.lockYLim = False
        self.intervalShift = 0
        self.intervalScale = 3 # [3] days - [2] weeks - [1] months
        self.activityTaskID = 0

        # Combobox for selecting the active task to be displayed.
        selTask = QtGui.QComboBox()
        selTask.insertItem(0, self.getString("lbl_stats_all"), None)
        for tID, tskName, pomoCount, pomoLast in self.pomo.pomoData.tasks:
            selTask.insertItem (0, tskName, None)
            
        selTask.currentIndexChanged['QString'].connect(self.onChangeTask)
        # Save handle for later use.
        self.activitySelTask = selTask

        # Navigation buttons to change the active timespan.
        farLeftButton = QtGui.QPushButton("<<", activityTab)
        farLeftButton.setStyleSheet('font-size: 12pt;')
        farLeftButton.setFixedSize(30,20)
        farLeftButton.clicked.connect(self.timeNavigate)
        # Save the handle for toggling the button state
        self.farLeftButtonHandle = farLeftButton

        farRightButton = QtGui.QPushButton(">>", activityTab)
        farRightButton.setStyleSheet('font-size: 12pt;')
        farRightButton.setFixedSize(30,20)
        farRightButton.setDisabled(True)
        farRightButton.clicked.connect(self.timeNavigate)
        # Save the handle for toggling the button state.
        self.farRightButtonHandle = farRightButton

        leftButton = QtGui.QPushButton("<", activityTab)
        leftButton.setStyleSheet('font-size: 12pt;')
        leftButton.setFixedSize(30,20)
        leftButton.clicked.connect(self.timeNavigate)
        # Save the handle for toggling the button state
        self.leftButtonHandle = leftButton
        
        rightButton = QtGui.QPushButton(">", activityTab)
        rightButton.setStyleSheet('font-size: 12pt;')
        rightButton.setFixedSize(30,20)
        rightButton.setDisabled(True)
        rightButton.clicked.connect(self.timeNavigate)
        # Save the handle for toggling the button state.
        self.rightButtonHandle = rightButton

        # Disable left navigation buttons when there are no finished pomos.
        if self.pomo.pomoData.firstPomo == 0:
            leftButton.setDisabled(True)
            farLeftButton.setDisabled(True)

        # Zoom buttons to change the active timespan.
        zoomOutButton = QtGui.QPushButton("−", activityTab)
        zoomOutButton.setStyleSheet('font-size: 12pt;')
        zoomOutButton.setFixedSize(30,20)
        zoomOutButton.clicked.connect(self.timeZoom)
        # Save the handle for toggling the button state.
        self.zoomOutButtonHandle = zoomOutButton
        
        zoomInButton = QtGui.QPushButton("+", activityTab)
        zoomInButton.setStyleSheet('font-size: 12pt;')
        zoomInButton.setFixedSize(30,20)
        zoomInButton.setDisabled(True)
        zoomInButton.clicked.connect(self.timeZoom)
        # Save the handle for toggling the button state.
        self.zoomInButtonHandle = zoomInButton

        # Get highest pomo count on a single day.
        self.highestPomoCount = list()
        
        self.highestPomoCount.append(self.pomo.pomoData.getHighestPomoCountMonthly())
        self.highestPomoCount.append(self.pomo.pomoData.getHighestPomoCountWeekly())
        self.highestPomoCount.append(self.pomo.pomoData.getHighestPomoCountDaily())

        # Draw the graph.
        self.fillActivityTab()

        # Create and set the layout.
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout2 = QtGui.QHBoxLayout()
        layout2.addWidget(farLeftButton)
        layout2.addWidget(leftButton)
        layout2.addWidget(rightButton)
        layout2.addWidget(farRightButton)
        layout2.addStretch()
        layout2.addWidget(zoomOutButton)
        layout2.addWidget(zoomInButton)
        layout2.addStretch()
        layout2.addWidget(selTask)
        layout.addLayout(layout2)

        activityTab.setLayout(layout) 
        return activityTab

    def fillActivityTab(self):
        """
        Fills and displays the bar graph in the activity tab.
        """
        taskID = self.activityTaskID

        # First get the absolute value of today.
        today = datetime.date.today()
        delta = datetime.timedelta(days=1)

        # Now construct shiftable intervals.
        beginInt = datetime.datetime
        endInt = datetime.datetime

        # Default scale (days): Begin interval at midnight of today.
        beginInt = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
        shiftDelta = delta

        if self.intervalScale == 2:     # Scale: Weeks
            # Begin interval at midnight of this weeks monday.
            weekDayNum = calendar.weekday(today.year, today.month, today.day)
            beginInt = beginInt - delta * weekDayNum
            shiftDelta = 7 * delta
        elif self.intervalScale == 1:   # Scale: Months
            # Begin interval at midnight of the first day of the month.
            beginInt = datetime.datetime(today.year, today.month, 1, 0, 0, 0)
            shiftDelta = 30 * delta
        self.shiftDelta = shiftDelta
        
        # Get the data of the last units since today.
        units = list()
        values = list()
        size = 6 + self.intervalScale
        
        for i in range(size):
            # Shift
            offset = (size-i-1-self.intervalShift)
            shiftedBegin = beginInt - offset * shiftDelta
            # When scaled to months, an arithmetical shift is not practical.
            if self.intervalScale == 1:
                yearDiff, monDiff = divmod(offset, 12)
                newMon = beginInt.month - monDiff
                if newMon < 0:
                    newMon = 12 + newMon
                    yearDiff += 1

                if newMon == 0:
                    newMon = 12
                    yearDiff += 1
                
                shiftedBegin = datetime.datetime(beginInt.year - yearDiff, newMon, 1, 0, 0, 0)
            shiftedEnd = datetime.datetime

            if self.intervalScale == 3:
                units.append(str(shiftedBegin.month) + "/" + str(shiftedBegin.day))
                shiftedEnd = datetime.datetime(shiftedBegin.year, shiftedBegin.month, shiftedBegin.day, 23, 59, 59)
            elif self.intervalScale == 2:
                units.append(shiftedBegin.strftime("CW %W"))
                shiftedEnd = datetime.datetime(shiftedBegin.year, shiftedBegin.month, shiftedBegin.day, 23, 59, 59)
                shiftedEnd = shiftedEnd + delta * 6
            else:
                units.append(shiftedBegin.strftime("%b %y"))
                lastDay = calendar.monthrange(shiftedBegin.year, shiftedBegin.month)[1]
                shiftedEnd = datetime.datetime(shiftedBegin.year, shiftedBegin.month, lastDay, 23, 59, 59)
            timeInt = [int(shiftedBegin.timestamp()), int(shiftedEnd.timestamp())]
            values.append(self.pomo.pomoData.getPomoCount(timeInt, taskID))

        # Disable left buttons once we scrolled far enough
        if self.pomo.pomoData.firstPomo != 0:
            shiftedBegin = beginInt - (size-1-self.intervalShift) * shiftDelta
            self.shiftedBegin = shiftedBegin
            if shiftedBegin.timestamp() <= self.pomo.pomoData.firstPomo:
                self.leftButtonHandle.setDisabled(True)
                self.farLeftButtonHandle.setDisabled(True)
            else:
                self.leftButtonHandle.setDisabled(False)
                self.farLeftButtonHandle.setDisabled(False)

        # Create a new subplot.
        ax = self.figure.add_subplot(111)
        ax.hold(False)

        # Create the bar graphs
        bars = ax.bar(list(range(1, size+1)),values, width=0.4, align="center", color="#E04B3F")
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x()+bar.get_width()/2., height+0.08, '%d'%int(height), ha='center', va='bottom', weight="medium")
        plt.xticks(list(range(1, size+1)), units)

        # y-Limit of the graph depends on the maximum bar height.
        yLim = self.highestPomoCount[self.intervalScale-1] * 1.24
        
        # To avoid rescaling the graph when changing the task, we lock the
        # y-Limit to the first one generated after startup.  
        if self.lockYLim is False:
            if yLim == 0:
                # When no pomodoros have been done, use a constant y-Limit.
                yLim = 15
            else:
                self.lockYLim = True
            self.yLim = yLim
        else:
            # Update the y-Limit when it exceeds the saved one.
            if yLim > self.yLim:
                self.yLim = yLim
        
        # Set the graph limits.        
        ax.set_ylim([0, self.yLim])
        ax.set_xlim([0.5, size+0.5])

        # Additional plot and graph settings.
        plt.subplots_adjust(left=0, right=0.99, top=1, bottom=0.087)
        ax.get_yaxis().set_visible(False)
        plt.minorticks_off()
        for tick in ax.get_xticklines():
            tick.set_visible(False)

        # Write currently viewed month and year in the upper right corner,
        # when zoomed out, only display the year.
        if self.intervalScale != 1:
            tempDate = beginInt - (size-1-self.intervalShift) * shiftDelta
            dateString = tempDate.strftime("%b %Y")
            if self.intervalScale != 3:
                dateString = tempDate.strftime("%Y") 
                
            plt.text(0.99, 0.937, dateString, horizontalalignment='right', verticalalignment='center', transform=ax.transAxes, weight="bold")

        # Show.
        self.canvas.draw()

    def timeNavigate(self):
        """
        Handling function for the navigation buttons in the activity tab.
        """
        sender = self.sender()
        
        if sender.text() == '<':
            self.intervalShift -= 6
            self.rightButtonHandle.setDisabled(False)
            self.farRightButtonHandle.setDisabled(False)
        elif sender.text() == '>':
            self.intervalShift += 6
            self.leftButtonHandle.setDisabled(False)
            self.farLeftButtonHandle.setDisabled(False)
            if self.intervalShift == 0:
                # Once we hit todays date, disable the right button.
                sender.setDisabled(True)
                self.farRightButtonHandle.setDisabled(True)
        elif sender.text() == '<<':
            sender.setDisabled(True)
            self.leftButtonHandle.setDisabled(True)
            self.rightButtonHandle.setDisabled(False)
            self.farRightButtonHandle.setDisabled(False)

            date = self.shiftedBegin
            while date.timestamp() >= self.pomo.pomoData.firstPomo:
                self.intervalShift -= 6
                date -= 6 * self.shiftDelta
        elif sender.text() == '>>':
            self.intervalShift = 0
            sender.setDisabled(True)
            self.rightButtonHandle.setDisabled(True)
            self.leftButtonHandle.setDisabled(False)
            self.farLeftButtonHandle.setDisabled(False)

        self.fillActivityTab()

    def timeZoom(self):
        """
        Handling function for the zoom buttons in the activity tab.
        """
        sender = self.sender()
        
        # Always reset the navigation while zooming
        self.intervalShift = 0
        self.lockYLim = False

        if self.pomo.pomoData.firstPomo != 0:
            self.leftButtonHandle.setDisabled(False)
            self.farLeftButtonHandle.setDisabled(False)
        self.rightButtonHandle.setDisabled(True)
        self.farRightButtonHandle.setDisabled(True)
        
        # Zoom Out:
        if sender.text() == '−':
            self.intervalScale -= 1
            if self.intervalScale == 1:
                self.zoomOutButtonHandle.setDisabled(True)
            self.zoomInButtonHandle.setDisabled(False)
        # Zoom In:
        else:
            self.intervalScale += 1
            if self.intervalScale == 3:
                sender.setDisabled(True)
            self.zoomOutButtonHandle.setDisabled(False)

        self.fillActivityTab()

    def onChangeTask(self, string=str()):
        """
        Will be called when the user changes the task in the activity tab.
        """
        try:
            self.activityTaskID = self.pomo.pomoData.getTaskID(string)
        except KeyError:
            self.activityTaskID = 0
        self.fillActivityTab()

    def promptUser(self, identifier, additional=None):
        """
        Creates predefined confirmation/warning dialogs.
        """
        if identifier == 'ask_paused':
            reply = QtGui.QMessageBox.question(self, self.getString("ask_paused_title"), self.getString("ask_paused_text"),
                                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.Yes:
                return True
            else:
                return False

        elif identifier == 'warn_notask':
            QtGui.QMessageBox.warning(self,
                    self.getString("warn_notask_title"),
                    self.getString("warn_notask_text"))
            return

        elif identifier == 'ask_taskdel' and additional != None:
            askText = self.getString("ask_taskdel_text")
            askText = str.replace(askText, "%taskname%", str(additional))
            
            reply = QtGui.QMessageBox.question(self, self.getString("ask_taskdel_title"), askText,
                                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.Yes:
                return True
            else:
                return False

        raise KeyError

def initGUI(pomo):
    app = QtGui.QApplication(sys.argv)
    pomoGUI = PomoWindow(pomo)
    pomo.pomoGUI = pomoGUI
    sys.exit(app.exec_())
