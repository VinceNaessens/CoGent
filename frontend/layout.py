from dash import html, Output, Input, dcc, State
import dash_bootstrap_components as dbc
from elements import create_map
from objects import LocationSet
import base64
import os

themecolor = "rgb(255,194,11)"

tabstyle = {
    "borderRadius": "2%",
    "border": "2px solid",
    "borderColor": f"{themecolor}",
    "fontSize": "20px",
    "fontWeight": "bold",
    "color": f"{themecolor}"
}

selected_tabstyle = {
    "borderTop": "0px solid",
    "borderRadius": "2%",
    "borderColor": f"{themecolor}",
    "backgroundColor": f"{themecolor}",
    "fontSize": "22px",
    "fontWeight": "bold",
    "color": "white",
    "transition": "background-color 0.5s ease"
}

image_filename = "./frontend/imgs/image.png"
encoded_image = base64.b64encode(open(image_filename, 'rb').read())


def get_app_layout():
    return dbc.Container(
        [
            html.Div([
                html.H1(children='C',
                    style={"marginTop": "1rem", "fontWeight": "bold"}),
                html.Img(src=f"data:image/png;base64,{encoded_image.decode()}", style={"objectFit": "cover", "width": "40px", "height": "40px", "marginTop": "1.3em"}),
                html.H1(children='gent Guide',
                    style={"marginTop": "1rem", "fontWeight": "bold"}),
            ], style={"display": "flex", "width": "5em"}),
            
            html.P(children="Your guide for your interests..."),
            dbc.Card([
                dbc.CardBody([
                        "Type a keyword of what you would like to see here",
                        dbc.Input(id="main_input", type="text", debounce=True, style={"marginBottom": "1em"}),
                        dcc.Loading(
                                id="search_loading",
                                type="cube",
                                children=html.Div(id="search_output",style={"display": "none"}),
                                color="#ffd863"
                            ),
                        html.Div([
                                dcc.Checklist(id="country_requirements",
                                options=[],
                                labelStyle={"marginRight": "1em", "marginLeft": "0.1em"},
                                style={"width": "80%", "display": "none"})], id="map_results"),
                        html.Div([], id="zone_requirement_selection", style={"display": "none"})
                    ]),
                ], style={"padding": "1em", "border": f"2px solid {themecolor}"}),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Tabs(id="tabs", value="tab-1-map", children=[
                            dcc.Tab(label="Map", value="tab-1-map", style=tabstyle, selected_style=selected_tabstyle),
                            dcc.Tab(label="Objects", value="tab-2-objects", style=tabstyle, selected_style=selected_tabstyle, children=[
                                html.Button(id="more_info_button", style={"display": "none"}),
                                html.Div(id="modal_holder")
                            ]),
                        ]),
                    ]),
                    html.Div([dcc.Graph(
                        id="map",
                        style={"width": "100%", "height": "80vh", "padding": "0px"},
                        figure=create_map(LocationSet(), None)
                        )], id="tabs-content"),
                ])
            ]),
            
        ],
        fluid=True,
        style={"width": "90%", "marginLeft": "5vw"}
    )