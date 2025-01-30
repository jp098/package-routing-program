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

#Creates the package object
class Package:
    def __init__(self, package_id, address, city, state, zip_code, deadline, weight, notes=""):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.notes = notes
        self.status = "At the Hub"
        self.departure_time = None
        self.delivery_time = None

    #Updates the status of the package
    def update_status(self, currentTime):
        if self.delivery_time and currentTime >= self.delivery_time:
            self.status = "Delivered"
        elif self.departure_time and currentTime >= self.departure_time:
            self.status = "En Route"
        else:
            self.status = "At the Hub"

    def __str__(self):
        return (f"Package ID: {self.package_id}, Address: {self.address}, {self.city}, {self.state}, {self.zip_code}, "
                f"Deadline: {self.deadline}, Weight: {self.weight} KILO, Status: {self.status}, "
                f"Departure Time: {self.departure_time}, Delivery Time: {self.delivery_time}")