import socket

def has_internet_connection(timeout: float = 3.0) -> bool:
    """
    Checks for an active internet connection by attempting to reach Google's DNS.
    Returns `true` if connections exists.
    
    Args:
        timeout (float): Wait time for checking in seconds.
    """
    try:
        # socket.AF_INET means IPv4, socket.SOCK_STREAM means TCP
        # We attempt to connect to 8.8.8.8 on port 53 (DNS port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(("8.8.8.8", 53))
        sock.close()
        return True
        
    except socket.error:
        return False