import webbrowser

from src.app import initialise_app, app

if __name__ == "__main__":
    # Initialise the app and open the web browser
    initialise_app()
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server(debug=False, port=8050)
