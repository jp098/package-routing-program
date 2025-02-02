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
        for kv in bucket_list:
            if kv[0] == key:
                return kv[1]
        return None

#Creates the package object to store package information
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
        #Updates the address for package 9 at 10:20AM
        if self.package_id == 9 and current_time >= datetime.timedelta(hours=10, minutes=20):
            self.address = "410 S State St"
            self.zip_code = "84111"

        if self.delivery_time and current_time >= self.delivery_time:
            self.status = "Delivered"
        elif self.departure_time and current_time >= self.departure_time:
            self.status = "En Route"
        else:
            self.status = "At the Hub"

#Creates the truck object to store truck information
class Truck:
    def __init__(self, speed, mileage, current_location, departure_time, packages):
        self.speed = speed
        self.mileage = mileage
        self.current_location = current_location
        self.departure_time = departure_time
        self.packages = packages

#Loads package data from packageCSV file into hash table
def load_package_data(file_name, hash_table):
    with open(file_name) as packages:
        package_data = csv.reader(packages, delimiter=',')
        next(package_data)#Skips header row

        for package in package_data:
            package_id=int(package[0])
            address = package[1]
            city = package[2]
            state = package[3]
            zip_code = package[4]
            deadline = package[5]
            weight = package[6]
            notes = package[7]

            package = Package(package_id, address, city, state, zip_code, deadline, weight, notes)
            hash_table.insert(package_id, package)

#Loads distance data from distanceCSV
def load_distance_data(file_name):
    with open(file_name) as csv_file:
        reader = csv.reader(csv_file)
        distance_data = list(reader)
    return distance_data

#Loads address data from addressCSV
def load_address_data(file_name):
    with open(file_name) as csv_file:
        reader = csv.reader(csv_file)
        return [row[2] for row in reader]

#Delivers packages using nearest neighbor algorithm
def truck_delivery_route(truck, hash_table, address_data, distance_matrix):
    #Starts at hub location
    current_location = address_data.index(truck.current_location)
    total_distance = 0.0 #Initializes total mileage for truck route
    current_time = truck.departure_time #Initializes current time to truck's departure time

    while truck.packages:
        nearest_package_id = None
        nearest_distance = float('inf')

        for package_id in truck.packages.copy():
            package = hash_table.search(package_id) #Retrieve package details from hash table by ID
            destination_index = address_data.index(package.address) #Gets index of delivery address in matrix
            #Calculates the distance between two locations using distance matrix
            distance = float(distance_matrix[current_location][destination_index] or distance_matrix[destination_index][current_location])

            #Check if this package is closer than the current nearest package
            if distance < nearest_distance:
                nearest_package_id = package_id
                nearest_distance = distance

        #Deliver the nearest package
        truck.packages.remove(nearest_package_id)
        package = hash_table.search(nearest_package_id)

        #Calculate travel time distance/speed and update current time
        travel_time = datetime.timedelta(hours=nearest_distance/18)
        current_time += travel_time

        #Update package delivery and departure times
        package.delivery_time = current_time
        package.departure_time = truck.departure_time

        #Update truck mileage and location
        total_distance += nearest_distance
        current_location = address_data.index(hash_table.search(nearest_package_id).address)

    #Update total mileage for the truck after all deliveries
    truck.mileage += total_distance

#Loads data from CSV files
package_hash_table = ChainingHashTable()
load_package_data("Data/packageCSV.csv", package_hash_table)
distance_matrix = load_distance_data("Data/distanceCSV.csv")
address_data = load_address_data("Data/addressCSV.csv")

#Manually loads the packages into the trucks
truck1 = Truck(18,0.0,"4001 South 700 East",datetime.timedelta(hours=8), [1,13,14,15,16,19,20,27,29,30,31,34,37,40])
truck2 = Truck(18,0.0,"4001 South 700 East",datetime.timedelta(hours=9, minutes=5), [2,3,4,5,9,18,26,28,32,33,35,36,38])
truck3 = Truck(18,0.0,"4001 South 700 East",datetime.timedelta(hours=9, minutes=5), [6,7,8,10,11,12,17,21,22,23,24,25,39])

#Executes the truck_delivery_route algorithm function for each truck
truck_delivery_route(truck1, package_hash_table, address_data, distance_matrix)
truck_delivery_route(truck2, package_hash_table, address_data, distance_matrix)
truck_delivery_route(truck3, package_hash_table, address_data, distance_matrix)

#Display header and total mileage
print("\nWestern Governors University Parcel Service (WGUPS)")
print("--------------------------------------------------")
print(f"Total Route Mileage: {truck1.mileage + truck2.mileage + truck3.mileage:.1f} miles\n")

#Gets the time input from user to check package status
def get_user_time():
    while True:
        time_input = input("Enter a time to check package status (HH:MM) or 'Q' to quit: ")
        if time_input.upper() == 'Q': #Allows user to quit program by typing Q
            exit()
        try:
            h, m = time_input.split(":") #Split input into hours and minutes
            return datetime.timedelta(hours=int(h), minutes=int(m)) #Convert to time delta
        except ValueError:
            print("Invalid format. Use HH:MM (e.g., 09:30).") #Error for invalid input format

#Gets user input for viewing All or Single package status or Quit
def get_package_choice():
    while True:
        choice = input("View: [A]ll packages, [S]ingle package, or [Q]uit: ").upper()
        if choice in ('A', 'S', 'Q'): #input validation
            return choice
        print("Invalid choice. Enter A/S/Q.") #Display error for invalid choice

#Displays package status
def display_package_status(package, time_change):
    package.update_status(time_change)
    print(
        f"Package {package.package_id:2}: {package.status:10} | Address: {package.address:25} | Deadline: {package.deadline:8} | "
        f"Delivered at: {str(package.delivery_time)[:5] if package.delivery_time else 'N/A':5}")


#Main UI loop
while True:
    #Get user input
    user_time = get_user_time()
    choice = get_package_choice()

    #Process user input
    if choice == 'Q': #Quit program if user inputs Q
        break
    elif choice == 'A': #Displays all packages if user chooses A
        print(f"\n{' ALL PACKAGE STATUS ':=^80}")
        packages_to_show = range(1, 41)
    else:
        package_id = int(input("Enter Package ID (1-40): ")) #Prompt user for package ID
        packages_to_show = [package_id]

    #Display status of each selected package
    print(f"\nStatus at {str(user_time)[:5]}:")
    print("-" * 80)
    for package_id in packages_to_show:
        package = package_hash_table.search(package_id) #Retreive package by ID from hash table
        if package:
            display_package_status(package, user_time) #Display status of package
    print("\n" + "=" * 80 + "\n")