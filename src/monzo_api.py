import requests
import json
from datetime import datetime, timedelta


def fetch_all_transactions(access_token, verbose=False):
    """Retrieves all transactions since the account was created. 
    Saves results in a JSON file: 'transactions.json'.

    Multiple calls must be made because Monzo's API allows the maximum 
    time between the 'since' and 'before' parametrs to be 8760 hours 
    (365 days) [1]. Additionally, the maximum number of transactions we 
    can receive in a single API call is 100 [2]. It's quite likely that 
    a user will have more than 100 transactions per year though, so the 
    time window will probably be the limiting factor.
    
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

    # Keep requesting transactions in blocks of 100 (the maximum) until we receive
    # a block with a size less than 100 (at which point we've got them all)
    block_size = 100    
    while block_size == 100:
        params = {"account_id": account_id,
                  "since": start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                  "before": end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                  "limit": block_size}
        response = requests.get("https://api.monzo.com/transactions", 
                            headers=header, params=params)
        tlist = response.json()["transactions"] # list of JSON-like transaction objects

        # Clean transactions (only keep quantities of interest)
        qois = ["amount", "created", "categories", "description", "id"]
        cleaned_transactions = [{key: t[key] for key in qois} for t in tlist]

        # Add cleaned block to full `transactions` list, then determine the size of
        # the block to check if we need to keep going
        transactions.extend(cleaned_transactions)
        block_size = len(cleaned_transactions)

        # Determine date of first and last transaction in the block
        first = tlist[0]["created"]
        last = tlist[-1]["created"]

        # Convert to datetime objects (makes manipulations below easier)
        first = datetime.strptime(first, "%Y-%m-%dT%H:%M:%S.%fZ")
        last = datetime.strptime(last, "%Y-%m-%dT%H:%M:%S.%fZ")

        # Verbose output to show progress (rough 1 API call per second)
        # Example output line: `24 Jun 2024 to 23 Jul 2024:  83 entries.`
        if verbose:
            print(f"{first.strftime('%d %b %Y')} to {last.strftime('%d %b %Y')}:  " \
                  f"{block_size} entries.")

        # Set start of next block to the end of this block and end to 1 year later
        start = last + timedelta(seconds=1)
        end = start + timedelta(hours=8760)

    # Save the final `transactions` list
    with open("transactions.json", "w") as file:
        json.dump({"transactions": transactions}, file, indent=2)

    print("Saved transaction data to: transactions.json.")
