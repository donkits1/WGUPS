from datetime import timedelta
from auditEvent import AuditEvent
from singleton import Singleton

class Truck:

    # Initializes truck state
    # O(1)
    def __init__(self, truckId):
        self.truckId = truckId
        self.driver = None
        self.packageList = []
        self.currentAddress = "4001 South 700 East"
        self.nextPackage = None
        self.distanceToDelivery = 0
        self.distanceTraveled = 0

    # Adds a package to the truck (max capacity 16)
    # O(1)
    def addPackage(self, order):
        if len(self.packageList) >= 16:
            return False
        self.packageList.append(order)
        return True

    # Computes travel time based on truck speed
    # O(1)
    def computeTravelTime(self, distance):
        return timedelta(hours=(float(distance) / Singleton.truckSpeed))

    # Advances the driver's clock
    # O(1)
    def elapse(self, delta):
        self.driver.currentTime += delta

    # Returns truck to the hub and updates distance/time
    # O(N)
    def returnToHub(self, townMap):
        hub = "4001 South 700 East"
        if self.currentAddress != hub:
            distance = townMap.getDistance(self.currentAddress, hub)
            if distance is not None:
                travelTime = self.computeTravelTime(distance)
                self.elapse(travelTime)
                self.distanceTraveled += float(distance)

        self.currentAddress = hub
        # # DEBUG HELPER
        # print(f"\n - ! - Truck {self.truckId} returned to hub at {self.driver.currentTime} - ! -\n")
        return True

    # Selects the next package to deliver:
    #   1. Earliest deadline
    #   2. Among those, nearest neighbor
    # O(N)
    def selectNextDelivery(self, townMap):
        # Find earliest deadline
        shortestDeadline = min(p.deliveryDeadline for p in self.packageList)

        # Filter packages with that deadline
        deadlineCandidates = [
            p for p in self.packageList
            if p.deliveryDeadline == shortestDeadline
        ]

        bestPackage = None
        bestDistance = float('inf')

        # Among earliest-deadline packages, choose closest
        for package in deadlineCandidates:
            distance = townMap.getDistance(self.currentAddress, package.address)
            if distance is None:
                print("ERROR: No route found")
                continue

            distance = float(distance)
            if distance < bestDistance:
                bestDistance = distance
                bestPackage = package

        # If no valid earliest-deadline route, fallback to nearest neighbor
        if bestPackage is None:
            for package in self.packageList:
                distance = townMap.getDistance(self.currentAddress, package.address)
                if distance is None:
                    print("ERROR: No route found")
                    continue

                distance = float(distance)
                if distance < bestDistance:
                    bestDistance = distance
                    bestPackage = package

        # Assign results
        self.nextPackage = bestPackage
        self.distanceToDelivery = bestDistance
        return True

    # Delivers the selected package and updates truck state
    # O(N)
    def makeDelivery(self, packageTable):
        # Compute travel time and advance clock
        travelTime = self.computeTravelTime(self.distanceToDelivery)
        self.elapse(travelTime)
        self.distanceTraveled += self.distanceToDelivery

        # Mark package delivered
        pkg = self.nextPackage
        pkg.timeDelivered = self.driver.currentTime
        pkg.status = "DELIVERED"

        # Remove from truck
        if pkg in self.packageList:
            self.packageList.remove(pkg)

        # Update truck state
        self.currentAddress = pkg.address
        packageTable.markDelivered(pkg)

        # Log audit event
        Truck.logAuditEvent(
            package=pkg,
            status="DELIVERED",
            timestamp=self.driver.currentTime,
            truck=self,
            driver=self.driver
        )

        # DEBUG HELPER
        # # Print status of the delivery to terminal
        # deadline = self.nextPackage.deliveryDeadline
        # if (self.driver.currentTime <= deadline):
        #     status = "ON TIME"
        # else:
        #     status = "LATE"
        # if deadline.strftime('%I:%M:%S %p') == "11:59:00 PM":
        #     deadline = "EOD"
        # else:
        #     deadline = deadline.strftime('%I:%M:%S %p')
        # print(f"[Package {self.nextPackage.packageId}] Delivered by Truck {self.truckId}, Driver {self.driver.driverId} at {self.driver.currentTime.strftime('%I:%M:%S %p')} - {status}")

    # Records an audit event
    # O(1)
    def logAuditEvent(package, status, timestamp, truck=None, driver=None):
        Singleton.auditLog.append(
            AuditEvent(
                packageId=package.packageId,
                timestamp=timestamp,
                status=status,
                truckId=truck.truckId if truck else None,
                driverId=driver.driverId if driver else None,
                address = truck.currentAddress
            )
        )
