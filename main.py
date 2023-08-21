import requests
import json
import folium
import webbrowser
import datetime
import humanize
from folium.plugins import Geocoder
import csv
import jellyfish
import re

class dirs:
    def __init__(self, dists, durs, insts):
        self.distance = dists
        self.duration = durs
        self.instruction = insts

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

def readabletime(time):
    temp = datetime.timedelta(seconds=time) # Makes minutes and seconds readable
    formatted_duration = humanize.precisedelta(temp, minimum_unit="seconds")
    return formatted_duration

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

# Make a GET request to the OpenRouteService API for geocoding autocomplete
# headers = {
#     'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
# }
# call = requests.get('https://api.openrouteservice.org/geocode/autocomplete?api_key=5b3ce3597851110001cf624864706b80a53\
# d4556b6fa3ed7cee7eebf&text=Tim&focus.point.lon=-75.942210&focus.point.lat=45.345580&boundary.country=CA',
#                     headers=headers)
#
# # Print the status code and reason for the API call
# print(call.status_code, call.reason)
#
# # Print the raw content of the API response
# print(call.content)
#
# # Parse the JSON response
# data = json.loads(call.text)
# result = data["features"]
# for locations in result:
#     print(" ")
#     locname = locations["properties"]['label']
#     distance = locations["properties"]['distance']
#
#     print("Location Name: ", locname)
#     print("Distance: ", distance)
#     try:
#         address = locations["properties"]["name"] + ", " + locations["properties"]["housenumber"] + " " + \
#                   locations["properties"]["street"]
#         print("Address : ", address)
#     except:
#         print("No Specific Address")
#
# #Select the Destination from user
# selected_destination = result[0]
#
# print("\n\n-==-==-0=-=--=-=-\n\nThe selected address is:\n")
# locname = selected_destination["properties"]['label']
# distance = selected_destination["properties"]['distance']
# geometry = selected_destination["geometry"]["coordinates"]
#
# print("Location Name: ", locname)
# print("Estimated Distance: ", distance)
# print("Coordinates: ", geometry)
#
#
# #Get the Directions
# headers = {
#     'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
# }
# call = requests.get(f'https://api.openrouteservice.org/v2/directions/driving-car?api_key=5b3ce3597851110001cf624864706b\
# 80a53d4556b6fa3ed7cee7eebf&start=-75.942210,45.3455801&end={geometry[0]},{geometry[1]}', headers=headers)
#
# print(call.status_code, call.reason)
# print(call.text)
# data = json.loads(call.text)
# result = data["features"]
#
# directions_list = []  # List to hold dirs objects for each step
# for step in result[0]["properties"]["segments"][0]["steps"]:
#     distance = step["distance"]
#     duration = step["duration"]
#     instruction = step["instruction"]
#
#     # Create a dirs object for the current step and add it to the list
#     step_dirs = dirs(distance, duration, instruction)
#     directions_list.append(step_dirs)
#
# Actual_Dist = (result[0]['properties']['segments'][0]['distance']/1000)
# print(f"\nLocation Name: {locname}\nThe Actual Distance: {Actual_Dist}km\nDuration: "
#       f"{readabletime(result[0]['properties']['segments'][0]['duration'])}")
#
# # Display the Directions
# print(f"\n\nThe directions to {locname} :")
# for d in directions_list:
#     print(d.instruction)
#     print("Distance: %.2f km" % float(d.distance/1000))
#     print(f"Duration: {readabletime(d.duration)}\n")
#     #Room of improvement, when destination is reached, dont write the distance and duration


#Ask for what Model Car user drive

#The information that is going to be asked to user:
# carfind_year = input("Enter the year: ")
# carfind_make = input("Enter the make: ")
# carfind_model = input("Enter the model: ")
carfind_make = "Toyota"
carfind_model = "RAy4"
carfind_year = "2019"

carsearch = readcsv()


foundcar = search_car(carsearch, int(carfind_year), carfind_make, carfind_model)
print("Cars Found:")
carid = 0
for c in foundcar:
    carid = carid + 1
    print(f"{carid} - {c.year} - {c.make} - {c.model} - {c.v_class} - {c.fuel_eco_city} L/100km")


# ----------------------------- TO DO List ----------------------------------
# - Ask for the source address anywhere in the world
# - Then ask for the destination, now focus point being the source address
# - List all the closest places dynamically "as the person types it pops up" (dont have to do it rn, maybe close to end)
# - Get the Latitude Longitude Of the destination place DONE (Staticly assigned the destination for now)
# - Make an API call to find the directions and distance to that place DONE
# - Let user put their Address dynamically
# - Plot the way to the destination
# - Ask the user for their Car Brand / Model / Year and find their fuel economy
# - Compare car's fuel economy to the general fuel prices close to his source
# - As the final Boss... Make all of the user interaction GUI based, no command line, and dynamically search addresses


# --------------- CTRL + /
# m = folium.Map(location=[45.424721, -75.695000])
#
# tooltip = "Click me!"
#
# folium.Marker(
#     [45.345580, -75.942210], popup="<i>Mt. Hood Meadows</i>", tooltip=tooltip
# ).add_to(m)
# folium.Marker(
#     [45.3311, -121.7113], popup="<b>Timberline Lodge</b>", tooltip=tooltip
# ).add_to(m)
#
# m.save(r'C:\Users\tcgul\PycharmProjects\Fuel Economy Python\example.html')
# webbrowser.open(r'C:\Users\tcgul\PycharmProjects\Fuel Economy Python\example.html')
#