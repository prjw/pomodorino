import configparser, os

from pomodorian.utils import *
from pomodorian.gui import initGUI
from pomodorian.data import initData


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
    initGUI()
    initData()
