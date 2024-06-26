# Monzo personal finance dashboard
Currently a work in progress! 
- **5th June 2024:** Brain storming session. Decided on this project.
- **13th June 2024:** Started playing around with the Monzo API and HTTP requests using Python.
- **18th June 2024:** Got basic Monzo API calls working from within Python (including retrieving transactions!)
- **19th June 2024:** Reviewing changes together and ensuring we've on the same page.

## Getting started
### Requirements
- A [Monzo](https://monzo.com/) bank account
- Python 3: to check whether you have Python 3 installed, type `python3 --version` into your terminal (or PowerShell on Windows). If Python is not installed, install it from [python.org](python.org)

### Creating an OAuth client ID
Before using the app, you'll need to set up a client ID using Monzo's Developer Tools. Details available here: [https://docs.monzo.com/](https://docs.monzo.com/)
1. Go to [https://developers.monzo.com/](https://developers.monzo.com/) and sign in.
2. Click on 'Clients' on the top-right of the page. 
3. Click the 'New OAuth Client' button. 
4. Give your client a sensible name and description (can be whatever you like) and set the redirect URL to `https://localhost:8080/`. Leave the logo URL blank (this can be changed later). Set the confidentiality to `Not Confidential`.

Keep this web page open. We'll need the **Client ID** and **Client Secret** shortly.

### Installing and setting up the app
**1. Clone this repository**
```
  git clone https://github.com/baiway/monzo-personal-finance-dashboard.git
```

**2. Change into the project directory**
```
  cd monzo-personal-finance-dashboard
```

**3. Create a virtual environment.** 
If you're not familiar with Python virtual environments, watch [this video](https://www.youtube.com/watch?v=Y21OR1OPC9A).
```
  python3 -m venv .venv
```

**4. Activate the virtual environment.**

On macOS or Linux, enter
```
  source .venv/bin/activate
```
If using PowerShell on Windows, enter
```
  .venv\Scripts\Activate.ps1
```

**5. Install dependencies**
```
  pip install -r requirements.txt
```

6. Copy & paste your **Client ID** and **Client Secret** into your `credentials.json` file.

## Running the app
You can run the app with
```
python3 get_transactions.py
```

When the app runs successfully, a browser window will open and ask for the email address associated with your Monzo account. Enter your email address. You'll then receive an email with a 'magic link' that you use to authenticate the app. Click on this link. It will redirect to a webpage that says something like "This site can’t be reached". This makes sense - we haven't created the webpage yet! (we'll do this later) The URL is still helpful though. Copy & paste the redirect URL into your terminal. You should then see the outputs of various API calls in your terminal (WHOAMI, accounts, current balance, and first few transactions).

## To-do list for Jack
- Try to run the code
- Ensure you understand every line and each step in the installation process
- ~~Attempt to get some transaction data using Monzo's API~~
- ~~Attempt to save transaction data to file (e.g. using an SQL database)~~
- Determine whether a large JSON file an appropriate data storage format. For context, I've been using Monzo as my primary current account since August 2018 and my `transactions.json` file is ~250k lines long and ~10 MiB in size. I don't think this is an issue as the file will still be < 1 GiB if I live to 100 (assuming my spending habits don't change to much). More important considerations are whether it's efficient to query large JSON files. Of course, we can also reduce the filesize *significantly* by cleaning the transaction data before we save it to disk (i.e. get rid of all unnecessary data).
- Create a more helpful redirect page (you may wish to use [Flask](https://flask.palletsprojects.com/en/3.0.x/) here)
- In the setup stage on [https://developers.monzo.com/](https://developers.monzo.com/), it may be worth us using a "confidential" client instead. This way, we'll be able to refresh our access tokens rather than re-authenticating. For details, see the [Refreshing access](https://docs.monzo.com/#refreshing-access) section of Monzo's API docs.
