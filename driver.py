from singleton import Singleton


class Driver:

    # O(1)
    def __init__(self, driverId):
        self.driverId = driverId
        self.truck = None #assigned truck
        self.currentTime = Singleton.startTime
        self.workDone = 0