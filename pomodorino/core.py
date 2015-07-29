import time
import math
import xml.etree.ElementTree as ET

from pomodorino.gui import initGUI
from pomodorino.data import initData


class PomoCore():
    def __init__(self):
        """
        Makes necessary variable initializations and calls other init methods.
        """
        super(PomoCore, self).__init__()
        self.initStrings()

    def initStrings(self):
        """
        Imports the strings.xml for further use.
        """
        try:
            tree = ET.parse('/usr/share/pomodorino/strings.xml')
            self.xmlRoot = tree.getroot()
            self.stringCache = dict()
        except:
            raise RuntimeError("Could not open strings.xml")

    def getString(self, identifier):
        """
        Returns the given string for a category and an identifier.
        """
        node = self.xmlRoot.find("strings")
        if node != None:
            for child in node:
                if child.get('name') == identifier:
                    return child.text
        raise ValueError("Cannot find string: '" + identifier + "'.")

def run():
    """
    Main function for the Pomodorino application.
    """
    pomo = PomoCore()
    initData(pomo)
    initGUI(pomo)
