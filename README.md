# Monzo personal finance dashboard
Currently a work in progress! 
- **5th June 2024:** Brain storming session. Decided on this project.
- **13th June 2024:** Started playing around with the Monzo API and HTTP requests using Python.
- **18th June 2024:** Got basic Monzo API calls working from within Python (including retrieving transactions!)
- **19th June 2024:** Reviewing changes together and ensuring we've on the same page.
- **26th June 2024:** Implementing basic redirect page using Flask web server.
- **10th July 2024:** Walked Jack through using Git and GitHub and briefly explained refactored source code structure (i.e. `src/` folder, `utils/` folder, etc.)
- **17th July 2024:** Cleaned transaction data so that only quantities of interest were saved to `transactions.json`
- **24th July 2024:** Attempted to start writing analysis code, but spent the lesson trying to debug the code! See commit 2ea84287 for details. Later that evening, I did a major refactoring of the code. See commits 2ea84287, 7367f09a, a3f344f4, 7a50dd52
- **31st July 2024:** Reviewed changes since last week, then started fleshing out the browser-based dashboard. I continued this after the session (see commit 51c82a1f). We've now got our first dashboard component! 🎉 It plots the spending by category between a start and end date chosen using a date-picker.

## Getting started
### Requirements
- [Monzo](https://monzo.com/) bank account
- [Python 3](https://www.python.org/). To check whether you have Python 3 installed, type `python3 --version` into your terminal (or PowerShell on Windows). If Python is not installed, you can download it from [python.org](python.org). You can find some concise guidance for installing Python on various operating systems [here](https://github.com/baiway/MScFE_python_refresher/blob/1e4f13588dfaee53c34a646d0443d86cbad1873a/docs/installing-python.md).

### Creating an OAuth client ID
Before using the app, you'll need to set up a client using Monzo's Developer Tools. Details available here: [https://docs.monzo.com/](https://docs.monzo.com/)
1. Go to [https://developers.monzo.com/](https://developers.monzo.com/) and sign in. You will also need to open the Monzo app on your phone and give [https://developers.monzo.com/](https://developers.monzo.com/) permission to access your account.
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

When the app runs for the first time, it will open [http://127.0.0.1:8050/](http://127.0.0.1:8050/credentials) in the browser. Enter the *client ID* and *client secret* that you created earlier. When you submit your credentials, they will be saved in a file `credentials.json` so you do not have to repeat this step again. 

Next, the app will attempt to use these credentials to secure a connection with Monzo's servers. A browser window will open and ask for the email address associated with your Monzo account. Enter your email address. You'll then receive an email with a 'magic link' that you use to authenticate the app. Click on this link. This will redirect you to `http://localhost:8080/callback`, which is the URL that our app's Flask webserver is running on. The webserver will capture the authentication code, then use it to authenticate the client with Monzo. The app is now able to communicate with Monzo's servers.

By default, the app stores a copy of your transactions on your machine called `transactions.csv`. This is so you do not have to repeat the authentication procedure each time you run the app (unless you wait to update the document). Just note that **this document is only as secure as your computer**. You may wish to delete `transactions.csv` between uses of the app for security purposes.

## Developing the app (i.e. using Git and GitHub)
All of this can be achieved with a GUI using [VS Code's Git Integration](https://code.visualstudio.com/docs/sourcecontrol/overview) (and the [GitHub extension](https://code.visualstudio.com/docs/sourcecontrol/github)). I'm just including the commands here to familiarise you with Git jargon. If you'd like a video explainer, I recommend this video: [Using Git with Visual Studio Code (Official Beginner Tutorial)](https://www.youtube.com/watch?v=i_23KUAEtUM). If you'd like to work from the command line on Windows, use Git Bash (this included with Git when you install it on Windows). Tutorial here: [Git Bash Windows Tutorial for Beginners | Part 1](https://www.youtube.com/watch?v=RBCq2mrXsMk)

### Using branches
If developing new features, it's good practice to create a new branch so that you don't overwrite (or break!) other people's code. To create a new branch based off an existing branch, first switch to the existing branch:
```sh
git switch <branch_name>
```

Then create a new branch named `<new_branch_name>` with
```sh
git branch <new_branch_name>
git switch <new_branch_name>
```

or as a one-liner, `git switch -c <new_branch_name> <base_branch_name>`.

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
You can fetch (i.e. download) changes on the remote repository (GitHub) to your computer using
```sh
git fetch
```
I recommend doing this rather than re-cloning, setting up the virtual environment, etc. each time as it's much faster.

## To-do list for Jack
- Ensure you understand every line of code and each step in the installation process. If there's anything you do not understand, make a note of it and raise it with me in our next session (or text/email)
- ~~Attempt to get some transaction data using Monzo's API~~
- ~~Attempt to save transaction data to file (e.g. using an SQL database)~~
- ~~Determine whether a large JSON file an appropriate data storage format. For context, I've been using Monzo as my primary current account since August 2018 and my `transactions.json` file is ~250k lines long and ~10 MiB in size. I don't think this is an issue as the file will still be < 1 GiB if I live to 100 (assuming my spending habits don't change to much). More important considerations are whether it's efficient to query large JSON files. Of course, we can also reduce the filesize *significantly* by cleaning the transaction data before we save it to disk (i.e. get rid of all unnecessary data).~~
- ~~Create a more helpful redirect page (you may wish to use [Flask](https://flask.palletsprojects.com/en/3.0.x/) here)~~
- Make the redirect page prettier using HTML and CSS.
- ~~Delete unnecessary fields from each transaction. For now, I think we only need `"amount"` and `"category"`. This will make querying `transactions.json` much faster (write about this in your write-up!)~~
- ~~Create a dashboard component~~
- Create more dashboard components! Examples: 
    - Pie chart to visualise spending over a defined period. 
    - Ability to enter budget information (and have this saved to persist across sessions)
- Expense categorisation. Some of this is done by Monzo, but not always very well. Examples: purchases from small businesses, transfers between accounts. It would be nice to handle these better so our dashboard shows us information that's actually useful.
- Write some unit tests. See `tests/README.md` to get started.
