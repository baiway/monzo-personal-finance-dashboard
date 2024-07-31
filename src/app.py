from dash import Dash, dcc, html
from dash_bootstrap_components.themes import BOOTSTRAP

from src.callbacks import register_callbacks

# Create Dash app with Flask server
app = Dash(
    __name__,
    external_stylesheets=[BOOTSTRAP], # can insert custom CSS here
    suppress_callback_exceptions=True
)
app.title = "Monzo dashboard"

def initialise_app():
    """
    Initialise the app layout, register callbacks and loads
    transaction data.
    """
    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),  # tracks the URL
        html.Div(id="page-content")  # content changes based on URL
    ])

    register_callbacks(app)
