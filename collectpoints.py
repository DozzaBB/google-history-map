# collectpoints.py
import json

precision = 5

def replaceandround(somestr):
    latlng = somestr.replace("Â°", "")
    parts = latlng.split(", ")
    lat = round(float(parts[0]), precision)
    lon = round(float(parts[1]), precision)
    return f"{lat}, {lon}"

def process_offline(filepath: str):
    output = []
    with open(filepath) as f:
        raw = json.load(f)

    for x in raw["semanticSegments"]:
        if "timelinePath" in x:
            path = x["timelinePath"]
            for point in path:
                output.append((replaceandround(point["point"]), point["time"]))
        elif "visit" in x:
            output.append((replaceandround(x["visit"]["topCandidate"]["placeLocation"]["latLng"]), x["startTime"]))
        elif "activity" in x:
            output.append((replaceandround(x["activity"]["start"]["latLng"]), x["startTime"]))
            output.append((replaceandround(x["activity"]["end"]["latLng"]), x["endTime"]))
        elif "timelineMemory" in x:
            pass
        else:
            raise Exception("unrecognised type")

    print(f"There are {len(output)} locations in the offline data set.")
    return output

def unique(somelist: list):
    return list(set(somelist))

def decode_str(coordstr):
    parts = coordstr[0].split(", ")
    return ([float(parts[0]), float(parts[1])], coordstr[1])

def process_online(filepath: str) -> list[tuple[str,str]]: 
    with open(filepath) as f:
        raw = json.load(f)

    onlinelocations = raw['locations']

    print(f"There are {len(onlinelocations)} locations in the online dataset.")

    valid_locations = 0
    output: list[tuple[str, str]] = []

    for location in onlinelocations:
        if 'latitudeE7' in location:
            valid_locations += 1
            lat_raw = location['latitudeE7']
            lon_raw = location['longitudeE7']
            lat = round(lat_raw / 10000000, precision)
            lon = round(lon_raw / 10000000, precision)
            string = f"{lat}, {lon}"
            output.append((string, location["timestamp"]))
    return output

onlinedatafile = "C:/dev/google history map/Takeout2/Location History (Timeline)/Records.json"
offlinedatafiles = [
    "C:/dev/google history map/offline/20241110 Timeline.json",
    "C:/dev/google history map/offline/20241229 Timeline.json",
                   ]

all_online = process_online(onlinedatafile)
all_offline = []
for offlinefile in offlinedatafiles:
    all_offline += process_offline(offlinefile)


def get_earliest_unique_vists(someiter):
    outputmap = {}
    for (latlng, time) in someiter:
        # put if not present
        if latlng not in outputmap:
            outputmap[latlng] = time
        # replace if earlier.
        current = outputmap[latlng]
        new = time
        if new < current:
            outputmap[latlng] = time
    return [x for x in outputmap.items()]
        




unique_locations_by_time = get_earliest_unique_vists(all_online + all_offline)

# rounded_loc_strings = unique(all_online + all_offline)
decoded_rounded = [decode_str(x) for x in unique_locations_by_time]

bigstr = "var rawPoints = " + json.dumps(decoded_rounded)
with open("./points.js", "w") as f:
    f.write(bigstr)




print(f"Found {len(all_online + all_offline)} number of actual datapoints.")

print(f"there are {len(unique_locations_by_time)} unique locations rounded to {precision} places.")