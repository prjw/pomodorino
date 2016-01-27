import os
import time
import threading
import datetime
import calendar

import sqlite3

class PomoData():
    def __init__(self, pomo):
        """
        Makes necessary variable initializations and calls other init methods.
        """
        super(PomoData, self).__init__()
        self.pomo = pomo
        self.connected = False
        self.initDB()
        self.firstPomo = self.getEarliest()
        
    def initDB(self):
        """
        Connects to the DB and prepares the connection for further use.
        """
        dbPath = os.path.expanduser("~/.local/share/pomodorino/");   
        # Create a folder for the DB if necessary
        if not os.path.exists(dbPath):
            os.makedirs(dbPath)
        try:
            self.conn = sqlite3.connect(dbPath + "pomo.db", check_same_thread = False)
            self.c = self.conn.cursor()
            self.c.execute('SELECT SQLITE_VERSION()')
            data = self.c.fetchone()
            self.connected = True
            self.createDB()
            self.readDB()
        except:
            raise RuntimeError("No DB connection available.")
        
    def createDB(self):
        """
        Creates the database layout
        """
        if self.connected is True:
            self.c.execute("CREATE TABLE IF NOT EXISTS Tasks(ID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT)")
            self.c.execute("CREATE TABLE IF NOT EXISTS Pomos(Timestamp INT, TaskID INT)")
            self.conn.commit()
        else:
            raise RuntimeError("No DB connection available.")

    def readDB(self):
        """
        Reads the entire DB.
        """
        if self.connected is True:
            self.c.execute("SELECT * FROM Tasks ORDER BY Name COLLATE NOCASE ASC")
            tasks = self.c.fetchall()
            self.tasks = list()
            counter = 0
            for taskID, taskName in tasks:
                self.c.execute("SELECT count(TaskID), MAX(Timestamp) FROM Pomos WHERE TaskID = '" + str(taskID) + "'")
                pomoData = self.c.fetchall()
                pomoCount = pomoData[0][0]
                pomoLast = pomoData[0][1]
                self.tasks.append([taskID, taskName, pomoCount, pomoLast])
                counter += 1
        else:
            raise RuntimeError("No DB connection available.")

    def getEarliest(self):
        if self.connected is True:
            self.c.execute("SELECT Timestamp FROM Pomos ORDER BY Timestamp ASC")
            timestamp = self.c.fetchone()
            if timestamp is not None:
                return timestamp[0]
            return 0
        else:
            raise RuntimeError("No DB connection available.")
    
    def addPomo(self, taskName, pomos):
        """
        Adds a pomodoro, returns whether a new task had to be added to the DB.
        """
        if self.connected is True:
            newTask = False
            try:
                taskID = self.getTaskID(taskName)
            except KeyError:
                # taskName was not found, insert new task.
                taskID = self.insertTask(taskName)
                newTask = True
            pomoTime = 0
            for i in range(0, pomos):
                pomoTime = int(time.time()) - ((i+1) * 25 * 60)
                statement = ("INSERT INTO Pomos(Timestamp, TaskID) VALUES(" + str(pomoTime) + "," + str(taskID) + ")")
                self.c.execute(statement)
                # Timestamp indicates the beginning of a pomo
            # We need to update our local cache as well.
            tasks = list()
            for tID, tskName, pomoCount, pomoLast in self.tasks:
                if tskName == taskName:
                    pomoCount += pomos
                    pomoLast = pomoTime
                tasks.append([tID, tskName, pomoCount, pomoLast])
            self.tasks = tasks
            self.conn.commit()
            return newTask
        else:
            raise RuntimeError("No DB connection available.")
        
    def getTaskID(self, name):
        """
        Returns the ID of a given task or raises a KeyError.
        """
        for taskID, taskName, pomoCount, pomoLast in self.tasks:
            if taskName == name:
                return taskID
        raise KeyError

    def getPomoCount(self, timeInt, taskID=0):
        """
        Returns the number of pomos [of a task] done in a certain time interval.
        """
        if self.connected is True:
            statement = "SELECT count(TaskID) FROM Pomos WHERE "
            if taskID > 0:
                statement += "TaskID = '" + str(taskID) + "' AND "
            statement += ("Timestamp BETWEEN " + str(timeInt[0]) +" AND " + str(timeInt[1]))
            self.c.execute(statement)
            val = self.c.fetchall()
            return val[0][0]
        else:
            raise RuntimeError("No DB connection available.")
        
    def getHighestPomoCountDaily(self):
        """
        Returns the highest number of pomodoros done on a single day.
        """
        first = self.getEarliest()
        if first == 0:
            return 0
        temp = datetime.date.fromtimestamp(first)
        begin = datetime.datetime(temp.year, temp.month, temp.day)
        end = datetime.datetime(temp.year, temp.month, temp.day, 23, 59, 59)
        delta = datetime.timedelta(days=1)
        todayStamp = datetime.datetime.now().timestamp()
        pomoCount = 0
        while begin.timestamp() <= todayStamp:
            val = self.getPomoCount([begin.timestamp(), end.timestamp()])
            if val > pomoCount:
                pomoCount = val
            begin += delta
            end += delta
        return pomoCount

    def getHighestPomoCountWeekly(self):
        """
        Returns the highest number of pomodoros done in a single week.
        """
        first = self.getEarliest()
        if first == 0:
            return 0
        temp = datetime.date.fromtimestamp(first)
        begin = datetime.datetime(temp.year, temp.month, temp.day)
        begin = begin - datetime.timedelta(days=begin.weekday())
        temp = begin + datetime.timedelta(days=6)
        end = datetime.datetime(temp.year, temp.month, temp.day, 23, 59, 59)
        delta = datetime.timedelta(days=7)
        todayStamp = datetime.datetime.now().timestamp()
        pomoCount = 0
        while begin.timestamp() <= todayStamp:
            val = self.getPomoCount([begin.timestamp(), end.timestamp()])
            if val > pomoCount:
                pomoCount = val
            begin += delta
            end += delta
        return pomoCount

    def getHighestPomoCountMonthly(self):
        """
        Returns the highest number of pomodoros done in a single month.
        """
        first = self.getEarliest()
        if first == 0:
            return 0
        temp = datetime.date.fromtimestamp(first)
        begin = datetime.datetime(temp.year, temp.month, 1)
        lastDay = calendar.monthrange(begin.year, begin.month)[1]
        end = datetime.datetime(begin.year, begin.month, lastDay, 23, 59, 59)
        todayStamp = datetime.datetime.now().timestamp()
        pomoCount = 0
        while begin.timestamp() <= todayStamp:
            val = self.getPomoCount([begin.timestamp(), end.timestamp()])
            if val > pomoCount:
                pomoCount = val

            month = begin.month + 1
            year = begin.year
            if month == 13:
                month = 1
                year += 1
            begin = datetime.datetime(year, month, 1)
            lastDay = calendar.monthrange(year, month)[1]
            end = datetime.datetime(year, month, lastDay, 23, 59, 59)
        return pomoCount    

    def insertTask(self, taskName):
        """
        Inserts a new task into the database and our local cache.
        """
        if self.connected is True:
            self.c.execute("INSERT INTO Tasks(Name) VALUES(\"" + taskName + "\")")
            self.conn.commit()
            taskID = self.c.lastrowid
            self.tasks.append((taskID, taskName, 0, 0))
            return taskID
        else:
            raise RuntimeError("No DB connection available.")

    def renameTask(self, taskID, newName):
        """
        Renames a task in the db and updates local cache.
        """
        if self.connected is True:
            # Update local cache
            tasks = list()
            for tID, taskName, pomoCount, pomoLast in self.tasks:
                if tID == taskID:
                    taskName = newName
                tasks.append([tID, taskName, pomoCount, pomoLast])
            self.tasks = tasks

            # Update DB
            statement = ("UPDATE Tasks SET Name = '" + newName + "' WHERE ID = " + str(taskID) + "")
            self.c.execute(statement)
            self.conn.commit()
        else:
            raise RuntimeError("No DB connection available.")
        

    def delTask(self, taskID):
        """
        Deletes a task with all pomos from the db and updates local cache.
        """
        if self.connected is True:
            tasks = list()
            for tID, taskName, pomoCount, pomoLast in self.tasks:
                if tID != taskID:
                    tasks.append([tID, taskName, pomoCount, pomoLast])
            self.tasks = tasks
            
            statement = ("DELETE FROM Tasks WHERE ID = " + str(taskID) + "")
            self.c.execute(statement)
            statement = ("DELETE FROM Pomos WHERE TaskID = " + str(taskID) + "")
            self.c.execute(statement)
            self.conn.commit()
        else:
            raise RuntimeError("No DB connection available.")
        
    def closeDB(self):
        """
        Closes the database connection
        """
        if self.connected is True:
            self.conn.close()
        else:
            raise RuntimeError("No DB connection available.")
        
def initData(pomo):
    pomoData = PomoData(pomo)
    pomo.pomoData = pomoData
