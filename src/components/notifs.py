import flet as ft
from typing import Optional
from components.text import DefaultText

@ft.control
class SimpleNotif(ft.SnackBar):
    duration: ft.DurationValue = 3
    
    def build(self):
        if isinstance(self.content, ft.Text):
            text: str = self.content.value
            self.content = DefaultText(text)

@ft.control
class SimpleErrorNotif(ft.SnackBar):
    duration: ft.DurationValue = 3
    bgcolor: Optional[ft.ColorValue] = ft.Colors.ERROR
    
    def build(self):
        if isinstance(self.content, ft.Text):
            text: str = self.content.value
            self.content = DefaultText(text, color=ft.Colors.ON_ERROR)