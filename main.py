# Student ID 011535752
# Donne Berberabe

import sys
sys.dont_write_bytecode = True

import csv
from datetime import datetime

from truck import Truck
from driver import Driver
from chainingHashTable import ChainingHashTable
from package import Package
from singleton import Singleton
from downtownMap import DowntownMap
from hub import Hub
from auditEvent import AuditEvent

# ----------------- Globals -----------------

addresses: list[str] = []
distances: list[list[str]] = []
downtownMap = DowntownMap(addresses, distances)
packages = ChainingHashTable()
trucks: list[Truck] = []
drivers: list[Driver] = []
hub = Hub(trucks, drivers)

# ----------------- File loading -----------------

# Store addresses, distance matrix, and packages from files
# O(N)
def readFiles() -> None:
    with (
        open('distances.csv', mode='r', newline='') as distanceFile,
        open('addresses.csv', mode='r', newline='') as addressFile,
        open('packages.csv', mode='r', newline='') as packageFile
    ):
        distanceReader = csv.reader(distanceFile, delimiter=',')
        addressReader = csv.reader(addressFile, delimiter=',')
        packageReader = csv.reader(packageFile, delimiter=',')

        # Addresses
        for row in addressReader:
            addresses.append(row[0])

        # Distance matrix
        for row in distanceReader:
            distances.append(list(row))

        # Map
        downtownMap.addresses = addresses
        downtownMap.distances = distances

        # Packages
        for row in packageReader:
            rawAddress = row[1]
            if " \\" in rawAddress:
                correct_address = rawAddress.split(" \\")[0]
            else:
                correct_address = rawAddress

            # Normalize deadline
            if row[5] == "EOD":
                deadline = datetime.strptime("11:59 PM", "%I:%M %p")
            else:
                deadline = datetime.strptime(row[5], "%I:%M %p")

            newPackage = Package(
                packageId=row[0],
                address=correct_address,
                city=row[2],
                state=row[3],
                zip=row[4],
                deliveryDeadline=deadline,
                weight=row[6],
                special_notes=row[7]
            )

            # Process special instructions and insert if valid
            if Singleton.processSpecialInstructions(newPackage, packages):
                packages.insert(newPackage.packageId, newPackage)


# ----------------- Setup -----------------

# Populates truck and driver lists
# O(N)
def createTrucksAndDrivers(totalTrucks: int, totalDrivers: int) -> None:
    for truckId in range(1, totalTrucks + 1):
        trucks.append(Truck(truckId))

    for driverId in range(1, totalDrivers + 1):
        drivers.append(Driver(driverId))


# ----------------- Delivery logic -----------------

# Delivers all packages on truck
# O(N^2)
def leaveHub(truck: Truck, driver: Driver):
    # Mark packages as en route
    for package in truck.packageList:
        package.status = "EN ROUTE"
        package.timeEnroute = driver.currentTime
        logAuditEvent(package, "EN_ROUTE", driver.currentTime, truck, driver)


    # Deliver until truck is empty
    while truck.packageList:
        truck.selectNextDelivery(downtownMap)
        truck.makeDelivery(packages)

    # Return to hub and update hub/driver state
    truck.returnToHub(downtownMap)
    hub.markReturnFromDelivery(truck, driver)
    hub.unassignTruckToDriver(truck, driver)

# Send a truck out for delivery if it has packages.
# O(N)
def sendOut(truck: Truck, driver: Driver) -> None:

    hub.assignTruckToDriver(truck, driver)

    if not truck.packageList:
        print(f"Truck {truck.truckId} is empty.")
        hub.unassignTruckToDriver(truck, driver)
        return

    if hub.markLeftForDelivery(truck, driver):
        leaveHub(truck, driver)
    else:
        # If hub refused departure, unassign to keep state consistent
        hub.unassignTruckToDriver(truck, driver)

# ----------------- Simulation Logic -----------------

# Resets globals for a clean simulation
# O(NlogN)
def startSimulator():
    trucks.clear()
    drivers.clear()
    addresses.clear()
    distances.clear()
    packages.clear()
    downtownMap.clear()
    hub.clear()
    readFiles()
    createTrucksAndDrivers(Singleton.totalTrucks, Singleton.totalDrivers)
    startSimulation()

