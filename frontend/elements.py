import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objects as go
import pandas as pd

from objects import LocationSet

# Creates the map that is displayed on the main page
# Draws locations of points of interest + counts how many objects it contains
def create_map(locationset: LocationSet, selected_state):

    selected_points = []
    if selected_state == None:
        selected_points = [i for i in range(len(locationset.all()))]
    else:
        selected_points = [point["pointIndex"] for point in selected_state["points"]]

    fig = go.Figure(go.Scattermapbox(
        lat=locationset.lats,
        lon=locationset.lons,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14
        ),
        textposition="top right",
        textfont=dict(size=16, color="black"),
        text=[f"{location}: {len(locationset.get(location).items)} point{'s' if len(locationset.get(location).items) != 1 else ''} of interest" for location in locationset.all()],
        selectedpoints=selected_points
    ))
    fig.update_layout(
        mapbox=dict(
            center=go.layout.mapbox.Center(
                lat=51.049999,
                lon=3.733333
            ),
            zoom=1.5,
            style="open-street-map"
        ),
        clickmode="event+select",
        hovermode="closest"
    )
    return fig

# Creates an message
def create_alert(message, color_type, style = None):
    return dbc.Alert(message, color=color_type, style=style)

# Creates a card from an item
def create_card(item, key):
    if not item["title"] or not item["synonym"]:
        return None

    card_title = item["title"]
    synonym = item["synonym"]

    card_image_url = None
    if item["image_transcode"] == "":
        card_image_url = "https://i.pinimg.com/474x/08/00/3f/08003f3fe33b585a7bbf8cb8864808d0.jpg"
    else:
        item_image_transcode = item["image_transcode"]
        card_image_url = f"https://api.collectie.gent/iiif/imageiiif/3/{item_image_transcode}/full/%5E1000,/0/default.jpg"

    card_description = ""
    if item["description"]:
        card_description = item["description"]

    card = dbc.Card(
            [
                dbc.CardImg(src=card_image_url, top=True, style={"height": "50%", "objectFit": "cover"}),
                dbc.CardBody(
                    [
                        dbc.Badge(synonym, pill=True, color="secondary", className="me-1", style={"marginBottom": "1em"}),
                        html.H4(card_title, className="card-title"),
                        html.P(
                            card_description,
                            className="card-text",
                        ),
                        dbc.Button("Read more", color="primary", id={"type": "read_more_button", "index": key}, name=str(key)),
                    ]
                ),
            ],
            style={"width": "18rem"},
        )
    return card

def create_modal(selected_object):
    card_image_url = None
    if selected_object["image_transcode"] == "":
        card_image_url = "https://i.pinimg.com/474x/08/00/3f/08003f3fe33b585a7bbf8cb8864808d0.jpg"
    else:
        item_image_transcode = selected_object["image_transcode"]
        card_image_url = f"https://api.collectie.gent/iiif/imageiiif/3/{item_image_transcode}/full/%5E1000,/0/default.jpg"

    modal_children = []
    if selected_object["description"]:
        modal_children.append(html.P(selected_object["description"], style={"fontSize": "18px"}))
    
    print(selected_object)
    if len(selected_object["metadata"]) > 0:
        pill_content = []
        for metadata in selected_object["metadata"]:
            for key, value in metadata.items():
                pill_content.append(dbc.Badge(value, pill=True, color="rgb(255,194,11)", className="me-1", style={"marginBottom": "1em"}),)
    
        pill_container = html.Div(pill_content, style={"display": "flex", "flexFlow": "row wrap-reverse", "justifyContent": "center"})
        modal_children.append(pill_container)

        content_holder = html.Div("Work in progress...")
        modal_children.append(content_holder)

    return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(selected_object["title"])),
                dbc.ModalBody([
                    
                    html.Div([
                        html.Div([ # The image
                            html.Img(src=card_image_url, style={"width": "100%"}),
                        ], style = {"flex": "1 1 0", "width": "0"}),
                        html.Div(modal_children,style={"flex": "1 1 0", "width": 0, "padding": "1em"})
                    ], style={"display": "flex", "flexFlow": "row wrap-reverse", "justifyContent": "center", "alignItems": "stretch"})
                ]),
            ],
            id="modal",
            size="xl",
            is_open=True,
        ),