# Monzo personal finance dashboard
Currently a work in progress! 
- **5th June 2024:** Brain storming session. Decided on this project.
- **13th June 2024:** Started playing around with the Monzo API and HTTP requests using Python.
- **18th June 2024:** Got basic Monzo API calls working from within Python (including retrieving transactions!)
- **19th June 2024:** Walked Jack through the OAuth flow using Python's [Requests](https://requests.readthedocs.io/en/latest/) library and Monzo's API
- **26th June 2024:** Implementing basic redirect page using Flask web server.
- **10th July 2024:** Walked Jack through using Git and GitHub and briefly explained refactored source code structure (i.e. `src/` folder, `utils/` folder, etc.)
- **17th July 2024:** Cleaned transaction data so that only quantities of interest were saved to `transactions.json`
- **24th July 2024:** Attempted to start writing analysis code, but spent the lesson debugging the code instead! See commit [2ea8428](https://github.com/baiway/monzo-personal-finance-dashboard/commit/2ea8428749a8d928689f8e0c92511e8255b141c8) for details. Later that evening, I did a major refactoring of the code. See commits [2ea8428](https://github.com/baiway/monzo-personal-finance-dashboard/commit/2ea8428749a8d928689f8e0c92511e8255b141c8), [7367f09](https://github.com/baiway/monzo-personal-finance-dashboard/commit/7367f09a4c2730d3fd1a49da41dace23c6aea54e), [a3f344f](https://github.com/baiway/monzo-personal-finance-dashboard/commit/a3f344f45c609b7988374a98e889fc6b08717fea) and [7a50dd5](https://github.com/baiway/monzo-personal-finance-dashboard/commit/7a50dd52b19f5e467a48618b62abab4ed463d0ea).
- **31st July 2024:** Reviewed changes since last week, then started fleshing out the browser-based dashboard. I continued this after the session (see commit [51c82a1](https://github.com/baiway/monzo-personal-finance-dashboard/commit/51c82a1f24a2080c0049f10d099965fbde58bb2e)). We've now got our first dashboard component! 🎉 It plots the spending by category over a period specified by the user with a date-picker.
- **6th August 2024:** Walked Jack through the changes to ensure he can run the dashboard on his machine too. Neither of us were particular fans of [Plotly Dash](https://dash.plotly.com/)'s syntax, but we decided to make do.
- **11th September 2024:** We both agreed to re-write the app to use [FastHTML](https://fastht.ml/) instead of an awkward mix of [Flask](https://flask.palletsprojects.com/en/3.0.x/) and [Plotly Dash](https://dash.plotly.com/). This way, we can write Dashboard components using straightforward [Matplotlib](https://matplotlib.org/) code.
- **18th September 2024:** Re-wrote the basic OAuth flow using [FastHTML](https://fastht.ml/). Walked Jack through the new code. Unfortunately, the program did not run on Jack's computer. Still investigating why.
- **19th September 2024:** Re-wrote the `fetch_transactions` function so that it saved transactions to SQLite database, `data/transactions.db`. Also implemented a simple spending by category plot that uses [Matplotlib](https://matplotlib.org/). The refactored app has now achieved feature pairty with the previous app.

## Getting started
### Requirements
- [Monzo](https://monzo.com/) bank account
- [Python 3](https://www.python.org/). To check whether you have Python 3 installed, type `python3 --version` into your terminal (or PowerShell on Windows). If Python is not installed, you can download it from [python.org](python.org). You can find some concise guidance for installing Python on various operating systems [here](https://github.com/baiway/MScFE_python_refresher/blob/1e4f13588dfaee53c34a646d0443d86cbad1873a/docs/installing-python.md).

### Creating an OAuth client ID
Before using the app, you'll need to set up a client using Monzo's Developer Tools. Details available here: [https://docs.monzo.com/](https://docs.monzo.com/)
1. Go to [https://developers.monzo.com/](https://developers.monzo.com/) and sign in. You will also need to open the Monzo app on your phone and give [https://developers.monzo.com/](https://developers.monzo.com/) permission to access your account.
2. Click on 'Clients' on the top-right of the page.
3. Click the 'New OAuth Client' button.
4. Give your client a sensible name and description (can be whatever you like) and set the redirect URL to `http://localhost:5001/callback`. Leave the logo URL blank (this can be changed later). Set the confidentiality to `Not Confidential`.

Keep this web page open. We'll need the **Client ID** and **Client Secret** shortly.

### Installing and setting up the app
**1. Clone this repository**
```sh
git clone https://github.com/baiway/monzo-personal-finance-dashboard.git
```

**2. Change into the project directory**
```sh
cd monzo-personal-finance-dashboard
```

**3. Create a virtual environment.** 
If you're not familiar with Python virtual environments, watch [this video](https://www.youtube.com/watch?v=Y21OR1OPC9A).
```sh
python3 -m venv .venv
```

**4. Activate the virtual environment.**

The command varies by operating system. On macOS or Linux, enter
```sh
source .venv/bin/activate
```
If using PowerShell on Windows, enter
```sh
.venv\Scripts\Activate.ps1
```

**5. Optional:** if using features on a particular branch, list the available branches then switch to the relevant branch:
```sh
git branch -a
git switch <branch_name>
```

**6. Install dependencies**
```sh
pip install -r requirements.txt
```

## Running the app
You can now run the app with
```sh
python3 launch_dashboard.py
```

When the app runs for the first time, it will open [http://localhost:5001/auth](http://localhost:5001/auth) in the browser. Enter the *client ID* and *client secret* that you created earlier. When you submit your credentials, they will be securely saved as a cookie in the file `.sesskey` so you do not have to repeat this step again.

Next, the app will attempt to use these credentials to secure a connection with Monzo's servers. You will be redirected to [https://auth.monzo.com/](https://auth.monzo.com/) asked for the email address associated with your Monzo account. Enter your email address. You'll then receive an email with a 'magic link' that you use to authenticate the app. Click on this link. This will redirect you to [http://localhost:5001/auth/callback?code=...](http://localhost:5001/auth/callback?code=...). The app will capture the authentication code, then exchange it with Monzo's servers for an access token. With this access token, the app is now able to make API requests to Monzo's servers.

The app stores a copy of your transactions on your machine called `data/transactions.db`. This is so you do not have to repeat the authentication procedure each time you run the app (unless you wait to update the database). Just note that **this document is only as secure as your computer**. You may wish to delete `data/transactions.db` between sessions for security purposes.

## To-do list for Jack
- Ensure you understand every line of code in the project and each step in the installation process. If there's anything you do not understand, make a note of it and raise it with me in our next session (or text/email).
- During the OAuth flow, instead of redirecting the user to [https://auth.monzo.com/](https://auth.monzo.com/) (and therefore away from our app), is it possible to embed a 'mini-browser' within our app? This would enable the user to authenticate without navigating away from [http://localhost:5001/auth](http://localhost5001/auth).
- Make a short screen recording on your laptop that demonstrates how to set up a client via [https://developers.monzo.com](https://developers.monzo.com) (i.e. getting a `client_id`, `client_secret` and setting the `redirect_uri`). Add this to the `/auth` page where the user enters their `client_id` and `client_secret`.
- Make a short screen recording on your phone that shows you receiving a push notification from Monzo and authenticating via the app. Blur your transactions! Add this to the `auth/callback` page (the one with the button that says "Proceed to webpage" -- this breaks if the user hasn't authenticated via the app, so this would be a great addition to improve user experience!)
- In the `auth/callback` GET router, check whether the user has authenticated via the app before attempting to route them to `"/"` (the dashboard). I think you could do this by calling the `/ping/whoami` endpoint and checking whether `authenticated` is `True`, although I've not tested this. See [https://docs.monzo.com](https://docs.monzo.com) for more information.
- Decorate the app to your taste by writing a file `styles/style.css`. You can then associated it with the FastHTML app by adding it as a header: `app, rt = fast_app(..., hdrs={picolink,"styles/style.css"})` (see `src/app.py`).
- Add more dashboard components, for example:
    - A static (i.e. does not update with the date-picker) pie chart that shows your spending by category since the account creation date
    - A static line graph that shows your monthly earnings and expendature since the account creation date
    - Ability to enter budget information (and have this saved to persist across sessions)
- Expense categorisation. Some of this is done by Monzo, but not always very well. Examples: purchases from small businesses, transfers between accounts. It would be nice to handle these better so our dashboard shows us information that's actually useful.
