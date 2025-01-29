import csv
import datetime

#Import CSV files data

#Source: C950-Webinar-1-Let's Go Hashing Webinar)
#Hash Table with chaining
class ChainingHashTable:
    #Initializes table with an initial bucket size of 40
    def __init__(self, initial_capacity=40):
        self.table = []
        # Buckets assigned with empty list
        for i in range(initial_capacity):
            self.table.append([])

    #Inserts new item into the hash table and updates keys already in bucket
    def insert(self, key, item):
        #Assigns item to bucket list
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        #Update key already in bucket
        for kv in bucket_list:
            if kv[0] == key:
                kv[1] = item
                return True

        #If not add the item to the end of the bucket list
        key_value = [key, item]
        bucket_list.append(key_value)
        return True

    #Searches for item with matching key in the hash table
    def search(self, key):
        #Get bucket list where matching key would be
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        #Search for key in bucket list and return if found
        for key_value in bucket_list:
            if key_value[0] == key:
                return key_value[1]
            return None

    #Removes item from hash table with matching key
    def remove(self, key):
        #Gets bucket list where item will be removed
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        #Removes item from bucket list if present
        for key_value in bucket_list:
            if key_value[0] == key:
                bucket_list.remove([key_value[0],key_value[1]])