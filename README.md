# Monzo personal finance dashboard
Currently a work in progress! 
- **5th June 2024:** Brain storming session. Decided on this project.
- **13th June 2024:** Started playing around with the Monzo API and HTTP requests using Python.
- **18th June 2024:** Got basic Monzo API calls working from within Python (including retrieving transactions!)
- **19th June 2024:** Reviewing changes together and ensuring we've on the same page.
- **26th June 2024:** Implementing basic redirect page using Flask web server.
- **10th July 2024:** Walked Jack through using Git and GitHub and briefly explained refactored source code structure (i.e. `src/` folder, `utils/` folder, etc.)

## Getting started
### Requirements
- A [Monzo](https://monzo.com/) bank account
- Python 3: to check whether you have Python 3 installed, type `python3 --version` into your terminal (or PowerShell on Windows). If Python is not installed, install it from [python.org](python.org)

### Creating an OAuth client ID
Before using the app, you'll need to set up a client ID using Monzo's Developer Tools. Details available here: [https://docs.monzo.com/](https://docs.monzo.com/)
1. Go to [https://developers.monzo.com/](https://developers.monzo.com/) and sign in.
2. Click on 'Clients' on the top-right of the page. 
3. Click the 'New OAuth Client' button. 
4. Give your client a sensible name and description (can be whatever you like) and set the redirect URL to `http://localhost:8080/callback`. Leave the logo URL blank (this can be changed later). Set the confidentiality to `Not Confidential`.

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

**5. Optional:** if using features on a particular branch, list the available branches then checkout (i.e. switch to) the relevant branch:
```sh
git branch -a
git checkout <branch_name>
```

**6. Install dependencies**
```sh
pip install -r requirements.txt
```

7. **Copy & paste your *Client ID* and *Client Secret* into your `credentials.json` file.**

## Running the app
You can run the app with
```sh
python3 launch_dashboard.py
```

When the app runs successfully, a browser window will open and ask for the email address associated with your Monzo account. Enter your email address. You'll then receive an email with a 'magic link' that you use to authenticate the app. Click on this link. This will redirect you to `http://localhost:8080/callback`, which is the URL our Flask webserver is running on. The webserver will capture the authentication code, then use it to authenticate the client with Monzo. The app is now able to communicate with Monzo's servers.

## Developing the app (i.e. using Git and GitHub)
All of this can be achieved with a GUI using [VS Code's Git Integration](https://code.visualstudio.com/docs/sourcecontrol/overview) (and the [GitHub extension](https://code.visualstudio.com/docs/sourcecontrol/github)). I'm just including the commands here to familiarise you with Git jargon. If you'd like a video explainer, I recommend this video: [Using Git with Visual Studio Code (Official Beginner Tutorial)](https://www.youtube.com/watch?v=i_23KUAEtUM). 

### Important: ignoring changes to `credentials.json`
When you're working with sensitive information, you need to take extreme care not to accidentally share it with the internet. Whilst it's not crucial for this project, it's good practice to get in the habit of protecting yourself against this. In this project, we want to ensure that we do not accidentally push our `credentials.json` (with our `client_id` and `client_secret`) to GitHub. To avoid this, we can tell Git to ignore changes to `credentials.json` on our working tree using
```sh
git update-index --skip-worktree credentials.json
```
This way, `credentials.json` will not appear as a modified file in `git status` (or in the VS Code GUI), so we will not accidentally stage it for commit. **Important:** this is a local setting (i.e. it only applies to the folder you're working in), so if you delete the folder then re-clone it, you'll have to run this command again.

I should emphasise that this is a very hacky workaround. We may wish to change how we handle this in future. Something like this is necessary though if we want to include a template `credentials.json` file in the repository though (as opposed to telling the user to create this file themselves). Alternatives are described [here](https://stackoverflow.com/questions/1753070/how-do-i-configure-git-to-ignore-some-files-locally). We could also use [environment variables](https://stackoverflow.com/questions/4906977/how-can-i-access-environment-variables-in-python), although I'm not a fan of this solution. Realistically, this only matters for developmers. Users will not experience this issue, so it's probably not worth thinking about.

### Using branches
If developing new features, it's good practice to create a new branch so that you don't overwrite (or break!) other people's code. To create a new branch based off an existing branch, first checkout (i.e. switch to) the existing branch:
```sh
git checkout <branch_name>
```

Then create a new branch named `<new_branch>` with
```sh
git branch <new_branch>
git checkout <new_branch>
```

or as a one-liner, `git checkout -b <new_branch>`.

### Committing your changes
To commit your changes, you first need to `add` (i.e. stage them), then commit them with a helpful message:
```sh
git add my_script.py
git commit -m "Add Google Calendar API"
```

As a general rule, commit titles should be short and declaritive. Advice on what *not* to do here: [How to commit better with Git](https://www.youtube.com/watch?v=Hlp-9cdImSM).


### Pushing your changes to the remote repository
You can push your changes to the remote repository (GitHub) using
```sh
git push <remote_name> <local_branch_name>
```

The remote name will usually be `origin`. As an example, a `push` command I used recently used was: 
```sh
git push origin refactor
```

### Updating your local repository
You can fetch (i.e. download) changes on the remote repository (GitHub) using
```sh
git fetch
```
I recommend doing this rather than re-cloning, setting up the virtual environment, etc. each time as it's much faster.

## To-do list for Jack
- Ensure you understand every line of code and each step in the installation process. If there's anything you do not understand, make a note of it and raise it with me in our next session (or text/email)
- ~~Attempt to get some transaction data using Monzo's API~~
- ~~Attempt to save transaction data to file (e.g. using an SQL database)~~
- Determine whether a large JSON file an appropriate data storage format. For context, I've been using Monzo as my primary current account since August 2018 and my `transactions.json` file is ~250k lines long and ~10 MiB in size. I don't think this is an issue as the file will still be < 1 GiB if I live to 100 (assuming my spending habits don't change to much). More important considerations are whether it's efficient to query large JSON files. Of course, we can also reduce the filesize *significantly* by cleaning the transaction data before we save it to disk (i.e. get rid of all unnecessary data).
- ~~Create a more helpful redirect page (you may wish to use [Flask](https://flask.palletsprojects.com/en/3.0.x/) here)~~
- Make the redirect page prettier using HTML and CSS.
- Delete unnecessary fields from each transaction. For now, I think we only need `"amount"` and `"category"`. This will make querying `transactions.json` much faster (write about this in your write-up!)
- Write some dummy HTML and CSS to display a webpage with various blank panels on it (e.g. one for spending by category, one for budgeted vs. actual spending, etc.)
- Attempt to populate these panels with transaction data. Do you want this to be interactive? (e.g. we select a start and end date and see a summary of transactions in between)
- Write some unit tests. See `tests/README.md` to get started.
