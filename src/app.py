import flet as ft
from datetime import datetime
from typing import Optional

from components.eight_ball import EightBall
from components.buttons import AnimatedFAB
from components.text import DefaultText
from components.notifs import SimpleNotif, SimpleErrorNotif
from core.routes import APP_ROUTES_DICT
from core.preferences import Preferences
from core.assets import Assets
from core.connection import has_internet_connection
from core.local_database import get_progress_stats, get_unseen_quote, set_all_progress, force_fresh_database
from core.components import try_update
from managers.apis import APIManager

class MainApp:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.prefs = Preferences()
        self._is_wifi_connected: bool = False
        self.wifi_btn = ft.IconButton(ft.Icons.WIFI)
        self._wifi_req_segs = [
            ft.Segment(
                value="cerebras", label="Cerebras",
                icon=ft.Icons.WEB_ASSET_SHARP,
                tooltip=self.get_wifi_req_tooltip
            ),
            ft.Segment(
                value="api_ninjas", label="API Ninjas",
                icon=ft.Icons.PERSON_SHARP,
                tooltip=self.get_wifi_req_tooltip
            )
        ]
        self.wifi_req_ctrls: list[ft.Control] = [*self._wifi_req_segs]
        self.api: APIManager = None
        self.quote_txt: DefaultText = None
        self.progress_txt: DefaultText = None
        print("[MainApp] Finished setup 1/3")
    
    @property
    def is_wifi_connected(self) -> bool:
        return self._is_wifi_connected
    
    @is_wifi_connected.setter
    def is_wifi_connected(self, value: bool) -> None:
        self._is_wifi_connected = value
        print(f"Setting wifi connection to: {value}")
        if len(self.wifi_req_ctrls) == 0: return
        print(f"{"enabling" if value else "disabling"} controls...")
        for control in self.wifi_req_ctrls:
            control.disabled = not value
            try_update(control)
        self.wifi_btn.icon = (
            ft.Icons.WIFI if value else ft.Icons.WIFI_OFF
        )
        try_update(self.wifi_btn)
    
    @property
    def get_wifi_req_tooltip(self) -> Optional[str]:
        return None if self.is_wifi_connected else "Feature needs a WiFI connection."
    
    async def check_bday(self) -> bool:
        now = datetime.now()
        user_name = await self.prefs.get("user_name")
        if user_name is None: return
        user_name = user_name.lower()
        if now.month != 4 or now.day != 22 or user_name != "isaac":
            return True
        return False
    
    def show_bday_dlg(self) -> None:
        dlg = ft.AlertDialog(
            title="Happy Birthday, Isaac!",
            content=ft.Column(
                controls=[
                    ft.Image(
                        Assets.images.bday_cake, fit=ft.BoxFit.COVER,
                        width=self.page.width * 0.25,
                    ),
                    ft.Text(
                        "This post was made by MetaDusk", size=16,
                        color=ft.Colors.SECONDARY, italic=True,
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True
            ),
            actions=[
                ft.Button(
                    content="Thanks", icon=ft.Icons.CAKE_ROUNDED,
                    on_click=lambda e: e.page.pop_dialog()
                )
            ]
        )
        self.page.show_dialog(dlg)
    
    def check_connection(self, *, show_notifs: bool = True) -> None:
        if self.is_wifi_connected:
            if not show_notifs: return
            self.page.show_dialog(
                SimpleNotif("WiFi is already connected!", duration=2000)
            )
            return
        
        if show_notifs:
            self.page.show_dialog(SimpleNotif("Attempting connection to WiFi..."))
            
        self.is_wifi_connected = has_internet_connection()
        self.wifi_btn.icon = (
            ft.Icons.WIFI if self.is_wifi_connected else ft.Icons.WIFI_OFF
        )
        try_update(self.wifi_btn)
        
        if not show_notifs: return
        if not self.is_wifi_connected:
            self.page.show_dialog(SimpleErrorNotif("Connection failed!", duration=2000))
            return
        self.page.show_dialog(SimpleNotif("Connection successful!", duration=2000))
    
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
        self.page.update()
        print("[MainApp] Finished setup 2/3")
    
    async def start_apis(self) -> None:
        self.api = APIManager()
        self.api.start()
        print("[MainApp] Finished setup 3/3")
    
    async def on_long_press_ttb(self, _) -> None:
        async def on_submit(e: ft.Event[ft.TextField]) -> None:
            data: str = e.data
            data.strip()
            if data is None or data == "":
                e.control.error = "Name cannot be empty!"
                e.control.update()
                return
            
            def clear_val(*, pop_dlg: bool = True) -> None:
                e.control.value = ""
                e.control.error = None
                e.control.update()
                if not pop_dlg: return
                e.page.pop_dialog()
            
            if data == "prefs.clear":
                success = await self.prefs.clear()
                clear_val()
                e.page.show_dialog(
                    SimpleNotif(
                        "Cleared all preferences!"
                        if success else
                        "Failed to clear all preferences...",
                        duration=3000
                    )
                )
                return
            
            elif data == "conn.disable":
                self.is_wifi_connected = False
                clear_val()
                return
            
            elif data == "db.reset":
                force_fresh_database()
                clear_val()
                self.quote_txt.value = "Press the heart to get a quote!"
                try_update(self.quote_txt)
                self.update_stats_txt()
                return
            
            elif data == "progress.reset":
                set_all_progress(0)
                clear_val()
                return
            
            elif data == "progress.finish":
                set_all_progress(1)
                clear_val()
                return
            
            elif data == "help.show":
                hidden_info.value = (
                    "prefs.clear\n"
                    "conn.disable\n"
                    "db.reset\n"
                    "progress.reset\n"
                    "progress.finish\n"
                    "help.show"
                )
                try_update(hidden_info)
                clear_val(pop_dlg=False)
                return
            
            e.control.error = None
            e.control.update()
            e.page.pop_dialog()
            
            success = await self.prefs.set("user_name", data)
            e.page.show_dialog(
                SimpleNotif(
                    f"Successfully set user_name to: {data}"
                    if success else
                    f"Failed to set user_name to: {data}",
                    duration=3000
                )
            )
            await self.check_bday()
        
        def on_change(e: ft.Event[ft.TextField]) -> None:
            data: str = e.data
            add_ctrl: bool = True
            if data == "prefs.clear":
                hidden_info.value = "Clears all preferences in this device."
            elif data == "conn.disable":
                hidden_info.value = "Disables the wifi connection of this device."
            elif data == "db.reset":
                hidden_info.value = "Makes a fresh copy of the local database."
            elif data == "progress.reset":
                hidden_info.value = "Resets the local quotes progress."
            elif data == "progress.finish":
                hidden_info.value = "Finishes all the local quotes progress."
            elif data == "help.show":
                hidden_info.value = "Shows all available commands."
            else:
                hidden_info.value = ""
                add_ctrl = False
            
            col: ft.Column = dlg.content
            if add_ctrl:
                col.controls.append(hidden_info)
                col.update()
            else:
                try:
                    col.controls.remove(hidden_info)
                    col.update()
                except ValueError: pass
        
        user_name = await self.prefs.get("user_name")
        hidden_info = ft.Text(color=ft.Colors.TERTIARY, italic=True, size=14)
        dlg = ft.AlertDialog(
            title="Enter Your Name",
            content=ft.Column(
                controls=[
                    ft.TextField(
                        max_lines=1, max_length=16, value=user_name,
                        on_submit=on_submit, on_change=on_change,
                        hint_text="Woah, what's this?", autofocus=True
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True
            ),
        )
        self.page.show_dialog(dlg)
    
    def get_home_view(self):
        if self.page.floating_action_button:
            self.page.floating_action_button = None
        self.page.appbar.title = "Home"
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

    def update_stats_txt(self, update: bool = True) -> None:
        stats = get_progress_stats()
        self.progress_txt.value = f"Discovered: {stats.seen} / {stats.total}"
        if update: try_update(self.progress_txt)
    
    def get_lqg_view(self):
        async def fetch_local_quote() -> None:
            stats = get_progress_stats()
            quote = get_unseen_quote()
            self.quote_txt.value = (
                f"{quote.quote}\n— {quote.author}"
                if quote else
                f"🏆 ACHIEVEMENT UNLOCKED 🏆\nYou have read all {stats.total} quotes!"
            )
            try_update(self.quote_txt)
            self.progress_txt.visible = True
            self.update_stats_txt()
        
        def fetch_api_quote(text: str) -> None:
            self.quote_txt.value = text
            try_update(self.quote_txt)
            self.progress_txt.visible = False
            try_update(self.progress_txt)
        
        async def on_fab_click(e: ft.Event[AnimatedFAB]) -> None:
            if e.page.floating_action_button:
                e.page.floating_action_button = None
            e.page.update()
            for seg in seg_btn.segments:
                if seg.disabled: continue
                seg.disabled = True
            try_update(seg_btn)
                
            value = seg_btn.selected[0]
            if value == "local":
                await fetch_local_quote()
            else:
                spinner.visible = True
                try_update(spinner)
                self.quote_txt.value = "Loading new quote..."
                try_update(self.quote_txt)
                
            if value == "api_ninjas":
                fetch_api_quote(await self.api.get_ninja_quote())
            elif value == "cerebras":
                fetch_api_quote(await self.api.get_cerebras_quote())
                
            spinner.visible = False
            try_update(spinner)
            for seg in seg_btn.segments:
                if (
                    seg in self._wifi_req_segs and
                    not self.is_wifi_connected and
                    seg.disabled
                ):
                    continue
                seg.disabled = False
            try_update(seg_btn)
            if e.page.floating_action_button is None:
                e.page.floating_action_button = AnimatedFAB(on_click=on_fab_click)
            e.page.update()
        
        def on_change(e: ft.Event[ft.SegmentedButton]) -> None:
            self.check_connection(show_notifs=False)
            if e.control.selected[0] != "local":
                self.progress_txt.visible = False
            else:
                self.progress_txt.visible = True
            try_update(self.progress_txt)
        
        self.quote_txt = DefaultText("Press the heart to get a quote!")
        spinner = ft.ProgressRing(width=50, height=50, visible=False)
        stats = get_progress_stats()
        self.progress_txt = DefaultText(
            f"Discovered: {stats.seen} / {stats.total}",
            size=14, color=ft.Colors.OUTLINE
        )
        
        if self.page.floating_action_button is None:
            self.page.floating_action_button = AnimatedFAB(on_click=on_fab_click)
        self.page.appbar.title = "Love Quotes Generator"
        
        seg_btn = ft.SegmentedButton(
            on_change=on_change,
            selected_icon=ft.Icons.CHECK_SHARP,
            selected=["local"],
            segments=[
                ft.Segment(
                    value="local", label="Local",
                    icon=ft.Icons.FOLDER_SHARED_SHARP,
                    tooltip="Pulls a random quote from the local database."
                ),
                *self._wifi_req_segs
            ]
        )
    
        return ft.Column(
            controls=[
                ft.Column(
                    controls=[
                        ft.AnimatedSwitcher(
                            self.quote_txt, duration=100,
                            reverse_duration=100
                        ),
                        self.progress_txt,
                        spinner
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True
                ),
                seg_btn
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            key="love_quotes_generator"
        )

    def get_meb_view(self):
        if self.page.floating_action_button:
            self.page.floating_action_button = None
        self.page.appbar.title = "Magic Eight Ball"
        return ft.Container(
            content=EightBall(),
            alignment=ft.Alignment.CENTER,
            expand=True, key="magic_eight_ball"
        )