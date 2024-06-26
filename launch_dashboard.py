from src.auth import authenticate
from src.monzo_api import fetch_transactions
from src.config import load_credentials

if __name__ == "__main__":
    # Authenticate using client_id and client_secret in credentials.json
    client_id, client_secret = load_credentials()
    access_token = authenticate(client_id, client_secret)

    # Wait for user to allow this app access their data in the Monzo app
    app_auth = ""
    while app_auth != "y":
        app_auth = input("Have you authenticated in the Monzo app? [y/n] ").lower()

    # Fetch all transactions since account creation
    fetch_transactions(access_token, verbose=True)
