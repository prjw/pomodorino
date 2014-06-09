import threading, time, math

from pomodorian.utils import *
from pomodorian.gui import initGUI
from pomodorian.data import initData


class PomoCore():
    def __init__(self):
        super(PomoCore, self).__init__()
        self.timerCount = 0
        
    def setGUI(self, pomoGUI):
        self.pomoGUI = pomoGUI
        
    def setData(self, pomoData):
        self.pomoData = pomoData
        
    def startTimer(self):
        self.timerActive = 1
        self.timerFix = time.time()+1
        threading.Timer(self.timerFix - time.time(), self.tickTimer).start()
        
    def tickTimer(self):
        if self.timerActive == 1:
            self.timerCount += 1
            self.timerFix += 1
            self.pomoGUI.sendTick(self.timerCount)
            threading.Timer(self.timerFix - time.time(), self.tickTimer).start()
    
    def stopTimer(self):
        self.timerActive = 0
        
    def resetTimer(self):
        self.stopTimer()
        self.timerCount = 0
        
    def finishTimer(self, minutes, task):
        self.resetTimer()
        pomos = math.ceil(minutes / 25)
        if pomos >= 1 and task != '':
            self.pomoData.addPomo(task, pomos)
            pass


def run():
    pomo = PomoCore()
    initData(pomo)
    initGUI(pomo)
