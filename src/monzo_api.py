import requests
import sqlite3
from datetime import datetime, timedelta

def get_account_details(access_token: str) -> tuple[str, str]:
    """Get account ID and account creation date. The latter is used to
    determine the date for earliest API call.
    """
    header = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.monzo.com/accounts", headers=header)
    if len(response.json()["accounts"]) > 2:
        raise ValueError(
            "Not yet implemented: two or more accounts "
            "associated with this email address."
        )
    account_id = response.json()["accounts"][0]["id"]
    created = response.json()["accounts"][0]["created"]
    return account_id, created

def fetch_transactions(access_token: str, verbose: bool = False) -> None:
    """
    Updates `data/transactions.db`. If the database already exists, it
    retrieves all transactions since the last transaction on file. If
    it doesn't exist, it retrieves all transactions since the account
    creation date.

    Multiple API calls are made to comply with Monzo's API limitations
    on time intervals and the maximum number of transactions per call.
    See Notes below for details.

    Notes
    -----
    The Monzo API allows a maximum time interval of 8760 hours
    (365 days) between the `since` and `before` parameters [1].
    Additionally, the maximum number of transactions that can be
    received in a single API call is 100 [2]. Therefore, the function
    splits the time range into multiple intervals if necessary and
    retrieves transactions in blocks of 100 until all transactions
    have been fetched.

    References
    ----------
    [1] https://docs.monzo.com/#list-transactions
    [2] https://docs.monzo.com/#pagination
    """
    # Get account ID and account creation date
    account_id, created = get_account_details(access_token)

    # Open `data/transactions.db`
    conn = sqlite3.connect("data/transactions.db")
    cursor = conn.cursor()

    # Fetch the latest transaction timestamp from the database
    # TODO will this work for strings in the format "%Y-%m-%dT%H:%M:%S.%fZ"?
    # not sure SQLite knows how to parse this
    cursor.execute("SELECT MAX(created) FROM transactions")
    most_recent = cursor.fetchone()[0]

    # Close `data/transactions.db`
    conn.close()

    # TODO will this get a smart default of `None` if SQLite cannot find
    # any transactions? (e.g. if the database is empty)
    if most_recent:
        start = datetime.strptime(most_recent, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        start = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Set end date to 1 year later (max allowed by Monzo API)
    end = start + timedelta(hours=8760)

    # Request transactions in blocks of 100 (the maximum) until we receive a
    # block with a size less than 100, at which point we've fetched them all.
    print(f"Fetching transactions since {start.strftime('%d %b %Y')}")
    header = {"Authorization": f"Bearer {access_token}"}
    block_size = 100
    while block_size == 100:
        params = {
            "account_id": account_id,
            "since": start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "before": end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "limit": block_size,
            "expand[]": "merchant"  # used to get more merchant info
        }
        response = requests.get(
            "https://api.monzo.com/transactions",
            headers=header,
            params=params
        )
        transactions = response.json()["transactions"] # list of transactions

        # Clean transaction data (only keep quantities of interest)
        cleaned_transactions = []
        for t in transactions:
            # Skip active card checks
            if t["amount"] == 0:
                continue

            # "merchant" and "metadata" keys do not always exist (e.g. for
            # incoming payments). In cases where they are not found, set other
            # "merchant_name", "category", etc. to `None`
            m = t.get("merchant")
            meta = m.get("metadata") if m else None
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

        # Add cleaned transactions to `data/transactions.db`
        insert_transactions_to_db(cleaned_transactions)

        # Determine date of first and last transaction in the block
        first = cleaned_transactions[0]["created"]
        last = cleaned_transactions[-1]["created"]

        # Convert to datetime objects (makes manipulations below easier)
        first = datetime.strptime(first, "%Y-%m-%dT%H:%M:%S.%fZ")
        last = datetime.strptime(last, "%Y-%m-%dT%H:%M:%S.%fZ")

        # Verbose output to show progress (roughly 1 API call per second)
        if verbose:
            print(
                f"{first.strftime('%d %b %Y')} to {last.strftime('%d %b %Y')}:"
                f" {block_size} entries."
            )

        # Set start of next block to the end of this block and
        # end to 1 year later
        start = last + timedelta(seconds=1)
        end = start + timedelta(hours=8760)

        # Update `block_size` to determine whether we need to keep going
        block_size = len(transactions)


def insert_transactions_to_db(transactions: list) -> None:
    """Inserts a list of cleaned transactions into the transactions
    database `data/transactions.db`
    """
    conn = sqlite3.connect("data/transactions.db")
    cursor = conn.cursor()

    for t in transactions:
        cursor.execute(
            """
            INSERT OR IGNORE INTO transactions
            (created, amount, description, merchant_name, category, tags,
            address, website)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                t["created"],
                t["amount"],
                t["description"],
                t["merchant_name"],
                t["category"],
                t["tags"],
                t["address"],
                t["website"],
            )
        )

    conn.commit()
    conn.close()
