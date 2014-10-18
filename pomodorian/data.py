import os
import time
import threading

from pomodorian.utils import *

import sqlite3


class PomoData():
    def __init__(self, pomo):
        super(PomoData, self).__init__()
        self.pomo = pomo
        self.connected = False
        
        self.initDB()
        
    def initDB(self):
        dbPath = os.path.expanduser("~/.local/share/pomodorian/");   
        
        if not os.path.exists(dbPath):
            os.makedirs(dbPath)
        
        self.conn = sqlite3.connect(dbPath+"pomo.db", check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute('SELECT SQLITE_VERSION()')
    
        data = self.c.fetchone()
    
        self.connected = True
        self.createDB()
        self.readDB()
        
        
    def createDB(self):
        if self.connected is True:
            self.c.execute("CREATE TABLE IF NOT EXISTS Tasks(ID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT)")
            self.c.execute("CREATE TABLE IF NOT EXISTS Pomos(Timestamp INT, TaskID INT)")
            self.conn.commit()
        else:
            pass
            #raise exception

    
    def addPomo(self, taskName, pomos):
        if self.connected is True:
            taskID, newTask = self.getTaskID(taskName)
            for i in range(0, pomos):
                statement = "INSERT INTO Pomos(Timestamp, TaskID) VALUES(" + str(int(time.time()) - ((i+1) * 25 * 60)) + "," + str(taskID) + ")"
                self.c.execute(statement)
                #timestamp indicates beginning of a pomo
            self.conn.commit()
            return newTask
        
    def getTaskID(self, name):
        # since we assume that the number of tasks will be far less than 1000 for most users, optimization has low priority at the moment
        for taskID, taskName, pomoCount, pomoLast in self.tasks:
            if taskName == name:
                return taskID, False
        return self.insertTask(name), True
        
        
    def getTasks(self):
        return self.tasks
        
        
    def insertTask(self, taskName):
        if self.connected is True:
            self.c.execute("INSERT INTO Tasks(Name) VALUES(\"" + taskName + "\")")
            self.conn.commit()
            taskID = self.c.lastrowid
            self.tasks.append((taskID, taskName, 0, 0))
            return taskID
        
    def readDB(self):
        if self.connected is True:
            self.c.execute("SELECT * FROM Tasks ORDER BY ID ASC")
            tasks = self.c.fetchall()
            
            self.c.execute("SELECT TaskID, count(TaskID), MAX(Timestamp) FROM Pomos GROUP BY TaskID ORDER BY TaskID ASC")
            pomoData = self.c.fetchall()
            
            self.tasks = list()
            counter = 0
            for taskID, taskName in tasks:
                data = pomoData[counter]
                pomoCount = data[1]
                pomoLast = data[2]
                
                self.tasks.append([taskID, taskName, pomoCount, pomoLast])
                counter += 1
        
        
    def closeDB(self):
        if self.connected is True:
            self.conn.close()
        
    


def initData(pomo):
    pomoData = PomoData(pomo)
    pomo.setData(pomoData)
