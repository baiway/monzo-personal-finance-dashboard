from plotly.graph_objs import Bar, Layout
from src.data import get_transactions_data

def generate_category_spending_chart(start_date, end_date):
    transactions = get_transactions_data()

    if transactions is None:
        return {'data': [], 'layout': Layout(title='No Data Available')}

    # Filter transactions based on the selected date range
    if start_date and end_date:
        filtered_transactions = transactions[
            (transactions["created"] >= start_date) & 
            (transactions["created"] <= end_date)
        ]
    else:
        filtered_transactions = transactions

    # Group by category and sum the amounts
    spending_by_category = filtered_transactions.groupby('category')['amount'].sum()

    # Divide by -100 (converts pence -> pounds and turns negative spends into
    # positive quantities for display purposes
    spending_by_category /= -100

    # Create bar chart
    data = [
        Bar(
            x=spending_by_category.index,
            y=spending_by_category.values
        )
    ]

    layout = Layout(
        title='Spending by category',
        xaxis=dict(title='Category'),
        yaxis=dict(title='Amount (£)')
    )

    return {'data': data, 'layout': layout}
