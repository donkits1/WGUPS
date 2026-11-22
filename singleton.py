from datetime import datetime

class Singleton:

    # Static configuration values
    startTime = datetime(1900, 1, 1, 8, 0, 0)   # 8:00 AM
    # startTime = datetime(1900, 1, 1, 9, 5, 0)   # 9:05 AM
    chainingHashTableBuckets = 41
    truckSpeed = 18  # miles per hour
    totalTrucks = 3
    totalDrivers = 2

    # Global audit log
    auditLog = []

    # Special instruction tracking
    bundledPackages = []
    delayedArrivals = []

    # Special note text for package 9
    specialNote_9 = (
        "The delivery address for package #9, Third District Juvenile Court, is wrong "
        "and will be corrected at 10:20 a.m. WGUPS is aware that the address is incorrect "
        "and will be updated at 10:20 a.m. However, WGUPS does not know the correct address "
        "(410 S. State St., Salt Lake City, UT 84111) until 10:20 a.m."
    )

    # Processes special instructions for a package
    # O(1)
    def processSpecialInstructions(package, packageTable):
        match package.packageId:

            # Packages restricted to Truck 2
            case "3" | "18" | "36" | "38":
                package.canOnlyBeOnTruck = 2
                return True

            # Delayed packages (arrive at 9:05 AM)
            case "6" | "25" | "28" | "32":
                package.delayedArrivalToHub = "9:05 AM"
                package.delayed = True
                Singleton.delayedArrivals.append(package)
                return True

            # Package 9: wrong address, corrected at 10:20 AM
            case "9":
                package.address = "410 S State St"
                package.city = "Salt Lake City"
                package.state = "UT"
                package.zip = "84111"
                package.delayedArrivalToHub = "10:20 AM"
                package.delayed = True
                Singleton.delayedArrivals.append(package)
                return True

            # Bundled packages (must be delivered together)
            case "13" | "14" | "15" | "16" | "19" | "20":
                Singleton.bundledPackages.append(package)
                return True

            # No special instructions
            case _:
                return True

    # Adds all bundled packages to a truck
    # O(N)
    def addBundleToTruck(truck, packageTable):
        for package in Singleton.bundledPackages:
            truck.addPackage(package)
            packageTable.markNotAtHub(package)
        Singleton.bundledPackages = []