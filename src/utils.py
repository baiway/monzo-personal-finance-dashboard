import io
import base64
import random
import string
import matplotlib
import matplotlib.pyplot as plt
from fasthtml.common import Img
from pathlib import Path
from datetime import datetime

# This is necessary to prevent matplotlib from causing memory leaks
# https://stackoverflow.com/questions/31156578/matplotlib-doesnt-release-memory-after-savefig-and-close
matplotlib.use('Agg')

def gen_rand_str(length=16):
    """Generates a random string of letters and numbers to create an
    unguessable state token for use in authentication. This protects
    against cross-site request forgery attacks.
    See: https://docs.monzo.com/#acquire-an-access-token"""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def get_update_date():
    """Get the date and time of that `data/transactions.db` was last
    modified. Example outout: "20:30 on 19 Sep 2024".
    """
    last_modified = Path("data/transactions.db").stat().st_mtime
    return datetime.fromtimestamp(last_modified).strftime(
        "%H:%M on %d %b %Y"
    )


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
