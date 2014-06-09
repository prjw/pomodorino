import os, sqlite3
from pomodorian.utils import *

class PomoData():
    def __init__(self, pomo):
        super(PomoData, self).__init__()
        self.pomo = pomo
        self.initDB()
        
    def initDB(self):
        dbPath = os.path.expanduser("~/.local/share/pomodorian/");   
        
        if not os.path.exists(dbPath):
            os.makedirs(dbPath)
        
        self.conn = sqlite3.connect(dbPath+"pomo.db")
        self.c = self.conn.cursor()
    
    def openDB(self):
        pass
        
    def createDB(self):
        pass
    
    def addPomo(self, task, pomos):
        pass
        
    def readAllTasks(self):
        pass
        
    


def initData(pomo):
    pomoData = PomoData(pomo)
    pomo.setData(pomoData)
