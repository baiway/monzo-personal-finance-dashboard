import json
import requests
import webbrowser
import random
import string
from datetime import datetime, timedelta
from flask import Flask, request, redirect
import threading

app = Flask(__name__)
auth_code = None
shutdown_event = threading.Event()

# TODO Consider placing this function in a `src/utils.py` file to avoid clutter.
def gen_rand_str(length=16):
    """Generates a random string of letters and numbers to create an
    unguessable state token for use in authentication. This protects against 
    cross-site request forgery attacks. 
    See: https://docs.monzo.com/#acquire-an-access-token"""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def run_flask():
    app.run(port=8080)


@app.route("/")
def index():
    return "Authentication successful. You can close this window."


@app.route("/callback")
def callback():
    global auth_code
    auth_code = request.args.get("code")
    return redirect("/")


# @app.route("/shutdown", methods=["POST"])
# def shutdown():
#     shutdown_event.set()
#     return "Shutting down Flask server..."


def authenticate(client_id, client_secret):
    """Authenticate with the Monzo API and acquire an access token.

    This function performs the OAuth2 authorization flow:
    1. Generates an authorization URL and opens it in the default web browser.
    2. Waits for the user to authorize the application and paste the redirect URL.
    3. Extracts the authorization code from the redirect URL.
    4. Exchanges the authorization code for an access token.

    Args:
        client_id (str): Monzo client ID from https://developers.monzo.com/
        client_secret (str): Monzo client secret from https://developers.monzo.com/
        redirect_uri (str): the redirect URI set in https://developers.monzo.com/

    Returns:
        str: Access token for authenticating with the Monzo API."""
    global auth_code
    auth_code = None
    
    base_auth_url = "https://auth.monzo.com/"
    token_url = "https://api.monzo.com/oauth2/token"
    redirect_uri="http://localhost:8080/callback"

    # Authorisation URL structure given in Monzo API docs
    # See: https://docs.monzo.com/#acquire-an-access-token
    auth_url = (
        f"{base_auth_url}?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&state={gen_rand_str()}"
    )

    # TODO If user enters client_id incorrectly into their credentials.json, 
    # they will be met with a blank web page. Not much we can do to help them here...
    # Perhaps provide a hint in our UI later down the line? (e.g. if this step does not
    # progress in 30 seconds, display a hint?)
    webbrowser.open(auth_url)
    print("Waiting for user to authenticate...")

    # Start a Flask server on a separate thread
    threading.Thread(target=run_flask, daemon=True).start()

    while auth_code is None:
        pass

    # Exchange the authorisation code for an access token
    response = requests.post(
        token_url,
        data={
            "grant_type": 'authorization_code', # must be spelled with a z...
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": auth_code,
        }
    )

    if response.ok:
        access_token = response.json()["access_token"]
        # requests.post("http://localhost:8080/shutdown") # shutdown the Flask server
        return access_token
    else:
        raise ValueError(f"Encountered HTTP error {response.status_code} while" \
                         "requesting access token. Check 'client_id' and" \
                         "'client_secret' in credentials.json.")


def get_all_transactions(access_token, verbose=False):
    """Retrieves all transactions since the account was created. Saves results in
    a JSON file transactions.json.

    Multiple calls must be made because Monzo's API allows the maximum time
    between the 'since' and 'before' parametrs to be 8760 hours (365 days) [1].
    Additionall, the maximum number of transactions we can receive in a single 
    API call is 100 [2]. It's quite likely that a user will have more than 100 
    transactions per year though, so the time window will probably be the limiting
    factor.
    
    References
    [1] https://docs.monzo.com/#list-transactions
    [2] https://docs.monzo.com/#pagination"""
    
    # Get account ID and creation date
    header = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.monzo.com/accounts", headers=header)
    if len(response.json()["accounts"]) > 2:
        raise ValueError("Not yet implemented: two or more accounts associated" \
                         "with this login.")
    account_id = response.json()["accounts"][0]["id"]
    created = response.json()["accounts"][0]["created"]

    # Set start and end date of first time period
    start = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%fZ")
    end = start + timedelta(hours=8760)  # max time interval allowed by Monzo's API

    transactions = []
    print("Attempting to fetch all previous transactions...")

    block_size = 100    
    while block_size >= 100:
        # Get block of transactions and append to transactions list
        params = {"account_id": account_id,
                  "since": start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                  "before": end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                  "limit": block_size}
        response = requests.get("https://api.monzo.com/transactions", 
                            headers=header, params=params)
        tlist = response.json()["transactions"]
        block_size = len(tlist)
        transactions.append(tlist)

        first = tlist[0]["created"]
        last = tlist[-1]["created"]
        first = datetime.strptime(first, "%Y-%m-%dT%H:%M:%S.%fZ")
        last = datetime.strptime(last, "%Y-%m-%dT%H:%M:%S.%fZ")

        # Verbose output to show progress (roughly 1 call per second)
        if verbose:
            print(f"{first.strftime('%d %b %Y')} to {last.strftime('%d %b %Y')}:  " \
                  f"{block_size} entries.")

        # Set start of next block to the end of this block
        start = last + timedelta(seconds=1)
        end = start + timedelta(hours=8760)

    with open("transactions.json", "w") as file:
        json.dump({"transactions": transactions}, file, indent=2)

    print("Saved transaction data to: transactions.json.")


if __name__ == "__main__":
    with open("credentials.json", "r") as file:
        credentials = json.load(file)

    client_id = credentials.get("client_id", None)
    client_secret = credentials.get("client_secret", None)
    access_token = credentials.get("access_token", None)
    time_stamp = credentials.get("time_stamp", None)

    # Validate inputs from credentials.json.
    if client_id is None:
        raise ValueError("'client_id' missing from credentials.json.")
    if client_secret is None:
        raise ValueError("'client_secret' is missing from credentials.json.")

    # If access_token in credentials.json is more than 4 mins 50 seconds old,
    # set access_token to None and reauthenticate (via email)
    if time_stamp is not None:
        t = datetime.strptime(time_stamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        if (datetime.now() - t) > timedelta(minutes=4, seconds=50): 
            access_token = None
    
    if access_token is None:
        access_token = authenticate(client_id, client_secret)
        time_stamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        credentials["access_token"] = access_token
        credentials["time_stamp"] = time_stamp
        with open("credentials.json", "w") as file:
            json.dump(credentials, file, indent=2)  # Save for future use
            
    app_auth = input("Have you authenticated in the Monzo app? [y/n] ").lower()
    if app_auth == "y":
        get_all_transactions(access_token, verbose=True)
