import json
import webbrowser
from requests_oauthlib import OAuth2Session

# Load credentials
with open("credentials.json", "r") as file:
    credentials = json.load(file)

# Define the necessary URLs and parameters
authorization_base_url = "https://auth.monzo.com/"
token_url = "https://api.monzo.com/oauth2/token"
redirect_uri = "https://localhost:8080/"

# Create an OAuth2 session
monzo = OAuth2Session(client_id=credentials["client_id"], redirect_uri=redirect_uri)

# Redirect the user to the Monzo authorization URL
authorization_url, state = monzo.authorization_url(authorization_base_url)
webbrowser.open(authorization_url)

# Wait for the user to authorize and paste the redirect URL here
redirect_response = input("Paste the full redirect URL here: ")

# Fetch the access token using the authorization response
token = monzo.fetch_token(token_url, authorization_response=redirect_response,
                          client_secret=credentials["client_secret"])

print("Access token:", token)

# Make an authenticated request to the Monzo API
whoami_url = 'https://api.monzo.com/ping/whoami'
response = monzo.get(whoami_url)
print("Who Am I response:", response.json())
