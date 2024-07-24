import requests
import json
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
    transactions : list
        A list of transactions, each in a JSON-like format.

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
        params = {"account_id": account_id,
                  "since": start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                  "before": end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                  "limit": block_size}
        response = requests.get("https://api.monzo.com/transactions", 
                                headers=header, params=params)
        tlist = response.json()["transactions"]  # list of JSON-like transaction objects

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
            print(f"{first.strftime('%d %b %Y')} to {last.strftime('%d %b %Y')}:  "
                  f"{block_size} entries.")

        # Set start of next block to the end of this block and end to 1 year later
        start = last + timedelta(seconds=1)
        end = start + timedelta(hours=8760)

    return transactions


def last_transaction():
    """
    Returns
    -------
    datetime
        The date of the last transaction in transactions.json.
    """
    with open("transactions.json", "r") as file:
        last = json.load(file)["transactions"][-1]["created"]

    return datetime.strptime(last, "%Y-%m-%dT%H:%M:%S.%fZ")
    

def update_wanted():
    """
    Returns
    -------
    bool
        Whether the user wants to fetch more recent transactions
        from Monzo's servers  
    """
    while True:
        update = input("Fetch more recent transactions?: (y/n)" ).lower().strip()
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
    transactions : list
        A list of transactions, each in a JSON-like format.
        
    """
    with open("transactions.json", "r") as file:
        transactions = json.load(file)["transactions"]
    new_trans = fetch_transactions(access_token, last_transaction, verbose=verbose)

    transactions.extend(new_trans)

    return transactions
