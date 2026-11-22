from chainingHashTableItem import ChainingHashTableItem
from singleton import Singleton

class ChainingHashTable():

    # Creates hash table structure
    # O(1)
    def __init__(self, initial_capacity = Singleton.chainingHashTableBuckets):
        self.table = [None] * initial_capacity

    # Task 2 - A
    # Inserts the specified key/value pair. If the key already exists, the
    # corresponding value is updated. If inserted or updated, True is returned.
    # If not inserted, then False is returned.
    # O(N)
    def insert(self, key, value):
        # Hash the key to get the bucket index
        bucket_index = self.hash(key) % len(self.table)
        
        # Traverse the linked list, searching for the key. If the key exists in
        # an item, the value is replaced. Otherwise a new item is appended.
        current_item = self.table[bucket_index]
        previous_item = None
        while current_item != None:
            if key == current_item.key:
                current_item.value = value
                return True
            previous_item = current_item
            current_item = current_item.next
            
        # Append to the linked list
        if self.table[bucket_index] == None:
            self.table[bucket_index] = ChainingHashTableItem(key, value)
        else:
            previous_item.next = ChainingHashTableItem(key, value)
        return True

    # Task 2 - B
    # Searches for the package ID. Returns the delivery address, deadline, city, zip code,
    # package weight, delivery status (i.e., at the hub, en route, or delivered), 
    # and delivery time if found or None if not delivered. Returns none if package ID not found
    # O(N)
    def lookUp(self, packageId):
        # Hash the key and compute bucket index
        bucket_index = self.hash(packageId) % len(self.table)
        package = None

        # Traverse the linked list in this bucket
        current = self.table[bucket_index]
        while current is not None:
            if current.key == packageId:
                package = current.value
                break
            current = current.next

        # Package ID not found
        if package is None:
            return None

        # Return components
        return [
            package.address, 
            package.deliveryDeadline, 
            package.city, 
            package.zip, 
            package.weight, 
            package.status, 
            package.timeDelivered
        ]

    # Returns a non-negative hash code for the specified key.
    # O(1)
    def hash(self, key):
        return abs(hash(key))

    # Searches for the package id. Returns the package if found, None if not found.
    # O(N)
    def get(self, packageId):
        # Hash the key and compute bucket index
        bucket_index = self.hash(packageId) % len(self.table)

        # Traverse the linked list in this bucket
        current = self.table[bucket_index]
        while current is not None:
            if current.key == packageId:
                return current.value
            current = current.next

        return None  # not found

    # Searches for the specified key. If found, the key/value pair is removed
    # from the hash table and True is returned. If not found, False is returned.
    # O(N)
    def remove(self, key, value):
        # Hash the key and compute bucket index
        bucket_index = self.hash(key) % len(self.table)
        packageToRemove = value

        # Search the bucket's linked list for the key
        current_package = self.table[bucket_index]
        previous_package = None
        while current_package != None:
            if key == current_package.key and current_package.value is packageToRemove:
                if previous_package == None:
                    # Remove linked list's first package
                    self.table[bucket_index] = current_package.next
                else:
                    previous_package.next = current_package.next
                return True
            previous_package = current_package
            current_package = current_package.next
        
        return False # key not found
    
    # Replace a package with a new package
    # O(N)
    def update(self, oldValue, newValue):
        oldKey = oldValue.packageId
        newKey = newValue.packageId

        # Remove the old package
        removed = self.remove(oldKey, oldValue)
        if not removed:
            return False

        # Insert the updated package
        inserted = self.insert(newKey, newValue)
        if not inserted:
            # rollback
            self.insert(oldKey, oldValue)
            return False

        return True

    # Return a list of all package values stored in the hash table.
    # O(N)
    def getAll(self):
        all_packages = []

        for bucket in self.table:
            current = bucket
            while current is not None:
                all_packages.append(current.value)
                current = current.next

        return all_packages


   # Searches for the earliest delivery time
   # O(N)
    def getEarliestDeadline(self):
        earliest = None

        for bucket in self.table:
            item = bucket
            while item is not None:
                package = item.value
                if package.atHub is True and package.isDelivered is False:
                    if earliest is None or package.deliveryDeadline < earliest:
                        earliest = package.deliveryDeadline
                item = item.next
        return earliest
    
    # Returns a list of packages with the earliest delivery time
    # O(N)
    def getEarliestPackagesDue(self):
        earliestDeadline = self.getEarliestDeadline()
        if earliestDeadline is None:
            return []
        earliestPackages = []

        for bucket in self.table:
            item = bucket
            while item is not None:
                package = item.value
                # Check if deadline is earliest deadline and is loaded on truck
                if package.deliveryDeadline == earliestDeadline and package.atHub is True and package.isDelivered is False:
                    earliestPackages.append(package)
                item = item.next
        return earliestPackages # Return list of packages

    # Checks if all packages are delivered
    # O(N)
    def allPackagesDelivered(self):
        for bucket in self.table:
            package = bucket
            while package is not None:
                if package.value.isDelivered is False:
                    return False
                package = package.next
        return True
    
    # Checks if all packages have been processed
    # O(N)
    def allPackagesAssigned(self):
        for bucket in self.table:
            package = bucket
            while package is not None:
                if package.value.atHub is True:
                    return False
                package = package.next
        return True

    # Marks a package delivered
    # O(N)
    def markDelivered(self, package):
        # Hash the key and compute bucket index
        key = package.packageId
        bucket_index = self.hash(key) % len(self.table)
        
        # Search the bucket's linked list for the key
        current_package = self.table[bucket_index]
        while current_package != None:
            if key == current_package.key:
                    current_package.value.isDelivered = True
                    return True
            current_package = current_package.next
        return
    
    # Used to mark a package was processed
    # O(N)
    def markNotAtHub(self, package):
        # Hash the key and compute bucket index
        key = package.packageId
        bucket_index = self.hash(key) % len(self.table)
        
        # Search the bucket's linked list for the key
        current_package = self.table[bucket_index]
        while current_package != None:
            if key == current_package.key:
                    current_package.value.atHub = False
                    return True
            current_package = current_package.next
        return

    # Clears the hash table
    # O(1)
    def clear(self):
        for bucket in self.table:
            if bucket is not None:
                bucket = None