import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
from src.utils import matplotlib2fasthtml

@matplotlib2fasthtml
def plot_spending_by_category(start_date: datetime, end_date: datetime):
    # Connect to the SQLite database
    # TODO I think we can use the variable `transactions` in `src/app.py` is
    # persistent. You may be able to pass that as an argument instead of
    # opening it again here.
    conn = sqlite3.connect("data/transactions.db")
    cursor = conn.cursor()

    # Query to filter transactions based on the date range
    query = """
    SELECT category, SUM(amount)
    FROM Transactions
    WHERE created BETWEEN ? AND ?
    GROUP BY category;
    """
    cursor.execute(query, (start_date, end_date))
    results = cursor.fetchall()

    # Close the connection
    conn.close()

    if not results:
        print("No data available for the selected range.")
        return

    # Extract categories and amounts
    # FIXME we should attempt to categorise these at some point
    categories = [row[0] if row[0] is not None else "uncategorised" for row in results]
    amounts = [-row[1] / 100 for row in results]  # convert pence to pounds

    # Create a bar chart using Matplotlib
    plt.bar(categories, amounts)

    # Add title and labels
    plt.title("Spending by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount (£)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
