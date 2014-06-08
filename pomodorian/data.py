from pomodorian.utils import *

class PomoData():
    def __init__(self, pomo):
        super(PomoData, self).__init__()
        
        self.pomo = pomo
        
        self.initData()
        
    def initData(self):
        pass


def initData(pomo):
    pomoData = PomoData(pomo)
    pomo.setData(pomoData)