# Main simulation logic
# O(NlogN)
def startSimulation():

    # Create log of all packages at runtime
    for p in packages.getAll():
        logAuditEvent(p, "AT_HUB", Singleton.startTime)

    # Reset hub state
    hub.clear()
    hub.driversAtHub.extend(drivers)
    hub.trucksAtHub.extend(trucks)

    delayedPackages = []
    bundleLoaded = False
    isEOD = False
    deliveryWave = 1
    eod = datetime.strptime("11:59 PM", "%I:%M %p")


    # Business day loop - only ends when stop condition is satisfied
    while True:
        # Stop condition: all packages delivered + all trucks back at hub
        if packages.allPackagesDelivered() and len(hub.trucksAtHub) == Singleton.totalTrucks:
            break

        if deliveryWave == 1:
            truck = hub.getTruckWithId(1)
            driver = hub.getDriverWithId(1)
        elif deliveryWave == 2:
            truck = hub.getTruckWithId(3)
            driver = hub.getDriverWithId(1)
        elif deliveryWave == 3:
            truck = hub.getTruckWithId(2)
            driver = hub.getDriverWithId(2)
        elif deliveryWave == 4:
            truck = hub.getTruckWithId(2)
            driver = hub.getDriverWithId(2)
        # driver = hub.getDriver()

        # Load packages
        while True:
            loadedSomething = False

            # Process delayed packages that are now ready
            for package in delayedPackages[:]:
                arrival = datetime.strptime(package.delayedArrivalToHub, "%I:%M %p")
                if driver.currentTime >= arrival and len(truck.packageList) < 16:
                    if truck.addPackage(package):
                        logAuditEvent(package, "EN_ROUTE", driver.currentTime, truck, driver)
                        delayedPackages.remove(package)
                        packages.markNotAtHub(package)
                        loadedSomething = True

            # Process more packages
            nextPackages = sorted(
                packages.getEarliestPackagesDue(),
                key=lambda p: int(p.packageId)
            )

            # Send packages with deadline before loading any EOD packages
            if nextPackages != []:
                if nextPackages[0].deliveryDeadline == eod and not isEOD:
                    isEOD = True
                    nextPackages.clear()
                    # Preload nextPackages to prioritize truck-restricted packages 
                    pkg3 = packages.get("3")
                    pkg18 = packages.get("18")
                    pkg36 = packages.get("36")
                    pkg38 = packages.get("38")
                    nextPackages.append(pkg3)
                    nextPackages.append(pkg18)
                    nextPackages.append(pkg36)
                    nextPackages.append(pkg38)
                    break

            for package in nextPackages:

                # Truck capacity reached
                if len(truck.packageList) >= 16:
                    break

                # Bundle logic
                if package in Singleton.bundledPackages:
                    bundle = Singleton.bundledPackages
                    if len(truck.packageList) + len(bundle) <= 16:
                        Singleton.addBundleToTruck(truck, packages)
                        Singleton.bundledPackages = []
                        loadedSomething = True
                    continue

                # Dispatch immediately after first bundle
                if not bundleLoaded:
                    bundleLoaded = True
                    # Added packages with the same addresses to save miles
                    pkg21 = packages.get("21")
                    pkg34 = packages.get("34")
                    pkg39 = packages.get("39")
                    truck.addPackage(pkg21)
                    truck.addPackage(pkg34)
                    truck.addPackage(pkg39)
                    packages.markNotAtHub(pkg21)
                    packages.markNotAtHub(pkg34)
                    packages.markNotAtHub(pkg39)
                    break 

                # Delayed package
                if package.delayed:
                    arrival = datetime.strptime(package.delayedArrivalToHub, "%I:%M %p")
                    if driver.currentTime < arrival:
                        delayedPackages.append(package)
                        packages.markNotAtHub(package)
                        continue

                # Package can only be on certain truck
                if package.canOnlyBeOnTruck is not None:
                    truckId = package.canOnlyBeOnTruck
                    specificTruck = hub.getTruckWithId(truckId)
                    truck = specificTruck # Change truck priority
                    hub.consolidateToTruck(truckId) # Move loaded packages to new truck
                    truck.addPackage(package)
                    packages.markNotAtHub(package)
                    continue

                # Normal package
                if truck.addPackage(package):
                    logAuditEvent(package, "EN_ROUTE", driver.currentTime, truck, driver)
                    packages.markNotAtHub(package)
                    loadedSomething = True

            # Stop loading if nothing else can be added
            if not loadedSomething or len(truck.packageList) >= 16:
                break

        # Dispatch truck
        sendOut(truck, driver)
        deliveryWave += 1
        

# ----------------- UI -----------------

