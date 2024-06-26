import requests
import webbrowser
import threading
from flask import Flask, request, redirect
from src.utils import gen_rand_str

app = Flask(__name__)
auth_code = None


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
    # they will be met with a blank web page. There is not much we can do to 
    # help them here as we do not know what the client_id should be. 
    # Later down the line, perhaps we could provide a hint that something may
    # have gone wrong? (e.g. if this step does not progress in 30 seconds, 
    # display a "Check your client_id" message)
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
        return access_token
    else:
        raise ValueError(f"Encountered HTTP error {response.status_code} while" \
                         "requesting access token. Check 'client_id' and" \
                         "'client_secret' in credentials.json.")
