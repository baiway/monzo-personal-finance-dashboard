from dash import Dash, dcc, html, Input, Output, State
from dash_bootstrap_components.themes import BOOTSTRAP
from pathlib import Path
import json

from src.auth import authenticate
from src.monzo_api import fetch_transactions, last_transaction, update_wanted, refresh
from src.components.layout import landing_page

# TODO refactor this
app = Dash(external_stylesheets=[BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Personal finance dashboard"

@app.callback(
    Output("credentials-output", "children"),
    Input("submit-credentials", "n_clicks"),
    State("client-id", "value"),
    State("client-secret", "value")
)
def save_credentials(n_clicks, client_id, client_secret):
    if n_clicks > 0 and (client_id and client_secret):
        credentials = {
            "client_id": client_id,
            "client_secret": client_secret
        }
        with open("credentials.json", "w") as file:
            json.dump(credentials, file, indent=2)
        return dcc.Location(id="redirect", pathname="/dashboard", refresh=True)
    else:
        return "Please enter both client ID and client secret."

@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/dashboard":
        return create_dashboard_layout(app)
    else:
        return landing_page()

def create_dashboard_layout(app):
    return html.Div([
        html.H1("Monzo dashboard"),
        # add dashboard components here
    ])

if __name__ == "__main__":
    # TODO refactor; separate blocks of code into functions/files.
    credentials_path = Path("credentials.json")
    if credentials_path.exists():
        initial_layout = html.Div([
            dcc.Location(id="url", refresh=False, pathname="/dashboard"),
            html.Div(id="page-content")                              
        ])
    else:
        initial_layout = html.Div([
            dcc.Location(id="url", refresh=False, pathname="/"),
            html.Div(id="page-content")
        ])

    app.layout = initial_layout
    app.run_server(debug=True)
    # Check whether `transactions.csv` already exists. If it does, ask user whether
    # they'd like to fetch more recent transactions, or continue with the existing
    # `transactions.csv`. If this doesn't exist, fetch all transactions since the
    # account was created.
    #
    # The advantage of this approach is that we only authenticate when we need to. 
    # This should lead to a much more pleasant user experience.

    tpath = Path(__file__).parent / "transactions.csv"

    if tpath.exists():
        # Print date of last transaction
        last_transaction = last_transaction()
        print(f"{tpath.name} already exists. The last transaction was on " \
              f"{last_transaction.strftime('%d %b %Y')}.")

        if update_wanted():
            # Authenticate then fetch new transactions
            access_token = authenticate()
            transactions = refresh(access_token, last_transaction, verbose=True)
            updated = True
        else:
            updated = False

    else:
        # No `transactions.json` found. Authenticate then fetch all transactions
        access_token = authenticate()
        transactions = fetch_transactions(access_token, verbose=True)
        updated = True

    # Save updated transactions data locally
    if updated:
        print(f"Saved transaction data to: {tpath.resolve()}")
        transactions.to_csv(tpath, index=False)
