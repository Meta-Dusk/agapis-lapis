import flet as ft
import socket

from tests.test_handler import setup_test

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

@setup_test("WiFi Connection Test")
def main(page: ft.Page) -> None:
    test_text = ft.Icon(
        icon=ft.Icons.WIFI if has_internet_connection() else ft.Icons.WIFI_OFF,
        size=64, color=ft.Colors.PRIMARY
    )
    page.add(test_text)

if __name__ == "__main__":
    ft.run(main)