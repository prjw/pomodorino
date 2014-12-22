import sys
import datetime
import math
import wave
import threading


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
        self.initUI()
        self.initAudio()
        self.tasksRefresh = False


    def initUI(self):      
        """
        Initializes the UI.
        """
        # Set some general window settings.
        self.setFixedSize(480, 310)
        self.move(250,250)
        self.setWindowTitle(self.getString("main", "app_name"))
        self.setWindowIcon(QtGui.QIcon('/usr/share/icons/pomodorino.png'))

        
        # Initialize and display the tabs
        pomoTab = self.initPomoTab()
        tasksTab = self.initTasksTab()
        activityTab = self.initActivityTab()
        statsTab = self.initStatsTab()
        
        tabWidget = QtGui.QTabWidget(self)
        tabWidget.resize(479,309)
        
        tabWidget.addTab(pomoTab, self.getString("gui", "tab_pomo"))
        tabWidget.addTab(tasksTab, self.getString("gui", "tab_tasks"))
        tabWidget.addTab(activityTab, self.getString("gui", "tab_activity"))
        tabWidget.addTab(statsTab, self.getString("gui", "tab_stats"))
        tabWidget.currentChanged.connect(self.onChangeTab)

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


    def onChangeTab(self, index=-1):
        """
        Function handler for whenever a tab is changed.
        """
        if index == 1:
            self.updateTasksTab()
        elif index == 2:
            self.fillTasksTable()
        elif index == 3:
            self.updateStatsTab()


    def closeEvent(self, event):
        """
        Prevents accidental shutdowns by asking the user.
        """
        if self.pomo.timerActive:
            self.pomo.stopTimer()
            
            if self.promptUser("ask_paused"):
                event.accept()
            else:
                event.ignore()
                self.pomo.startTimer(0, restart=True)
        else:
            event.accept()


    def getString(self, cat, identifier):
        """
        Calls the pomo getString function to enhance readability.
        """
        return self.pomo.getString(cat, identifier)


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
        taskBarLine.setPlaceholderText(self.getString("gui", "input_task"))
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
        mainBtn = QtGui.QPushButton(self.getString("gui", "btn_start"), pomoTab)
        mainBtn.setFixedSize(180, 60)
        mainBtn.setStyleSheet('font-size: 17pt;')


        # Create the 25 min button.
        timeBtn = QtGui.QPushButton(
                self.getString("gui", "lbl_regularpomo"), pomoTab)
        timeBtn.setToolTip(self.getString("gui", "ttp_regularpomo"))
        timeBtn.setFixedSize(50, 25)
        timeBtn.setStyleSheet('font-size: 9pt;')

        
        # Create the 50 min button.
        longTimeBtn = QtGui.QPushButton(
                self.getString("gui", "lbl_longpomo"), pomoTab)
        longTimeBtn.setToolTip(self.getString("gui", "ttp_longpomo"))
        longTimeBtn.setFixedSize(50, 25)
        longTimeBtn.setStyleSheet('font-size: 9pt;')


        # Create the 5 min button.
        pauseBtn = QtGui.QPushButton(
                self.getString("gui", "lbl_shortpause"), pomoTab)
        pauseBtn.setToolTip(self.getString("gui", "ttp_shortpause"))
        pauseBtn.setFixedSize(50, 25)
        pauseBtn.setStyleSheet('font-size: 9pt;')
        

        # Create the 10 min button.
        longPauseBtn = QtGui.QPushButton(
                self.getString("gui", "lbl_longpause"), pomoTab)
        longPauseBtn.setToolTip(self.getString("gui", "ttp_longpause"))
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

        if self.pomo.timerActive:
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


    

            
    def receiveTick(self, timerCount):
        """
        Updates the GUI every second when the timer is running.
        """
        if self.pomo.timerActive:
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
        
        tasksTab.setLayout(self.tasksVBox)
        return tasksTab


    def fillTasksTable(self):
        """
        Fills the table in the tasks tab.
        """
        tasks = self.pomo.pomoData.tasks

        # Create a table with three columns.
        table = QtGui.QTableWidget(len(tasks),3)
        table.setShowGrid(True)
        table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        table.setHorizontalHeaderLabels([self.getString("gui", "lbl_stats_task"),
                self.getString("gui", "lbl_stats_pomos"),
                self.getString("gui", "lbl_stats_last")])

        table.verticalHeader().setVisible(False)
        table.setColumnWidth(0, 345)
        table.setColumnWidth(1, 48)
        table.setColumnWidth(2, 60)


        # There must be a row counter since the taskID can be different.
        rowCount = 0


        # Fill the table rows.
        for taskID, taskName, pomoCount, pomoLast in tasks:
            # First column: taskName
            item = QtGui.QTableWidgetItem()
            item.setText(taskName)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            table.setItem(rowCount, 0, item)


            # Second column: pomoCount
            item = QtGui.QTableWidgetItem()
            item.setText(str(pomoCount))
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            item.setToolTip("~" + str(round((pomoCount * 25) / 60, 1)) + "h")
            table.setItem(rowCount, 1, item)

            
            # Third column: pomoLast
            pomoLastDate = datetime.datetime.fromtimestamp(pomoLast)
            item = QtGui.QTableWidgetItem()
            item.setText(pomoLastDate.strftime("%x"))
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            table.setItem(rowCount, 2, item)

            rowCount += 1

        
        return table


    def doTasksRefresh(self):
        """
        Forces a tasks tab refresh once the user clicks on it the next time.
        Cannot do a real refresh here because of threading issues.
        """
        self.tasksRefresh = True


    def updateTasksTab(self):
        """
        Updates the pomodoro statistics in the tasks tab.
        """
        if self.tasksRefresh is True:
            self.tasksVBox.removeWidget(self.tasksTable)
            self.tasksTable = self.fillTasksTable()
            self.tasksVBox.insertWidget(0, self.tasksTable)
            self.tasksRefresh = False


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
        self.activityTaskID = 0


        # Draw the graph.
        self.fillActivityTab()


        # Combobox for selecting the active task to be displayed.
        selTask = QtGui.QComboBox()
        selTask.insertItem(0, self.getString("gui", "lbl_stats_all"), None)
        for tID, tskName, pomoCount, pomoLast in self.pomo.pomoData.tasks:
            selTask.insertItem (0, tskName, None)
            
        selTask.currentIndexChanged['QString'].connect(self.onChangeTask)


        # Navigation buttons to change the active timespan.
        leftButton = QtGui.QPushButton("<", activityTab)
        leftButton.setStyleSheet('font-size: 12pt;')
        leftButton.setFixedSize(30,20)
        leftButton.clicked.connect(self.timeNavigate)
        
        rightButton = QtGui.QPushButton(">", activityTab)
        rightButton.setStyleSheet('font-size: 12pt;')
        rightButton.setFixedSize(30,20)
        rightButton.setDisabled(True)
        rightButton.clicked.connect(self.timeNavigate)
        # Save the handle for toggling the button state.
        self.rightButtonHandle = rightButton 
        

        # Create and set the layout.
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout2 = QtGui.QHBoxLayout()
        layout2.addWidget(leftButton)
        layout2.addWidget(rightButton)
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


        # "Today" marks the end of our viewed interval and will be relative.
        delta = datetime.timedelta(days=1)
        today = datetime.date.today() + self.intervalShift * delta


        # Get the data of the ten last days since today.
        days = list()
        values = list()
        size = 10
        
        for i in range(size):
            tempDate = today-(size-1-i)*delta
            days.append(str(tempDate.month) + "/" + str(tempDate.day))
            first = datetime.datetime(tempDate.year, tempDate.month,
                tempDate.day, 0, 0, 0)
            last = first + datetime.timedelta(hours=23, minutes=59, seconds=59)
            timeInt = [int(first.timestamp()), int(last.timestamp())]
            values.append(self.pomo.pomoData.getPomoCount(timeInt, taskID))
                

        # Create a new subplot.
        ax = self.figure.add_subplot(111)
        ax.hold(False)


        # Create the bar graphs
        bars = ax.bar(list(range(1, size+1)),values, width=0.4, align="center", color="#E04B3F")
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x()+bar.get_width()/2., height+0.08, '%d'%int(height),
                ha='center', va='bottom', weight="medium")
        plt.xticks(list(range(1, size+1)), days)


        # y-Limit of the graph depends on the maximum bar height.
        yLim = max(values) * 1.22

        
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


        # Write currently viewed month and year in the upper right corner.
        tempDate = today - (size-1)*delta
        dateString = tempDate.strftime("%b %Y")
        plt.text(0.91, 0.937, dateString, horizontalalignment='center',
            verticalalignment='center', transform=ax.transAxes, weight="bold")


        # Show.
        self.canvas.draw()


    def timeNavigate(self, direction):
        """
        Handling function for the navigation buttons in the activity tab.
        """
        sender = self.sender()
        
        if sender.text() == '<':
            self.intervalShift -= 7
            self.rightButtonHandle.setDisabled(False)
            
        else:
            self.intervalShift += 7
            if self.intervalShift == 0:
                # Once we hit todays date, disable the right button.
                sender.setDisabled(True)

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


    ###############
    ## stats tab ##
    ###############
    

    def initStatsTab(self):
        """
        Creates the layout of the stats tab
        """
        statsTab = QtGui.QWidget()
        aboutText = QtGui.QLabel("todo")
        vbox = QtGui.QVBoxLayout()
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(aboutText)
        hbox.addStretch()
        vbox.addStretch()
        vbox.addLayout(hbox)
        vbox.addStretch()
        statsTab.setLayout(vbox)
        return statsTab


    def updateStatsTab(self):
        """
        Updates the displayed statistics in the stats tab.
        """
        pass


    def promptUser(self, identifier):
        """
        Creates predefined confirmation/warning dialogs.
        """
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



def initGUI(pomo):
    app = QtGui.QApplication(sys.argv)
    pomoGUI = PomoWindow(pomo)
    pomo.pomoGUI = pomoGUI
    sys.exit(app.exec_())
