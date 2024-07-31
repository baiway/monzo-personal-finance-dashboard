import json
from pathlib import Path
from dash import Input, Output, State, html, dcc

from src.data import load_transactions_data
from src.layout import create_credentials_layout, create_dashboard_layout
from src.components import generate_category_spending_chart

def register_callbacks(app):
    """
    Callbacks for displaying the correct content based on the URL
    and handling form submissions.
    """
    @app.callback(
        Output("page-content", "children"),
        [Input("url", "pathname")]
    )
    def display_page(pathname):
        """
        Display the appropriate page based on the pathname. 
        
        This may seem unnecessarily convoluted, but it's to protect 
        against users manually entering the incorrect URL. For example, 
        if a user enters `http://127.0.0.1:8050/dashboard` but doesn't 
        have a `credentials.json` file, they'll run into issues if they 
        try to refresh their `transactions.csv` file. To protect 
        against this, we redirect them to 
        `http://127.0.0.1:8050/credentials`.
        """
        print(f"{pathname = }")
        if pathname in ["/", "/credentials"]:
            if not Path("credentials.json").exists():
                return create_credentials_layout()
            return dcc.Location(pathname="/dashboard", id="redirect-to-dashboard")
        elif pathname == "/dashboard":
            if Path("credentials.json").exists():
                load_transactions_data()
                return create_dashboard_layout(app)
            return create_credentials_layout()
        return html.Div("404 - Page not found.")


    @app.callback(
        Output("url", "pathname"),
        [Input("submit-credentials", "n_clicks")],
        [State("client-id", "value"), State("client-secret", "value")],
        prevent_initial_call=True
    )
    def save_credentials_and_redirect(n_clicks, client_id, client_secret):
        """
        Save the credentials to credentials.json and redirect to the dashboard.
        """
        if n_clicks > 0 and client_id and client_secret:
            credentials = {
                "client_id": client_id,
                "client_secret": client_secret
            }
            with open("credentials.json", "w") as file:
                json.dump(credentials, file, indent=2)
            return "/dashboard"
        return "/credentials"


    @app.callback(
        Output("category-spending-bar-chart", "figure"),
        [Input("update-button", "n_clicks")],
        [State("date-picker-range", "start_date"),
         State("date-picker-range", "end_date")]
    )
    def update_bar_chart(n_clicks, start_date, end_date):
        return generate_category_spending_chart(start_date, end_date)
