class Package:

    # O(N)
    def __init__(self, 
                 packageId = None, 
                 address = None, 
                 city = None, 
                 state = None,
                 zip = None,
                 deliveryDeadline = None,
                 weight = None, 
                 special_notes = None,
                 isDelivered = False,
                 atHub = True,
                 timeDelivered = None,
                 timeEnroute = None,
                 delayedArrivalToHub = None,
                 delayed = False,
                 canOnlyBeOnTruck = None,
                 status = "AT HUB"):
        self.packageId = packageId
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.deliveryDeadline = deliveryDeadline
        self.weight = weight
        self.special_notes = special_notes 
        self.isDelivered = isDelivered
        self.atHub = atHub
        self.timeDelivered = timeDelivered
        self.timeEnroute = timeEnroute
        self.delayedArrivalToHub = delayedArrivalToHub
        self.delayed = delayed
        self.canOnlyBeOnTruck = canOnlyBeOnTruck
        self.status = status
