# Developing the app (i.e. using Git and GitHub)
All of this can be achieved with a GUI using [VS Code's Git Integration](https://code.visualstudio.com/docs/sourcecontrol/overview) (and the [GitHub extension](https://code.visualstudio.com/docs/sourcecontrol/github)). I'm just including the commands here to familiarise you with Git jargon. If you'd like a video explainer, I recommend this video: [Using Git with Visual Studio Code (Official Beginner Tutorial)](https://www.youtube.com/watch?v=i_23KUAEtUM). If you'd like to work from the command line on Windows, use Git Bash (this included with Git when you install it on Windows). Tutorial here: [Git Bash Windows Tutorial for Beginners | Part 1](https://www.youtube.com/watch?v=RBCq2mrXsMk)

## Using branches
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

## Committing your changes
To commit your changes, you first need to `add` (i.e. stage them), then commit them with a helpful message:
```sh
git add my_script.py
git commit -m "Add Google Calendar API"
```

As a general rule, commit titles should be short and declaritive. Advice on what *not* to do here: [How to commit better with Git](https://www.youtube.com/watch?v=Hlp-9cdImSM).


## Pushing your changes to the remote repository
You can push your changes to the remote repository (GitHub) using
```sh
git push <remote_name> <local_branch_name>
```

The remote name will usually be `origin`. As an example, a `push` command I used recently used was: 
```sh
git push origin refactor
```

## Updating your local repository
You can fetch (i.e. download) changes on the remote repository (GitHub) to your computer using
```sh
git fetch
```
I recommend doing this rather than re-cloning, setting up the virtual environment, etc. each time as it's much faster.
