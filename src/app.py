import flet as ft
from datetime import datetime

from components.eight_ball import EightBall
from core.routes import APP_ROUTES_DICT
from core.preferences import Preferences

class MainApp:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.prefs = Preferences()
    
    async def check_bday(self) -> None:
        now = datetime.now()
        user_name = await self.prefs.get("user_name")
        if user_name is None: return
        user_name = user_name.lower()
        if now.month == 4 and now.day == 22 and user_name == "isaac":
            print("Happy birthday!")
    
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
        theme_toggle_btn.on_long_press = self.on_long_press
    
    async def on_long_press(self, _) -> None:
        async def on_submit(e: ft.Event[ft.TextField]) -> None:
            data: str = e.data
            data.strip()
            if data is None or data == "":
                e.control.error = "Name cannot be empty!"
                e.control.update()
            else:
                e.control.error = ""
                e.control.update()
                e.page.pop_dialog()
                if await self.prefs.set("user_name", data):
                    e.page.show_dialog(
                        ft.SnackBar(f"Successfully set user_name to: {data}")
                    )
                else:
                    e.page.show_dialog(
                        ft.SnackBar(f"Failed to set user_name to: {data}")
                    )
        
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
                    "To start, please open the navigation menu to the top-left of the screen.",
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