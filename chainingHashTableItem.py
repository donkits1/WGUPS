class ChainingHashTableItem:

    # O(1)
    def __init__(self, key, item):
        self.key = key
        self.value = item
        self.next = None