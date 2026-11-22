class Hub:

    # O(N)
    def __init__(self, trucksAtHub, driversAtHub):
        self.trucksAtHub = list(trucksAtHub)
        self.driversAtHub = list(driversAtHub)

    # O(1)
    def clear(self):
        self.trucksAtHub = []
        self.driversAtHub = []

    # Returns the truck with a matching ID
    # O(N)
    def getTruckWithId(self, index):
        for truck in self.trucksAtHub:
            if truck.truckId == index:
                return truck
            
    # Returns the driver with a matching ID
    # O(N)
    def getDriverWithId(self, index):
        for driver in self.driversAtHub:
            if driver.driverId == index:
                return driver
        print(f"No driver with ID: {index}")

    # Returns the truck with the most packages loaded
    # O(N)
    def getTruck(self):
        if not self.trucksAtHub:
            return None
        return max(self.trucksAtHub, key=lambda t: len(t.packageList))

    # Returns the driver with the least work done
    # O(N)
    def getDriver(self):
        return min(self.driversAtHub, key=lambda d: d.currentTime)

    # Assigns a truck to a driver
    # O(1)
    def assignTruckToDriver(self, truck, driver):
        truck.driver = driver
        driver.truck = truck

    # Unassigns a truck and driver
    # O(1)
    def unassignTruckToDriver(self, truck, driver):
        truck.driver = None
        driver.truck = None

    # Marks a truck and driver as leaving the hub
    # O(N)
    def markLeftForDelivery(self, truck, driver):
        if truck not in self.trucksAtHub:
            print(f"ERROR: Truck {truck.truckId} not at hub when leaving")
            return False

        if driver not in self.driversAtHub:
            print(f"ERROR: Driver {driver.driverId} not at hub when leaving")
            return False

        self.trucksAtHub.remove(truck)
        self.driversAtHub.remove(driver)
        return True

    # Marks a truck and driver as returned to the hub
    # O(N)
    def markReturnFromDelivery(self, truck, driver):
        if truck not in self.trucksAtHub:
            self.trucksAtHub.append(truck)

        if driver not in self.driversAtHub:
            self.driversAtHub.append(driver)

    def consolidateToTruck(self, truckId):
        allPackages = []
        for truck in self.trucksAtHub:
            for package in truck.packageList:
                allPackages.append(package)
            truck.packageList = []
        consolidateToTruck = self.getTruckWithId(truckId)
        for package in allPackages:
            consolidateToTruck.packageList.append(package)
        # print("Changed packing priority to Truck 2@@@@")
