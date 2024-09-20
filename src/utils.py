import io
import base64
import random
import string
import sqlite3
import matplotlib
import matplotlib.pyplot as plt
from fasthtml.common import Img
from pathlib import Path
from datetime import datetime

def gen_rand_str(L=16):
    """Generates a random string of letters and numbers of length `L`
    to create an unguessable state token for use in authentication.
    This protects against cross-site request forgery attacks.
    See: https://docs.monzo.com/#acquire-an-access-token"""
    return "".join(random.choices(string.ascii_letters + string.digits, k=L))

def get_update_date():
    """Get the date and time that `data/transactions.db` or
    `data/transactions.db-wal` was last modified, whichever is more
    recent. The `.db-wal` file is a "write-ahead log" file. It stores
    changes made to the database (e.g by this script) before they are
    committed to the main `.db` file. Example output: "20:30 on 19 Sep
    2024".
    """
    db_path = Path("data/transactions.db")
    wal_path = Path("data/transactions.db-wal")

    # Get modification times for both files
    db_mtime = db_path.stat().st_mtime
    wal_mtime = wal_path.stat().st_mtime if wal_path.exists() else 0

    # Determine the most recent modification time
    last_modified = max(db_mtime, wal_mtime)

    return datetime.fromtimestamp(last_modified).strftime(
        "%H:%M on %d %b %Y"
    )

def has_entries() -> bool:
    """Checks if the `transactions` table in `data/transactions.db` has
    any entries.
    """
    db_path = "data/transactions.db"
    conn = sqlite3.connect(db_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions")
        result = cursor.fetchone()
    return result[0] > 0 # if number of rows > 0


def matplotlib2fasthtml(func):
    """Defines a function decorator that allows FastHTML to render
    Matplotlib figures. Usage:
    ```python
    import numpy as np
    import matplotlib.pylab as plt
    from src.utils import matplotlib2fasthtml

    # This function will return a proper Img that can be rendered
    @matplotlib2fasthtml
    def matplotlib_function():
        plt.plot(np.arange(25), np.random.exponential(1, size=25))
    ```
    Code from: https://github.com/koaning/fh-matplotlib/
    """
    matplotlib.use('Agg')
    def wrapper(*args, **kwargs):
        fig = plt.figure()

        # Run function as normal
        func(*args, **kwargs)

        # Store it as base64 and put it into an image.
        my_stringIObytes = io.BytesIO()
        plt.savefig(my_stringIObytes, format="jpg")
        my_stringIObytes.seek(0)
        my_base64_jpgData = base64.b64encode(my_stringIObytes.read()).decode()

        # Close the figure to prevent memory leaks
        plt.close(fig)
        return Img(src=f"data:image/jpg;base64, {my_base64_jpgData}")
    return wrapper
