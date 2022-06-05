import dash
from dash import html, Output, Input
import dash_bootstrap_components as dbc
from layout import get_app_layout
from callbacks import register_callbacks

# choose your own theme here: https://bootswatch.com/default/
app = dash.Dash(external_stylesheets=[dbc.themes.MINTY], suppress_callback_exceptions=True)
app.title = "Cogent"
app.layout = html.Div(get_app_layout())
register_callbacks(app)

if __name__ == "__main__":
    app.run_server(
        debug=True, port=8000, dev_tools_hot_reload=True, use_reloader=True
    )