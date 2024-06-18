import json
import requests
import webbrowser
import random
import string
import re
from datetime import datetime, timedelta

# TODO Consider placing this function in a `src/utils.py` file to avoid clutter.
def gen_rand_str(length=16):
    """Generates a random string of letters and numbers to create an
    unguessable state token for use in authentication. This protects against 
    cross-site request forgery attacks. 
    See: https://docs.monzo.com/#acquire-an-access-token"""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def authenticate(client_id, client_secret, redirect_uri="https://localhost:8080/"):
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
    base_auth_url = "https://auth.monzo.com/"
    token_url = "https://api.monzo.com/oauth2/token"

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
    
    # Wait for the user to authorize and paste the redirect URL here
    redirect_response = input("Paste the full redirect URL here: ") # TODO nicer method?

    # Extract the authorisation code from the redirect_response
    match = re.search(r"[?&]code=([^&]*)", redirect_response)
    if match is None:
        raise ValueError("No authorisation code found in redirect response.")
    authorisation_code = match.group(1)

    # Exchange the authorisation code for an access token
    response = requests.post(
        token_url,
        data={
            "grant_type": 'authorization_code', # needs to spelled with a z...
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": authorisation_code,
        }
    )

    if response.ok:
        return response.json()["access_token"]
    else:
        raise ValueError(f"Encountered HTTP error {response.status_code} while \
                         requesting access token. Check 'client_id' and \
                         'client_secret' in credentials.json.")

if __name__ == "__main__":
    with open("credentials.json", "r") as file:
        credentials = json.load(file)

    client_id = credentials.get("client_id", None)
    client_secret = credentials.get("client_secret", None)
    access_token = credentials.get("access_token", None)

    # Validate inputs from credentials.json.
    if client_id is None:
        raise ValueError("'client_id' missing from credentials.json.")
    if client_secret is None:
        raise ValueError("'client_secret' is missing from credentials.json.")
    
    if access_token is None:
        access_token = authenticate(client_id, client_secret)
        credentials["access_token"] = access_token
        with open("credentials.json", "w") as file:
            json.dump(credentials, file, indent=2)  # Save for future use
    
    whoami = requests.get("https://api.monzo.com/ping/whoami", 
                        headers={"Authorization": f"Bearer {access_token}"})
    print(f"WHOAMI response: \n  {whoami.json()}\n")

    # If any of the below requests fail due to permissions errors, open the Monzo app.
    # You just need to authenticate via the app.
    # FIXME in code below, selecting account 'zero' is bad practice.
    #  - Check whether user has multiple accounts
    #    i.e. if len(accounts.json()["accounts"] > 2
    #  - If true, ask them which account they'd like to select
    #  - If false, don't bother them with this
    accounts = requests.get("https://api.monzo.com/accounts", 
                        headers={"Authorization": f"Bearer {access_token}"})
    print(f"Accounts: \n  {accounts.json()}\n")
    account_id = accounts.json()["accounts"][0]["id"]

    balance = requests.get("https://api.monzo.com/balance", 
                        headers={"Authorization": f"Bearer {access_token}"},
                        params={"account_id": account_id})
    print(f"Balance (in pence): \n  {balance.json()}\n")

    # ===================
    # Fetch transactions
    # ===================
    #
    # This is complicated for a couple of reasons. For details, see Refs. [1, 2].
    #  1) The maximum time between 'since' and 'before' in the list transactions
    #     API call [1] is 8760 hours (365 days), and the maximum number of transactions
    #     we can receive in a single call is 100 [2]. It's quite likely that a user will
    #     have more than 100 transactions per year though, so the time limit is likely 
    #     the more important one.
    #   2) After authenticating, we've only got 5 minutes to fetch transaction data.
    #      We should account for this in some way. For example, when we save the
    #      access_token in credentials.json, we could also save a timestamp. When
    #      re-using this access_token, we can check whether it's been more than 5 mins. 
    # References
    # [1] https://docs.monzo.com/#list-transactions
    # [2] https://docs.monzo.com/#pagination
    created = accounts.json()["accounts"][0]["created"]
    start = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%fZ")
    start.replace(hour=0, minute=0, second=0, microsecond=0) # set to midnight
    end = start + timedelta(hours=8760)  # max time interval allowed by Monzo's API

    transactions = requests.get("https://api.monzo.com/transactions", 
                        headers={"Authorization": f"Bearer {access_token}"},
                        params={"account_id": account_id,
                                "since": start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                "before": end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                "limit": 100})
    print(f"First batch of transactions on account: \n  {transactions.json()}\n")
