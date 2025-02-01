#StudentID: 012029709
#StudentName: Jair Palacios

import csv
import datetime

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
    def update_status(self, current_time):
        if self.delivery_time and current_time >= self.delivery_time:
            self.status = "Delivered"
        elif self.departure_time and current_time >= self.departure_time:
            self.status = "En Route"
        else:
            self.status = "At the Hub"

    def __str__(self):
        return (f"Package ID: {self.package_id}, Address: {self.address}, {self.city}, {self.state}, {self.zip_code}, "
                f"Deadline: {self.deadline}, Weight: {self.weight} KILO, Status: {self.status}, "
                f"Departure Time: {self.departure_time}, Delivery Time: {self.delivery_time}")

#Creates the truck object
class Truck:
    def __init__(self, truck_id, speed=18):
        self.truck_id = truck_id
        self.speed = speed
        self.mileage = 0.0
        self.current_location = "4001 South 700 East"
        self.departure_time = None
        self.packages = []

    def __str__(self):
        return (f"Truck ID: {self.truck_id}, Speed: {self.speed} mph, Mileage: {self.mileage:.2f} miles, "
                f"Current Location: {self.current_location}, Departure Time: {self.departure_time}, "
                f"Packages on Truck: {[p.package_id for p in self.packages]}")

def load_package_data(file_name, hash_table):
    with open(file_name) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            package_id = int(row["PackageID"])
            address = row["Address"]
            city = row["City"]
            state = row["State"]
            zip_code = row["Zip"]
            deadline = row["DeliveryDeadline"]
            weight = int(row["WeightKILO"])
            notes = row["SpecialNotes"]

            package = Package(package_id, address, city, state, zip_code, deadline, weight, notes)
            hash_table.insert(package_id, package)

def load_distance_data(file_name):
    with open(file_name) as csv_file:
        reader = csv.reader(csv_file)
        distance_data = list(reader)
    return distance_data

def load_address_data(file_name):
    with open(file_name) as csv_file:
        reader = csv.reader(csv_file)
        address_data = [row[0] for row in reader]
    return address_data

def calculate_distance(starting_address, destination_address, distance_matrix):
    distance = distance_matrix[starting_address][destination_address]
    if distance == '':
        distance = distance_matrix[destination_address][starting_address]
    return float(distance)

def truck_delivery_route(truck, hash_table, address_data, distance_matrix):
    current_location = address_data.index(truck.current_location)
    total_distance = 0.0

    while truck.packages:
        nearest_package_id = None
        nearest_distance = float('inf')

        for package_id in truck.packages:
            package = hash_table.search(package_id)
            destination_index = address_data.index(package.address)
            distance_to_package = calculate_distance(current_location, destination_index, distance_matrix)

            #Check if this package is closer than the current nearest package
            if distance_to_package < nearest_distance:
                nearest_package_id = package_id
                nearest_distance = distance_to_package

        #Deliver the nearest package
        truck.packages.remove(nearest_package_id)

        #Update truck mileage and location
        total_distance += nearest_distance
        current_location = address_data.index(hash_table.search(nearest_package_id).address)

    #Update total mileage for the truck after all deliveries
    truck.mileage += total_distance

    #Initialize variables and load data
    package_hash_table = ChainingHashTable
    load_package_data("packageCSV.csv", package_hash_table)

    distance_matrix = load_distance_data("distanceCSV.csv")

    address_data = load_address_data("addressCSV.csv")

    truck1