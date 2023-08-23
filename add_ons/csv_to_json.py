import csv
import json
import os


# CSV
current_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the CSV file located one level back
csv_file_path = os.path.join(current_directory, "..", "Original MY2000-2023 Fuel Consumption Ratings.csv")
csv_file_name = "Original MY2000-2023 Fuel Consumption Ratings"
# JSON
json_dosya_adi = 'Fuel Consumption Ratings 2000-2023.json'
title = ["year", "make", "model", "vehicle_class", "engine_size", "cylinders", "transmission", "fuel_type", "fuel_consumption", "co2_emissions"]
csvdata = []
# CSV dosyasını aç ve JSON dosyasını yaz
with open(csv_file_path, 'r') as file:
    # CSV dosyasını bir sözlük listesine dönüştür
    csv_reader = csv.reader(file)
    json_data = []
    csv_reader.__next__()
    csv_reader.__next__()

    for row in csv_reader:
        csvdata.append(row)
print(csvdata[0])
fueleco = {'city' : [],
           'hwy' : [],
           'comb' : [],
           'comb_mpg' : []
           }
fueleco_array = []  # Initialize as a list, not a dictionary
title = []  # Make sure title is defined somewhere
json_data = {}

for f in csvdata:
    fuel_data = {
        'city': f[8],
        'hwy': f[9],
        'comb': f[10],
        'comb_mpg': f[11]
    }

    row_dict = dict(year = f[0], make = f[1], model = f[2], vehicle_class = f[3], engine_size = f[4], cylinders = f[5],
                    transmission = f[6], fuel_type = f[7],
                    fuel_consumption = [{
                        'city': f[8],
                        'hwy': f[9],
                        'comb': f[10],
                        'comb_mpg': f[11]
                    }], co2_emission = f[11])
    # Create a dictionary for the current row

    fueleco_array.append(row_dict)

print(fueleco_array)

year = 2000
for c in fueleco_array:
    print(c)
    if int(c["year"]) > year:
        year = year + 1
    if str(year) not in json_data:
        json_data[str(year)] = []
    if year == int(c["year"]):
        json_data[str(year)].append(c)
with open(json_dosya_adi, 'w') as json_dosya:
    json.dump(json_data, json_dosya, indent=4, ensure_ascii=False)

print(f'{csv_file_name} file has successfully been converted to {json_dosya_adi} file.')