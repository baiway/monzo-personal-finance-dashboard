from dash import html, dcc

def create_credentials_layout():
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
    
def create_dashboard_layout(app):
    return html.Div([
        html.H1("Monzo Dashboard"),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date",
            display_format='YYYY-MM-DD'
        ),
        html.Button(
            'Update', 
            id='update-button',
            n_clicks=0
        ),
        dcc.Graph(
            id='category-spending-bar-chart'
        )
    ])