# Prints delivery time of each package, distance traveled of each truck, and time of EOD
# O(N)
def printEndOfDayAuditReport():
    print("\n--------------- Full Report ---------------")

    # End of day time
    endOfDay = datetime.strptime("11:59 PM", "%I:%M %p")

    # Get all packages sorted by ID
    allPackages = sorted(
        packages.getAll(),
        key=lambda p: int(p.packageId)
    )

    for p in allPackages:
        event = getAuditStatus(p.packageId, endOfDay)
        print(formatAuditResult(event, endOfDay))

    totalDistance = sum(truck.distanceTraveled for truck in trucks)
    endTime = max(driver.currentTime for driver in drivers)
    print("")
    for truck in hub.trucksAtHub:
        print(f"Truck {truck.truckId} traveled {truck.distanceTraveled:.2f} miles.")
    print(f"Total Miles Traveled: {totalDistance:.2f}")
    print(f"Work Day End: {endTime.strftime('%I:%M:%S %p')}")
    print("--------------- End Report ---------------")

# Used to create a record at each step of package delivery
def logAuditEvent(package, status, timestamp, truck=None, driver=None):
    Singleton.auditLog.append(
        AuditEvent(
            packageId=package.packageId,
            timestamp=timestamp,
            status=status,
            truckId=truck.truckId if truck else None,
            driverId=driver.driverId if driver else None,
            address = package.address
        )
    )

# Format audit reports
# O(N)
def formatAuditResult(event, queryTime):
    if event is None:
        return f"[Package ?] No audit data available."

    t = queryTime.strftime("%I:%M %p")

    if event.status == "AT_HUB":
        return f"[Package {event.packageId}] AT HUB at {t}"

    if event.status == "EN_ROUTE":
        return (
            f"[Package {event.packageId}] EN ROUTE to \"{event.address}\" at {t} "
            f"(Truck {event.truckId}, Driver {event.driverId})"
        )

    if event.status == "DELIVERED":
        delivered_at = event.timestamp.strftime("%I:%M %p")
        return (
            f"[Package {event.packageId}] DELIVERED to \"{event.address}\" at {delivered_at} "
            f"(Truck {event.truckId}, Driver {event.driverId})"
        )

# Returns the audit report of a package at requested time
# O(N)
def getAuditStatus(packageId, queryTime):
    events = [e for e in Singleton.auditLog if e.packageId == str(packageId)]
    events.sort(key=lambda e: e.timestamp)

    last = None
    for e in events:
        if e.timestamp <= queryTime:
            last = e
        else:
            break
    return last

# Prompts user for selected packages and audit time
# O(N)
def auditReport():
    selected = []

    while True:
        if not selected:
            print("\n\t--- Audit ---\n")
            print("(ALL) All packages")
            print("(1-40) Select a package")
            print("(-1) Back")
            print("(0) Run Audit")
        else:
            print("\n\t--- Audit ---\n")
            print(f"Selected: {', '.join(selected)}")
            print("(ALL) All packages")
            print("(1-40) Select a package")
            print("(-1) Back")
            print("(0) Run Audit")

        user = input("INPUT: ")

        if user == "-1":
            return
        elif user == "0":
            timeInput = input("Audit time (ex. 9:35 AM): ")
            try:
                queryTime = datetime.strptime(timeInput, "%I:%M %p")
            except:
                print("Invalid time format.")
                continue

            # Run simulation
            startSimulator()

            # Print results
            print("")
            for pid in selected:
                event = getAuditStatus(pid, queryTime)
                print(formatAuditResult(event, queryTime))
            return
        elif user.isdigit() and 1 <= int(user) <= 40:
            if user not in selected:
                selected.append(user)
            else:
                print("Already selected.")
        elif user.upper() == "ALL":
            selected = [str(i) for i in range(1, 41)]
            print("All packages selected.")
            timeInput = input("Audit time (ex. 9:35 AM): ")
            try:
                queryTime = datetime.strptime(timeInput, "%I:%M %p")
            except:
                print("Invalid time format.")
                continue

            # Run simulation
            startSimulator()

            # Print results
            print("")
            for pid in selected:
                event = getAuditStatus(pid, queryTime)
                print(formatAuditResult(event, queryTime))
            return
        else:
            print("Invalid input.")

# Displays options to user
# O(N)
def mainMenu():
    exitApp = False
    while not exitApp:
        userInput = input(
            "\n\t--- Main Menu ---\n\n"
            "(1) Full Report\n"
            "(2) Audit Report\n"
            "(3) Exit\n"
            "INPUT: "
        )
        match userInput:
            case "1":
                startSimulator()
                printEndOfDayAuditReport()
            case "2":
                auditReport()
            case "3":
                exitApp = True
            case _:
                print(f"Invalid input: {userInput}")


# ----------------- Entry Point -----------------

# Main method
# O(N)
def main():
    print(
        "\n\t-------- WGUPS --------\n\n"
        "Student ID: 011535752\n"
        "Donne Berberabe"
    )
    mainMenu()

if __name__ == "__main__":
    main()
