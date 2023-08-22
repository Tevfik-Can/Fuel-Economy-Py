import datetime
import humanize
#from folium.plugins import Geocoder
import csv
import jellyfish
import re

class dirs:
    def __init__(self, dists, durs, insts, coordinates):
        self.distance = dists
        self.duration = durs
        self.instruction = insts
        self.coordinates = coordinates

class cars:
    def __init__(self, year, make, model, v_class, enginesize, transmission, fueltype, fuel_eco_city, fuel_eco_hwy):
        self.year = year
        self.make = make
        self.model = model
        self.v_class = v_class
        self.transmission = transmission
        self.fuel_eco_city = fuel_eco_city
        self.fuel_eco_hwy = fuel_eco_hwy
        self.fueltype = fueltype
        self.enginesize = enginesize

def displayaddress(result):
    #Shows the addresses found after a search
    for locations in result:
        print(" ")
        locname = locations["properties"]['label']
        print("Location Name: ", locname)

        if locations["properties"].get('distance') is not None:
            distance = locations["properties"]['distance']
            print("Distance: ", distance)

        try:
            address = locations["properties"]["name"] + ", " + locations["properties"]["housenumber"] + " " + \
                      locations["properties"]["street"]
            print("Address : ", address)
        except:
            print("No Specific Address")


def search_car(carsearch, year, make, model):
    selectedcars = []
    changed = True
    for car in carsearch:  #Search for the implicit cars
        if car.year == year and re.search(make, car.make) and re.search(model, car.model):
            selectedcars.append(car)
    if selectedcars:
        return selectedcars

    for car in carsearch: #If nothing is found, search for closer to input cars
        #Search if there are any typos in the name, if there is, change it to what it "could" be
        if jellyfish.jaro_winkler(car.make, make) >= 0.8 and car.year == year and jellyfish.jaro_winkler(car.model, model) >= 0.8 and changed:
            make = car.make
            model = car.model
            changed = False
            print(model) #Model Changes to AWD since its "80% close to RAV4"

        #Check if there are sub categories for them and append to selected cars
        if car.year == year and re.search(make, car.make) and re.search(model, car.model):
            selectedcars.append(car)
    if selectedcars:
        return selectedcars
    else:
        return None

def readabletime(time):
    temp = datetime.timedelta(seconds=time) # Makes minutes and seconds readable
    formatted_duration = humanize.precisedelta(temp, minimum_unit="seconds")
    return formatted_duration

def readcsv():
    carsearch = []
    with open("./Original MY2000-2023 Fuel Consumption Ratings.csv", "r") as file:
        csvreader = csv.reader(file)
        csvreader.__next__()  #Hop over the first 2 lines of csv (Titles)
        csvreader.__next__()
        for row in csvreader:
            # 0 year, 1 make, 2 model, 3 v_class, 4 enginesize, 6 transmission, 7 fueltype, 8 fuel_eco_city, 9 fuel_eco_hwy
            car = cars(int(row[0]), row[1], row[2], row[3], row[4], row[6], row[7], row[8], float(row[9]))
            carsearch.append(car)
    return carsearch


def addr_instructions(result):
    i = 0
    direction_cords = []
    c = []
    for cords in result[0]["geometry"]["coordinates"]:
        c1 = cords[1]  # Flip Log and Lat for the folium map (its flipped)
        c2 = cords[0]
        c = [c1, c2]
        direction_cords.append(c)

    directions_list = []  # List to hold dirs objects for each step
    for step in result[0]["properties"]["segments"][0]["steps"]:
        distance = step["distance"]
        duration = step["duration"]
        instruction = step["instruction"]

        # Create a dirs object for the current step and add it to the list
        step_dirs = dirs(distance, duration, instruction, direction_cords[i])
        print(direction_cords[i])
        i = i + 1
    return directions_list


def displaycars(foundcar, titles):
    print("Cars Found:")
    if not foundcar:
        exit("Car is not found")
    carid = 0

    print("%-2s - %-4s - %-8s - %-15s - %-11s - %-8s - %-3s" % (titles[0], titles[1], titles[2], titles[3],
                                                                titles[4], titles[7], titles[5]))
    for c in foundcar:
        carid = carid + 1
        print("%-2d - %-4d - %-8s - %-15s - %-11s - %-8s - %-3s L/100km" % (carid, c.year, c.make, c.model, c.v_class,
                                                                            c.transmission, c.fuel_eco_city))