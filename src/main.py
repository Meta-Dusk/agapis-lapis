import flet as ft
import asyncio

from setup import setup_main, PC_PLATFORMS
from app import MainApp
from core.routes import AppRoutes
from components.text import DefaultText

@setup_main()
async def main(page: ft.Page):
    app = MainApp(page)
    
    def route_change():
        anim_sw: ft.AnimatedSwitcher = view_container.content
        match (page.route):
            case AppRoutes.root:
                anim_sw.content = app.get_home_view()
            case AppRoutes.love_quotes_generator:
                anim_sw.content = app.get_lqg_view()
            case AppRoutes.magic_eight_ball:
                anim_sw.content = app.get_meb_view()
        
        if page.platform in PC_PLATFORMS:
            page.appbar.title = ft.WindowDragArea(
                content=ft.GestureDetector(
                    content=ft.Text(str(page.appbar.title)),
                    mouse_cursor=ft.MouseCursor.MOVE
                ),
                maximizable=False
            )
        page.update()
    
    view_container = ft.SafeArea(
        content=ft.AnimatedSwitcher(
            content=ft.Column(
                controls=[
                    ft.ProgressRing(width=50, height=50),
                    DefaultText("Loading...")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=400, reverse_duration=200,
            switch_in_curve=ft.AnimationCurve.EASE_OUT
        ),
        expand=True, align=ft.Alignment.CENTER
    )
    
    page.on_route_change = route_change
    page.add(view_container)
    app.setup()
    route_change()
    
    if await app.check_bday():
        await asyncio.sleep(2)
        app.show_bday_dlg()

ft.run(main)