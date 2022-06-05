import requests
import json

API_LOCATION_URL = "http://api.positionstack.com/v1/forward?access_key=4ee7646bb6c043254bedb60ce5a733f4" # Use dummydata for now
API_SYNONYM_URL = "http://localhost:5000/art"

# Tries to fetch the element from the object
def try_fetch_element(object, selectors):
    result = ""
    try:
        objcpy = object
        for selector in selectors:
            objcpy = objcpy[selector]
        result = objcpy
    except:
        print(f"Selectors {selectors} not valid on {object}")
    return result

# If the type of the object is an asset
def handle_asset(asset, displayready_object):
    # We can fetch title, description and mediafile
    displayready_object["title"] = try_fetch_element(asset, ["title", 0, "value"])
    displayready_object["description"] = try_fetch_element(asset, ["description", 0, "value"])
    displayready_object["image_transcode"] = try_fetch_element(asset, ["primary_transcode"])

    handle_metadata(asset["metadataCollection"], displayready_object)

# Iteratively digs in metadata for interesting information
def handle_metadata(metadata, displayready_object):
    content = []
    handle_metadata_recursive(metadata, content)
    displayready_object["metadata"] = content

def handle_metadata_recursive(metadata_list, content):
    for data in metadata_list:
        if data["nested"]:
            for d in data["data"]:
                label = d["label"]
                if "nestedMetaData" in d:
                    nested_obj = d["nestedMetaData"]
                    handle_nested_metadata(nested_obj, content)
        else:
            info = try_fetch_element(data, ["data", 0, "value"])
            content.append({data["label"]: info})

# Adds relations to metadatalist
def append_relations(relations, metadatalist):
    for relation in relations:
            lbl = try_fetch_element(relation, ["label"])
            val = try_fetch_element(relation, ["value"])
            metadatalist.append({lbl: val})

# Handles different types of nested metadata
def handle_nested_metadata(nested_obj, metadatalist):
    if nested_obj["type"] == "classification":
        append_relations(nested_obj["relations"], metadatalist)
    elif nested_obj["type"] == "getty":
        val = try_fetch_element(nested_obj, ["title", 0, "value"])
        metadatalist.append({"related": val})
    elif nested_obj["type"] == "person":
        handle_metadata_recursive(nested_obj["metadataCollection"], metadatalist)
    elif nested_obj["type"] == "production":
        append_relations(nested_obj["relations"], metadatalist)
        handle_metadata_recursive(nested_obj["metadataCollection"], metadatalist)
    elif nested_obj["type"] == "aquisition":
        append_relations(nested_obj["relations"], metadatalist)
        handle_metadata_recursive(nested_obj["metadataCollection"], metadatalist)
    elif nested_obj["type"] == "role":
        val = try_fetch_element(nested_obj, ["title", 0, "value"])
        metadatalist.append({"role": val})
    else:
        pass
        #print(nested_obj["type"])

# Handle the object
def handle_object(object):
    displayready_object = {}
    displayready_object["synonym"] = try_fetch_element(object, ["synonym"])

    object_details = object["details"]
    if object_details["type"] == "asset":
        handle_asset(object_details, displayready_object)
    else:
        print(object_details["type"])

    return displayready_object

# Query the location api
def fetch_location_information(location_string):
    params = {
        "query": location_string
    }
    response = requests.get(API_LOCATION_URL, params=params)
    json_response = response.json()
    return json_response

class STATUS:
    OK = "ok"
    ERROR = "error"

# Query the backend for synonyms
def request_synonyms(input_value):
    params = {
        "basis_word": input_value
    }
    json_result = {}
    try:
        r = requests.get(API_SYNONYM_URL, params=params)
        if (r.status_code == 200):
            json_result = json.loads(r.text)
            json_result["status"] = STATUS.OK
        else:
            json_result["status"] = STATUS.ERROR        
    except:
        json_result["status"] = STATUS.ERROR
    return json_result

# For speed purposes, return dummy data
def create_dummy_results():
    j = None
    dummy = {"status": STATUS.OK}
    with open("dummy_data.json") as fd:
        j = json.load(fd)
    dummy["message"] = j
    return dummy

def create_dummy_locations():
    j = None
    with open("dummy_locations.json") as fd:
        j = json.load(fd)
    return j

class Location:
    def __init__(self, name):
        self._name = name
        self._coordinates = (None, None)
        self._metadata = None
        self._items = []
        self._zone = None

    @property
    def zone(self):
        return self._zone
    @zone.setter
    def zone(self, value):
        self._zone = value

    @property
    def coordinates(self):
        return self._coordinates
    @coordinates.setter
    def coordinates(self, value):
        self._coordinates = value

    @property
    def metadata(self):
        return self._metadata
    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    @property
    def items(self):
        return self._items
    def add_item(self, item):
        self._items.append(item)

    @property
    def name(self):
        return self._name

class LocationSet:
    def __init__(self):
        self._locations = {}
        self._fetched_locations = False
        self._filter = []

    def apply_restriction_filter(self, filter):
        if filter != None: self._filter = filter
        else: self._filter = []

    def add(self, location: Location):
        if location.name not in self._locations:
            self._locations[location.name] = location

    def get(self, locationname):
        return self._locations[locationname]

    def all(self):
        return [loc.name for loc in self._locations.values() if loc.zone not in self._filter]

    def add_item(self, locationname, item):
        self._locations[locationname].add_item(item)

    def __str__(self):
        strs = [f"{key} -> {len(self._locations[key].items)} items" for key in self.all()]
        return "\n".join(strs)

    def get_locations_of_zones(self, zones):
        locations = []
        for loc in self._locations.values():
            if loc.zone in zones:
                locations.append(loc)
        return locations

    @property
    def lats(self):
        lats = []
        for loc in self._locations.values():
            if loc.zone not in self._filter: lats.append(loc.coordinates[0])
        return lats

    @property
    def lons(self):
        lons = []
        for loc in self._locations.values():
            if loc.zone not in self._filter: lons.append(loc.coordinates[1])
        return lons

    @property
    def zones(self):
        zoneset = set()
        for loc in self._locations.values():
            zoneset.add(loc.zone)
        return list(zoneset)

    def get_locations_of_zone(self, zonename):
        locations = []
        for loc in self._locations.values():
            if loc.zone == zonename: locations.append(loc)
        return locations

    @property
    def has_locations(self):
        return len(self._locations.keys()) > 0

    @property
    def fetched_locations(self):
        return self._fetched_locations
    @fetched_locations.setter
    def fetched_locations(self, value: bool):
        self._fetched_locations = value
