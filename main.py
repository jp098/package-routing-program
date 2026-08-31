#Name: Jair Palacios

import csv
import datetime
import re

#Constants
TRUCK_CAPACITY = 16
TRUCK_SPEED_MPH = 18
HUB_ADDRESS = "4001 South 700 East"
PACKAGE_COUNT = 40
PACKAGE_9_ADDRESS_CORRECTION_TIME = datetime.timedelta(
    hours=10,
    minutes=20
)

PACKAGE_9_CORRECTED_ADDRESS = "410 S State St"
PACKAGE_9_CORRECTED_ZIP = "84111"

END_OF_DAY_TIME = datetime.timedelta(
    hours = 23,
    minutes = 59
)

TRUCK_DEPARTURE_TIMES = {
        1: datetime.timedelta(hours = 8),
        2: datetime.timedelta(hours = 9, minutes = 5),
        3: datetime.timedelta(hours = 9, minutes = 5),
}

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
        for key_value in bucket_list:
            if key_value[0] == key:
                key_value[1] = item
                return True

        #If not add the item to the end of the bucket list
        bucket_list.append([key, item])
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

#Creates the package object to store package information
class Package:
    def __init__(
            self,
            package_id,
            address,
            city,
            state,
            zip_code,
            deadline,
            weight,
            notes= ""
    ):

            self.package_id = package_id
            self.address = address
            self.city = city
            self.state = state
            self.zip_code = zip_code
            self.deadline = deadline
            self.weight = weight
            self.notes = notes

            #Preserve original address so status searches at earlier times remain
            #accurate even after a later search changes package 9's address.
            self.original_address = address
            self.original_zip_code = zip_code

            self.status = "At the Hub"
            self.departure_time = None
            self.delivery_time = None
            self.delivered_by_truck = None

    #Updates the status of the package
    def update_status(self, current_time):
        #Updates the address for package 9 at 10:20AM
        if self.package_id == 9:
            if current_time >= PACKAGE_9_ADDRESS_CORRECTION_TIME:
                self.address = PACKAGE_9_CORRECTED_ADDRESS
                self.zip_code = PACKAGE_9_CORRECTED_ZIP
            else:
                self.address = self.original_address
                self.zip_code = self.original_zip_code

        if self.delivery_time is not None and current_time >= self.delivery_time:
            self.status = "Delivered"
        elif self.departure_time is not None and current_time >= self.departure_time:
            self.status = "En Route"
        else:
            self.status = "At the Hub"

#Creates the truck object to store truck information
class Truck:
    def __init__(
            self,
            speed,
            mileage,
            current_location,
            departure_time,
            packages
    ):
        self.speed = speed
        self.mileage = mileage
        self.current_location = current_location
        self.departure_time = departure_time
        self.packages = packages
        self.route_history = []

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

            package = Package(
                package_id,
                address,
                city,
                state,
                zip_code,
                deadline,
                weight,
                notes
            )

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

#Return each package currently stored in the hash table
def get_all_packages(hash_table, package_count = PACKAGE_COUNT):
    packages = []

    for package_id in range(1, package_count + 1):
        package = hash_table.search(package_id)

        if package is not None:
            packages.append(package)

    return packages

#Convert '10:30 AM' to timedelta and makes EOD lowest priority
def deadline_to_timedelta(deadline):
    if deadline.strip().upper() == "EOD":
        return END_OF_DAY_TIME

    parsed_time = datetime.datetime.strptime(
        deadline.strip(),
        "%I:%M %p"
    ).time()

    return datetime.timedelta(
        hours = parsed_time.hour,
        minutes = parsed_time.minute
    )

# Reads restriction such as 'Can only be on truck 2' from the SpecialNotes column
def get_truck_restrictions(package):
    match = re.search(
        r"can\s+only\s+be\s+on\s+truck\s+(\d+)",
        package.notes.lower()
    )

    if match:
        return int(match.group(1))

    return None

