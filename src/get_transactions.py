import requests
import json
from datetime import datetime, timedelta


def get_all_transactions(access_token, verbose=False):
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

    block_size = 100    
    while block_size >= 100:
        # Get block of transactions and append to transactions list
        params = {"account_id": account_id,
                  "since": start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                  "before": end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                  "limit": block_size}
        response = requests.get("https://api.monzo.com/transactions", 
                            headers=header, params=params)
        tlist = response.json()["transactions"][0]

        # Clean transactions (only keep quantities of interest)
        qois = ["amount", "created", "categories", "description", "id"]
        cleaned_transactions = [{key: t[key] for key in qois} for t in tlist]

        block_size = len(cleaned_transactions)
        transactions.append(cleaned_transactions)

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
