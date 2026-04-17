import flet as ft
from typing import Optional

@ft.control
class DefaultText(ft.Text):
    size: Optional[ft.Number] = 22
    text_align: ft.TextAlign = ft.TextAlign.CENTER