#Returns the depot-arrival time for packages whose notes indicate it was delayed
def get_delayed_arrival_time(package):
    if "delayed" not in package.notes.lower():
        return None

    match = re.search(
        r"until\s+(\d{1,2}:\d{2}\s*[ap]m)",
        package.notes.lower()
    )

    if match is None:
        return None

    parsed_time = datetime.datetime.strptime(
        match.group(1).upper().replace(" ", ""),
        "%I:%M%p"
    ).time()

    return datetime.timedelta(
        hours = parsed_time.hour,
        minutes = parsed_time.minute
    )

#Builds groups automatically from notes such as: "Must be delivered with..."
#A connected group is kept together. For this CSV, the result includes {13, 14, 15, 16, 19,20}
def get_delivery_groups(packages):
    graph = {}

    for package in packages:
        package_id = package.package_id
        graph.setdefault(package_id, set())

        if "must be delivered with" not in package.notes.lower():
            continue

        related_ids = re.findall(r"\d+", package.notes)

        for related_id in related_ids:
            related_id = int(related_id)

            graph.setdefault(related_id, set())
            graph[package.package_id].add(related_id)
            graph[related_id].add(package.package_id)

    groups = []
    visited = set()

    for package_id in graph:
        if package_id in visited or not graph[package_id]:
            continue

        group = set()
        stack = [package_id]

        while stack:
            current_id = stack.pop()

            if current_id in visited:
                continue

            visited.add(current_id)
            group.add(current_id)

            for neighbor in graph[current_id]:
                if neighbor not in visited:
                    stack.append(neighbor)

        if len(group) > 1:
            groups.append(group)

    return groups

#Returns all package IDs already assigned to a truck
def assigned_package_ids(truck_loads):
    return set(
        truck_loads[1] +
        truck_loads[2] +
        truck_loads[3]
    )

#Return trucks with enough available capacity
def available_trucks_with_capacity(
        truck_loads,
        allowed_trucks,
        needed_slots=1
):

    return [
        truck_number
        for truck_number in allowed_trucks
        if len(truck_loads[truck_number]) + needed_slots <= TRUCK_CAPACITY
    ]

#Choose the truck with the fewest packages
def choose_least_loaded_truck(truck_loads, truck_numbers):
    return min(
        truck_numbers,
        key=lambda truck_number: len(truck_loads[truck_number])
    )

#Return trucks allowed to load a package
def get_allowed_trucks(package, truck_departure_times):
    delayed_until = get_delayed_arrival_time(package)

    if delayed_until is None:
        return tuple(sorted(truck_departure_times.keys()))

    return tuple(
        truck_number
        for truck_number, departure_time in truck_departure_times.items()
        if departure_time >= delayed_until
    )

#Automatically loads packages onto trucks
#Priorities: 1.Packages restricted to a specific truck, 2.Packages that must be delivered together,
#3.Deadline packages, 4.Remaining EOD packages
def build_truck_loads(hash_table):
    truck_loads = {
        1: [],
        2: [],
        3: [],
    }

    packages = get_all_packages(hash_table)

    #1. Assign truck-only packages from SpecialNotes
    for package in packages:
        required_truck = get_truck_restrictions(package)

        if required_truck is None:
            continue

        if len(truck_loads[required_truck]) >= TRUCK_CAPACITY:
            raise ValueError(
                f"Truck {required_truck} has no room for package"
                f"{package.package_id}"
            )

        truck_loads[required_truck].append(package.package_id)

    #2. Keeps linked packages together
    package_groups = get_delivery_groups(packages)

    for group in package_groups:
        assigned_ids = assigned_package_ids(truck_loads)
        unassigned_group = group - assigned_ids

        if not unassigned_group:
            continue

        #If any linked package already has a truck assigned, the entire group
        #must be placed on the same truck
        trucks_already_used = [
            truck_number
            for truck_number in (1, 2, 3)
            if any(
                package_id in truck_loads[truck_number]
                for package_id in group
            )
        ]

        if len(trucks_already_used) > 1:
            raise ValueError(
                f"Packages in group {sorted(group)} were split"
                f"across multiple trucks."
            )

        allowed_trucks = (
            trucks_already_used
            if trucks_already_used
            else (1, 2, 3)
        )

        trucks_with_space = available_trucks_with_capacity(
            truck_loads,
            allowed_trucks,
            len(unassigned_group)
        )

        if not trucks_with_space:
            raise ValueError(
                f"No truck has room for grouped packages {sorted(group)}."
            )

        selected_truck = choose_least_loaded_truck(
            truck_loads,
            trucks_with_space
        )

        truck_loads[selected_truck].extend(sorted(unassigned_group))

    #3. Sort unassigned packages by delivery deadline.
    remaining_packages = [
        package
        for package in packages
        if package.package_id not in assigned_package_ids(truck_loads)
    ]

    remaining_packages.sort(
        key=lambda package: deadline_to_timedelta(package.deadline)
    )

    for package in remaining_packages:
        allowed_trucks = get_allowed_trucks(
            package,
            TRUCK_DEPARTURE_TIMES
        )

        trucks_with_space = available_trucks_with_capacity(
            truck_loads,
            allowed_trucks
        )

        if not trucks_with_space:
            raise ValueError(
                f"No compatible truck has room for package {package.package_id}"
            )

        selected_truck = choose_least_loaded_truck(
            truck_loads,
            trucks_with_space
        )

        truck_loads[selected_truck].append(package.package_id)

    return truck_loads

