class AuditEvent:

    # O(1)
    def __init__(self, packageId, timestamp, status, truckId=None, driverId=None, address = None):
        self.packageId = str(packageId)
        self.timestamp = timestamp
        self.status = status          # "AT_HUB", "EN_ROUTE", "DELIVERED"
        self.truckId = truckId
        self.driverId = driverId
        self.address = address
