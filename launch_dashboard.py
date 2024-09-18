import webbrowser
import threading
from src.app import run_app

if __name__ == "__main__":
    # Start the FastHTML app in a separate thread
    server_thread = threading.Thread(target=run_app)
    server_thread.start()

    # Open app in default browser
    webbrowser.open("http://localhost:5001/")