#Return distance between two address-matrix indexes
def get_distance(distance_matrix, location_a, location_b):
    distance_value = (
        distance_matrix[location_a][location_b]
        or distance_matrix[location_b][location_a]
    )

    return float(distance_value)

#Return true when a package deadline is before end of day
def is_early_deadline(package):
    return deadline_to_timedelta(package.deadline) < END_OF_DAY_TIME

#Select next package using deadline aware routing
#Priority: 1. Packages that can still be delivered by their deadline, 2. Earlier deadlines,
#3. Shorter distance for packages with the same deadline
def select_best_next_package(
        truck,
        hash_table,
        address_data,
        distance_matrix,
        current_location,
        current_time
):
    best_package_id = None
    best_distance = float('inf')
    best_deadline = END_OF_DAY_TIME

    for package_id in truck.packages:
        package = hash_table.search(package_id)

        #Package 9 cannot be delivered before its address is corrected
        if (
            package.package_id == 9
            and current_time <PACKAGE_9_ADDRESS_CORRECTION_TIME
        ):
            continue

        destination_index = address_data.index(package.address)

        distance = get_distance(
            distance_matrix,
            current_location,
            destination_index
        )

        travel_time = datetime.timedelta(
            hours = distance / truck.speed
        )

        estimated_arrival_time = current_time + travel_time
        package_deadline = deadline_to_timedelta(package.deadline)

        #Do not selec a package that would already be late
        if estimated_arrival_time > package_deadline:
            continue

        #Choose earliest deadline, for equal deadlines chooses closest stop
        if (
            package_deadline < best_deadline
            or (
            package_deadline == best_deadline
            and distance < best_distance
            )
        ):
            best_package_id = package_id
            best_distance = distance
            best_deadline = package_deadline

    return best_package_id, best_distance

#Return the closest deliverable package without enforcing its deadline
#Only used as a fallback after no remaining package can meet its deadline
def select_closest_available_package(
    truck,
    hash_table,
    address_data,
    distance_matrix,
    current_location,
    current_time
):
    closest_package_id = None
    closest_distance = float('inf')

    for package_id in truck.packages:
        package = hash_table.search(package_id)

        if (
            package.package_id == 9
            and current_time <PACKAGE_9_ADDRESS_CORRECTION_TIME
        ):
            continue

        destination_index = address_data.index(package.address)

        distance = get_distance(
            distance_matrix,
            current_location,
            destination_index
        )

        if distance < closest_distance:
            closest_package_id = package_id
            closest_distance = distance

    return closest_package_id, closest_distance

