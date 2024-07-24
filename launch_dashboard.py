from src.auth import authenticate
from src.monzo_api import fetch_transactions, last_transaction, update_wanted, refresh

import json
from pathlib import Path

if __name__ == "__main__":
    # Check whether `transactions.json` already exists. If it does, ask user whether
    # they'd like to fetch more recent transactions, or continue with the existing
    # `transactions.json`. If this doesn't exist, fetch all transactions since the
    # account was created.
    #
    # The advantage of this approach is that we only authenticate when we need to. 
    # This should lead to a much more pleasant user experience.

    transactions_path = Path(__file__).parent / "transactions.json"

    if transactions_path.is_file():
        # Print date of last transaction
        last_transaction = last_transaction()
        print("transactions.json already exists. The last transaction was on " \
              f"{last_transaction.strftime('%d %b %Y')}.")

        if update_wanted():
            # Authenticate then fetch new transactions
            access_token = authenticate()
            transactions = refresh(access_token, last_transaction, verbose=True)

            # Save updated `transactions.json`.
            with open("transactions.json", "w") as file:
                json.dump({"transactions": transactions}, file, indent=2)
            print("Saved updated transaction data to: transactions.json.")

    else:
        # No `transactions.json` found. Authenticate then fetch all transactions
        access_token = authenticate()
        transactions = fetch_transactions(access_token, verbose=True)

        # Save `transactions.json` for future use.
        with open("transactions.json", "w") as file:
            json.dump({"transactions": transactions}, file, indent=2)
        print("Saved transaction data to: transactions.json.")
        
