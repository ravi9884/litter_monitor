import plexapi
import time
from plexapi.myplex import MyPlexAccount
def plex_connection(plex_user: str, plex_passwd: str, plex_server_name: str) -> plexapi.server.PlexServer:
    """Returns the plex connection to roku stick/tv. This needs to be initialized once as it takes a long time to return

    Args:
        plex_user (str): roku login username in roku website
        plex_passwd (str): roku password
        plex_server_name (str): local plex server name (or ip) in another rasperry pi

    Returns:
        plexapi.server.PlexServer: connection object to Roku client
    """    
    account = MyPlexAccount(plex_user, plex_passwd)
    plex = account.resource(plex_server_name).connect() 
    return plex

def stream_picture( plex: plexapi.server.PlexServer, client_name: str, library_section='Photos', tmp_playlist = 'test_play_playlist3') -> None:
    """Streams a picture into plex client

    Args:
        plex (plexapi.server.PlexServer): plex connection object
        client_name (str): tv/stick name to project the picture
        library_section (str, optional): I've set it up to photos. Defaults to 'Photos'.
        tmp_playlist (str, optional): Temporary play list name given to roku. Defaults to 'test_play_playlist2'.
    """    
    # returns a PlexServer instance
    try:   
        client=plex.client(client_name)
    except plexapi.exceptions.NotFound:
        time.sleep(5)
        client=plex.client(client_name)
    photos = plex.library.section(library_section)
    photos.update()
    photoalbums = photos.all()
    playlist = plex.createPlaylist(tmp_playlist, photoalbums)
    try:
        client.playMedia(playlist)
    finally:
        playlist.delete()
