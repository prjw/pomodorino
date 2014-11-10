import os
import time
import threading

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
        
        
    def initDB(self):
        """
        Connects to the DB and prepares the connection for further use.
        """
        # TODO: cross-platform support
        dbPath = os.path.expanduser("~/.local/share/pomodorian/");   

        # Create a folder for the DB if necessary
        if not os.path.exists(dbPath):
            os.makedirs(dbPath)

        try:
            self.conn = sqlite3.connect(dbPath + "pomo.db",
                                        check_same_thread = False)
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
            self.c.execute("CREATE TABLE IF NOT EXISTS "
                           "Tasks(ID INTEGER PRIMARY KEY AUTOINCREMENT, "
                           "Name TEXT)")
                           
            self.c.execute("CREATE TABLE IF NOT EXISTS "
                           "Pomos(Timestamp INT, TaskID INT)")
            self.conn.commit()
        else:
            raise RuntimeError("No DB connection available.")


    def readDB(self):
        """
        Reads the entire DB.
        """
        if self.connected is True:
            self.c.execute("SELECT * FROM Tasks ORDER BY ID ASC")
            tasks = self.c.fetchall()
            
            self.c.execute("SELECT TaskID, count(TaskID), MAX(Timestamp) "
                           "FROM Pomos GROUP BY TaskID ORDER BY TaskID ASC")
                           
            pomoData = self.c.fetchall()
            
            self.tasks = list()
            counter = 0
            for taskID, taskName in tasks:
                data = pomoData[counter]
                pomoCount = data[1]
                pomoLast = data[2]
                self.tasks.append([taskID, taskName, pomoCount, pomoLast])
                counter += 1
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
                statement = ("INSERT INTO Pomos(Timestamp, TaskID) VALUES(" 
                            + str(pomoTime) + "," + str(taskID) + ")")
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
        # Number of tasks in general < 500 => We can get away with this.
        for taskID, taskName, pomoCount, pomoLast in self.tasks:
            if taskName == name:
                return taskID
                
        raise KeyError     
           
        
    def getTasks(self):
        """
        Returns the cached list of tasks.
        """
        return self.tasks
        
        
    def insertTask(self, taskName):
        """
        Inserts a new task into the database and our local cache.
        """
        if self.connected is True:
            self.c.execute("INSERT INTO Tasks(Name)"
                           " VALUES(\"" + taskName + "\")")
            self.conn.commit()
            taskID = self.c.lastrowid
            self.tasks.append((taskID, taskName, 0, 0))
            return taskID
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
    pomo.setData(pomoData)
