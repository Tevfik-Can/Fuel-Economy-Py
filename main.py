import requests
import json
import folium
import webbrowser
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
def searchaddress(addr, coordinates):
    # Make a GET request to the OpenRouteService API for geocoding autocomplete
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    }
    if coordinates:
        call = requests.get(f'https://api.openrouteservice.org/geocode/autocomplete?api_key=5b3ce3597851110001cf624864'
                            f'706b80a53d4556b6fa3ed7cee7eebf&text={addr}&focus.point.lon={coordinates[0]}&'
                            f'focus.point.lat={coordinates[1]}&boundary.country=CA', headers=headers)
    else:
        call = requests.get(f'https://api.openrouteservice.org/geocode/autocomplete?api_key=5b3ce3597851110001cf624864'
                            f'706b80a53d4556b6fa3ed7cee7eebf&text={addr}&boundary.country=CA', headers=headers)

    # Print the status code and reason for the API call
    print(call.status_code, call.reason)
    # Print the raw content of the API response
    #print(call.content)

    # Parse the JSON response
    data = json.loads(call.text)
    return data["features"]

def finddirections(s_geo, d_geo):
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    }
    call = requests.get(f'https://api.openrouteservice.org/v2/directions/driving-car?api_key=5b3ce3597851110001cf624864'
                        f'706b80a53d4556b6fa3ed7cee7eebf&start={s_geo[0]},{s_geo[1]}&end={d_geo[0]},{d_geo[1]}',
                        headers=headers)

    print(call.status_code, call.reason)
    #print(call.text)

    data = json.loads(call.text)
    return data["features"]

def displayaddress(result):
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

addr = "121 Forestbrook st"
coordinates = []
result = searchaddress(addr, coordinates)
print("Source Address:")
displayaddress(result)


#Select the Source from user
selected_source = result[0]
print("\n\n-==-==-0=-=--=-=-\n\nThe selected SOURCE address is:\n")
s_locname = selected_source["properties"]['label']
s_geometry = selected_source["geometry"]["coordinates"]

print("Location Name: ", s_locname)
print("Coordinates: ", s_geometry)

addr = "Burrito Gringo"
coordinates = s_geometry
result = searchaddress(addr, coordinates)

print("DESTINATION:")
displayaddress(result)

#Select the Destination from user
selected_destination = result[0]

print("\n\n-==-==-0=-=--=-=-\n\nThe selected DESTINATION address is:\n")
d_locname = selected_destination["properties"]['label']
d_distance = selected_destination["properties"]['distance']
d_geometry = selected_destination["geometry"]["coordinates"]

print("Location Name: ", d_locname)
print("Estimated Distance: ", d_distance)
print("Coordinates: ", d_geometry)

#Find the direcitons from source to destination
result = finddirections(s_geometry, d_geometry)
i = 0
direction_cords = []
c = []
for cords in result[0]["geometry"]["coordinates"]:
    c1 = cords[1]  #Flip Log and Lat for the folium map (its flipped)
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
    i = i+1
    directions_list.append(step_dirs)

Actual_Dist = (result[0]['properties']['segments'][0]['distance']/1000)
print(f"\nLocation Name: {d_locname}\nThe Actual Distance: {Actual_Dist}km\nDuration: "
      f"{readabletime(result[0]['properties']['segments'][0]['duration'])}")

# Display the Directions
print(f"\n\nThe directions to {d_locname} from {s_locname}:")
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
carfind_model = "RAV4 Hy"
carfind_year = "2019"

carsearch = readcsv()


foundcar = search_car(carsearch, int(carfind_year), carfind_make, carfind_model)
print("Cars Found:")
carid = 0
titles = ["ID", "YEAR", "MAKE", "MODEL", "VHCL CLASS", "FUEL ECO CITY", "FUEL ECO HWY", "TRANSMSN"]
print("%-2s - %-4s - %-8s - %-15s - %-11s - %-8s - %-3s" % (titles[0], titles[1], titles[2], titles[3],
                                                             titles[4], titles[7], titles[5]))
for c in foundcar:
    carid = carid + 1
    print("%-2d - %-4d - %-8s - %-15s - %-11s - %-8s - %-3s L/100km" % (carid, c.year, c.make, c.model, c.v_class,
                                                                        c.transmission, c.fuel_eco_city))
# selected_model = input("Select the Car by its ID that you want to select: ")
selected_model = 1-1 #ID starts from 1, decrement 1 for array

c = foundcar[selected_model]
selected_car = cars(c.year, c.make, c.model, c.v_class, c.enginesize, c.transmission, c.fueltype,
                    c.fuel_eco_city, c.fuel_eco_hwy)

print("\nYou have selected:\n")
print("%-4s - %-8s - %-15s - %-11s - %-8s - %-3s - %-3s" % (titles[1], titles[2], titles[3],
                                                             titles[4], titles[7], titles[5], titles[6]))
print("%-4d - %-8s - %-15s - %-11s - %-8s - %-3s L/100km - %-3s L/100km" % (selected_car.year, selected_car.make,
                                                                            selected_car.model, selected_car.v_class,
                                                                            selected_car.transmission,
                                                                            selected_car.fuel_eco_city,
                                                                            selected_car.fuel_eco_hwy))

#Room of improvement, gas prices are static, and calculation does not take in the account for Highway
gasprices = 1.722
convertLkm_kmL = 1/(float(selected_car.fuel_eco_city)/100)   #Convert L/100km to L/km -> 8.8L/100km 1km/1L -> 1/0.088
calculated_Lkm = float(Actual_Dist / convertLkm_kmL)
calculated_cost = calculated_Lkm * gasprices
print(f"\nFor the giventrip {Actual_Dist:.2f}km with {selected_car.model} the amount of gas it will cost you is "
      f"{calculated_cost:0.2f}$")
# ----------------------------- TO DO List ----------------------------------
# - Ask for the source address anywhere in the world DONE
# - Then ask for the destination, now focus point being the source address DONE
# - List all the closest places dynamically "as the person types it pops up" (don't do it rn, maybe close to end) -------
# - Get the Latitude Longitude Of the destination place DONE (Staticly assigned the destination for now) ------------
# - Make an API call to find the directions and distance to that place DONE
# - Let user put their Address dynamically ------------
# - Plot the way to the destination DONE
# - Ask the user for their Car Brand / Model / Year and find their fuel economy ------------
# - Compare car's fuel economy to the general fuel prices close to his source DONE
# - As the final Boss... Make all the user interaction GUI based, no CMD, and dynamically search addresses ----------


# --------------- CTRL + /
m = folium.Map(location=[s_geometry[1], s_geometry[0]])

tooltip = "Click me!"

folium.Marker(
    [d_geometry[1], d_geometry[0]], popup=f"<h4> {d_locname}</h4>", tooltip=tooltip
).add_to(m)
folium.Marker(
    [s_geometry[1], s_geometry[0]], popup=f"<h4> {s_locname}</h4>", tooltip=tooltip
).add_to(m)

folium.PolyLine(direction_cords, tooltip="Directions").add_to(m)
m.save(r'C:\Users\tcgul\PycharmProjects\Fuel Economy Python\example.html')
webbrowser.open(r'C:\Users\tcgul\PycharmProjects\Fuel Economy Python\example.html')
#