#Delivers packages using deadline aware nearest neighbor algorithm
def truck_delivery_route(
    truck,
    hash_table,
    address_data,
    distance_matrix,
    truck_number
):

    #Starts at hub location
    current_location = address_data.index(truck.current_location)
    total_distance = 0.0 #Initializes total mileage for truck route
    current_time = truck.departure_time #Initializes current time to truck's departure time

    while truck.packages:
        package_id, distance = select_best_next_package(
            truck,
            hash_table,
            address_data,
            distance_matrix,
            current_location,
            current_time
        )

        #If no on-time package can be selected, use the nearest available package
        if package_id is None:
            package_id, distance = select_closest_available_package(
                truck,
                hash_table,
                address_data,
                distance_matrix,
                current_location,
                current_time
            )

        #If only package 9 remains before 10:20am, wait for address correction
        if package_id is None:
            if current_time < PACKAGE_9_ADDRESS_CORRECTION_TIME:
                current_time = PACKAGE_9_ADDRESS_CORRECTION_TIME
                continue

            raise RuntimeError(
                f"Truck {truck_number} has no deliverable package."
            )

        package = hash_table.search(package_id)

        #Record a warning when the fallback route will deliver a package late
        travel_time = datetime.timedelta(
            hours = distance / truck.speed
        )
        estimated_arrival_time = current_time + travel_time
        deadline = deadline_to_timedelta(package.deadline)

        if (
            deadline < END_OF_DAY_TIME
            and estimated_arrival_time > deadline
        ):
            print(
                f"Warning: Truck {truck_number} will deliver "
                f"package {package.package_id} late. "
                f"Deadline: {package.deadline}. "
                f"estimated arrival time: {estimated_arrival_time}."
            )

        #Deliver the selected package
        truck.packages.remove(package_id)

        current_time = estimated_arrival_time

        #Update package delivery, departure times, and truck number
        package.departure_time = truck.departure_time
        package.delivery_time = current_time
        package.delivered_by_truck = truck_number

        #Stores route history using a dictionary
        truck.route_history.append(
            {
                "package_id": package.package_id,
                "address": package.address,
                "city": package.city,
                "state": package.state,
                "zip_code": package.zip_code,
                "delivery_time": package.delivery_time,
                "distance_from_previous_stop": distance
            }
        )

        #Update truck mileage and location
        total_distance += distance
        current_location = address_data.index(package.address)

    #Update total mileage for the truck after all deliveries
    truck.mileage += total_distance

#Loads data from CSV files
package_hash_table = ChainingHashTable()
load_package_data("Data/packageCSV.csv", package_hash_table)
distance_matrix = load_distance_data("Data/distanceCSV.csv")
address_data = load_address_data("Data/addressCSV.csv")

#Automatically assign packages based on CSV constraints
truck_loads = build_truck_loads(package_hash_table)

trucks = {
    truck_number: Truck(
        speed = TRUCK_SPEED_MPH,
        mileage = 0.0,
        current_location = HUB_ADDRESS,
        departure_time = departure_time,
        packages = truck_loads[truck_number]
    )
    for truck_number, departure_time in TRUCK_DEPARTURE_TIMES.items()
}


#Display header and total mileage
print("\n Fast Deliveries Parcel Service")
print("-" * 90)

print("\nAutomatic truck assignments:")

for truck_number, truck in trucks.items():
    print(
        f"Truck {truck_number}: "
        f"{sorted(truck.packages)}"
    )

#Creates route after package assignment
for truck_number, truck in trucks.items():
    truck_delivery_route(
        truck,
        package_hash_table,
        address_data,
        distance_matrix,
        truck_number
    )

print("\nRoute mileage:")

for truck_number, truck in trucks.items():
    print(
        f"Truck {truck_number}: "
        f"{truck.mileage:.1f} miles"
    )

total_mileage = sum(
    truck.mileage
    for truck in trucks.values()
)

print(f"Total route mileage: {total_mileage:.1f} miles\n")

