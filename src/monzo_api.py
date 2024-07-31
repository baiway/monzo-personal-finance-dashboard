import requests
import pandas as pd
from datetime import datetime, timedelta


def fetch_transactions(access_token, since=None, verbose=False):
    """
    Retrieves transactions on the account since the date `since`. If 
    `since` is not provided, all transactions since account creation
    will be fetched. Results are saved to `transactions.json`.

    Multiple API calls are made to comply with Monzo's API limitations 
    on time intervals and the maximum number of transactions per call.
    See Notes below for details.

    Parameters
    ----------
    access_token : str
        The access token used to authenticate with the Monzo API.
    since : datetime, optional
        The function will retrieve all transactions from this date.
        If not set, all transactions since account creation will
        be retrieved.
    verbose : bool, optional
        If True, prints progress information while API calls are
        being made (default is False).

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing transaction data.

    Raises
    ------
    ValueError
        If there are two or more accounts associated with the provided 
        login (this will only occur if e.g. you have a personal and
        business account associated with your Monzo login).

    Notes
    -----
    The Monzo API allows a maximum time interval of 8760 hours 
    (365 days) between the 'since' and 'before' parameters [2]. 
    Additionally, the maximum number of transactions that can be 
    received in a single API call is 100 [3]. Therefore, the function 
    splits the time range into multiple intervals if necessary and 
    retrieves transactions in blocks of 100 until all transactions 
    are fetched.

    References
    ----------
    [1] https://docs.python.org/3/library/datetime.html#format-codes
    [2] https://docs.monzo.com/#list-transactions
    [3] https://docs.monzo.com/#pagination
    """    
    # Get account ID and creation date
    header = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.monzo.com/accounts", headers=header)
    if len(response.json()["accounts"]) > 2:
        raise ValueError(
            "Not yet implemented: two or more accounts associated" "with this login."
        )
    account_id = response.json()["accounts"][0]["id"]
    created = response.json()["accounts"][0]["created"]

    # Set start and end date of first API call.
    if since is not None:
        start = since
    else:
        start = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    end = start + timedelta(hours=8760)  # max time interval allowed by Monzo's API

    transactions = []
    print(f"Attempting to fetch transactions since {start.strftime('%d %b %Y')}")

    # Keep requesting transactions in blocks of 100 (the maximum) until we receive
    # a block with a size less than 100 (at which point we've got them all)
    block_size = 100
    while block_size == 100:
        params = {
            "account_id": account_id,
            "since": start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "before": end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "limit": block_size,
            "expand[]": "merchant"  # expand for more merchant info
        }
        response = requests.get(
            "https://api.monzo.com/transactions",
            headers=header, 
            params=params
        )
        tlist = response.json()["transactions"]  # list of JSON-like transaction objects

        # Clean transaction data (only keep quantities of interest)
        cleaned_transactions = []
        for t in tlist:
            # skip active card checks
            if t["amount"] == 0:
                continue

            m = t.get("merchant")    # doesn't always exist (e.g. incoming payment)
            meta = m.get("metadata") if m else None      # ditto
            cleaned_t = {
                "created": t.get("created"),
                "amount": t.get("amount"),
                "description": t.get("description"),
                "merchant_name": m.get("name") if m else None,
                "category": m.get("category") if m else None,
                "tags": m.get("suggested_tags") if m else None,
                "address": m.get("address").get("formatted") if m else None,
                "website": meta.get("website") if meta else None
            }

            cleaned_transactions.append(cleaned_t)

        # Add cleaned block to full `transactions` list, then determine the size of
        # the block to check if we need to keep going
        transactions.extend(cleaned_transactions)
        block_size = len(tlist)

        # Determine date of first and last transaction in the block
        first = tlist[0]["created"]
        last = tlist[-1]["created"]

        # Convert to datetime objects (makes manipulations below easier)
        first = datetime.strptime(first, "%Y-%m-%dT%H:%M:%S.%fZ")
        last = datetime.strptime(last, "%Y-%m-%dT%H:%M:%S.%fZ")

        # Verbose output to show progress (rough 1 API call per second)
        # Example output line: `24 Jun 2024 to 23 Jul 2024:  83 entries.`
        if verbose:
            print(f"{first.strftime('%d %b %Y')} to {last.strftime('%d %b %Y')}:  "
                  f"{block_size} entries.")

        # Set start of next block to the end of this block and end to 1 year later
        start = last + timedelta(seconds=1)
        end = start + timedelta(hours=8760)

    # Convert the transactions list to a DataFrame
    return pd.DataFrame(transactions)
    

def update_wanted():
    """
    Returns
    -------
    bool
        Whether the user wants to fetch more recent transactions
        from Monzo's servers  
    """
    while True:
        update = input("Fetch more recent transactions?: (y/n) ").lower().strip()
        if update in ["y", "n"]:
            return update == "y"


def refresh(access_token, last_transaction, verbose=False):
    """
    Retrieves transactions on the account since `last_transaction`. For
    details, see `fetch_transactions` function.

    Parameters
    ----------
    access_token : str
        The access token used to authenticate with the Monzo API.
    last_transaction : datetime
        The function will retrieve all transactions from this date.
        If not set, all transactions since account creation will
        be retrieved.
    verbose : bool, optional
        If True, prints progress information while API calls are
        being made (default is False).

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame containing transaction data.
    """
    df = pd.read_csv("transactions.csv")
    new_df = fetch_transactions(access_token, last_transaction, verbose=verbose)

    return pd.concat([df, new_df])
