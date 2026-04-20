import flet as ft
from typing import Optional
from datetime import datetime

from components.eight_ball import EightBall
from components.buttons import AnimatedFAB
from components.text import DefaultText
from components.notifs import SimpleNotif, SimpleErrorNotif
from components.layouts import CenteredColumn
from core.routes import APP_ROUTES_DICT
from core.preferences import Preferences
from core.connection import has_internet_connection
from core.local_database import (
    get_progress_stats, get_unseen_quote, set_all_progress, force_fresh_database)
from core.components import try_update
from managers.apis import APIManager, QuoteData
from managers.bday import BdayManager

class MainApp:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.prefs = Preferences()
        self._is_wifi_connected: bool = False
        self.wifi_btn = ft.IconButton(ft.Icons.WIFI, tooltip="Checks internet connection.")
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
        self.api = APIManager()
        self.quote_txt: DefaultText = None
        self.progress_txt: DefaultText = None
        self.bday_manager = BdayManager(page)
        print("[MainApp] Finished setup 1/2")
    
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
        """Returns tooltips for features that needs an internet connection."""
        return None if not self.is_wifi_connected else "Feature needs an internet connection."
    
    async def check_bday(self) -> None:
        self.bday_manager.greet(await self.prefs.get("user_name"))
    
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
        """**IMPORTANT**: Final MainApp setup."""
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
        theme_toggle_btn.on_long_press = self.ttb_handle_long_press
        self.check_connection(show_notifs=False)
        self.wifi_btn.on_click = lambda _: self.check_connection()
        self.page.appbar.actions.insert(1, self.wifi_btn)
        self.page.update()
        print("[MainApp] Finished setup 2/2")
        
        async def wake_proxy_server() -> None:
            print("[MainApp] Sending silent wake-up ping to proxy server...")
            if await self.api.ping_proxy_server():
                print("[MainApp] Proxy server is awake and ready!")
        
        self.page.run_task(wake_proxy_server)
    
    async def ttb_handle_long_press(self, _) -> None:
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
            content=CenteredColumn(
                controls=[
                    ft.TextField(
                        max_lines=1, max_length=16, value=user_name,
                        on_submit=on_submit, on_change=on_change,
                        hint_text="Woah, what's this?", autofocus=True
                    ),
                ], tight=True
            ),
        )
        self.page.show_dialog(dlg)
    
    async def get_quote_of_the_day(self) -> QuoteData:
        today_str = datetime.now().date().isoformat() # "example: 2026-04-20"
        saved_date = await self.prefs.get("qotd_date")
        
        if saved_date == today_str:
            quote = await self.prefs.get("qotd_quote")
            author = await self.prefs.get("qotd_author")
            return QuoteData(quote=quote, author=author, source="local")
        else:
            new_quote = get_unseen_quote() 
            
            if not new_quote:
                new_quote = QuoteData(
                    quote="Love is the beauty of the soul.", 
                    author="Saint Augustine", 
                    source="local"
                )
            
            await self.prefs.set("qotd_date", today_str)
            await self.prefs.set("qotd_quote", new_quote.quote)
            await self.prefs.set("qotd_author", new_quote.author)
            
            return new_quote
    
    # * === ROUTE VIEWS ===
    def get_home_view(self):
        if self.page.floating_action_button:
            self.page.floating_action_button = None
        self.page.appbar.title = "Home"
        
        qotd_label = DefaultText(
            "☀️ Quote of the Day ✨", size=18,
            color=ft.Colors.TERTIARY, weight=ft.FontWeight.BOLD
        )
        qotd_text = DefaultText(
            "Awaiting the local oracle's response...",
            size=16, color=ft.Colors.SECONDARY
        )
        shim = ft.Shimmer(
            base_color=ft.Colors.SECONDARY,
            highlight_color=ft.Colors.PRIMARY,
            content=qotd_text
        )
        
        qotd_card = ft.Container(
            content=CenteredColumn(
                controls=[
                    qotd_label,
                    ft.Divider(ft.Colors.SECONDARY),
                    shim
                ],
                tight=True, scroll=ft.ScrollMode.ALWAYS
            ),
            padding=20, bgcolor=ft.Colors.SURFACE_CONTAINER,
            border_radius=15, margin=ft.Margin.symmetric(vertical=20)
        )
        
        async def load_home_qotd() -> None:
            quote_data = await self.get_quote_of_the_day()
            qotd_text.value = f'"{quote_data.quote}"\n\n— {quote_data.author}'
            try_update(qotd_text)
            
        self.page.run_task(load_home_qotd)
        
        return CenteredColumn(
            controls=[
                ft.Shimmer(
                    content=ft.Text(
                        "Welcome to Agapis Lapis!",
                        size=32, color=ft.Colors.PRIMARY, weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    base_color=ft.Colors.PRIMARY, highlight_color=ft.Colors.INVERSE_PRIMARY,
                    period=3000
                ),
                qotd_card,
                ft.Text(
                    "Some features require an internet connection.",
                    size=14, color=ft.Colors.OUTLINE, italic=True
                ),
            ], expand=True, key="home"
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
                "🏆 ACHIEVEMENT UNLOCKED 🏆\n"
                f"You have read all {stats.total} local quotes!"
            )
            try_update(self.quote_txt)
            self.progress_txt.visible = True
            self.update_stats_txt()
        
        def fetch_api_quote(text: Optional[QuoteData]) -> None:
            self.quote_txt.value = (
                f"{text.quote}\n— {text.author}"
                if text is not None else
                "Error: Please try again later"
            )
            try_update(self.quote_txt)
            self.progress_txt.visible = False
            try_update(self.progress_txt)
        
        async def on_fab_click(e: ft.Event[AnimatedFAB]) -> None:
            if e.page.floating_action_button:
                e.page.floating_action_button = None
            
            for seg in seg_btn.segments:
                if not seg.disabled:
                    seg.disabled = True
                    
            value = seg_btn.selected[0]
            
            if value != "local":
                spinner.visible = True
                self.quote_txt.value = "Loading new quote..."
            
            e.page.update()
            
            async def perform_fetch():
                if value == "local":
                    await fetch_local_quote()
                elif value == "api_ninjas":
                    fetch_api_quote(await self.api.get_ninja_quote())
                elif value == "cerebras":
                    fetch_api_quote(await self.api.get_cerebras_quote())
                    
                spinner.visible = False
                
                for seg in seg_btn.segments:
                    if seg in self._wifi_req_segs and not self.is_wifi_connected:
                        continue
                    seg.disabled = False
                    
                if e.page.floating_action_button is None:
                    e.page.floating_action_button = AnimatedFAB(on_click=on_fab_click)
                
                e.page.update()
                
            e.page.run_task(perform_fetch)
        
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
    
        return CenteredColumn(
            controls=[
                CenteredColumn(
                    controls=[
                        ft.AnimatedSwitcher(
                            self.quote_txt, duration=100,
                            reverse_duration=100
                        ),
                        self.progress_txt,
                        spinner
                    ], tight=True
                ),
                seg_btn
            ], key="love_quotes_generator", scroll=ft.ScrollMode.ALWAYS
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