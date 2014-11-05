import threading
import time
import math
import xml.etree.ElementTree as ET

from pomodorian.gui import initGUI
from pomodorian.data import initData


class PomoCore():
    def __init__(self):
        """
        Makes necessary variable initializations and calls other init methods.
        """
        super(PomoCore, self).__init__()
        self.timerActive = False
        self.timerCount = 0
        self.initStrings()


    def initStrings(self):
        """
        Imports the strings.xml for further use.
        """
        try:
            tree = ET.parse('data/strings.xml')
            self.xmlRoot = tree.getroot()
        except:
            raise RuntimeError("Could not open strings.xml")
        
        
    def setGUI(self, pomoGUI):
        """
        Connects the gui class with the core.
        """
        self.pomoGUI = pomoGUI
        
        
    def setData(self, pomoData):
        """
        Connects the data class with the core.
        """
        self.pomoData = pomoData
        

    def getString(self, cat, identifier):
        """
        Returns the given string for a category and an identifier.
        """
        node = self.xmlRoot.find(cat)
        if node != None:
            for child in node:
                if child.get('name') == identifier:
                    return child.text
        raise ValueError("Cannot find string: '" + identifier + "'.")

        
    def isTimerRunning(self):
        """
        Returns the boolean status of the timer activity.
        """
        return self.timerActive

        
    def startTimer(self):
        """
        Starts the timer in a new thread, calling a tick function after 1sec.
        """
        self.timerActive = True
        self.timerFix = time.time()+1
        timer = threading.Timer(self.timerFix - time.time(), self.tickTimer)
        timer.daemon = True
        timer.start()
        
        
    def stopTimer(self):
        """
        Stops the running timer.
        """
        if self.timerActive == True:
            self.timerActive = False
        else:
            raise Warning("Trying to stop an offline timer.")
        
        
    def resetTimer(self):
        """
        Stops the timer and resets the count.
        """
        try:
            self.stopTimer()
        except Warning:
            pass
        
        self.timerCount = 0
        
        
    def tickTimer(self):
        """
        Primary timer function. Starts a new thread until the timer finishes.
        """
        if self.timerActive == True:
            self.timerCount += 1
            self.timerFix += 1
            self.pomoGUI.receiveTick(self.timerCount)
            timer = threading.Timer(self.timerFix - time.time(), self.tickTimer)
            timer.daemon = True
            timer.start()

        
    def finishTimer(self, minutes, task):
        """
        Resets the timer and updates the DB/GUI once the timer is finished.
        """
        self.resetTimer()
        pomos = math.floor(minutes / 25)
        if pomos >= 1 and task != '':
            newTask = self.pomoData.addPomo(task, pomos)
            if newTask == True:
                self.pomoGUI.addTask(task)
                # TODO: Update all GUI infos.


    def getAllTasks(self):
        """
        Returns an array with all the tasks.
        """
        return self.pomoData.getTasks()


def run():
    """
    Main function for the Pomodorian application.
    """
    pomo = PomoCore()
    initData(pomo)
    initGUI(pomo)
