# Various notes on the FastHTML migration

## Pylance warnings with FastHTML
FastHTML isn't compatible with Pylance (see [issue #329](https://github.com/AnswerDotAI/fasthtml/issues/329#issue-2471897892) on the FastHTML repo). As a workaround, add `# type: ignore` at the top of files containing FastHTML code. This will suppress Pylance warnings. Alternatively, you can just ignore them.

## Using Matplotlib for plotting
I found a plugin called [fh-matplotlib](https://github.com/koaning/fh-matplotlib/) that makes it easier to show figures generated via Matplotlib (Python's most popular plotting library) using FastHTML. Currently, the only file that does anything is in [fh-matplotlib/__init__.py](https://github.com/koaning/fh-matplotlib/blob/b74177417662d4a8d74af1476574a8f47667528c/fh_matplotlib/__init__.py). It simply defines a function decorator `@matplotlib2fasthtml`. It's usage is explained in the file (copied below).

```python
import matplotlib.pyplot
from fasthtml.common import Img
import matplotlib.pylab as plt
import matplotlib
import io
import base64

# This is necessary to prevent matplotlib from causing memory leaks
# https://stackoverflow.com/questions/31156578/matplotlib-doesnt-release-memory-after-savefig-and-close
matplotlib.use('Agg')


def matplotlib2fasthtml(func):
    """Ensure that matplotlib yielding function returns a renderable 
    item for FastHTML.

    Usage:
      import numpy as np
      import matplotlib.pylab as plt
      from fh_matplotlib import matplotlib2fasthtml

      # This function will return a proper Img that can be rendered
      @matplotlib2fasthtml
      def matplotlib_function():
          plt.plot(np.arange(25), np.random.exponential(1, size=25))
    """
    def wrapper(*args, **kwargs):
        # Reset the figure to prevent accumulation. 
        # Maybe we need a setting for this?
        fig = plt.figure()

        # Run function as normal
        func(*args, **kwargs)

        # Store it as base64 and put it into an image.
        my_stringIObytes = io.BytesIO()
        plt.savefig(my_stringIObytes, format='jpg')
        my_stringIObytes.seek(0)
        my_base64_jpgData = base64.b64encode(my_stringIObytes.read()).decode()

        # Close the figure to prevent memory leaks
        plt.close(fig)
        plt.close('all')
        return Img(src=f'data:image/jpg;base64, {my_base64_jpgData}')
    return wrapper
```

Currently the plugin only supports JPEG files, which use lossy compression. The developer has made a start on an SVG (non-lossy) implementation (see [see issue #3](https://github.com/koaning/fh-matplotlib/issues/3#issue-2446343094)), but it's not complete:
```python
import io
import base64
from IPython.display import display, HTML

plt.scatter([1,2,3], [54,12,2])
plt.title('this is a demo')

my_stringIObytes = io.BytesIO()
plt.savefig(my_stringIObytes, format='svg')
my_stringIObytes.seek(0)
HTML(my_stringIObytes.read().decode())
```

We could extend this and submit a pull request. Contributing to free and open-source (FOSS) software would be cool thing to mention in your write-up!
