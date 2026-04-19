import flet as ft

from core.test_handler import setup_test
from core.connection import has_internet_connection

@setup_test("WiFi Connection Test")
def main(page: ft.Page) -> None:
    test_text = ft.Icon(
        icon=ft.Icons.WIFI if has_internet_connection() else ft.Icons.WIFI_OFF,
        size=64, color=ft.Colors.PRIMARY
    )
    page.add(test_text)

if __name__ == "__main__":
    ft.run(main)