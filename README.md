# Monzo personal finance dashboard
Currently a work in progress!

## Getting started
### Requirements
- Python3: to check whether you have Python installed on macOS or Linux, type `which python` into the terminal. On Windows, type `where python` into PowerShell. If Python is not installed, install it from [python.org](python.org)
- Add more dependencies (e.g. MySQL) here as they arise

### Creating an OAuth client ID
Before using the app, you'll need to set up a client ID using Monzo's Developer Tools. Details available here: [https://docs.monzo.com/](https://docs.monzo.com/)
1. Go to [https://developers.monzo.com/](https://developers.monzo.com/) and sign in.
2. Click on 'Clients' on the top-right of the page. 
3. Click the 'New OAuth Client' button. 
4. Give your client a sensible name and description (can be whatever you like) and set the redirect URL to `https://localhost:8080/`. Leave the logo URL blank (this can be changed later). Set the confidentiality to `Not Confidential`.

Keep this web page open. We'll need the **Client ID** and **Client Secret** shortly.

### Installing and setting up the app
1. Clone this repository:
```
  git clone https://github.com/baiway/monzo-personal-finance-dashboard.git
```

2. Change into the project directory:
```
  cd monzo-personal-finance-dashboard
```

2. Create a virtual environment. If you're not familiar with Python virtual environments, watch [this video](https://www.youtube.com/watch?v=Y21OR1OPC9A).
```
  python3 -m venv .venv
```

3. Activate the virtual environment
```
  source .venv/bin/activate
```

4. Install dependencies
```
  pip install -r requirements.txt
```

5. Copy & paste your **Client ID** and **Client Secret** into your `credentials.json` file.

## Running the app
You can run the app with
```
python3 test.py
```

When the app runs successfully, a browser window will open and ask for the email address associated with your Monzo account. Enter your email address. You'll then receive an email with a 'magic link' that you use to authenticate the app. Click on this link. It will redirect to a webpage that says something like "This site can’t be reached". This makes sense - we haven't created the webpage yet! (we'll do this later) The URL is still helpful though. Copy & paste the redirect URL into your terminal. You should then see your access token and 'who am I' response printed to the screen.

## To-do list for Jack
- Try to run the code
- Ensure you understand every line and each step in the installation process
- Attempt to get some transaction data using Monzo's API
- Attempt to save transaction data to file (e.g. using an SQL database)
- Create a more helpful redirect page (you may wish to use Flask here)
