import requests
import json

API_KEY = "5b3ce3597851110001cf624864706b80a53d4556b6fa3ed7cee7eebf"

def finddirections(s_geo, d_geo):
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    }
    call = requests.get(f'https://api.openrouteservice.org/v2/directions/driving-car?api_key={API_KEY}&start={s_geo[0]}'
                        f',{s_geo[1]}&end={d_geo[0]},{d_geo[1]}',
                        headers=headers)

    print(call.status_code, call.reason)
    #print(call.text)

    data = json.loads(call.text)
    return data["features"]

def searchaddress(addr, coordinates):
    # Make a GET request to the OpenRouteService API for geocoding autocomplete
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    }
    if coordinates:
        call = requests.get(f'https://api.openrouteservice.org/geocode/autocomplete?api_key={API_KEY}&text={addr}&'
                            f'focus.point.lon={coordinates[0]}&focus.point.lat={coordinates[1]}&boundary.country=CA',
                            headers=headers)
    else:
        call = requests.get(f'https://api.openrouteservice.org/geocode/autocomplete?api_key={API_KEY}&text={addr}&'
                            f'boundary.country=CA', headers=headers)

    # Print the status code and reason for the API call
    print(call.status_code, call.reason)
    # Print the raw content of the API response
    #print(call.content)

    # Parse the JSON response
    data = json.loads(call.text)
    return data["features"]
