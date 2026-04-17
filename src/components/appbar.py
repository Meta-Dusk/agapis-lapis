import flet as ft
from typing import Optional
from dataclasses import field

from components.buttons import ToggleThemeButton

@ft.control
class GlobalAppBar(ft.AppBar):
    actions: Optional[list[ft.Control]] = field(
        default_factory=lambda: [ToggleThemeButton()]
    )
    title: Optional[ft.StrOrControl] = "Agapis Lapis"
    bgcolor: Optional[ft.ColorValue] = ft.Colors.SURFACE_CONTAINER_HIGHEST
    elevation: Optional[ft.Number] = 10
    adaptive: Optional[bool] = True