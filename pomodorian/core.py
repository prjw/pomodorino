import threading
import time
import math

from pomodorian.utils import *
from pomodorian.gui import initGUI
from pomodorian.data import initData


class PomoCore():
    def __init__(self):
        super(PomoCore, self).__init__()
        self.resetTimer()
        
    def setGUI(self, pomoGUI):
        self.pomoGUI = pomoGUI
        
    def setData(self, pomoData):
        self.pomoData = pomoData
        
    def isTimerRunning(self):
        if self.timerActive == 1:
            return True
        return False
        
    def startTimer(self):
        self.timerActive = 1
        self.timerFix = time.time()+1
        timer = threading.Timer(self.timerFix - time.time(), self.tickTimer)
        timer.daemon = True
        timer.start()
        
    def tickTimer(self):
        if self.timerActive == 1:
            self.timerCount += 1
            self.timerFix += 1
            self.pomoGUI.receiveTick(self.timerCount)
            timer = threading.Timer(self.timerFix - time.time(), self.tickTimer)
            timer.daemon = True
            timer.start()
    
    def stopTimer(self):
        self.timerActive = 0
        
    def resetTimer(self):
        self.stopTimer()
        self.timerCount = 0
        
    def finishTimer(self, minutes, task):
        self.resetTimer()
        pomos = math.ceil(minutes / 25)
        if pomos >= 1 and task != '':
            newTask = self.pomoData.addPomo(task, pomos)
            if newTask == True:
                self.pomoGUI.addTask(task)

    def getAllTasks(self):
        return self.pomoData.getTasks()

def run():
    pomo = PomoCore()
    initData(pomo)
    initGUI(pomo)
