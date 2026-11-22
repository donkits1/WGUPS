class DowntownMap:

    # O(1)
    def __init__ (self, addresses, distances):
        self.addresses = addresses
        self.distances = distances

    # O(N)
    def clear(self):
        self.addresses.clear()
        self.distances.clear()

    # Searches for a building that matches an address on file
    # O(N)
    def getBuilding(self, address):
        for building in self.addresses:
            if address in building:
                return building
        return None
        
    # Returns the distance between two buildings
    # O(N)
    def getDistance(self, start, end):
        # Get the building of starting address
        startBuilding = self.getBuilding(start)
        if startBuilding is None:
            print(f"Invalid starting location: {start}")
            return None

        # Get the building of destination address
        endBuilding = self.getBuilding(end)
        if endBuilding is None:
            print(f"Invalid ending location: {end}")
            return None

        # Get a distance value from the distance matrix
        i = self.addresses.index(startBuilding)
        j = self.addresses.index(endBuilding)
        distance = self.distances[i][j] # check x,y
        if distance == "" or distance is None: # no value at x,y
            distance = self.distances[j][i] # check y,x
            if distance == "" or distance is None: # no distance value found between locations
                print(f"Invalid route between {start} and {end}.")
                return None
        return float(distance)