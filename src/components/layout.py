from dash import html, dcc

def landing_page():
    return html.Div([
        html.H2("Enter your Monzo API Credentials"),
        dcc.Input(
            id="client-id", 
            type="text", 
            placeholder="Client ID", 
            style={"margin": "10px"}
        ),
        dcc.Input(
            id="client-secret", 
            type="text", 
            placeholder="Client secret", 
            style={"margin": "10px"}
        ),
        html.Button(
            "Submit",
            id="submit-credentials",
            n_clicks=0
        ),
        html.Div(
            id="credentials-output"
        )
    ])


def create_layout(app):
    return html.Div(id="page-content")
