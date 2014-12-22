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
        self.timerType = 25
        self.initStrings()


    def initStrings(self):
        """
        Imports the strings.xml for further use.
        """
        try:
            tree = ET.parse('data/strings.xml')
            self.xmlRoot = tree.getroot()
            self.stringCache = dict()
        except:
            raise RuntimeError("Could not open strings.xml")
        

    def getString(self, cat, identifier):
        """
        Returns the given string for a category and an identifier.
        """
        stringName = identifier + "@" + cat
        if stringName in self.stringCache:
            return self.stringCache[stringName]
        
        node = self.xmlRoot.find(cat)
        if node != None:
            for child in node:
                if child.get('name') == identifier:
                    # Cache the result since a high number of individual
                    # requests might be causing a Fatal IO Error.
                    self.stringCache[stringName] = child.text
                    return child.text
        raise ValueError("Cannot find string: '" + identifier + "'.")

        
    def startTimer(self, timeSpan, restart=False):
        """
        Starts the timer in a new thread, calling a tick function after 1sec.
        """
        self.timerActive = True
        if restart is False and timeSpan != 0:
            self.timerCount = timeSpan * 60
            self.timerType = timeSpan
        self.timerFix = time.time() + 1
        timer = threading.Timer(self.timerFix - time.time(), self.tickTimer)
        timer.daemon = True
        timer.start()
        
        
    def stopTimer(self):
        """
        Stops the running timer.
        """
        self.timerActive = False
        
        
    def resetTimer(self):
        """
        Stops the timer and resets the count.
        """
        self.stopTimer()
        self.timerCount = 0
        
        
    def tickTimer(self):
        """
        Primary timer function. Starts a new thread until the timer finishes.
        """
        if self.timerActive == True:
            self.timerCount -= 1
            self.timerFix += 1
            self.pomoGUI.receiveTick(self.timerCount)
            timer = threading.Timer(self.timerFix - time.time(), self.tickTimer)
            timer.daemon = True
            timer.start()

        
    def finishTimer(self, task):
        """
        Resets the timer and updates the DB/GUI once the timer is finished.
        """
        self.resetTimer()
        # Define the regular length of a pomodoro. Mainly for debugging reasons
        POMO_CONST = 25
        pomos = math.floor(self.timerType / POMO_CONST)
        if pomos >= 1 and task != '':
            newTask = self.pomoData.addPomo(task, pomos)
            if newTask == True:
                self.pomoGUI.addTask(task)
            self.pomoGUI.doTasksRefresh()


def run():
    """
    Main function for the Pomodorian application.
    """
    pomo = PomoCore()
    initData(pomo)
    initGUI(pomo)
