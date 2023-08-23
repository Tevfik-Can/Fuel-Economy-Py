import api_calls
import functions

import folium
import webbrowser

addr = "121 forestbrook st"
coordinates = []
result = api_calls.searchaddress(addr, coordinates)
if len(result) == 0:
    exit("The address is not found")
print("Source Address:")
functions.displayaddress(result)

#Select the Source from user
selected_source = result[0]
print("\n\n-==-==-0=-=--=-=-\n\nThe selected SOURCE address is:\n")
s_locname = selected_source["properties"]['label']
s_geometry = selected_source["geometry"]["coordinates"]

print("Location Name: ", s_locname)
print("Coordinates: ", s_geometry)

addr = "bayshore"
coordinates = s_geometry
result = api_calls.searchaddress(addr, coordinates)

print("DESTINATION:")
if len(result) == 0:
    exit("The address is not found")
functions.displayaddress(result)

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
result = api_calls.finddirections(s_geometry, d_geometry)

directions_list = functions.addr_instructions(result)

Actual_Dist = (result[0]['properties']['segments'][0]['distance']/1000)
print(f"\nLocation Name: {d_locname}\nThe Actual Distance: {Actual_Dist}km\nDuration: "
      f"{functions.readabletime(result[0]['properties']['segments'][0]['duration'])}")

# Display the Directions
print(f"\n\nThe directions to {d_locname} from {s_locname}:")
for d in directions_list:

    print(d.instruction)
    print("Distance: %.2f km" % float(d.distance/1000))
    print(f"Duration: {functions.readabletime(d.duration)}\n")
    #Room of improvement, when destination is reached, dont write the distance and duration

#Ask for what Model Car user drive
#The information that is going to be asked to user:
# carfind_year = input("Enter the year: ")
# carfind_make = input("Enter the make: ")
# carfind_model = input("Enter the model: ")
carfind_make = "Honda"
carfind_model = "Civic"
carfind_year = "2022"

carsearch = functions.readcsv()

foundcar = functions.search_car(carsearch, int(carfind_year), carfind_make, carfind_model)
titles = ["ID", "YEAR", "MAKE", "MODEL", "VHCL CLASS", "FUEL ECO CITY", "FUEL ECO HWY", "TRANSMSN"]

functions.displaycars(foundcar, titles)

# selected_model = input("Select the Car by its ID that you want to select: ")
selected_model = 1-1 #ID starts from 1, decrement 1 for array

c = foundcar[selected_model]
selected_car = functions.cars(c.year, c.make, c.model, c.v_class, c.enginesize, c.transmission, c.fueltype,
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

print(f"\nFor the given trip {Actual_Dist:.2f} km with {selected_car.model} the amount of gas it will cost you is "
      f"{calculated_cost:0.2f}$")
# ----------------------------- TO DO List ----------------------------------
# - Ask for the source address anywhere in the world DONE
# - Then ask for the destination, now focus point being the source address DONE
# - Get the Latitude Longitude Of the destination place DONE (Staticly assigned the destination for now) DONE
# - Make an API call to find the directions and distance to that place DONE
# - Let user put their Address dynamically DONE
# - Plot the way to the destination DONE
# - Ask the user for their Car Brand / Model / Year and find their fuel economy DONE
# - Compare car's fuel economy to the general fuel prices close to his source DONE

# - As the final Boss... Make all the user interaction GUI based, no CMD, and dynamically search addresses ----------
# - List all the closest places dynamically "as the person types it pops up" (don't do it rn, maybe close to end) -----
# - Take in the account for highway fuel economy

# --------------- CTRL + /
m = folium.Map(location=[s_geometry[1], s_geometry[0]])

tooltip = "Click me!"

#Setup a marker for both location
folium.Marker(
    [d_geometry[1], d_geometry[0]], popup=f"<h4> {d_locname}</h4>", tooltip=tooltip
).add_to(m)
folium.Marker(
    [s_geometry[1], s_geometry[0]], popup=f"<h4> {s_locname}</h4>", tooltip=tooltip
).add_to(m)

#Get all the coordinates for each step
all_cords = []
c = []
for cords in result[0]["geometry"]["coordinates"]:
    c1 = cords[1]  # Flip Log and Lat for the folium map (its flipped)
    c2 = cords[0]
    c = [c1, c2]
    all_cords.append(c)

folium.PolyLine(all_cords, tooltip="Directions").add_to(m)
m.save(r'C:\Users\tcgul\PycharmProjects\Fuel Economy Python\example.html')
webbrowser.open(r'C:\Users\tcgul\PycharmProjects\Fuel Economy Python\example.html')
