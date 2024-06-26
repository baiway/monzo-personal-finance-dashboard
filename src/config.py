import json

def load_credentials():
    with open("credentials.json", "r") as file:
        credentials = json.load(file)

    client_id = credentials.get("client_id", None)
    client_secret = credentials.get("client_secret", None)

    if client_id is None:
        raise ValueError("'client_id' missing from credentials.json.")
    if client_secret is None:
        raise ValueError("'client_secret' is missing from credentials.json.")

    return client_id, client_secret
