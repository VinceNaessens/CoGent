import json
import time
import dash
from dash.dependencies import Input, Output, ALL
from dash import html, dcc
import random

from objects import *
from elements import create_card, create_alert, create_map, create_modal

# Latitudes, longitudes and metadata of interesting locations
locationset = LocationSet()

# Statekeeping
selected_zones = None
selected_state = None
selected_object_state = None

# The current query and results
current_query = None
current_results = []

def load_map():
    global locationset
    global selected_state
    global selected_zones

    # We have interesting locations but we have not fetched them
    if not locationset.fetched_locations and locationset.has_locations:
        
        # Fetch the dummy locations
        dummy_locations = create_dummy_locations()["data"]

        print(locationset)

        # Fetch the real locations here
        for i,location in enumerate(locationset.all()):
            # Fetch from api
            locations = fetch_location_information(location)["data"]
            print(locations)
            for i,loc in enumerate(locations):
                locationset.get(location).coordinates = (
                                                            loc["latitude"],
                                                            loc["longitude"]
                                                        )
                locationset.get(location).metadata = loc
                
                # Extract the zones from the location (for now just country)
                locationset.get(location).zone = loc["country"]
            # locationset.get(location).coordinates = (
            #                                             dummy_locations[i]["latitude"],
            #                                             dummy_locations[i]["longitude"]
            #                                         )
            # locationset.get(location).metadata = dummy_locations[i]
            
            # # Extract the zones from the location (for now just country)
            # locationset.get(location).zone = dummy_locations[i]["country"]
        
        locationset.fetched_locations = True
    #lats, lons = fetch_location_information(list(interesting_locations)[0])

    figure = create_map(locationset, selected_state)
    return dcc.Graph(
            id="map",
            style={"width": "100%", "height": "80vh", "padding": "0px"},
            figure=figure
            )


def load_objects():
    global current_results
    content = []

    if len(current_results) <= 0:
        content.append(create_alert("No objects found", "danger", {"width": "50%", "marginTop": "1em"}))
    else:
        cards = []
        for i,result in enumerate(current_results):
            if result["displayed"]:
                cards.append(create_card(result, i))
        content.append(html.Div(cards, style={
                                "width": "100%",
                                "display": "flex",
                                "flexWrap": "wrap",
                                "gap": "1em",
                                "marginTop": "1em",
                                "justifyContent": "center"
                                }))

    return html.Div(content, style={"display": "flex", "justifyContent": "center"})

# Register the callback for the dash app
def register_callbacks(app):

    @app.callback(
        Output("modal_holder", "children"),
        [Input({"type": "read_more_button", "index": ALL}, "n_clicks_timestamp"), Input({"type": "read_more_button", "index": ALL}, "name")]
    )
    def handle_more_info(button_list, name_list):
        global current_results

        most_recent = -1
        most_recent_index = None
        for idx,btn in enumerate(button_list):
            if btn != None and btn > most_recent:
                most_recent = btn
                most_recent_index = idx

        if most_recent_index == None:
            return []
        
        selected_object_index = name_list[most_recent_index]
        selected_object = current_results[int(selected_object_index)]
        return create_modal(selected_object)

    # Callback for handling selected points on the map
    # Called when points are selected/deselected on the map
    @app.callback(
        Output("map_results", "children"),
        [Input("map", "selectedData"), Input("zone_requirement_selection", "children")]
    )
    def handle_map_select(selected_data, zone_reqs):
        global locationset
        global current_results
        global selected_state
        global selected_zones

        # Hide all items by default
        for item in current_results:
                item["displayed"] = False

        filtered_item_indices = []
        for loc in locationset.all():
            filtered_item_indices = [*filtered_item_indices, *locationset.get(loc).items]
        filtered_item_indices = set(filtered_item_indices)
        filtered_items = [current_results[idx] for idx in filtered_item_indices]
        
        selected_state = selected_data

        # Determine which objects will be showed based on map selection
        if selected_data == None:
            for item in filtered_items:
                item["displayed"] = True
        else:
            selected_state = selected_data
            location_indices = [point["pointIndex"] for point in selected_state["points"]]
            locations_to_display = [locationset.all()[idx] for idx in location_indices]

            objects_to_display = []
            for loc in locations_to_display:
                objects_to_display = [*objects_to_display, *locationset.get(loc).items]
            
            for item in filtered_items:
                item["displayed"] = False
            for idx in objects_to_display:
                current_results[idx]["displayed"] = True
            
        if len(locationset.zones) < 1:
            return [dcc.Checklist(id="zone_requirements",
                                options=[],
                                labelStyle={"margin-right": "1em", "margin-left": "0.1em"},
                                style={"width": "80%", "display": "none"})]
        else:
            options = []
            values = []
            for zone in locationset.zones:
                options.append({"label": f" {zone}", "value": zone})

            if selected_zones is None:
                values = [option["value"] for option in options]
                selected_zones = values
            else:
                values = selected_zones
            
            return [html.H4("Zones:", style={"marginTop": "1em"}), dcc.Checklist(id="zone_requirements",
                                value=values,
                                options=options,
                                labelStyle={"margin-right": "1em", "margin-left": "0.1em"},
                                style={"width": "80%"})]

    # Callback for handling the tabs
    # Initiated when tab is updated or when new objects have been loaded
    @app.callback(
        Output("tabs-content", "children"),
        [Input("tabs", "value"), Input("search_output", "children"), Input("zone_requirement_selection", "children")]
    )
    def load_tabs(tab, search_result, zone_req):
        if tab == "tab-1-map":
            return load_map()
        elif tab == "tab-2-objects":
            return load_objects()

    @app.callback(
        Output("zone_requirement_selection", "children"),
        Input("zone_requirements", "value")
    )
    def handle_change_country_requirements(zone_reqs):
        global selected_zones
        global locationset

        selected_zones = zone_reqs

        if selected_zones != None:
            locationset.apply_restriction_filter(set(locationset.zones).symmetric_difference(set(selected_zones)))

        return "loaded"
    

    # What to do when the search field has been activated
    # Called when input has changed
    @app.callback(
        Output("search_output", "children"),
        Input("main_input", "value"))
    def handle_search(search_query):
        if search_query is None or not search_query:
            return

        # Simulate loading a bit here
        time.sleep(2)

        # Start by fetching synonyms of the search query
        result = request_synonyms(search_query)
        #result = create_dummy_results()

        if result["status"] == STATUS.OK:
            # If we have not received a message, throw an error message
            if "message" not in result:
                return create_alert("Something went wrong", "danger", {"width": "50%"})

            global current_results
            global current_query
            global locationset

            global selected_state
            global selected_zones
            global selected_object_state

            current_query = search_query
            current_results = []
            selected_state = None
            selected_zones = None
            selected_object_state = None

            locationset = LocationSet()

            # Iterate over the found objects
            for item_idx, item in enumerate(result["message"]):
                if not item["title"] or not item["synonym"]:
                    continue
                
                # Fetch elements from the object
                displayable = handle_object(item)
                # Give every displayable item a displayed field -> used for map
                displayable["displayed"] = True

                current_results.append(displayable)
                
                # Fetch anything location based from the metadata of the object
                for data in displayable["metadata"]:
                    for key in data.keys():
                        if "plaats" in key.lower():
                            # Add it to the location set
                            locationset.add(Location(data[key]))
                            # Make sure we know which objects were linked to which location again
                            locationset.add_item(data[key], len(current_results) - 1)

            #current_results.reverse()
            return "loaded"

        elif result["status"] == STATUS.ERROR:
            return create_alert("Something went wrong", "danger", {"width": "50%"})