#Convert timedelta back to a 12-hour time string.
def format_time(time_value):
    if time_value is None:
        return "N/A"

    total_minutes = int(time_value.total_seconds() // 60)
    hours_24 = total_minutes // 60
    minutes = total_minutes % 60

    suffix = "AM" if hours_24 < 12 else "PM"
    hours_12 = hours_24 % 12

    if hours_12 == 0:
        hours_12 = 12

    return f"{hours_12}:{minutes:02} {suffix}"

#Gets the time input from user to check package status
def get_user_time():
    while True:
        time_input = input("Enter a time to check package status (HH:MM) or 'Q' to quit: ")
        if time_input.upper() == 'Q': #Allows user to quit program by typing Q
            return None
        try:
            h, m = time_input.split(":") #Split input into hours and minutes
            return datetime.timedelta(hours=int(h), minutes=int(m)) #Convert to time delta
        except ValueError:
            print("Invalid format. Use HH:MM (e.g., 09:30).") #Error for invalid input format

#Gets user input for viewing All or Single package status or Quit
def get_package_choice():
    while True:
        choice = input("View: [A]ll packages, [S]ingle package, [R]oute, or [Q]uit: ").upper()
        if choice in ('A', 'S', 'R', 'Q'): #input validation
            return choice
        print("Invalid choice. Enter A, S, R, or Q.") #Display error for invalid choice

#Gets user input for viewing All or a single
def get_truck_number(trucks):
    while True:
        truck_input = input(
            f"Enter Truck Number ({', '.join(map(str, trucks.keys()))}), "
            f"or [Q]uit: "
        ).upper()

        if truck_input == "Q":
            return None

        try:
            truck_number = int(truck_input)

            if truck_number in trucks:
                return truck_number

            print("Invalid Truck Number")

        except ValueError:
            print("Invalid Truck Number. Enter a valid Truck Number or [Q]uit.")

def display_package_status(package, time_change):
    package.update_status(time_change)
    print(
        f"Package {package.package_id:2}: "
        f"{package.status:10} | "
        f"Address: {package.address:25} | "
        f"Deadline: {package.deadline:8} | "
        f"Delivered at: {format_time(package.delivery_time):8} | "
        f"Assigned To Truck: {package.delivered_by_truck}"
    )

def display_truck_route(truck_number, truck):
    print(f"\n{"TRUCK " + str(truck_number) + " ROUTE ":=^90}")
    print(
        f"Departure time: {format_time(truck.departure_time)} | "
        f"Total mileage: {truck.mileage:.1f} miles"
    )
    print("-" * 100)

    if not truck.route_history:
        print("No route information available for this truck.")
        return

    print(f"{'Stop':<6} {'Package':<10} {'Address':<58} {'Delivered':<14} {'Distance':<12}")
    print("-" * 100)

    for stop_number, stop in enumerate(truck.route_history, start=1):
        full_address = (
            f"{stop['address']}, "
            f"{stop['city']}, "
            f"{stop['state']}, "
            f"{stop['zip_code']}"
        )

        distance = stop.get(
            "distance_from_previous_stop", 0.0
        )

        print(
            f"{stop_number:<6} "
            f"{stop['package_id']:<10} "
            f"{full_address:<58} "
            f"{format_time(stop['delivery_time']):<14} "
            f"{stop['distance_from_previous_stop']:.1f} mi"
        )

    print("-" * 100)

#Main UI loop
while True:
    #Get user input
    choice = get_package_choice()

    #Process user input
    if choice == 'Q': #Quit program if user inputs Q
        break

    if choice == 'R':
        truck_number = get_truck_number(trucks)

        if truck_number is not None:
            display_truck_route(
                truck_number,
                trucks[truck_number]
            )

        continue

    user_time = get_user_time()

    if choice == 'A': #Displays all packages if user chooses A
        print(f"\n{' ALL PACKAGE STATUSES ':=^130}")
        packages_to_show = range(1, PACKAGE_COUNT + 1)
    else:
        package_id = int(input(f"Enter Package ID (1-{PACKAGE_COUNT}): ")) #Prompt user for package ID
        packages_to_show = [package_id]

    #Display status of each selected package
    print(f"\nStatus at {format_time(user_time)}:")
    print("-" * 130)
    for package_id in packages_to_show:
        package = package_hash_table.search(package_id) #Retrieve package by ID from hash table
        if package:
            display_package_status(package, user_time) #Display status of package
    print("\n" + "=" * 130 + "\n")

print("\nThank you for using Fast Deliveries Parcel Service.")