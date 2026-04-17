import flet as ft

from setup import setup_main


@setup_main()
def main(page: ft.Page) -> None:
    page.add(ft.Text("Hello"))

ft.run(main)