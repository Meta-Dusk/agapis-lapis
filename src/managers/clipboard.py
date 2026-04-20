import flet as ft

from components.notifs import SimpleNotif

class ClipboardManager:
    def __init__(self, page: ft.Page, *, show_notifs: bool = False):
        self.page = page
        self.show_notifs = show_notifs
    
    async def set_to_clipboard(self, value: str) -> None:
        await ft.Clipboard().set(value)
        if not self.show_notifs: return
        self.page.show_dialog(SimpleNotif("Text copied to clipboard!"))