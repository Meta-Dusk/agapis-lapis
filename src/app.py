import flet as ft
from datetime import datetime

from components.eight_ball import EightBall
from core.routes import APP_ROUTES_DICT
from core.preferences import Preferences
from core.assets import Assets
from core.connection import has_internet_connection

class MainApp:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.prefs = Preferences()
        self.is_wifi_connected: bool = False
        self.wifi_btn = ft.IconButton(ft.Icons.WIFI)
    
    async def check_bday(self) -> None:
        now = datetime.now()
        user_name = await self.prefs.get("user_name")
        if user_name is None: return
        user_name = user_name.lower()
        if now.month != 4 or now.day != 22 or user_name != "isaac": return
        
        self.page.show_dialog(
            ft.AlertDialog(
                title="Happy Birthday, Isaac!",
                content=ft.Image(
                    Assets.images.bday_cake, fit=ft.BoxFit.COVER,
                    width=self.page.width * 0.25,
                ),
                actions=[
                    ft.Button(
                        content="Thanks", icon=ft.Icons.CAKE_ROUNDED,
                        on_click=lambda e: e.page.pop_dialog()
                    )
                ]
            )
        )
    
    def check_connection(self, *, show_notifs: bool = True) -> None:
        if self.is_wifi_connected:
            if not show_notifs: return
            self.page.show_dialog(
                ft.SnackBar("WiFi is already connected!", duration=2000)
            )
            return
        
        if show_notifs:
            self.page.show_dialog(ft.SnackBar("Attempting connection to WiFi..."))
            
        self.is_wifi_connected = has_internet_connection()
        self.wifi_btn.icon = (
            ft.Icons.WIFI if self.is_wifi_connected else ft.Icos.WIFI_OFF
        )
        try: self.wifi_btn.update()
        except RuntimeError: pass
        
        if not show_notifs: return
        if not self.is_wifi_connected:
            self.page.show_dialog(ft.SnackBar("Connection failed!", duration=2000))
            return
        self.page.show_dialog(ft.SnackBar("Connection successful!", duration=2000))
    
    def setup(self) -> None:
        """Adds other page-specific configurations."""
        self.page.drawer = ft.NavigationDrawer(
            controls=[
                ft.NavigationDrawerDestination(icon=ft.Icons.HOME_SHARP, label="Home"),
                ft.NavigationDrawerDestination(icon=ft.Icons.FAVORITE_SHARP, label="Love Quotes Generator"),
                ft.NavigationDrawerDestination(icon=ft.Icons.QUESTION_ANSWER_SHARP, label="Magic Eight Ball"),
            ],
            tile_padding=ft.Padding(top=10),
            on_change=lambda e: self.page.run_task(
                self.page.push_route, APP_ROUTES_DICT.get(e.control.selected_index)
            )
        )
        theme_toggle_btn: ft.IconButton = self.page.appbar.actions[0]
        theme_toggle_btn.on_long_press = self.on_long_press_ttb
        self.check_connection(show_notifs=False)
        self.wifi_btn.on_click = lambda _: self.check_connection()
        self.page.appbar.actions.insert(1, self.wifi_btn)
    
    async def on_long_press_ttb(self, _) -> None:
        async def on_submit(e: ft.Event[ft.TextField]) -> None:
            data: str = e.data
            data.strip()
            if data is None or data == "":
                e.control.error = "Name cannot be empty!"
                e.control.update()
                return
            
            e.control.error = ""
            e.control.update()
            e.page.pop_dialog()
            
            if data.lower() == "clear":
                success = await self.prefs.clear()
                e.page.show_dialog(
                    ft.SnackBar(
                        "Cleared all preferences!"
                        if success else
                        "Failed to clear all preferences...",
                        duration=3000
                    )
                )
                e.control.value = ""
                e.control.update()
                return
            
            success = await self.prefs.set("user_name", data)
            e.page.show_dialog(
                ft.SnackBar(
                    f"Successfully set user_name to: {data}"
                    if success else
                    f"Failed to set user_name to: {data}",
                    duration=3000
                )
            )
            await self.check_bday()
        
        user_name = await self.prefs.get("user_name")
        dlg = ft.AlertDialog(
            title="Enter Your Name",
            content=ft.TextField(
                max_lines=1, max_length=16, on_submit=on_submit,
                value=user_name
            ),
        )
        self.page.show_dialog(dlg)
    
    def get_home_view(self):
        return ft.Column(
            controls=[
                ft.Text(
                    "Welcome to Agapis Lapis!",
                    size=32, color=ft.Colors.PRIMARY, weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "To start, please open the navigation menu at the top-left of the screen.",
                    size=16, color=ft.Colors.SECONDARY,
                ),
                ft.Text(
                    "Some features requires an internet connection.",
                    size=16, color=ft.Colors.SECONDARY, italic=True
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True, key="home"
        )

    def get_lqg_view(self):
        return ft.Column(
            controls=[
                ft.Text("Love Quotes Generator", size=64, color=ft.Colors.PRIMARY),
                ft.SegmentedButton(
                    on_change=lambda e: print(e),
                    selected_icon=ft.Icons.CHECK_SHARP,
                    selected=["local"],
                    segments=[
                        ft.Segment(
                            value="local",
                            label="Local",
                            icon=ft.Icons.FOLDER_SHARED_SHARP
                        ),
                        ft.Segment(
                            value="cerebras",
                            label="Cerebras",
                            icon=ft.Icons.WEB_ASSET_SHARP
                        ),
                        ft.Segment(
                            value="api_ninjas",
                            label="API Ninjas",
                            icon=ft.Icons.PERSON_SHARP
                        )
                    ]
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            key="love_quotes_generator"
        )

    def get_meb_view(self):
        return ft.Container(
            content=EightBall(),
            alignment=ft.Alignment.CENTER,
            expand=True, key="magic_eight_ball"
        )