from src.auth import authenticate
from src.monzo_api import fetch_transactions, last_transaction, update_wanted, refresh

from pathlib import Path

if __name__ == "__main__":
    # Check whether `transactions.csv` already exists. If it does, ask user whether
    # they'd like to fetch more recent transactions, or continue with the existing
    # `transactions.csv`. If this doesn't exist, fetch all transactions since the
    # account was created.
    #
    # The advantage of this approach is that we only authenticate when we need to. 
    # This should lead to a much more pleasant user experience.

    tpath = Path(__file__).parent / "transactions.csv"

    if tpath.is_file():
        # Print date of last transaction
        last_transaction = last_transaction()
        print(f"{tpath.name} already exists. The last transaction was on " \
              f"{last_transaction.strftime('%d %b %Y')}.")

        if update_wanted():
            # Authenticate then fetch new transactions
            access_token = authenticate()
            transactions = refresh(access_token, last_transaction, verbose=True)
            updated = True
        else:
            updated = False

    else:
        # No `transactions.json` found. Authenticate then fetch all transactions
        access_token = authenticate()
        transactions = fetch_transactions(access_token, verbose=True)
        updated = True

    # Save updated transactions data locally
    if updated:
        print(f"Saved transaction data to: {tpath.resolve()}")
        transactions.to_csv(tpath, index=False)
