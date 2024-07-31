from pathlib import Path
import webbrowser

from src.app import initialise_app, app

if __name__ == "__main__":
    # Determine initial pathname based on whether `credentials.json` already exists
    if Path("credentials.json").exists():
        initial_pathname = "dashboard"
    else:
        initial_pathname = "credentials"

    # Initialise the app and open the web browser
    initialise_app()
    webbrowser.open(f"http://127.0.0.1:8050/{initial_pathname}")
    app.run_server(debug=False, port=8050)
    
