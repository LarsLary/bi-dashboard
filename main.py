import os
import sys
import webbrowser
from threading import Thread
from time import sleep

from dash_app import interaction


def open_browser(port_num: int):
    """
    Parameters
    ----------
    port_num : int which represents a port number

    opens a browser with a specified ip and port

    Returns
    -------
    None
    """
    sleep(1)
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new(f"http://127.0.0.1:{port_num}/")
    sys.exit()  # Close thread


if __name__ == "__main__":
    port = 8050
    Thread(target=open_browser, args=[port]).start()
    interaction.app.run_server(
        # Set debug false when deploy
        debug=True, port=port
    )
