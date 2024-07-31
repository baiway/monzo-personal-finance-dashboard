import pandas as pd
from datetime import datetime
from pathlib import Path

from src.auth import authenticate
from src.monzo_api import fetch_transactions, update_wanted, refresh

# Global variable to store transactions data
# this is defined as a global here to avoid the need to repeatedly
# read from `transactions.csv` each time a Dash component is refreshed
# here we read once, then store it in memory for the duration of the
# app's lifetime
transactions_data = None

def load_transactions_data():
    """
    If `transactions.csv` already exists, asks user whether they'd 
    like to fetch more recent transactions. If `transactions.csv` 
    doesn't exist, fetch all transactions since the account 
    was created.
    
    The advantage of this approach is that we only authenticate when 
    we need to. This should lead to a much more pleasant user 
    experience.  
    """
    global transactions_data

    tpath = Path("transactions.csv")
    if tpath.exists():
        transactions = pd.read_csv("transactions.csv")
        last = datetime.strptime(transactions.iloc[-1]["created"], 
                                "%Y-%m-%dT%H:%M:%S.%fZ")
        print(f"{tpath.name} already exists. The last transaction was on " \
              f"{last.strftime('%d %b %Y')}.")

        if update_wanted():
            access_token = authenticate()
            transactions = refresh(access_token, last, verbose=True)
            updated = True
        else:
            updated = False

    else:
        # No `transactions.csv` found. Authenticate then fetch all transactions
        access_token = authenticate()
        transactions = fetch_transactions(access_token, verbose=True)
        updated = True

    # Store transactions data as global variable for use in other modules
    # and save if updates
    transactions_data = transactions
    if updated:
        print(f"Saved transaction data to: {tpath.resolve()}")
        transactions.to_csv(tpath, index=False)

def get_transactions_data():
    return transactions_data

