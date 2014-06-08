import configparser, os, threading, time, math

from pomodorian.utils import *
from pomodorian.gui import initGUI
from pomodorian.data import initData


class MyThread(threading.Thread):
    def __init__(self, event, fun):
        threading.Thread.__init__(self)
        self.stopped = event
        self.fun = fun

    def run(self):
        while not self.stopped.wait(0.5):
            self.fun

class PomoCore():
    def __init__(self, config):
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
        
    def finishTimer(self, minutes):
        # get task
        self.resetTimer()
        pomos = math.ceil(minutes / 25)
        if pomos >= 1:
            # add pomodoro to current task
            pass
            
        


def writeDefaultConfig(configPath):
    if configPath == '':
        fatalError("Error while initializing config")
        
    config = configparser.ConfigParser()
        
    if not os.path.exists(configPath):
            os.makedirs(configPath)
    with open(configPath + "/pomo.cfg", 'w+') as configfile:
        config.write(configfile)
            
    return config


def validateConfig(config):
    return False


def initConfig():
    config = configparser.ConfigParser()
    configPath = os.path.expanduser("~/.pomodorian");    
        
    try:
        config.read_file(open(configPath + "/pomo.cfg"))
    except IOError:
        config = writeDefaultConfig(configPath)
    else:
        if validateConfig(config) == False:
            config = writeDefaultConfig(configPath)

            
    return config
    #if open config
    #load values
    #else create new config with default values


def run():
    config = initConfig()
    pomo = PomoCore(config)
    initGUI(pomo)
    initData()
