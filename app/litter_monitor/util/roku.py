import time
import os
import logging
from roku import Roku

FORMAT = '%(asctime)-15s %(module)s %(name)-8s %(funcName)20s() %(message)s'
logging.basicConfig(format=FORMAT)
logging.getLogger().setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

def launch_app(server_ip: str, app_name: str ='Plex - Free Movies & TV') -> None:
    """Launches the plex app in Roku tv. Powers on roku if it is not on.
    Waits for 3 seconds before returning as it takes some time to 
    launch the app in tv

    Args:
        server_ip (str): IP of the roku tv/stick
        app_name (str, optional): application to launch. Defaults to 'Plex - Stream for Free'.
    """      
    logging.info(f'Connecting to Roku server {server_ip}')
    roku = Roku(server_ip)
    current_app = roku.current_app.name
    logging.info(f'current app is {current_app}')
    if current_app != app_name:
        plex = roku[app_name]
        logging.info(f'Launching app {app_name}')
        plex.launch()
    else:
        logging.info(f'The app is already {app_name}')