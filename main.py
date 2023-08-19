import requests
import json
import folium
import webbrowser

# Make a GET request to the OpenRouteService API for geocoding autocomplete
headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
}
call = requests.get('https://api.openrouteservice.org/geocode/autocomplete?api_key=5b3ce3597851110001cf624864706b80a53\
d4556b6fa3ed7cee7eebf&text=Tim&focus.point.lon=-75.942210&focus.point.lat=45.345580&boundary.country=CA',
                    headers=headers)

# Print the status code and reason for the API call
print(call.status_code, call.reason)

# Print the raw content of the API response
print(call.content)

# Parse the JSON response
data = json.loads(call.text)
result = data["features"]
for locations in result:
    print(" ")
    locname = locations["properties"]['label']
    distance = locations["properties"]['distance']

    print("Location Name: ", locname)
    print("Distance: ", distance)
    try:
        address = locations["properties"]["name"] + ", " + locations["properties"]["housenumber"] + " " + \
                  locations["properties"]["street"]
        print("Address : ", address)
    except:
        print("No Specific Address")


# ----------------------------- TO DO List ----------------------------------
# - List all the closest places dynamically (dont have to do it rn, maybe close to end)
# - Get the Latitude Longitude Of the destination place
# - Make an API call to find the directions and distance to that place
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
    # m.save (r'C:\Users\tcgul\PycharmProjects\Fuel Economy Python\example.html')
    # webbrowser.open(r'C:\Users\tcgul\PycharmProjects\Fuel Economy Python\example.html')
#